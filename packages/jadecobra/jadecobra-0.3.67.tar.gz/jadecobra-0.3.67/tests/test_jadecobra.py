import src.jadecobra
import src.jadecobra.tester


class TestJadeCobra(src.jadecobra.tester.TestCase):

    def test_jadecobra(self):
        self.assert_attributes_equal(
            src.jadecobra,
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
                '__version__',
                'aws_environment',
                'aws_lambda',
                'tester',
                'toolkit',
                'versioning'
            ]
        )