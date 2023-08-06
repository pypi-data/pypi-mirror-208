import click
import boto3
import requests
from os import environ
import time

def create_role(iam):
    role_name = 'availabl-access'

    try:
        # create the role
        role = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument="""{
            "Version": "2012-10-17",
            "Statement": [
              {
                "Action": "sts:AssumeRole",
                "Effect": "Allow",
                "Sid": "",
                "Principal": {
                  "AWS": [
                    "arn:aws:iam::155313039464:root"
                  ]
                }
              }
            ]
          }"""
        )
    except Exception as e:
        #  if the role already exists:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print('Role already exists')
            role = iam.get_role(RoleName=role_name)
        else:
            raise e

    # attach the policy
    iam.attach_role_policy(
        RoleName=role_name,
        PolicyArn='arn:aws:iam::aws:policy/CloudWatchReadOnlyAccess'
    )

    return role['Role']['Arn']

@click.command()
@click.option('--profile', required=False, help='The AWS profile to use.')
@click.option('--region', required=True, help='The AWS region to use. eg us-east-1')
@click.option('--api-key', required=True, help='Your availabl api key.')
@click.option('--app-id', required=True, help='Your availabl App ID.')
@click.option('--role-arn', required=False, help='The ARN of the role to use. If not provided, a new role will be created.')
def run(profile, region, api_key, app_id, role_arn):
    # determine the current aws account
    session = boto3.Session(profile_name=profile)
    client = session.client('sts')
    account_id = client.get_caller_identity().get('Account')

    click.echo('Granting availabl access to telemetry data in : {} {} ...'.format(
        account_id, region))

    if not role_arn:
        click.confirm('Confirm the creation of a new IAM role with CloudWatchReadOnlyAccess'.format(
            account_id), abort=True)

    # create a IAM role with the availabl policy
    iam = session.client('iam')
    
    if not role_arn:
        role_arn = create_role(iam)

    click.echo('Registering role {} with availabl'.format(role_arn))

    headers = {
        'x-request-timestamp': str(round(time.time() * 1000)),
        'x-app-id': app_id,
        'x-api-key': api_key,
        'Content-Type': 'application/json'
    }

    ENDPOINT = environ.get('CLI_ENDPOINT', 'https://app.availabl.co/api/internal/cli')

    try:
        # register the role with availabl
        response = requests.post(
            ENDPOINT,
            json={
                'roleArn': role_arn,
                'region': region,
                'index': True
            }, 
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            click.echo('Success! Your availabl account is now connected to AWS.')
        else:
            click.echo('Error: {}'.format(response.text))
    except requests.exceptions.RequestException as e:
        click.echo('Error: {}'.format(e))

if __name__ == '__main__':
    run()
