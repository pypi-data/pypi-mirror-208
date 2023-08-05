import src.jadecobra.aws_environment
import src.jadecobra.toolkit


class TestAwsEnvironment(src.jadecobra.tester.TestCase):

    def test_environment_attributes(self):
        self.assert_attributes_equal(
            src.jadecobra.aws_environment.Environment,
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
                'account_id',
                'arn',
                'aws_environment',
                'aws_profile',
                'base_cidr',
                'environment_name',
                'get_environment',
                'iam_role_arn',
                'name_tag',
                'region',
                'today',
                'vpc_id'
            ]
        )