import pathlib

import jinja2
import pkg_resources

package = __name__.split(".")[0]
templates_dir = pathlib.Path(pkg_resources.resource_filename(package, "templates"))
loader = jinja2.FileSystemLoader(searchpath=templates_dir)
env = jinja2.Environment(loader=loader, keep_trailing_newline=True)


def render_templates(project_path: pathlib.Path):
    makefile(project_path)
    goreleaser(project_path)
    github_workflows_ci(project_path)
    github_workflows_release(project_path)
    create_gitingore(project_path)


def create_gitingore(_dir: pathlib.Path):
    gitignore = _dir / ".gitignore"
    gitignore.touch()

    # Check if 'dist/' is already in .gitignore
    if "dist/" not in gitignore.read_text():
        # Append 'dist/' to .gitignore
        with gitignore.open(mode="a") as f:
            f.write("\ndist/\n")


def goreleaser(path: pathlib.Path):
    template = env.get_template("goreleaser.yaml.j2")
    out_path = pathlib.Path(".goreleaser.yaml")

    data = {
        "new_app_name": pathlib.Path(path).name,
    }
    out = template.render(data=data)
    out_path.write_text(out)


def makefile(path: pathlib.Path):
    template = env.get_template("Makefile.j2")
    out_path = pathlib.Path("Makefile")

    data = {
        "new_app_name": pathlib.Path(path).name,
    }
    out = template.render(data=data)
    out_path.write_text(out)


def github_workflows_ci(path: pathlib.Path):
    template = env.get_template("github_ci.yml")
    out_path = pathlib.Path.cwd() / ".github/workflows/ci.yml"
    out_path.parent.mkdir(exist_ok=True, parents=True)

    data = {
        "new_app_name": pathlib.Path(path).name,
    }
    out = template.render(data=data)
    out_path.write_text(out)


def github_workflows_release(path: pathlib.Path):
    template = env.get_template("github_release.yml")
    out_path = pathlib.Path.cwd() / ".github/workflows/release.yml"
    out_path.parent.mkdir(exist_ok=True, parents=True)

    data = {
        "new_app_name": pathlib.Path(path).name,
    }
    out = template.render(data=data)
    out_path.write_text(out)
