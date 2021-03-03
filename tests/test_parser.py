from unittest import TestCase

from cli.builtins import Cat, Echo, Eq, Exit
from cli.clicommandfactory import _del_conseq, _remove_quotes_if_needed, _splitat
from cli.clilexer import CliLexer
from cli.cliparser import CliParser


class CliParserTest(TestCase):
    def test_echo(self):
        raw = "echo"
        parsed = list(map(str, CliParser().parse(raw)))
        expected = [str(Echo("echo", []))]
        self.assertEqual(parsed, expected)

    def test_echo_with_args(self):
        raw = "echo hello world"
        parsed = list(map(str, CliParser().parse(raw)))
        split = raw.split(" ")
        expected = [str(Echo(split[0], split[1:]))]
        self.assertEqual(parsed, expected)

    def test_pipe(self):
        hello = "echo hello world"
        cat = "cat"
        raw = hello + "|" + cat
        prs = CliParser().parse(raw)
        parsed = list(map(str, prs))
        hello_split = hello.split(" ")
        shouldbe = [
            str(Echo(hello_split[0], hello_split[1:], 0, prs[0].outfd, 2)),
            str(Cat(cat, [], prs[1].infd, 1, 2)),
        ]
        self.assertEqual(str(shouldbe), str(parsed))

    def test_single_quotes(self):
        raw = "echo 'hello world'"
        parsed = list(map(str, CliParser().parse(raw)))
        self.assertEqual(parsed, [str(Echo("echo", ["hello world"]))])

    def test_double_quotes(self):
        raw = 'echo "hello world"'
        parsed = list(map(str, CliParser().parse(raw)))
        self.assertEqual(parsed, [str(Echo("echo", ["hello world"]))])

    def test_expansion(self):
        var = "a"
        raw = 'echo "$' + var + '"'
        parsed = list(map(str, CliParser({"a": "b"}).parse(raw)))
        self.assertEqual(parsed, [str(Echo("echo", ["b"]))])

    def test_no_expansion(self):
        s = "$a"
        raw = "echo '" + s + "'"
        parsed = list(map(str, CliParser({"a": "b"}).parse(raw)))
        self.assertEqual(parsed, [str(Echo("echo", [s]))])

    def test_unbalanced(self):
        raw = "echo ' hello world"
        with self.assertRaises(SyntaxError):
            _ = CliParser().parse(raw)

    def test_quotes(self):
        raw = "echo \"hello '$a' world\""
        parsed = list(map(str, CliParser({"a": "b"}).parse(raw)))
        shouldbe = [str(Echo("echo", ["hello 'b' world"]))]
        self.assertEqual(str(shouldbe), str(parsed))

    def test_quotes2(self):
        raw = "$a$b"
        parsed = list(map(str, CliParser({"a": "ex", "b": "it"}).parse(raw)))
        shouldbe = [str(Exit("exit", []))]
        self.assertEqual(parsed, shouldbe)

    def test_variable(self):
        raw = "a=b"
        shouldbe = [str(Eq("=", ["a", "b"]))]
        self.assertEqual(shouldbe, list(map(str, CliParser().parse(raw))))


class TokenizeTest(TestCase):
    lexer = CliLexer({})

    def test_echo(self):
        raw = "echo"
        self.assertEqual([raw], self.lexer.tokenize(raw))

    def test_args(self):
        raw = ["echo", " ", "hello"]
        self.assertEqual(raw, self.lexer.tokenize("".join(raw)))

    def test_squotes(self):
        raw = "'echo hello'"
        self.assertEqual([raw], self.lexer.tokenize(raw))

    def test_dquotes(self):
        raw = '"echo hello"'
        self.assertEqual([raw], self.lexer.tokenize(raw))

    def test_quotes_1(self):
        raw = ["echo", " ", '"echo hello"', " ", "|", " ", "cat"]

        self.assertEqual(raw, self.lexer.tokenize("".join(raw)))

    def test_quotes_2(self):
        raw = ["echo", " ", '\'" " "\'']
        self.assertEqual(raw, self.lexer.tokenize("".join(raw)))

    def test_quotes_3(self):
        raw = ["echo", " ", "\" ' ' ' \""]
        self.assertEqual(raw, self.lexer.tokenize("".join(raw)))

    def test_expansion(self):
        raw = "$a$b"
        lexer = CliLexer({"a": "ex", "b": "it"})
        self.assertEqual(["ex", "it"], lexer.tokenize(raw))

    def test_expansion2(self):
        raw = "$a $b"
        lexer = CliLexer({"a": "ex", "b": "it"})
        self.assertEqual(["ex", " ", "it"], lexer.tokenize(raw))

    def test_expansion3(self):
        raw = "\"hello '$a' world\""
        lexer = CliLexer({"a": "ex"})
        self.assertEqual(["\"hello 'ex' world\""], lexer.tokenize(raw))

    def test_variable(self):
        raw = "a=b"
        self.assertEqual(["a", "=", "b"], self.lexer.tokenize(raw))


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
