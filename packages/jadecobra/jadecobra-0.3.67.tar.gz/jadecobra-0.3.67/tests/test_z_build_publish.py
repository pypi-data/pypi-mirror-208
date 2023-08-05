import importlib
import src.jadecobra.tester
import src.jadecobra.versioning
import src.jadecobra.toolkit


class TestZBuildDeploy(src.jadecobra.tester.TestCase):

    library = 'jadecobra'
    version = src.jadecobra.versioning.Version(library)

    def assert_published_version_is_source_version(self):
        src.jadecobra.toolkit.get_latest_published_version(self.library)
        import jadecobra
        importlib.reload(jadecobra)
        self.assertEqual(
            jadecobra.__version__,
            src.jadecobra.__version__
        )
        self.assertEqual(
            jadecobra.__version__,
            self.version.current_pyproject_version
        )

    def test_z_published_version_is_test_version(self):
        result = src.jadecobra.toolkit.publish(True)
        if result and 'ERROR' in result.stdout.decode():
            self.version.update()
            src.jadecobra.toolkit.publish(True)
        self.assert_published_version_is_source_version()
