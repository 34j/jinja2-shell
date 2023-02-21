import os
from unittest import TestCase

from jinja2 import Environment
from parameterized import parameterized_class


@parameterized_class(
    ("command", "expected"),
    [
        ("echo Hello World", "Hello World"),
        ("echo 'Hello World'", "'Hello World'" if os.name == "nt" else "Hello World"),
        (
            r"echo \"Hello World\"",
            '"Hello World"' if os.name == "nt" else "Hello World",
        ),
        (
            "echo Hello World | tr ' ' '_'",
            "Hello_World_" if os.name == "nt" else "Hello_World",
        ),
    ],
)
class TestMain(TestCase):
    # https://jinja.palletsprojects.com/en/3.0.x/templates/
    environment: Environment
    command: str
    expected: str

    def setUp(self):
        self.environment = Environment(extensions=["jinja2_shell.ShellExtension"])

    def test_statement(self):
        template = self.environment.from_string(
            "{% shell " + f'"{self.command}"' + " %}"
        )
        self.assertEqual(template.render(), self.expected)

    def test_statement_no_rstrip(self):
        template = self.environment.from_string(
            "{% shell " + f'"{self.command}"' + ", False %}"
        )
        self.assertEqual(template.render(), self.expected + "\n")

    def test_expression(self):
        template = self.environment.from_string(
            "{{ " + f'"{self.command}"' + " | shell }}"
        )
        self.assertEqual(template.render(), self.expected)

    def test_expression_no_rstrip(self):
        template = self.environment.from_string(
            "{{ " + f'"{self.command}"' + " | shell(False) }}"
        )
        self.assertEqual(template.render(), self.expected + "\n")
