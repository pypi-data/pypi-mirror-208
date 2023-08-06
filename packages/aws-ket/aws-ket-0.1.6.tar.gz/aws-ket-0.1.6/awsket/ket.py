#!/usr/bin/env python

# TO DO
# Be able to initallize DynamoDB backend

import boto3
import botocore


def get_iam_user():
    """get_iam_user()

    Retrieves information about the specified IAM user, including the user creation date, path, unique ID, and ARN.
    It uses the AWS Access Key and Secret Key to retrieve the user information
    
    Returns
    -------
    dict
        A dictioary scontaining details about the IAM user.

    """
    try:
        client_iam = boto3.client('iam')
        response = client_iam.get_user()
        return response['User']
    except botocore.exceptions.ClientError as error:
        response = error.response
        if (
            response["Error"]["Code"] == "UnrecognizedClientException"
            and response["ResponseMetadata"]["HTTPStatusCode"] == 400
        ):
            print("Invalid AWS Client Token")
            return "UnrecognizedClientException"
        if response["Error"]["Code"] == "AccessDenied" and response["ResponseMetadata"]["HTTPStatusCode"] == 403:
            print(response['Error']['Message'])


def create_s3_bucket(bucket_name, region):
    """Create S3 Bucket

    Creates an s3 bucket in AWS with the provided name and specified region. The user must have create bucket permission.
    
    Parameters
    ----------
    bucket_name : str
        Name of the bucket to be created
    region : str
        Region where the bucket will be created. e.g. us-east-2. (Note: S3 and KMS must be in same region)

    """
    try:
        client_s3 = boto3.client('s3', region_name=region)
        response = client_s3.create_bucket(
            ACL='private',
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': 'us-east-2'},
            ObjectLockEnabledForBucket=True,
            ObjectOwnership='BucketOwnerEnforced',
        )
    except botocore.exceptions.ClientError as error:
        response = error.response
        if (
            response["Error"]["Code"] == "BucketAlreadyOwnedByYou"
            and response["ResponseMetadata"]["HTTPStatusCode"] == 409
        ):
            print(response['Error']['Message'])
        if response["Error"]["Code"] == "InvalidBucketName" and response["ResponseMetadata"]["HTTPStatusCode"] == 400:
            print(response['Error']['Message'])


def push_to_s3(bucket_name, remote_file_name, content, region):
    """Push files or texts to S3

    Creates an s3 bucket in AWS with the provided name and specified region. The user must have create bucket permission.
    
    Parameters
    ----------
    bucket_name : str
        Name of the bucket to be created
    remote_file_name : str
        File or object name with which it will be stored as in the remote S3 bucket
    content: str
        Text, object or file that will be pushed to S3. Often referred as the body of the request.
    region: str
        Region where the bucket is located. e.g. us-east-2. (Note: S3 and KMS must be in same region)

    Raises
    ----------
    NoSuchBucket Exception
        If trying to push to a bucket that does nnot exists. Can be casued by typing an incorrect bucket name.
    AllAccessDisabled Exception
        Usually raised if no filename provided in the parameter
    """
    try:
        print(bucket_name)
        client_s3 = boto3.resource('s3', region_name=region)
        client_s3.Bucket(bucket_name).put_object(Key=remote_file_name, Body=content)
    except botocore.exceptions.ClientError as error:
        response = error.response
        if response["Error"]["Code"] == "NoSuchBucket" and response["ResponseMetadata"]["HTTPStatusCode"] == 404:
            print(response['Error']['Message'])
        if response["Error"]["Code"] == "AllAccessDisabled" and response["ResponseMetadata"]["HTTPStatusCode"] == 403:
            print(response['Error']['Message'])
    except botocore.exceptions.ParamValidationError as param_error:
        print(param_error)


def create_kms_key(region):
    """Create KMS Key in AWS

    Creates a KMS key in AWS in the specified region. The user must have create bucket permission.
    
    Parameters
    ----------
    region: str
        Region where the KMS key will be created. e.g. us-east-2. (Note: S3 and KMS must be in same region)

    Returns
    -------
    str
        ID of the KMS key
        
    Raises
    -------
    UnrecognizedClientException
        If AWS Access key does not exists
    AccessDeniedException
        If the user does not have suffiecient permission to create a KMS key
    """
    try:
        client_kms = boto3.client('kms', region_name=region)
        response = client_kms.create_key(Description='AWS KET KMS KEY', KeyUsage='ENCRYPT_DECRYPT', Origin='AWS_KMS')
        return response['KeyMetadata']['KeyId']

    except botocore.exceptions.ClientError as error:
        response = error.response
        if (
            response["Error"]["Code"] == "UnrecognizedClientException"
            and response["ResponseMetadata"]["HTTPStatusCode"] == 400
        ):
            print(response['Error']['Message'])
            return response['Error']['Code']
        if (
            response["Error"]["Code"] == "AccessDeniedException"
            and response["ResponseMetadata"]["HTTPStatusCode"] == 400
        ):
            print(response['Error']['Message'])
            return response['Error']['Code']


