import os
import sys
import unittest as ut
from contextlib import contextmanager

from cli.builtins import Cat, Cd, Echo, Eq, Exit, Grep, Ls, Pwd, Wc
from cli.common import Command
from cli.shell import Shell


# https://stackoverflow.com/questions/47066063/how-to-capture-python-subprocess-stdout-in-unittest
@contextmanager
def redirect(new_in, new_out, new_err):
    old_stdin = os.dup(0)
    old_stdout = os.dup(1)
    old_stderr = os.dup(2)
    try:
        os.dup2(new_in, sys.stdin.fileno())
        os.dup2(new_out, sys.stdout.fileno())
        os.dup2(new_err, sys.stderr.fileno())
        yield
    finally:
        os.dup2(old_stdin, 0)
        os.dup2(old_stdout, 1)
        os.dup2(old_stderr, 2)


class ExecutorTest(ut.TestCase):
    def test_system(self):
        hello = "Hello, world!\n"
        pipeline = [Command("./tests/test.sh", [])]
        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with open(stdin[1], "w") as sin:
            sin.write(hello)

        with open(stdin[0], "r") as sin, open(stdout[1], "w") as sout, open(
                stderr[1], "w"
        ) as serr:
            sh = Shell(sin, sout, serr, {}, None)
            sh._execute(pipeline)
        with open(stdout[0], "r") as res:
            self.assertEqual(res.read(), hello)

    def test_echo(self):
        hello = "Hello, world!"
        pipeline = [Echo("echo", [hello])]
        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with open(stdin[0], "r") as sin, open(stdout[1], "w") as sout, open(
                stderr[1], "w"
        ) as serr:
            sh = Shell(sin, sout, serr, {}, None)
            sh._execute(pipeline)
        with open(stdout[0], "r") as res:
            self.assertEqual(res.read(), hello + "\n")

    def test_cat(self):
        testfile = "./tests/test.txt"
        pipeline = [Cat("cat", [testfile])]
        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with open(stdin[0], "r") as sin, open(stdout[1], "w") as sout, open(
                stderr[1], "w"
        ) as serr:
            sh = Shell(sin, sout, serr, {}, None)
            sh._execute(pipeline)

        with open(testfile, "r") as f:
            content = f.read()

        with open(stdout[0], "r") as res:
            self.assertEqual(content, res.read())

    def test_cd(self):
        dir = "../cli/tests"
        pipeline = [Cd("cd", [dir])]
        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with open(stdin[0], "r") as sin, open(stdout[1], "w") as sout, open(
                stderr[1], "w"
        ) as serr:
            sh = Shell(sin, sout, serr, {}, None)
            sh._execute(pipeline)

        content = "/cli/tests"

        with open(stdout[0], "r") as res:
            self.assertEqual(content, res.read())

    def test_wc(self):
        testfile = "./tests/test.txt"
        content = "1 5 21"
        pipeline = [Wc("wc", [testfile])]
        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()

        with open(stdin[0], "r") as sin, open(stdout[1], "w") as sout, open(
                stderr[1], "w"
        ) as serr:
            sh = Shell(sin, sout, serr, {}, None)
            sh._execute(pipeline)

        with open(stdout[0], "r") as res:
            self.assertEqual(content, res.read())

    def test_ls(self):
        pipeline = [Ls("ls", [])]
        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with open(stdin[0], "r") as sin, open(stdout[1], "w") as sout, open(
                stderr[1], "w"
        ) as serr:
            sh = Shell(sin, sout, serr, {}, None)
            sh._execute(pipeline)

        content = ".bashrc\n.profile\n.cache\n.wget-hsts\n.python_history\n"

        with open(stdout[0], "r") as res:
            self.assertEqual(content, res.read())

    def test_pwd(self):
        pwd = os.getcwd()
        pipeline = [Pwd("pwd", [])]
        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()

        with open(stdin[0], "r") as sin, open(stdout[1], "w") as sout, open(
                stderr[1], "w"
        ) as serr:
            sh = Shell(sin, sout, serr, {"PWD": pwd}, None)
            sh._execute(pipeline)

        with open(stdout[0], "r") as res:
            self.assertEqual(pwd, res.read())

    def test_exit(self):
        pipeline = [Exit("exit", [])]
        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with open(stdin[0], "r") as sin, open(stdout[1], "w") as sout, open(
                stderr[1], "w"
        ) as serr:
            sh = Shell(sin, sout, serr, {}, None)
            with self.assertRaises(SystemExit):
                sh._execute(pipeline)

    def test_pipes(self):
        hello = "hello world"

        pipe1, pipe2 = os.pipe(), os.pipe()
        err1, err2 = os.pipe(), os.pipe()
        pipeline = [
            Echo("echo", hello.split(" "), outfd=pipe1[1], errfd=err1[1]),
            Cat("cat", [], infd=pipe1[0], outfd=pipe2[1], errfd=err2[1]),
            Cat("cat", [], infd=pipe2[0]),
        ]
        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with open(stdin[0], "r") as sin, open(stdout[1], "w") as sout, open(
                stderr[1], "w"
        ) as serr:
            sh = Shell(sin, sout, serr, {}, None)
            sh._execute(pipeline)
        with open(stdout[0], "r") as res:
            self.assertEqual(hello + "\n", res.read())

    def test_eq(self):
        pipeline = [Eq("=", ["a", "b"])]
        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with open(stdin[0], "r") as sin, open(stdout[1], "w") as sout, open(
                stderr[1], "w"
        ) as serr:
            env = {}
            sh = Shell(sin, sout, serr, env, None)
            sh._execute(pipeline)
            self.assertIn("a", env)
            self.assertEqual("b", env["a"])


