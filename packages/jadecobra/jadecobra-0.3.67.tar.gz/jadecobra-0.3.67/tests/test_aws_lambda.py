import src.jadecobra.aws_lambda
import src.jadecobra.toolkit


class TestAwsLambda(src.jadecobra.tester.TestCase):

    def test_aws_lambda(self):
        self.assert_attributes_equal(
            src.jadecobra.aws_lambda,
            [
                '__builtins__',
                '__cached__',
                '__doc__',
                '__file__',
                '__loader__',
                '__name__',
                '__package__',
                '__path__',
                '__spec__',
                'deploy',
                'get_arn',
            ]
        )

    def test_get_lambda_function_arn(self):
        region = "region"
        account = "012345678901"
        name = "lambda_function_name"
        self.assertEqual(
            src.jadecobra.aws_lambda.get_arn(
                region=region,
                account=account,
                name=name
            ),
            f"arn:aws:lambda:{region}:{account}:function:{name}"
        )