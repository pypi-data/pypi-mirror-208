import shutil
import zipfile
import os

from . import deploy_lambda


class LambdaFunction(deploy_lambda.LambdaDeployer):

    def __init__(self, function_name: str = None, bucket_name=None, profile_name=None):
        super().__init__(bucket_name=bucket_name, profile_name=profile_name)
        self.function_name = function_name
        self.package_code()
        self.upload_to_s3()
        self.update_lambda_code()
        self.delimiter()
        self.delete_zipfile()

    @staticmethod
    def directory():
        return "lambda_functions"

    def zip_filename(self):
        return f"{self.function_name}.zip"

    def python_filename(self):
        return f"{self.function_name}.py"


    def package_code(self):
        # add everything in the folder except files/directories named tests
        self.delimiter()
        print(f"\tzipping up {self.function_name} ...")
        with zipfile.ZipFile(self.zip_filename(), "w", compresslevel=9) as compressor:
            for filename in os.listdir():
                if "tests" in filename or filename.endswith(".zip") or "scent.py" in filename:
                    continue
                else:
                    compressor.write(filename)

    def update_lambda_code(self):
        self.delimiter()
        message = f'\tupdating {self.function_name} in {self.environment_name}::'
        try:
            self.lambda_client.update_function_code(
                FunctionName=self.function_name,
                S3Bucket=self.s3_bucket,
                S3Key=self.s3_key(),
                Publish=True,
            )
        except self.lambda_client.exceptions.ClientError as error:
            print(f"{message}:{error}")
        else:
            print(f"{message}:success")
