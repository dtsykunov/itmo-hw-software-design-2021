import os
import sys
import unittest as ut
from contextlib import contextmanager
from unittest import mock, skip

from cli.common import Command
from cli.shell import Shell
from cli.builtins import Echo, Cat, Wc, Pwd, Exit, Eq


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
            self.assertEqual(res.read(), hello)

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
            self.assertEqual(hello, res.read())

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
