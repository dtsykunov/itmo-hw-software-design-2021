import os
from unittest import TestCase, mock

from cli.common import Command, Pipeline
from cli.parser import (
    Parser,
    _check_balanced,
    _del_conseq,
    _remove_quotes_if_needed,
    _splitat,
    _tokenize,
)


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
        hello_split = hello.split(" ")
        shouldbe = Pipeline([Command(hello_split[0], hello_split[1:]), Command(cat)])
        self.assertEqual(str(shouldbe), str(parsed))

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
        shouldbe = Pipeline([Command("echo", ["hello 'b' world"])])
        self.assertEqual(str(shouldbe), str(parsed))

    @mock.patch.dict(os.environ, {"a": "ex", "b": "it"})
    def test_quotes2(self):
        raw = "$a$b"
        parsed = Parser.parse(raw)
        shouldbe = Pipeline([Command("exit")])
        self.assertEqual(parsed, shouldbe)

    def test_variable(self):
        raw = "a=b"
        shouldbe = Pipeline([Command("=", ["a", "b"])])
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(str(shouldbe), str(Parser.parse(raw)))


class TokenizeTest(TestCase):
    def test_echo(self):
        raw = "echo"
        self.assertEqual([raw], _tokenize(raw))

    def test_args(self):
        raw = ["echo", " ", "hello"]
        self.assertEqual(raw, _tokenize("".join(raw)))

    def test_squotes(self):
        raw = "'echo hello'"
        self.assertEqual([raw], _tokenize(raw))

    def test_dquotes(self):
        raw = '"echo hello"'
        self.assertEqual([raw], _tokenize(raw))

    def test_quotes_1(self):
        raw = ["echo", " ", '"echo hello"', " ", "|", " ", "cat"]

        self.assertEqual(raw, _tokenize("".join(raw)))

    def test_quotes_2(self):
        raw = ["echo", " ", '\'" " "\'']
        self.assertEqual(raw, _tokenize("".join(raw)))

    def test_quotes_3(self):
        raw = ["echo", " ", "\" ' ' ' \""]
        self.assertEqual(raw, _tokenize("".join(raw)))

    def test_expansion(self):
        raw = "$a$b"
        with mock.patch.dict(os.environ, {"a": "ex", "b": "it"}, clear=True):
            self.assertEqual(["ex", "it"], _tokenize(raw))

    def test_expansion2(self):
        raw = "$a $b"
        with mock.patch.dict(os.environ, {"a": "ex", "b": "it"}, clear=True):
            self.assertEqual(["ex", " ", "it"], _tokenize(raw))

    def test_expansion3(self):
        raw = "\"hello '$a' world\""
        with mock.patch.dict(os.environ, {"a": "ex"}, clear=True):
            self.assertEqual(["\"hello 'ex' world\""], _tokenize(raw))

    def test_variable(self):
        raw = "a=b"
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(["a", "=", "b"], _tokenize(raw))


class HelpersTest(TestCase):
    def test_splitat(self):
        echo = [" ", " ", "echo", " ", "hello", " "]
        cat = [" ", "cat"]
        pipe = echo + ["|"] + cat
        self.assertEqual([echo, cat], _splitat(pipe, lambda x: x == "|"))

    def test__del_conseq(self):
        echo = [" ", " ", "echo", " ", "hello", " "]
        self.assertEqual(echo[1:], _del_conseq(echo, lambda x: x == " "))

    def test_remove_quotes_if_needed(self):
        a = "'heck'"
        self.assertEqual(a[1:-1], _remove_quotes_if_needed(a))
        self.assertEqual(a[1:-1], _remove_quotes_if_needed(a[1:-1]))
        self.assertEqual("", _remove_quotes_if_needed(""))

    def test_check_balanced(self):
        raw = '""'
        self.assertIsNone(_check_balanced(raw))
        raw1 = '"""'
        with self.assertRaises(SyntaxError):
            _check_balanced(raw1)
