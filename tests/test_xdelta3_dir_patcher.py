import unittest
from mock import Mock
from shutil import rmtree
from subprocess import CalledProcessError, check_output, STDOUT
from tempfile import mkdtemp
from os import path, remove

# Dashes are standard for exec scipts but not allowed for modules in Python. We
# use the script standard since we will be running that file as a script most
# often.
patcher = __import__("xdelta3-dir-patcher")

class TestXDelta3DirPatcher(unittest.TestCase):
    EXECUTABLE="xdelta3-dir-patcher.py"

    def setUp(self):
        self.temp_dir = mkdtemp(prefix="%s_" % self.__class__.__name__)

    def tearDown(self):
        rmtree(self.temp_dir)

    # Integration tests
    def test_version_is_correct(self):
        output = check_output(["./%s" % self.EXECUTABLE, '--version'],
                               universal_newlines=True)
        self.assertEqual(output, "%s v0.1\n" % self.EXECUTABLE)

    def test_help_is_available(self):
        self.assertIsNotNone(check_output(["./%s" % self.EXECUTABLE, '-h']))
        self.assertIsNotNone(check_output(["./%s" % self.EXECUTABLE, '--help']))

    def test_debugging_is_available(self):
        output = check_output(["./%s" % self.EXECUTABLE, '--debug'])
        self.assertNotIn("unrecognized arguments", output)

    def test_help_is_printed_if_no_action_command(self):
        output = check_output(["./%s" % self.EXECUTABLE])
        self.assertIn("usage: ", output)

    def test_apply_is_allowed_as_action_command(self):
        try:
            check_output(["./%s" % self.EXECUTABLE, "apply"],
                         stderr=STDOUT)
        except CalledProcessError as e:
            self.assertIn("usage: ", e.output)
            self.assertNotIn("invalid choice: ", e.output)
        else: self.fail()

    def test_apply_usage_is_printed_if_not_enough_args(self):
        try:
            check_output(["./%s" % self.EXECUTABLE, "apply"],
                         stderr=STDOUT)
        except CalledProcessError as e:
            self.assertIn("the following arguments are required: ", e.output)
        else: self.fail()

    def test_apply_usage_is_not_printed_if_args_are_correct(self):
        old_path = path.join('tests', 'test_files', 'old_version1')
        delta_path = path.join('tests', 'test_files', 'patch1.xdelta.tgz')
        output = check_output(["./%s" % self.EXECUTABLE, "apply", old_path, delta_path, self.temp_dir, "--ignore-euid"] )
        self.assertNotIn("usage: ", output)

    def test_diff_usage_is_printed_if_not_enough_args(self):
        try:
            check_output(["./%s" % self.EXECUTABLE, "diff"],
                         stderr=STDOUT)
        except CalledProcessError as e:
            self.assertIn("the following arguments are required: ", e.output)
        else: self.fail()

    def test_diff_is_allowed_as_action_command(self):
        try:
            check_output(["./%s" % self.EXECUTABLE, "diff"],
                         stderr=STDOUT)
        except CalledProcessError as e:
            self.assertIn("usage: ", e.output)
            self.assertNotIn("invalid choice: ", e.output)
        else: self.fail()

    def test_diff_usage_is_not_printed_if_args_are_correct(self):
        old_path = path.join('tests', 'test_files', 'old_version1')
        new_path = path.join('tests', 'test_files', 'new_version1')
        delta_path = path.join(self.temp_dir, 'foo.tgz')
        output = check_output(["./%s" % self.EXECUTABLE, "diff", old_path, new_path, delta_path] )
        self.assertNotIn("usage: ", output)

    def test_other_actions_are_not_allowed(self):
        try:
            check_output(["./%s" % self.EXECUTABLE, "foobar"],
                         stderr=STDOUT)
        except CalledProcessError as e:
            self.assertIn("usage: ", e.output)
            self.assertIn("invalid choice: ", e.output)
        else: self.fail()

    # Unit tests
    def test_run_calls_diff_with_correct_arguments_if_action_is_diff(self):
        args = patcher.AttributeDict()
        args.action = 'diff'
        args.old_dir = 'old'
        args.new_dir = 'new'
        args.patch_bundle = 'target'

        test_object = patcher.XDelta3DirPatcher(args)
        test_object.diff = Mock()

        test_object.run()

        test_object.diff.assert_called_once_with('old', 'new', 'target')

    def test_run_calls_apply_with_correct_arguments_if_action_is_apply(self):
        args = patcher.AttributeDict()
        args.action = 'apply'
        args.old_dir = 'old'
        args.patch_bundle = 'patch'
        args.ignore_euid = True
        args.target_dir = 'target'

        test_object = patcher.XDelta3DirPatcher(args)
        test_object.apply = Mock()

        test_object.run()

        test_object.apply.assert_called_once_with('old', 'patch', 'target')