class GrepTest(ut.TestCase):
    def test_grep(self):
        pipeline = [Grep("grep", ["test", "./tests/1.txt"])]
        output = """This is a test line number one.
This is another line that has the word test in it.\n"""

        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with open(stdin[0], "r") as sin, open(stdout[1], "w") as sout, open(
                stderr[1], "w"
        ) as serr:
            sh = Shell(sin, sout, serr, None, None)
            sh._execute(pipeline)
        with open(stdout[0], "r") as res:
            self.assertEqual(output, res.read())

    def test_insensitive(self):
        pipeline = [Grep("grep", ["-i", "test", "./tests/1.txt"])]
        output = """This is a test line number one.
This is another line that has the word test in it.
This one has capitalized Test.\n"""
        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with open(stdin[0], "r") as sin, open(stdout[1], "w") as sout, open(
                stderr[1], "w"
        ) as serr:
            sh = Shell(sin, sout, serr, None, None)
            sh._execute(pipeline)
        with open(stdout[0], "r") as res:
            self.assertEqual(output, res.read())

    def test_regex(self):
        pipeline = [Grep("grep", [".*?", "./tests/1.txt"])]
        with open("./tests/1.txt", "r") as f:
            output = f.read()
        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with open(stdin[0], "r") as sin, open(stdout[1], "w") as sout, open(
                stderr[1], "w"
        ) as serr:
            sh = Shell(sin, sout, serr, None, None)
            sh._execute(pipeline)
        with open(stdout[0], "r") as res:
            self.assertEqual(output, res.read())

    def test_literal_regex(self):
        pipeline = [Grep("grep", ["-w", ".*?", "./tests/1.txt"])]
        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with open(stdin[0], "r") as sin, open(stdout[1], "w") as sout, open(
                stderr[1], "w"
        ) as serr:
            sh = Shell(sin, sout, serr, None, None)
            sh._execute(pipeline)
        with open(stdout[0], "r") as res:
            self.assertEqual("", res.read())

    def test_after_context(self):
        pipeline = [Grep("grep", ["-A", "2", "test", "./tests/1.txt"])]
        output = """This is a test line number one.
This is another line that has the word test in it.
This one has capitalized Test.
some dumb line\n"""
        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with open(stdin[0], "r") as sin, open(stdout[1], "w") as sout, open(
                stderr[1], "w"
        ) as serr:
            sh = Shell(sin, sout, serr, None, None)
            sh._execute(pipeline)
        with open(stdout[0], "r") as res:
            self.assertEqual(output, res.read())

    def test_from_stdin(self):
        pipe1, pipe2 = os.pipe(), os.pipe()
        pipeline = [
            Cat("cat", ["./tests/1.txt"], outfd=pipe1[1], errfd=pipe2[1]),
            Grep("grep", ["test"], infd=pipe1[0]),
        ]
        output = """This is a test line number one.
This is another line that has the word test in it.\n"""
        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with open(stdin[0], "r") as sin, open(stdout[1], "w") as sout, open(
                stderr[1], "w"
        ) as serr:
            sh = Shell(sin, sout, serr, None, None)
            sh._execute(pipeline)
        with open(stdout[0], "r") as res:
            self.assertEqual(output, res.read())
