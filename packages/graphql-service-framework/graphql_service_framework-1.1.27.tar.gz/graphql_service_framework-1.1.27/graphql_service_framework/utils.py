import dataclasses
import difflib
import importlib
import inspect
import json
import os
import pprint
import subprocess
import sys

from typing import Optional


def dataclass_from_dict(klass, d):
    # noinspection PyBroadException
    try:
        f_types = {f.name: f.type for f in dataclasses.fields(klass)}
        return klass(**{f: dataclass_from_dict(f_types[f], d[f]) for f in d})
    except Exception:
        return d


def set_schema_version(code, new_version):
    from graphql_service_framework.schema import Schema

    schema_class_name = Schema.__name__
    if f"{schema_class_name}, schema_version=" not in code.lower():
        old = f"{schema_class_name}):\n"
        new = f'{schema_class_name}, schema_version="{new_version}"):\n'
        code = code.replace(old, new)
    return code


def get_py_code_changes(a, b, _version):
    import glob

    a_data = {}
    b_data = {}

    for _path in glob.glob(os.path.join(a, "*.py")):
        with open(_path) as f:
            a_data[_path.replace(a, "")] = set_schema_version(f.read(), _version)

    for _path in glob.glob(os.path.join(b, "*.py")):
        with open(_path) as f:
            b_data[_path.replace(b, "")] = f.read()

    if a_data != b_data:
        return "\n" + "\n".join(
            difflib.ndiff(
                pprint.pformat(b_data).splitlines(), pprint.pformat(a_data).splitlines()
            )
        )

    return None


def increment_version(version, i=2, amount=1, reset=True):
    version = version.split(".")
    version[i] = str(int(version[i]) + amount)
    while reset and i != len(version) - 1:
        i += 1
        version[i] = "0"
    return ".".join(version)


def find_schema(modules):
    schemas = set()

    for module in modules:
        for name, obj in module.__dict__.items():
            from graphql_service_framework import Schema

            if inspect.isclass(obj) and issubclass(obj, Schema) and obj != Schema:
                schemas.add(obj)

    if len(schemas) > 1:
        raise TypeError(
            f"The {modules} folder defined multiple schemas '{schemas}'."
            f"Each schema should only have a single schema subclass."
        )
    elif len(schemas) == 1:
        return schemas.pop()
    else:
        raise TypeError(
            f"The {modules} folder didn't define a schema."
            f" Each schema should have a single schema subclass."
        )


def install_package(package, index_url) -> Optional[dict]:
    # noinspection PyBroadException
    try:
        print(f"Installing package {package}")
        report_path = f"{package}-report.json"
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                package,
                f"--index-url={index_url}",
                "--no-deps",
                "--ignore-installed",
                f"--report={report_path}",
                "--quiet",
                "--quiet",
                "--quiet",
            ]
        )

        _report = json.loads(open(report_path).read())

        # Edge case where we are being redirected by gitlab
        if "pythonhosted.org" in _report["install"][0]["download_info"]["url"]:
            print(f"Ignoring gitlab redirect for package {package}")
            return None

        pip_show_response = subprocess.check_output(
            [sys.executable, "-m", "pip", "show", package]
        ).decode(sys.stdout.encoding)

        pip_show = {}

        for line in pip_show_response.splitlines():
            split_line = line.split(": ", 1)
            if len(split_line) == 2:
                pip_show[split_line[0]] = split_line[1]

        _report["pip_show"] = pip_show

        return _report
    except Exception:
        return None


def find_modules(modules_path, package_name):
    print(
        f"Searching for modules in {modules_path} with package name " f"{package_name}"
    )
    _modules = []
    for root, dirs, files in os.walk(modules_path):
        relative_path = root.replace(modules_path + "/", "").replace(modules_path, "")

        print(f" - Searching path {root}.")

        for _file in files:
            _file_name = os.path.join(relative_path, _file)
            print(f" - Found file {_file_name}")
            if (
                _file.endswith(".py")
                and not _file.endswith("setup.py")
                and not _file.endswith("__init__.py")
                and not _file.endswith(".pyc")
                and "__pycache__" not in _file
            ):
                print(f"    - Checking file {_file_name}")
                module_name = _file_name.replace("/", ".").rsplit(".", 1)[0]
                print(f"    - Found module {module_name} in {_file_name}")
                try:
                    _modules.append(
                        importlib.import_module(f"{package_name}.{module_name}")
                    )
                    print(f"    - Imported module {module_name} in {_file_name}")
                except Exception as err:
                    print(
                        f"    - Unable to import module {module_name} in "
                        f"{_file_name}, {err}"
                    )
    return _modules
