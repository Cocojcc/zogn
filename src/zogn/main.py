from zogn.builders import build_article, build_category, build_about, build_links, build_sitemap, writer, build_static, \
    build_index
import click
from datetime import date
from slugify import slugify
from zogn.server import app
from zogn import conf
import functools


def root_command(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not conf.CONF_PATH.exists():
            raise Exception("请切换到主目录运行该命令")
        return func(*args, **kwargs)

    return wrapper


def exact_filename(filename):
    filename = filename.split("/")[-1]
    filename = filename.split(".")[0]
    return filename


@click.group(name="zogn", short_help="A simple static blog generator.")
@click.version_option(version="0.1")
def cli():
    pass


@cli.command("build", short_help="构建项目")
@root_command
def build():
    build_article()
    build_links()
    build_sitemap()
    build_about()
    build_category()
    build_static()
    build_index()


@cli.command("new", short_help="新建文章")
@click.argument('filename')
@root_command
def generate_markdown(filename):
    tmp_str_list = []
    title = exact_filename(filename)
    data = {"title": title, "slug": slugify(title), "category": "draft",
            "date": date.today().strftime("%Y-%m-%d"), "status": "draft"}
    for key, val in data.items():
        tmp_str_list.append(f"{key}: {val}")
    meta_str = "\n".join(tmp_str_list)
    template = conf.DEFAULT_POST_TEMPLATE.format(meta_str).strip()
    filename = conf.CONTENT_PATH.joinpath(filename)
    if conf.POST_FOLDER_NAME in filename.parts:
        conf.POST_PATH.mkdir(parents=True, exist_ok=True)
    writer(filename, template)


@cli.command("init", short_help="新建项目")
@click.argument("name")
def init_command(name):
    project_path = conf.BASE_DIR.joinpath(name)
    project_path.mkdir(parents=True, exist_ok=True)
    project_path.joinpath(conf.CONTENT_FOLDER_NAME).mkdir(parents=True, exist_ok=True)
    project_path.joinpath(conf.HTML_FOLDER_NAME).mkdir(parents=True, exist_ok=True)
    project_path.joinpath(conf.THEME_FOLDER_NAME).mkdir(parents=True, exist_ok=True)

    writer(project_path.joinpath("settings.toml"), conf.TOML_TEMPLATE)
    writer(project_path.joinpath(conf.CONTENT_FOLDER_NAME, "about.md"), "")


@cli.command("server", short_help="本地预览")
@root_command
def server_command():
    app.run(port=9999, debug=True)


if __name__ == '__main__':
    cli()
