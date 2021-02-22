import os
from unittest import TestCase, mock

from cli.common import Command, Pipeline
from cli.parser import Parser


class ParserTest(TestCase):
    def test_echo(self):
        raw = "echo"
        parsed: Pipeline = Parser.parse(raw)
        self.assertEqual(parsed, Pipeline([Command("echo")]))

    def test_echo_with_args(self):
        raw = "echo hello world"
        parsed: Pipeline = Parser.parse(raw)
        split = raw.split(" ")
        self.assertEqual(parsed, Pipeline([Command(split[0], split[1:])]))

    def test_pipe(self):
        hello = "echo hello world"
        cat = "cat"
        raw = hello + "|" + cat
        parsed: Pipeline = Parser.parse(raw)
        hello_split = raw.split(" ")
        self.assertEqual(
            parsed, Pipeline([Command(hello_split[0], hello_split[1:]), Command(cat)])
        )

    def test_single_quotes(self):
        raw = "echo 'hello world'"
        parsed = Parser.parse(raw)
        self.assertEqual(parsed, Pipeline([Command("echo", ["hello world"])]))

    def test_double_quotes(self):
        raw = 'echo "hello world"'
        parsed = Parser.parse(raw)
        self.assertEqual(parsed, Pipeline([Command("echo", ["hello world"])]))

    @mock.patch.dict(os.environ, {"a": "b"})
    def test_expansion(self):
        var = "a"
        raw = 'echo "$' + var + '"'
        parsed = Parser.parse(raw)
        self.assertEqual(parsed, Pipeline([Command("echo", [os.environ["a"]])]))

    @mock.patch.dict(os.environ, {"a": "b"})
    def test_no_expansion(self):
        s = "$a"
        raw = "echo '" + s + "'"
        parsed = Parser.parse(raw)
        self.assertEqual(parsed, Pipeline([Command("echo", [s])]))

    def test_unbalanced(self):
        raw = "echo ' hello world"
        with self.assertRaises(SyntaxError):
            _ = Parser.parse(raw)

    @mock.patch.dict(os.environ, {"a": "b"})
    def test_quotes(self):
        raw = "echo \"hello '$a' world\""
        parsed = Parser.parse(raw)
        self.assertEqual(parsed, Command("echo", ["hello 'b' world"]))
