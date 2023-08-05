import unittest
import os
import sys

from . import toolkit

def create_scaffolding():
    for command in (
        'npm install -g npm aws-cdk',
        'cdk init app --language python',
        'python -m pip install -U pip',
        'python -m pip install -r requirements.txt',
    ):
        os.system(command)

def remove_unwanted_files(project_name):
    os.remove('requirements-dev.txt')
    os.rmdir('tests/unit')
    os.rmdir(project_name)

def run_tests():
    os.system('sniffer')

def update_requirements():
    requirements = ['sniffer']
    if sys.platform.startswith('linux'):
        requirements.append('pyinotify')
    elif sys.platform.startswith('win32'):
        requirements.append('pywin32')
    elif sys.platform.startswith('darwin'):
        requirements.append('macfsevents')
    with open('requirements.txt') as file:
        requirements.append((line.strip() for line in file))
    with open('requirements.txt', 'a') as file:
        for requirement in list(set(requirements)):
            file.write(requirement)

def create_test_file(project_name):
    toolkit.write_file(
        filepath='tests/__init__.py',
        data=f'''import jadecobra.tester

class Test{project_name}(jadecobra.tester.TestCase):

    def test_failure(self):
        self.assertFalse(True)'''
    )

def create_scent():
    toolkit.write_file(
        filepath='scent.py',
        data="""import sniffer.api
import subprocess
watch_paths = ['tests/', 'src/']

@sniffer.api.runnable
def run_tests(*args):
    if subprocess.run(
        'python -m unittest -f tests/*.*',
        shell=True
    ).returncode == 0:
        return True"""
    )

def create_app(project_name):
    toolkit.write_file(
        filepath='app.py',
        data=f'''import aws_cdk
import jadecobra.toolkit
import os
import {project_name}

app = aws_cdk.App()
{project_name}.Stack(
    app, {project_name},
    env=aws_cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=os.getenv('CDK_DEFAULT_REGION')
    ),
)

jadecobra.toolkit.time_it(
    function=app.synth,
    description='cdk ls for {project_name}'
)
        '''
    )

def create_tdd_project(project_name):
    return

def get_project_name(project_name):
    return os.path.split(os.getcwd())[-1]

def create_tdd_cdk_project(project_name=None):
    if not project_name:
        project_name = get_project_name(project_name)
    create_scaffolding()
    update_requirements()
    create_app(project_name)
    create_test_file(project_name)
    create_scent()
    remove_unwanted_files(project_name)
    run_tests()


class TestCase(unittest.TestCase):

    maxDiff = None

    @staticmethod
    def clean_up_cdk_assets():
        (
            os.rmdir(item) for item in os.listdir('cdk.out')
            if item.startswith('asset.')
        )


    def create_cdk_templates(self):
        '''Create CloudFormation using CDK with presets'''
        self.clean_up_cdk_assets()
        result = toolkit.run_in_shell(
            (
                'cdk ls '
                '--no-version-reporting '
                '--no-path-metadata '
                '--no-asset-metadata'
            )
        )
        self.assertEqual(result.returncode, 0)

    @staticmethod
    def filter_keys(dictionary:dict=None, filter=None):
        return (
            name for name in list(dictionary.keys())
            if filter in name
        )

    def assert_cdk_templates_equal(self, stack_name):
        '''Check if stack_name in cdk.out folder and tests/fixtures are the same
        Remove Layer assets because they change on every run which creates an infinite loop in testing
        '''
        reality = toolkit.read_json(f'cdk.out/{stack_name}')
        expectation = toolkit.read_json(f'tests/fixtures/{stack_name}')
        for dictionary in (reality, expectation):
            for asset in self.filter_keys(
                dictionary=dictionary.get('Parameters', {}),
                filter='Asset',
            ):
                try:
                    dictionary['Parameters'].pop(asset)
                except KeyError:
                    'nothing to do here'
            for layer in self.filter_keys(
                dictionary=dictionary.get('Resources'),
                filter='LambdaLayer',
            ):
                try:
                    dictionary['Resources'][layer]['Properties'].pop('Content')
                except KeyError:
                    'nothing to do here'
        self.assertEqual(reality, expectation)

    def assert_attributes_equal(self, thing=None, attributes=None):
        '''Check that the given attributes match the attributes of thing'''
        self.assertEqual(
            sorted(dir(thing)), sorted(attributes)
        )

    def publish(self):
        toolkit.publish()