# Python app for Zenduty and AWS
- This app integrates Zenduty with AWS using the AWS SDK for Python called Boto3
- It updates an IAM user group in AWS with whoever is on call in Zenduty schedule

## Zenduty API
- Gets the appropriate team id
- Gets the user who is on-call
#### Zenduty Workflow
- team -> service-> escalation policy -> schedule -> user on call at that moment

## AWS API
- Add the on call IAM user to prod-team IAM user group
  - since user in zenduty has the same username in AWS - we can use that to add them to the IAM user group

## Notes
- There is already an integration for AWS on Zenduty that allows Cloudtrail, Cloudwatch, Guardduty or Security Hub events to be routed through Zenduty
- This app is to show an explicit example of using boto3 with Zenduty


## Getting Started
### Prerequisites
- AWS Account
- Zenduty account

### Setup
- Copy `sample.env` to `.env`
```
cp sample.env .env
```
- App can be run with:
```
python botozenduty.py
```

### API
- `/getOnCallUser`
  - Get user who is on call from zenduty
- `/updateProdTeam`
  - Add on call user to prod IAM user group
