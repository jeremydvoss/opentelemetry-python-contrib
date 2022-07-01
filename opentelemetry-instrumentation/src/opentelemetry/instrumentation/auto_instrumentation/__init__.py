#!/usr/bin/env python3

# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from argparse import REMAINDER, ArgumentParser
from logging import getLogger
from os import environ, execl, getcwd
from os.path import abspath, dirname, pathsep
from re import sub
from shutil import which

from pkg_resources import iter_entry_points

from opentelemetry.instrumentation.version import __version__

_logger = getLogger(__name__)


def run() -> None:

    print("JEREMYVOSS: auto_instrumentation/__init__/run()")
    parser = ArgumentParser(
        description="""
        opentelemetry-instrument automatically instruments a Python
        program and its dependencies and then runs the program.
        """,
        epilog="""
        Optional arguments (except for --help and --version) for opentelemetry-instrument
        directly correspond with OpenTelemetry environment variables. The
        corresponding optional argument is formed by removing the OTEL_ or
        OTEL_PYTHON_ prefix from the environment variable and lower casing the
        rest. For example, the optional argument --attribute_value_length_limit
        corresponds with the environment variable
        OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT.

        These optional arguments will override the current value of the
        corresponding environment variable during the execution of the command.
        """,
    )

    argument_otel_environment_variable = {}
    print("JEREMYVOSS: len(iter_entry_points): %s" % sum(1 for _ in iter_entry_points(
        "opentelemetry_environment_variables"
    )))     
    for entry_point in iter_entry_points(
        "opentelemetry_environment_variables"
    ):
        print("\tJEREMYVOSS: entry_point: %s" % entry_point)
        environment_variable_module = entry_point.load()
        print("\tJEREMYVOSS: environment_variable_module: %s" % environment_variable_module)

        for attribute in dir(environment_variable_module):
            print("\t\tJEREMYVOSS: attribute: %s" % attribute)

            if attribute.startswith("OTEL_"):

                argument = sub(r"OTEL_(PYTHON_)?", "", attribute).lower()

                parser.add_argument(
                    f"--{argument}",
                    required=False,
                )
                argument_otel_environment_variable[argument] = attribute

    parser.add_argument(
        "--version",
        help="print version information",
        action="version",
        version="%(prog)s " + __version__,
    )
    parser.add_argument("command", help="Your Python application.")
    parser.add_argument(
        "command_args",
        help="Arguments for your application.",
        nargs=REMAINDER,
    )

    args = parser.parse_args()

    for argument, otel_environment_variable in (
        argument_otel_environment_variable
    ).items():
        print("JEREMYVOSS: argument: %s" % argument)
        print("JEREMYVOSS: otel_environment_variable: %s" % otel_environment_variable)
        value = getattr(args, argument)
        if value is not None:

            environ[otel_environment_variable] = value

    python_path = environ.get("PYTHONPATH")
    print("JEREMYVOSS: init PYTHONPATH: %s" % python_path)

    if not python_path:
        python_path = []

    else:
        python_path = python_path.split(pathsep)

    cwd_path = getcwd()
    print("JEREMYVOSS: cwd_path: %s" % cwd_path)


    # This is being added to support applications that are being run from their
    # own executable, like Django.
    # FIXME investigate if there is another way to achieve this
    if cwd_path not in python_path:
        python_path.insert(0, cwd_path)

    filedir_path = dirname(abspath(__file__))
    print("JEREMYVOSS: filedir_path: %s" % filedir_path)

    python_path = [path for path in python_path if path != filedir_path]

    python_path.insert(0, filedir_path)

    environ["PYTHONPATH"] = pathsep.join(python_path)

    executable = which(args.command)
    execl(executable, executable, *args.command_args)
