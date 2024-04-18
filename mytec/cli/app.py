import os
from typing import Annotated, List
from pathlib import Path
import rich
import typer

from mytec.cli.venv import create_virtual_env
from jinja2 import Environment, FileSystemLoader

app = typer.Typer()

templates = Environment(loader=FileSystemLoader(Path(__file__).parent / "templates"))


@app.command("test")
def test(
    name: Annotated[str, typer.Argument(help="Some name", envvar="GRIM_NAME")] = "Oz",
    option: Annotated[
        str, typer.Option("--option", "-o", help="Some option")
    ] = "Option",
    prompt_opt: Annotated[str, typer.Option(prompt=True)] = "",
    custom_ptompt_opt: Annotated[
        str, typer.Option(prompt="Some custom prompt")
    ] = "Default",
):
    """
    Test command
    """

    print(name)
    print(option)
    print(prompt_opt)


def get_create_venv_prompt():
    if os.environ.get("VIRTUAL_ENV") is not None:
        return False
    return "Create virtual environment"


class ProjectNode:
    """
    Represents file or folder in project
    """

    def sync(self, parent: Path = None, dry_run=True):
        ...


class File(ProjectNode):
    def __init__(self, path, template: str) -> None:
        self.path = path
        self.template = template

    def sync(self, parent: Path = None, dry_run=True):
        path = Path(parent) / self.path
        if path.exists():
            return

        template = templates.get_template(self.template)
        code = template.render()

        import ast
        # rich.print(ast.dump(ast.parse(code), indent=4, include_attributes=True))
        # rich.print([x.lineno for x in ast.parse(code).body])
        rich.print(code)
        if dry_run is False:
            path.parent.mkdir(exist_ok=True)
            path.touch()
        rich.print(f"[bold]Created... [/bold] {path}")


class Dir(ProjectNode):
    def __init__(self, name: str = None, children: List[ProjectNode] = []) -> None:
        self.name = name
        self.children = children

    def set_name(self, name: str):
        self.name = name


class ProjectTemplate(Dir):
    def __init__(self, children: List[ProjectNode]) -> None:
        super().__init__(children=children)

    def sync(self, dry_run=True):
        root = Path.cwd() / self.name
        for child in self.children:
            child.sync(parent=root.resolve(), dry_run=dry_run)


fastapi_project = ProjectTemplate(children=[])


def create_fastapi_project_template(
    name: str, *, use_database: bool = False, use_jinja2: bool = False
):
    children = [
        File("__init__.py", "__init__.py.tpl"),
        File("app.py", "app.py.tpl"),
        File("settings.py", "settings.py.tpl"),
        File("lifespan.py", "lifespan.py.tpl"),
    ]
    if use_database is True:
        children = children + [
            File("models/__init__.py", "__init__.py.tpl"),
            File("models/base.py", "models_base.py.tpl"),
            File("repositories/__init__.py", "__init__.py.tpl"),
            File("repositories/base.py", "repositories_base.py.tpl"),
        ]
    if use_jinja2 is True:
        children = children + [
            File("templates.py", "templates.py.tpl"),
            File("templates/base.html", "templates_base_html.tpl"),
        ]
    template = ProjectTemplate(children=children)
    template.set_name(name)
    return template


@app.command("init")
def fastapi_new(
    project_name: Annotated[
        str, typer.Option(resolve_path=True, prompt="Project Name")
    ],
    create_venv: Annotated[
        bool,
        typer.Option(
            "--venv",
            "-v",
            prompt=get_create_venv_prompt(),
            help="Create virtual environment not under it",
        ),
    ] = False,
    use_database: Annotated[
        bool, typer.Option("--use-database", "-d", prompt="Use database?")
    ] = True,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = True,
):
    full_path = Path.cwd() / project_name
    if full_path.exists():
        raise Exception("Path already exists")

    if dry_run is False:
        full_path.mkdir()

    if create_venv:
        create_virtual_env(full_path / "venv")

    fastapi_project = create_fastapi_project_template(
        project_name, use_database=use_database
    )
    fastapi_project.sync(dry_run=dry_run)
