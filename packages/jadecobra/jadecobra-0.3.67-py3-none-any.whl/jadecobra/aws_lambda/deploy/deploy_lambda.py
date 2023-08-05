import boto3
import os
import shutil


class LambdaDeployer:

    def __init__(self, profile_name=None, bucket_name=None, region="us-west-2"):
        print('-'*70)
        print(f'currently in {os.getcwd()}')
        print('-'*70)
        self.environment_name = profile_name
        self.s3_bucket = bucket_name
        self.region = region
        self.session = boto3.session.Session(
            region_name=self.region,
            profile_name=profile_name,
        )
        self.s3 = self.session.client("s3")
        self.lambda_client = self.session.client("lambda")

    def delimiter(self):
        print("=" * 100)

    def s3_key(self):
        return f"{self.directory()}/{self.zip_filename()}"

    def upload_to_s3(self):
        self.delimiter()
        print(
            f"Uploading {self.zip_filename()} to S3://{self.s3_bucket}/{self.directory()}..."
        )
        with open(self.zip_filename(), "rb") as data:
            self.s3.upload_fileobj(data, self.s3_bucket, self.s3_key())

    def delete_directory(self):
        return shutil.rmtree(self.directory(), ignore_errors=True)

    def delete_zipfile(self):
        return os.remove(self.zip_filename())