def create_kms_alias(key_id, alias_name, region):
    """Create an Alias for KMS Key in AWS

    Creates an alias for kms key in AWS in the specified region. The user must have create kms alias permission.
    
    Parameters
    ----------
    key_id: str
        ID of the kms key
    alias_name: str
        Alias for the kms key. Prefer a simple name that can be used. For this project it is set as alias/aws-ket
    region: str
        Region where the KMS key will be created. e.g. us-east-2. (Note: S3 and KMS must be in same region)

    Returns
    -------
    str
        name of the alias
        
    Raises
    -------
    ValidationException
        If the alias name does not follow AWS guidelines or convention
    AlreadyExistsException
        If an alias with same name already exists in the same region
    """
    try:
        client_kms = boto3.client('kms', region_name=region)
        response = client_kms.create_alias(AliasName=alias_name, TargetKeyId=key_id)
        return alias_name
    except botocore.exceptions.ClientError as error:
        response = error.response
        if response["Error"]["Code"] == "ValidationException" and response["ResponseMetadata"]["HTTPStatusCode"] == 400:
            print(response['Error']['Message'])
            return "ValidationException"
        if (
            response["Error"]["Code"] == "AlreadyExistsException"
            and response["ResponseMetadata"]["HTTPStatusCode"] == 400
        ):
            print(response['Error']['Message'])
            return "AlreadyExistsException"


def check_alias(alias_name, region):
    """Check for AWS KMS alias

    Checks if an alias for kms key with specified name already exists in a region.
    
    Parameters
    ----------
    alias_name: str
        Alias for the kms key. For this project it is set as alias/aws-ket
    region: str
        Region where the KMS key is be created. e.g. us-east-2. (Note: S3 and KMS must be in same region)

    Returns
    -------
    str
        Name of the alias or None
        
    Raises
    -------
    UnrecognizedClientException
        Incorrect name for alias is provided
    AccessDeniedException
        If user does not have permisions to check for kms key alias name
    """
    try:
        client_kms = boto3.client('kms', region_name=region)
        aliases = client_kms.list_aliases()
        for alias in aliases['Aliases']:
            if alias_name == alias['AliasName']:
                return alias_name
        return None
    except botocore.exceptions.ClientError as error:
        response = error.response
        if (
            response["Error"]["Code"] == "UnrecognizedClientException"
            and response["ResponseMetadata"]["HTTPStatusCode"] == 400
        ):
            print("Invalid AWS Client Token")
            return "UnrecognizedClientException"
        if (
            response["Error"]["Code"] == "AccessDeniedException"
            and response["ResponseMetadata"]["HTTPStatusCode"] == 400
        ):
            print(response['Error']['Message'])
            return response['Error']['Code']


def encrypt_text(kms_key, text, region):
    """Encrypt text using KMS

    Encrypts plaintext of up to 4,096 bytes using a KMS key from the specified region.
    
    Parameters
    ----------
    kms_key: str
        This can be either kms key id, kms arn, alias or alias arn
    text: str
        Either plain text or any type of content that needs to be encrypted
    region: str
        Region where the KMS key is located. e.g. us-east-2. (Note: S3 and KMS must be in same region)

    Returns
    -------
    dict
        CiphertextBlob
        
    Raises
    -------
    UnrecognizedClientException
        Incorrect name for alias is provided
    AccessDeniedException
        If user does not have permisions to encrypt using kms key or alias name
    """
    try:
        client_kms = boto3.client('kms', region_name=region)
        encrypted_kms_request = client_kms.encrypt(KeyId=kms_key, Plaintext=text)
        encrypted_string = encrypted_kms_request["CiphertextBlob"]
        return encrypted_string
    except botocore.exceptions.ClientError as error:
        response = error.response
        if response["Error"]["Code"] == "NotFoundException" and response["ResponseMetadata"]["HTTPStatusCode"] == 400:
            print(response['Error']['Message'])
            return response['Error']['Code']
        if response['Error']['Code'] == "ValidationException" and response["ResponseMetadata"]["HTTPStatusCode"] == 400:
            print('The text you provided must be greater than 0 characters in length')
            return response['Error']['Code']
        if (
            response['Error']['Code'] == "AccessDeniedException"
            and response["ResponseMetadata"]["HTTPStatusCode"] == 400
        ):
            print(response['Error']['Message'])
            return response['Error']['Code']
    except botocore.exceptions.ParamValidationError as param_error:
        print(param_error)


