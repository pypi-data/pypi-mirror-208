import src.jadecobra.aws_lambda.deploy.deploy_lambda
import src.jadecobra.tester

class TestAwsLambdaTools(src.jadecobra.tester.TestCase):

    def test_lambda_deployer(self):
        src.jadecobra.aws_lambda.deploy.deploy_lambda.LambdaDeployer()

    def test_lambda_deployer_attributes(self):
        self.assert_attributes_equal(
            src.jadecobra.aws_lambda.deploy.deploy_lambda.LambdaDeployer,
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
                's3_key',
                'upload_to_s3'
            ]
        )
