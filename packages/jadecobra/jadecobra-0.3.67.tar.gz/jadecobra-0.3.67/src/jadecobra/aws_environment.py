import datetime
import os


class Environment(object):

    def __init__(self, environment):
        self.environment = self.get_environment(environment)

    def environment_name(self):
        return self.environment.name()

    @classmethod
    def name_tag(cls, name):
        return name if name else cls.name

    @staticmethod
    def region():
        return 'us-west-2'

    @staticmethod
    def today():
        return f"{datetime.datetime.today().date()}"

    @staticmethod
    def aws_profile():
        return os.environ.get('AWS_PROFILE', 'DEV').lower()

    @staticmethod
    def arn(value):
        return f'arn:aws:{value}'

    def iam_role_arn(self, account=None, role_name=None):
        return self.arn(f'iam::{account}:role/{role_name}')

    def account_id(self):
        return self.environment.account_id()

    def vpc_id(self):
        return self.environment.vpc_id()

    def aws_environment(self):
        return dict(
            account=self.account_id(),
            region=self.region()
        )

    def get_environment(self, environment):
        '''Return Environment Module based on AWS_PROFILE given in Command Line'''
        return dict(
            dev=environment.dev,
            tst=environment.tst,
            prd=environment.prod,
        ).get(
            self.aws_profile(), environment.dev
        )

    @staticmethod
    def base_cidr():
        return '10.0.0.0/8'