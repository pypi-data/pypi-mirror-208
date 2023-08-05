import os
import src.jadecobra
import src.jadecobra.tester


class TestJadeCobraTester(src.jadecobra.tester.TestCase):

    def test_tester_attributes(self):
        self.assert_attributes_equal(
            src.jadecobra.tester,
            [
                'TestCase',
                '__builtins__',
                '__cached__',
                '__doc__',
                '__file__',
                '__loader__',
                '__name__',
                '__package__',
                '__spec__',
                'create_app',
                'create_scaffolding',
                'create_scent',
                'create_tdd_cdk_project',
                'create_tdd_project',
                'create_test_file',
                'get_project_name',
                'remove_unwanted_files',
                'run_tests',
                'sys',
                'os',
                'toolkit',
                'unittest',
                'update_requirements',
            ]
        )

    def test_tester_test_case_attributes(self):
        self.assert_attributes_equal(
            src.jadecobra.tester.TestCase,
            [
                '__call__',
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
                '_addExpectedFailure',
                '_addUnexpectedSuccess',
                '_baseAssertEqual',
                '_callCleanup',
                '_callSetUp',
                '_callTearDown',
                '_callTestMethod',
                '_classSetupFailed',
                '_class_cleanups',
                '_deprecate',
                '_diffThreshold',
                '_formatMessage',
                '_getAssertEqualityFunc',
                '_truncateMessage',
                'addClassCleanup',
                'addCleanup',
                'addTypeEqualityFunc',
                'assertAlmostEqual',
                'assertAlmostEquals',
                'assertCountEqual',
                'assertDictContainsSubset',
                'assertDictEqual',
                'assertEqual',
                'assertEquals',
                'assertFalse',
                'assertGreater',
                'assertGreaterEqual',
                'assertIn',
                'assertIs',
                'assertIsInstance',
                'assertIsNone',
                'assertIsNot',
                'assertIsNotNone',
                'assertLess',
                'assertLessEqual',
                'assertListEqual',
                'assertLogs',
                'assertMultiLineEqual',
                'assertNoLogs',
                'assertNotAlmostEqual',
                'assertNotAlmostEquals',
                'assertNotEqual',
                'assertNotEquals',
                'assertNotIn',
                'assertNotIsInstance',
                'assertNotRegex',
                'assertNotRegexpMatches',
                'assertRaises',
                'assertRaisesRegex',
                'assertRaisesRegexp',
                'assertRegex',
                'assertRegexpMatches',
                'assertSequenceEqual',
                'assertSetEqual',
                'assertTrue',
                'assertTupleEqual',
                'assertWarns',
                'assertWarnsRegex',
                'assert_',
                'assert_attributes_equal',
                'assert_cdk_templates_equal',
                'clean_up_cdk_assets',s
                'countTestCases',
                'create_cdk_templates',
                'debug',
                'defaultTestResult',
                'doClassCleanups',
                'doCleanups',
                'enterClassContext',
                'enterContext',
                'fail',
                'failIf',
                'failIfAlmostEqual',
                'failIfEqual',
                'failUnless',
                'failUnlessAlmostEqual',
                'failUnlessEqual',
                'failUnlessRaises',
                'failureException',
                'filter_keys',
                'id',
                'longMessage',
                'maxDiff',
                'publish',
                'run',
                'setUp',
                'setUpClass',
                'shortDescription',
                'skipTest',
                'subTest',
                'tearDown',
                'tearDownClass'
            ]
        )

    def test_create_scaffold(self):
        return

    def test_create_test_file(self):
        return

    def test_create_tdd_cdk_project(self):
        project_name = 'project_name'
        self.assertEqual(
            sorted(os.listdir(project_name)),
            [

            ]
        )
        # self.assertEqual(
        #     src.jadecobra.tester.create_tdd_cdk_project(project_name),
        #     ''''''
        # )
        # self.assertEqual(
        #     sorted(os.listdir(project_name)),
        #     [

        #     ]
        # )
        # self.assertFalse(True)