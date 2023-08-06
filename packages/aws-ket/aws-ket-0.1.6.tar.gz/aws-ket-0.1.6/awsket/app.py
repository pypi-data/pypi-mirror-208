#!/usr/bin/env python


# TO DO
# Provide more option to encrypt and decryupt files/text
# Option to choose backend storage for encrypted file
# Bettwer way to ame files
# Only use pwd as filename when nbo filename provided
# Be able to list ncrypted files using a key
# Better logginng
# Handle Exception
# More will be added!

import os
import boto3
import argparse
from ket import *


# kms_key_id = os.environ.get('KMS_KEY_ID')
# bucket_name = os.environ.get('S3_BUCKET')
# file_name = os.getcwd()

# client = boto3.client('kms')

AWS_REGION = 'us-east-2'
KMS_ALIAS = 'alias/aws-ket'

parser = argparse.ArgumentParser()
parser.add_argument("--text", "-T", help="Text to encrypt. Usage python app.py --text <TEXT> --save <REMOTE_FILE_NAME>")
parser.add_argument(
    "--file", "-F", help="Filename to encrypt. Usage python app.py --file <FILE_PATH> --save <REMOTE_FILE_NAME>"
)
parser.add_argument(
    "--decrypt", "-D", help="File name in S3 to decrypt. Usage python app.py --decrypt <REMOTE_FILE_NAME>"
)
parser.add_argument("--save", "-S", help="Save in remote location. e.g. object name in S3")


def main(kms_key_id, bucket_name, region):
    try:
        args = parser.parse_args()
        if args.text and args.save:
            encrypted_string = encrypt_text(kms_key_id, args.text, region)
            push_to_s3(bucket_name, args.save, encrypted_string, region)
            print('Successfully encrypted file and pushed to S3')
            return encrypted_string
        elif args.file and args.save:
            encrypted_file = encrypt_file(kms_key_id, args.file, region)
            push_to_s3(bucket_name, args.save, encrypted_file, region)
            print('Successfully encrypted file and pushed to S3')
            return encrypted_file
        elif args.decrypt and args.save:
            decrypted_text = decrypt_text(bucket_name, args.decrypt, kms_key_id, region)
            file = open(args.save, "x")
            file.write(decrypted_text)
            file.close()
            print(decrypted_text)
            print(f'Successfully downloaded {args.decrypt} file from {bucket_name} and decrypted text')
        elif args.decrypt:
            decrypted_text = decrypt_text(bucket_name, args.decrypt, kms_key_id, region)
            file = open(args.decrypt, "x")
            file.write(decrypted_text)
            file.close()
            print(decrypted_text)
            print(f'Successfully downloaded {args.decrypt} file from {bucket_name} and decrypted text')
        else:
            print("Invalid arguments. Use python ./app.py --help")
    except FileExistsError as file_exist_error:
        print(file_exist_error)
    except FileNotFoundError as file_not_found_error:
        print(file_not_found_error)


if __name__ == "__main__":
    bucket_name = f'aws-ket-{get_iam_user()["UserId"].lower()}'
    main(KMS_ALIAS, bucket_name, AWS_REGION)
