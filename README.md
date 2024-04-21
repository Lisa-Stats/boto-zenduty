# Python app for Zenduty and AWS
- This app integrates Zenduty with AWS using the AWS SDK for Python called Boto
- It updates an IAM User group in AWS with whoever is on-call in Zenduty

## Zenduty API
- Gets the appropriate team id
- Gets the user who is on-call
### Zenduty flow
- team -> service-> escalation policy -> schedule -> user on call at that moment

## AWS API
- Add the on-call IAM user to prod-team IAM user group
  - since user in zenduty has the same username in AWS - we can use that to add them to the IAM user group

## Notes
- There is already an integration for AWS on Zenduty that allows Cloudtrail, Cloudwatch, Guardduty or Security Hub events to be routed through Zenduty
- This app is to show an explicit example of using boto3 with Zenduty
