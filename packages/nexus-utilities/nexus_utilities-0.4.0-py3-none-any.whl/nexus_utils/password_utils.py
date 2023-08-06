"""Password-related utilities"""
import boto3
import os
from botocore.exceptions import ClientError
import keyring

def get_password(password_method, password_key, account_name=None, access_key=None, secret_key=None, endpoint_url=None, region_name=None, password_path=None, encoding='utf-8'):
    """Retrieve password based on method provided"""
    if password_method == 'keyring':
        try:
            response = keyring.get_password(account_name, password_key)
        except Exception as e:
            print(f"Error retrieving secret: {e}")
            return None
        else:
            secret_value = response
            return secret_value
        
    elif password_method == 'ssm':
        access_key = os.environ.get('AWS_SSM_ACCESS_KEY_ID') or access_key
        secret_key = os.environ.get('AWS_SSM_SECRETACCESS_KEY_ID') or secret_key
        ssm_endpoint_url = os.environ.get('AWS_SSM_ENDPOINT_URL') or endpoint_url
        ssm_region_name = os.environ.get('AWS_SSM_REGION_NAME') or region_name
        ssm_password_path = os.environ.get('AWS_SSM_PASSWORD_PATH') or password_path

        if not all([access_key, secret_key, ssm_endpoint_url, ssm_region_name, ssm_password_path]):
            raise ValueError('One or more required environment variables is not set')

        sts_client = boto3.client('sts', aws_access_key_id=access_key, aws_secret_access_key=secret_key)

        response = sts_client.get_session_token()
        access_key_id = response['Credentials']['AccessKeyId']
        secret_access_key = response['Credentials']['SecretAccessKey']
        session_token = response['Credentials']['SessionToken']

        client = boto3.client(
            'ssm',
            # endpoint_url='https://ssm.us-west-1.amazonaws.com',
            # region_name='us-west-1',
            region_name=ssm_region_name,
            endpoint_url=ssm_endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            aws_session_token=session_token
        )

        # password_path = '/flat_file_loader/passwords/dev'
        password_path = ssm_password_path
        # parameter_name = f"{account_name}_{password_key}"
        parameter_name = password_key
        if password_path is not None and password_path != '':
            # parameter_name = f"{password_path}/{account_name}_{password_key}"
            parameter_name = f"{password_path}/{password_key}"
        try:
            response = client.get_parameter(Name=parameter_name, WithDecryption=True)
        except ClientError as e:
            print(f"Error retrieving secret: {e}")
            return None
        else:
            secret_value = response['Parameter']['Value']
            supported_encodings = ['utf-8', 'ascii', 'latin-1', 'utf-16']
            if encoding not in supported_encodings:
                print(f"Unsupported encoding: {encoding}")
                return None
            if isinstance(secret_value, bytes):
                secret_value = secret_value.decode(encoding)
        
        return secret_value
    
    elif password_method == 'secretsmanager':
        access_key = os.environ.get('AWS_SM_SECRET_ACCESS_KEY') or access_key
        secret_key = os.environ.get('AWS_SM_ACCESS_KEY_ID') or secret_key
        sm_endpoint_url = os.environ.get('AWS_SM_ENDPOINT_URL') or endpoint_url
        sm_region_name = os.environ.get('AWS_SM_REGION_NAME') or region_name
        password_key = os.environ.get('AWS_SM_PASSWORD_KEY') or password_key

        if not all([access_key, secret_key, sm_endpoint_url, sm_region_name, password_key]):
            raise ValueError('One or more required environment variables is not set')

        sts_client = boto3.client('sts', aws_access_key_id=access_key, aws_secret_access_key=secret_key)

        response = sts_client.get_session_token()
        access_key_id = response['Credentials']['AccessKeyId']
        secret_access_key = response['Credentials']['SecretAccessKey']
        session_token = response['Credentials']['SessionToken']

        client = boto3.client(
            'secretsmanager',
            endpoint_url=sm_endpoint_url,
            region_name=sm_region_name,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            aws_session_token=session_token
        )

        if password_key is not None and password_key != '':
            secret_name = password_key
        try:
            response = client.get_secret_value(SecretId=secret_name)
        except ClientError as e:
            print(f"Error retrieving secret: {e}")
            return None
        else:
            secret_value = response['SecretString']
            supported_encodings = ['utf-8', 'ascii', 'latin-1', 'utf-16']
            if encoding not in supported_encodings:
                print(f"Unsupported encoding: {encoding}")
                return None
            if isinstance(secret_value, bytes):
                secret_value = secret_value.decode(encoding)

        return secret_value
    else:
        raise ValueError(f'invalid password method supplied: "{password_method}".  Valid values include "keyring", "ssm" and "secretsmanager".')