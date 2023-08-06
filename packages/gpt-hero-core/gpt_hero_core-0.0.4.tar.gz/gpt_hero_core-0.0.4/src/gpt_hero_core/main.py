import pathlib
import sys
from importlib.metadata import EntryPoint
from inspect import getsourcefile, isabstract, isclass
from itertools import groupby
from types import GenericAlias
from typing import Any

import jinja2
import pydantic
import typer
from devtools import ansi, debug, sprint
from tomlkit import dump, load, table

from .plugins.base import _PluginBase

app = typer.Typer()


@pydantic.validate_arguments
def _load_class(module_path: pydantic.PyObject) -> pydantic.PyObject:
    return module_path


def _loader(module_path: str) -> pydantic.PyObject:
    __import__(module_path)
    return _load_class(module_path)  # type: ignore[arg-type]


def _is_correct_module_path(obj: type[_PluginBase], module_path: pathlib.Path) -> bool:
    try:
        source_path = getsourcefile(obj)
    except OSError:
        return False

    if not source_path:
        # ignore if obj doesn't have a source_path (e.g. Lambda)
        return False

    if module_path.resolve() != pathlib.Path(source_path).resolve():
        # ignore if obj is not defined in module_path (reexport)
        debug(f"ignore reexport {obj} because {module_path} != {source_path}")
        return False

    return True


def scan_plugin_entrypoints(scan_target: pathlib.Path, python_root: pathlib.Path) -> list[EntryPoint]:
    modules = scan_target.rglob("*.py")
    entrypoints: dict[tuple[str, str], EntryPoint] = {}

    for module_path in modules:
        if module_path.name.startswith("_") or not module_path.is_file() or module_path.suffix != ".py":
            # ignore module_path startswith "_" and not file and not .py
            sprint(f"ignore path: {module_path}", ansi.Style.blue)
            continue

        module_name = str(module_path.relative_to(python_root)).split(".")[0].replace("/", ".")
        module_path_str = f"{module_name}"

        try:
            sprint(f"loading {module_path_str}")
            module = _loader(module_path_str)
        except Exception as e:
            sprint(f"cannot load {module_path_str} Error: {e}", ansi.Style.red)
            continue

        for name, obj in module.__dict__.items():
            print(f"{name=} {obj=}")

            if type(obj) == GenericAlias:
                # NOTE: GenericAlias
                continue

            if isclass(obj) and issubclass(obj, _PluginBase):
                if name.startswith("_") or isabstract(obj):
                    sprint(f"ignore Driver {name}", ansi.Style.yellow)
                    continue

                if not _is_correct_module_path(obj, module_path):
                    continue

                sprint(f"found {obj.__name__} in {module_path_str}", ansi.Style.green)

                entrypoint = obj.entrypoint()
                print(f"Load Test: {entrypoint.load()}")

                assert (
                    entrypoint.group,
                    entrypoint.name,
                ) not in entrypoints, f"{entrypoint} conflict with {entrypoints[(entrypoint.group, entrypoint.name)]}"
                entrypoints[(entrypoint.group, entrypoint.name)] = entrypoint

    debug(entrypoints)
    return list(entrypoints.values())


PLUGIN_PY_TEMPLATE = """# Auto Generate by scan-plugins
import enum

{% for group, items in entrypoint_groups %}
class {{group.capitalize()}}(str, enum.Enum):
    {%- for item in items %}
    {{item.name.replace("-", "_")}} = "{{item.name}}"
    {%- endfor %}

{% endfor %}
"""


@app.command()
@pydantic.validate_arguments
def main(
    python_root: pathlib.Path,
    scan_target: pathlib.Path,
    repo_root: pathlib.Path = None,
    refresh: bool = True,
) -> None:
    sys.path.append(str(python_root))

    if not repo_root:
        repo_root = python_root / ".."

    entrypoints = sorted(
        scan_plugin_entrypoints(scan_target, python_root),
        key=lambda x: (x.group, x.name),
    )

    with open("plugins.py", "w") as f:
        f.write(jinja2.Template(PLUGIN_PY_TEMPLATE).render(entrypoint_groups=groupby(entrypoints, lambda x: x.group)))

    with open(repo_root / "pyproject.toml", "r") as f:
        pyproject: dict[str, Any] = load(f)

    if refresh:
        pyproject["tool"]["poetry"]["plugins"] = table()

    for group, items in groupby(entrypoints, lambda x: x.group):
        if "plugins" not in pyproject["tool"]["poetry"]:
            pyproject["tool"]["poetry"]["plugins"] = table()

        if group not in pyproject["tool"]["poetry"]["plugins"]:
            pyproject["tool"]["poetry"]["plugins"][group] = table()

        for item in items:
            pyproject["tool"]["poetry"]["plugins"][group][item.name] = item.value

    debug(pyproject)

    with open(repo_root / "pyproject.toml", "w") as f:
        dump(pyproject, f)


if __name__ == "__main__":
    app()
