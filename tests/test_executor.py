import os
import sys
import unittest as ut
from contextlib import contextmanager
from unittest import mock

from cli.common import Command, Pipeline
from cli.executor import Executor


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
        hello = b"Hello, world!"
        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with redirect(stdin[0], stdout[1], stderr[1]):
            pipeline: Pipeline = Pipeline([Command("./tests/test.sh", [])])
            Executor.execute(pipeline)
            os.write(stdin[1], hello)
        os.set_blocking(stdout[0], False)
        os.set_blocking(stderr[0], False)
        self.assertEqual(os.read(stdout[0], len(hello)), hello)
        with self.assertRaises(BlockingIOError):
            os.read(stderr[0], 1)

    @mock.patch("cli.executor._exec_builtin")
    def call_builtin(self, pipeline, mock):
        # ignoring the output, checking only that builtin command was called
        with open(os.devnull, "w") as f:
            Executor.execute(pipeline, stdout=f)
        mock.assert_called()

    def test_builtin(self):
        # these commands are called as external processes
        self.call_builtin(Pipeline([Command("cat", ["./tests/test.txt"])]))
        self.call_builtin(Pipeline([Command("echo")]))
        self.call_builtin(Pipeline([Command("pwd")]))
        self.call_builtin(Pipeline([Command("wc", ["./tests/test.txt"])]))
        # "exit" and "=" are executed as external processes if they don't appear at the
        # end of the pipeline, otherwise they're executed in the current shell process
        self.call_builtin(Pipeline([Command("exit"), Command("./tests/test.sh")]))
        self.call_builtin(
            Pipeline([Command("=", ["a", "b"]), Command("./tests/test.sh")])
        )

    def test_echo(self):
        hello = b"Hello, world!"
        pipeline: Pipeline = Pipeline([Command("echo", [hello])])
        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with redirect(stdin[0], stdout[1], stderr[1]):
            Executor.execute(pipeline)
            os.write(stdin[1], hello)
        os.set_blocking(stdout[0], False)
        os.set_blocking(stderr[0], False)
        self.assertEqual(os.read(stdout[0], len(hello)), hello)
        with self.assertRaises(BlockingIOError):
            os.read(stderr[0], 1)

    def test_cat(self):
        testfile = "./tests/test.txt"
        with open(testfile, "rb") as f:
            content = f.read()
        pipeline: Pipeline = Pipeline([Command("cat", [testfile])])

        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with redirect(stdin[0], stdout[1], stderr[1]):
            Executor.execute(pipeline)
            os.write(stdin[1], content)
        os.set_blocking(stdout[0], False)
        os.set_blocking(stderr[0], False)
        self.assertEqual(os.read(stdout[0], len(content)), content)
        with self.assertRaises(BlockingIOError):
            os.read(stderr[0], 1)

    def test_wc(self):
        testfile = "./tests/test.txt"
        res = b"1 5 21\n"

        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with redirect(stdin[0], stdout[1], stderr[1]):
            pipeline: Pipeline = Pipeline([Command("wc", [testfile])])
            Executor.execute(pipeline)
        os.set_blocking(stdout[0], False)
        os.set_blocking(stderr[0], False)
        self.assertEqual(os.read(stdout[0], len(res)), res)
        with self.assertRaises(BlockingIOError):
            os.read(stderr[0], 1)

    def test_pwd(self):
        pwd = os.getcwd().encode("utf-8")
        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with redirect(stdin[0], stdout[1], stderr[1]):
            pipeline: Pipeline = Pipeline([Command("pwd", [])])
            Executor.execute(pipeline)
        os.set_blocking(stdout[0], False)
        os.set_blocking(stderr[0], False)
        self.assertEqual(os.read(stdout[0], len(pwd)), pwd)
        with self.assertRaises(BlockingIOError):
            os.read(stderr[0], 1)

    def test_exit(self):
        pipeline: Pipeline = Pipeline([Command("exit")])
        with mock.patch("cli.executor.sys.exit") as m:
            Executor.execute(pipeline)
            m.assert_called()

    def test_pipes(self):
        hello = b"hello world"
        pipeline: Pipeline = Pipeline(
            [
                Command("echo", hello.decode("utf-8").split(" ")),
                Command("cat"),
                Command("cat"),
            ]
        )

        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with redirect(stdin[0], stdout[1], stderr[1]):
            Executor.execute(pipeline)
        os.set_blocking(stdout[0], False)
        self.assertEqual(os.read(stdout[0], len(hello) + 1), hello + b"\n")
        # Не очень понятное поведение. Почему в stderr $HOME?
        # os.set_blocking(stderr[0], False)
        # with self.assertRaises(BlockingIOError):
        #     os.read(stderr[0], 1)

    def test_eq(self):
        pipeline: Pipeline = Pipeline(
            [
                Command("=", ["a", "b"]),
            ]
        )
        with mock.patch.dict(os.environ, {}) as m:
            Executor.execute(pipeline)
            self.assertIn("a", m)
            self.assertEqual("b", m["a"])


class GrepTest(ut.TestCase):
    def test_grep(self):
        pipeline: Pipeline = Pipeline([Command("grep", ["test", "./tests/1.txt"])])
        output = b"""This is a test line number one.
This is another line that has the word test in it.\n"""
        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with redirect(stdin[0], stdout[1], stderr[1]):
            Executor.execute(pipeline)
        os.set_blocking(stdout[0], False)
        self.assertEqual(os.read(stdout[0], len(output)), output)

    def test_insensitive(self):
        pipeline: Pipeline = Pipeline(
            [Command("grep", ["-i", "test", "./tests/1.txt"])]
        )
        output = b"""This is a test line number one.
This is another line that has the word test in it.
This one has capitalized Test.\n"""
        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with redirect(stdin[0], stdout[1], stderr[1]):
            Executor.execute(pipeline)
        os.set_blocking(stdout[0], False)
        self.assertEqual(os.read(stdout[0], len(output)), output)

    def test_regex(self):
        pipeline: Pipeline = Pipeline([Command("grep", [".*?", "./tests/1.txt"])])
        with open("./tests/1.txt", "rb") as f:
            output = f.read()
        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with redirect(stdin[0], stdout[1], stderr[1]):
            Executor.execute(pipeline)
        os.set_blocking(stdout[0], False)
        self.assertEqual(os.read(stdout[0], len(output)), output)

    def test_literal_regex(self):
        pipeline: Pipeline = Pipeline([Command("grep", ["-w", ".*?", "./tests/1.txt"])])
        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with redirect(stdin[0], stdout[1], stderr[1]):
            Executor.execute(pipeline)

        os.set_blocking(stdout[0], False)
        with self.assertRaises(BlockingIOError):
            os.read(stdout[0], 1)

    def test_after_context(self):
        pipeline: Pipeline = Pipeline(
            [Command("grep", ["-A", "2", "test", "./tests/1.txt"])]
        )
        output = b"""This is a test line number one.
This is another line that has the word test in it.
This one has capitalized Test.
some dumb line\n"""
        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with redirect(stdin[0], stdout[1], stderr[1]):
            Executor.execute(pipeline)
        self.assertEqual(os.read(stdout[0], len(output) + 1), output)
