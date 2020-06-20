# pylint: disable=global-statement,redefined-outer-name
""" Script used to create|delete AWS Cognito user """
import argparse
import sys


def create_user(client, profile, user):
    """ Creates a new user in the specified user pool """
    response = client.admin_create_user(
        UserPoolId=profile.pool_id,
        Username=user.email,
        UserAttributes=[
            {"Name": "email", "Value": user.email},
            {"Name": "custom:name", "Value": user.name},
        ],
        ValidationData=[{"Name": "string", "Value": "string"},],
        MessageAction="RESEND",
        DesiredDeliveryMediums=["EMAIL"],
    )
    return response


def delete_user(client, profile, user):
    """ Deletes a user from the pool """
    response = client.admin_delete_user(UserPoolId=profile.pool_id, Username=user.email)
    return response


def parse_arguments():
    """ Parse Arguments """
    parser = argparse.ArgumentParser(
        description="AWS Cognito User Command Line",
        usage="cognito_user.py [-h] [-c|-d] user_file aws_profile",
    )
    parser.add_argument(
        "-c",
        "--create",
        action="store_true",
        default=True,
        help="Create users listed in the file (default)",
    )
    parser.add_argument(
        "-d",
        "--delete",
        action="store_true",
        default=False,
        help="Delete users listed in the file",
    )
    parser.add_argument(
        "user_file", help="The file contains user information for AWS Cognito",
    )
    parser.add_argument("aws_profile", help="The file contains AWS profile")

    args = parser.parse_args()
    if args.create and args.delete:
        parser.print_help()
        sys.exit(2)

    return parser.parse_args()


def parse_file():
    """ Parse user file to read user information """
    users = []
    return users


if __name__ == "__main__":
    args = parse_arguments()
    user_file = args.user_file
    aws_profile = args.aws_profile
    # client = boto3.client(
    #     "cognito-idp",
    #     aws_access_key_id="AKIAIO5FODNN7EXAMPLE",
    #     aws_secret_access_key="ABCDEF+c2L7yXeGvUyrPgYsDnWRRC1AYEXAMPLE",
    # )
