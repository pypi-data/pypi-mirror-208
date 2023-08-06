import pathlib

import jinja2
import pkg_resources

package = __name__.split(".")[0]
templates_dir = pathlib.Path(pkg_resources.resource_filename(package, "templates"))
loader = jinja2.FileSystemLoader(searchpath=templates_dir)
env = jinja2.Environment(loader=loader, keep_trailing_newline=True)


def render_templates(path: pathlib.Path):
    makefile(path)
    goreleaser(path)
    github_workflows_ci(path)
    github_workflows_release(path)


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