def encrypt_file(kms_key, file_name, region):
    """Encrypt file using KMS

    Encrypts the content of a specified file using a KMS key.
    
    Parameters
    ----------
    kms_key: str
        This can be either kms key id, kms arn, alias or alias arn
    file_name: str
        File name or path to a file that needs to be encrypted
    region: str
        Region where the KMS key is located. e.g. us-east-2. (Note: S3 and KMS must be in same region)

    Returns
    -------
    dict
        CiphertextBlob
        
    Raises
    -------
    NotFoundException
        Incorrect name of file or file does not exist
    ValidationException
        The file must contain more than 0 characters text
    AccessDeniedException
        If user does not have permisions to check for kms key alias name
    ParamValidationError
        Incorrect parameter passed to the function
    """
    try:
        client_kms = boto3.client('kms', region_name=region)
        file = open(file_name, "r")
        encrypted_kms_request = client_kms.encrypt(KeyId=kms_key, Plaintext=file.read())
        encrypted_string = encrypted_kms_request["CiphertextBlob"]
        return encrypted_string
    except FileNotFoundError as error:
        print(error)
    except botocore.exceptions.ClientError as error:
        response = error.response
        if response["Error"]["Code"] == "NotFoundException" and response["ResponseMetadata"]["HTTPStatusCode"] == 400:
            print(response['Error']['Message'])
            return response['Error']['Code']
        if response['Error']['Code'] == "ValidationException" and response["ResponseMetadata"]["HTTPStatusCode"] == 400:
            print('The text you provided must be greater than 0 characters in length')
            return response['Error']['Code']
        if (
            response['Error']['Code'] == "AccessDeniedException"
            and response["ResponseMetadata"]["HTTPStatusCode"] == 400
        ):
            print(response['Error']['Message'])
            return response['Error']['Code']
    except botocore.exceptions.ParamValidationError as param_error:
        print(param_error)


def decrypt_text(bucket_name, remote_file_name, kms_key_id, region):
    """Decrypt file from S3 using KMS

    Decrypts file from S3 using KMS key.
    
    Parameters
    ----------
    bucket_name: str
        Bucket where the enrypted file is stored
    remote_file_name: str
        Object name or path to an object in S3 that needs to be decrypted
    kms_key_id: str
        This can be either kms key id, kms arn, alias or alias arn
    region: str
        Region where the KMS key is located. e.g. us-east-2. (Note: S3 and KMS must be in same region)

    Returns
    -------
    str
        Plaintext
        
    Raises
    -------
    NoSuchBucket
        Incorrect bucket name provided
    NoSuchKey
        Incorret object name or object does not exist in S3
    IncorrectKeyException
        The key does not match with what was used to encrypt the file
    ParamValidationError
        Incorrect parameter passed to the function
    """
    try:
        client_kms = boto3.client('kms', region_name=region)
        client_s3 = boto3.client('s3', region_name=region)
        s3_object = client_s3.get_object(Bucket=bucket_name, Key=remote_file_name)
        body = s3_object["Body"].read()
        kms_decrypt_request = client_kms.decrypt(CiphertextBlob=body, KeyId=kms_key_id)
        kms_decrypted_text = kms_decrypt_request["Plaintext"].decode("UTF-8")
        return kms_decrypted_text
    except botocore.exceptions.ClientError as error:
        response = error.response
        if response["Error"]["Code"] == "NoSuchBucket" and response["ResponseMetadata"]["HTTPStatusCode"] == 404:
            print(response['Error']['Message'])
        if response["Error"]["Code"] == "NoSuchKey" and response["ResponseMetadata"]["HTTPStatusCode"] == 404:
            print(f'The specified file: {remote_file_name} in {bucket_name} bucket does not exist')
        if (
            response["Error"]["Code"] == "IncorrectKeyException"
            and response["ResponseMetadata"]["HTTPStatusCode"] == 400
        ):
            print(response['Error']['Message'])
    except botocore.exceptions.ParamValidationError as param_error:
        print(param_error)


def save_to_file(file_name, decrypted_string):
    """Save file

    Saves the derypted text to a local file
    
    Parameters
    ----------
    file_name: str
        Local file name where the decrypted output will be sotred
    decrypted_string: str
        Decrypted utput in string format.
    """
    file = open(file_name, "w")
    file.write(decrypted_string)
    file.close()
