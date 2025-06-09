import unittest
from unittest.mock import patch
import sys
import os

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)
from CommandLineParser import CommandLineParser


class CommandLineParserTest(unittest.TestCase):
    def setUp(self):
        # Patch configparser to avoid writing to disk
        patcher = patch("CommandLineParser.configparser.ConfigParser")
        self.addCleanup(patcher.stop)
        self.mock_config = patcher.start()()
        self.mock_config.read.return_value = None

    def test_parse_args_with_api_token(self):
        test_args = ["prog", "-a", "test-token"]
        with patch.object(sys, "argv", test_args), patch(
            "CommandLineParser.keyring.set_password"
        ) as mock_set_password:
            parser = CommandLineParser()
            self.assertEqual(parser.args.api, "test-token")
            mock_set_password.assert_called_with(
                "system", "todoist-api-token", "test-token"
            )

    def test_parse_args_with_priorities(self):
        test_args = ["prog", "-p1", "3", "-p2", "5", "-p3", "7"]
        with patch.object(sys, "argv", test_args):
            parser = CommandLineParser()
            self.assertEqual(parser.args.p1, 3)
            self.assertEqual(parser.args.p2, 5)
            self.assertEqual(parser.args.p3, 7)

    def test_parse_args_with_run_time(self):
        test_args = ["prog", "-hh", "10", "-mm", "30"]
        with patch.object(sys, "argv", test_args):
            parser = CommandLineParser()
            self.assertEqual(parser.args.hh, 10)
            self.assertEqual(parser.args.mm, 30)

    def test_parse_args_with_task_limits(self):
        test_args = ["prog", "-nd", "2", "-du", "45"]
        with patch.object(sys, "argv", test_args):
            parser = CommandLineParser()
            self.assertEqual(parser.args.nd, 2)
            self.assertEqual(parser.args.du, 45)

    def test_parse_args_with_parent_and_reset(self):
        test_args = ["prog", "-p", "parentid", "-r"]
        with patch.object(sys, "argv", test_args), patch("sys.exit") as mock_exit:
            parser = CommandLineParser()
            self.assertEqual(parser.args.parent, "parentid")
            self.assertTrue(parser.args.reset)
            mock_exit.assert_called()

    def test_parse_args_with_debug(self):
        test_args = ["prog", "-d"]
        with patch.object(sys, "argv", test_args):
            parser = CommandLineParser()
            self.assertTrue(parser.args.debug)

    def test_user_input_configure(self):
        user_inputs = iter(
            ["y", "n", "api-token", "2", "3", "4", "12", "34", "5", "60", "n", "n"]
        )
        with patch("builtins.input", lambda prompt: next(user_inputs)), patch(
            "sys.exit"
        ) as mock_exit:
            parser = CommandLineParser()
            parser.args.api = None
            with patch.object(CommandLineParser, "parse_args") as mock_parse_args:
                parser.user_input()
                mock_parse_args.assert_called_with(True)


if __name__ == "__main__":
    unittest.main()
