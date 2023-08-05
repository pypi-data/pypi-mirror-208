import src.jadecobra.aws_lambda.deploy.lambda_function
import src.jadecobra.toolkit
import os

class TestAwsDeployLambdaFunction(src.jadecobra.tester.TestCase):

    def test_deploy_lambda_function(self):
        with self.assertRaises(TypeError):
            src.jadecobra.aws_lambda.deploy.lambda_function.LambdaFunction(
                function_name='bob_function'
            )
            os.remove('bob_function.zip')

    def test_deploy_lambda_function_attributes(self):
        self.assert_attributes_equal(
            src.jadecobra.aws_lambda.deploy.lambda_function.LambdaFunction,
            [
                '__class__',
                '__delattr__',
                '__dict__',
                '__dir__',
                '__doc__',
                '__eq__',
                '__format__',
                '__ge__',
                '__getattribute__',
                '__getstate__',
                '__gt__',
                '__hash__',
                '__init__',
                '__init_subclass__',
                '__le__',
                '__lt__',
                '__module__',
                '__ne__',
                '__new__',
                '__reduce__',
                '__reduce_ex__',
                '__repr__',
                '__setattr__',
                '__sizeof__',
                '__str__',
                '__subclasshook__',
                '__weakref__',
                'delete_directory',
                'delete_zipfile',
                'delimiter',
                'directory',
                'package_code',
                'python_filename',
                's3_key',
                'update_lambda_code',
                'upload_to_s3',
                'zip_filename'
            ]
        )