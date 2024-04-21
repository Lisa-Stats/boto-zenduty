from bottle import Bottle, default_app, route, run, template
import botocore as botocore
import boto3 as boto3
from dotenv import load_dotenv, find_dotenv
import logging
import requests
import os

load_dotenv(find_dotenv())

ZENDUTY_SECRET_KEY = os.environ.get("ZENDUTY_ACCESS_TOKEN")

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

prod_user_group = 'prod-team'

def remove_users_from_user_group(group):
    """remove old user(s) from the prod-team IAM user group"""
    try:
        logger.info(f'Calling IAM user group: {group}')
        client = boto3.client('iam')
    except botocore.exceptions.ClientError as err:
        raise SystemExit(f"boto3 error: {err}")
    except botocore.exceptions.EndpointConnectionError as err:
        raise SystemExit(f"AWS Endpoint Connection Error: {err}")

    response = client.get_group(GroupName=group)
    for user in response['Users']:
        username = user['UserName']
        logger.info(f'Removing {username} from {group}')
        response = client.remove_user_from_group(GroupName=group, UserName=user['UserName'])
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            logger.info(f'Successfully removed user: {username} from group: {group}')
            return username
            # return f'Successfully removed user: {username} from group: {group}'


def get_team_id():
    """get appropriate team id"""
    url = 'https://www.zenduty.com' + '/api/account/teams'
    headers = {'Authorization': 'Token ' + ZENDUTY_SECRET_KEY}
    try:
        r = requests.get(url, headers=headers, timeout=5)
        r.raise_for_status()
        team_name = r.json()[0]['name']
        logger.info(f'Getting team id for Zenduty team: {team_name}')

    except requests.exceptions.ConnectionError as err:
        raise SystemExit(f"Error Connecting: {err}")
    except requests.exceptions.Timeout as err:
        raise SystemExit(f"Timeout error: {err}")
    except requests.exceptions.HTTPError as err:
        raise SystemExit(f"HTTP err: {err}")
    except requests.exceptions.RequestException as err:
        raise SystemExit(f"Oops something else: {err}")

    team_id = r.json()[0]['unique_id']
    return team_id


# team -> service-> escalation policy -> schedule -> user on call at that moment
def get_on_call_user_email():
    """get email of user who is on-call from zenduty"""
    team_id = get_team_id()
    url = 'https://www.zenduty.com' + '/api/v2/account/teams/' + team_id + '/oncall/'
    headers = {'Authorization': 'Token ' + ZENDUTY_SECRET_KEY}
    try:
        logger.info(f'Getting user from Zenduty')
        r = requests.get(url, headers=headers, timeout=5)
        r.raise_for_status()

    except requests.exceptions.ConnectionError as err:
        raise SystemExit(f"Error Connecting: {err}")
    except requests.exceptions.Timeout as err:
        raise SystemExit(f"Timeout error: {err}")
    except requests.exceptions.HTTPError as err:
        raise SystemExit(f"HTTP err: {err}")
    except requests.exceptions.RequestException as err:
        raise SystemExit(f"Oops something else: {err}")

    # we know the first oncall object will be the on call person at that time,
    # since the escalation policy has the team on call schedule as the user to be notified
    team = r.json()[0]['oncalls'][0]['oncalls'][0]['email']
    return team.split('@')[0]


# add the on-call user to prod-team IAM user group
def add_user_to_user_group(group):
    """add the on-call IAM user to the user group in AWS
    FYI: since user in zenduty has the same username in AWS - we can use that to add them to the IAM user group"""
    user_on_call = get_on_call_user_email()
    try:
        logger.info(f'Calling IAM user group: {group}')
        client = boto3.client('iam')
    except botocore.exceptions.ClientError as err:
        raise SystemExit(f"boto3 error: {err}")
    except botocore.exceptions.EndpointConnectionError as err:
        raise SystemExit(f"AWS Endpoint Connection Error: {err}")

    logger.info(f'Attempting to add user: {user_on_call} to group: {group}')
    response = client.add_user_to_group(GroupName=group, UserName=user_on_call)
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        logger.info(f'Successfully added user: {user_on_call} to group: {group}')
        return user_on_call
        # return f'Successfully added user: {user_on_call} to group: {group}'

@route('/')
def homepage():
    """homepage"""
    return 'Welcome!'

@route('/getOnCallUser')
def get_on_call_user():
    """get user who is on-call from zenduty"""
    team_id = get_team_id()
    url = 'https://www.zenduty.com' + '/api/v2/account/teams/' + team_id + '/oncall/'
    headers = {'Authorization': 'Token ' + ZENDUTY_SECRET_KEY}
    try:
        logger.info(f'Getting user from Zenduty')
        r = requests.get(url, headers=headers, timeout=5)
        r.raise_for_status()

    except requests.exceptions.ConnectionError as err:
        raise SystemExit(f"Error Connecting: {err}")
    except requests.exceptions.Timeout as err:
        raise SystemExit(f"Timeout error: {err}")
    except requests.exceptions.HTTPError as err:
        raise SystemExit(f"HTTP err: {err}")
    except requests.exceptions.RequestException as err:
        raise SystemExit(f"Oops something else: {err}")

    # we know the first oncall object will be the on call person at that time,
    # since the escalation policy has the team on call schedule as the user to be notified
    team = r.json()[0]['oncalls'][0]['oncalls'][0]
    first_name = team['first_name']
    last_name = team['last_name']
    return template('On call user: {{first_name}} {{last_name}}', first_name=first_name, last_name=last_name)


@route('/updateProdTeam')
def update_prod_team():
    # first, remove all users from IAM user group
    removed_user = remove_users_from_user_group(prod_user_group)
    # add on call user to prod IAM user group
    added_user = add_user_to_user_group(prod_user_group)
    return template('Previous on call user: {{removed}} || Current on call user:{{current}}',
                    removed=removed_user,
                    current=added_user)

if __name__ == "__main__":
    run(host='localhost', port=8080, debug=True)
