import pathlib

import jinja2
import pkg_resources

package = __name__.split(".")[0]
templates_dir = pathlib.Path(pkg_resources.resource_filename(package, "templates"))
loader = jinja2.FileSystemLoader(searchpath=templates_dir)
env = jinja2.Environment(loader=loader, keep_trailing_newline=True)


def doit(path: str):
    template = env.get_template("goreleaser.yaml.j2")
    out_path = pathlib.Path(".goreleaser.yaml")

    data = {
        "new_app_name": pathlib.Path(path).name,
    }
    out = template.render(data=data)
    out_path.write_text(out)

    template = env.get_template("Makefile.j2")
    out_path = pathlib.Path("Makefile")

    data = {
        "new_app_name": pathlib.Path(path).name,
    }
    out = template.render(data=data)
    out_path.write_text(out)
