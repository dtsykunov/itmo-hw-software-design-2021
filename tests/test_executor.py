import io
import os
import subprocess as sp
import sys
import unittest as ut
from contextlib import contextmanager

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
        self.assertEqual(os.read(stdout[0], len(hello)), hello)

    # I wanted to use "mock" package to assert the fact that it is builtin commands
    # that are being called here, not external ones. "mock.patch", however, somehow messes
    # with file descriptors just as I do with "redirect", making me unable to check the output.
    # You will have to trust me that it is builtin commands that are actually called.
    def test_echo(self):
        hello = b"Hello, world!"
        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with redirect(stdin[0], stdout[1], stderr[1]):
            pipeline: Pipeline = Pipeline([Command("echo", [hello])])
            Executor.execute(pipeline)
            os.write(stdin[1], hello)
        self.assertEqual(os.read(stdout[0], len(hello)), hello)

    def test_cat(self):
        testfile = "./tests/test.txt"
        with open(testfile, "rb") as f:
            content = f.read()

        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with redirect(stdin[0], stdout[1], stderr[1]):
            pipeline: Pipeline = Pipeline([Command("cat", [testfile])])
            Executor.execute(pipeline)
            os.write(stdin[1], content)
        os.set_blocking(stdout[0], False)
        os.set_blocking(stderr[0], False)
        self.assertEqual(os.read(stdout[0], len(content)), content)
        with self.assertRaises(BlockingIOError):
            os.read(stderr[0], 1)

    def test_wc(self):
        testfile = "./tests/test.txt"
        with open(testfile, "rb") as f:
            content = f.read()

        stdin, stdout, stderr = os.pipe(), os.pipe(), os.pipe()
        with redirect(stdin[0], stdout[1], stderr[1]):
            pipeline: Pipeline = Pipeline([Command("wc", [testfile])])
            Executor.execute(pipeline)
            os.write(stdin[1], content)
        os.set_blocking(stdout[0], False)
        os.set_blocking(stderr[0], False)
        self.assertEqual(os.read(stdout[0], len(content)), content)
        with self.assertRaises(BlockingIOError):
            os.read(stderr[0], 1)
