import os

from zogn.builders import build_article, build_category, build_about, build_sitemap, writer, build_static, \
    build_index, build_tags, build_all_tags, build_rss, build_links
import click
from datetime import date
from slugify import slugify

from zogn.parsers import load_all_articles
from zogn.server import app
from zogn import conf
import functools
import shutil


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
    if os.path.exists(conf.HTML_OUTPUT_PATH):
        CNAME_PATH = conf.HTML_OUTPUT_PATH / "CNAME"
        if not os.path.exists(CNAME_PATH):
            shutil.rmtree(conf.HTML_OUTPUT_PATH)
        else:
            # 复制CNAME的内容并重新写入
            with CNAME_PATH.open("r") as f:
                CNAME = f.read()
            shutil.rmtree(conf.HTML_OUTPUT_PATH)
            conf.HTML_OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
            with CNAME_PATH.open("w") as f:
                f.write(CNAME)

    articles = load_all_articles()
    build_article(articles)
    build_sitemap(articles)
    build_category(articles)
    build_tags(articles)
    build_all_tags(articles)
    build_index(articles)
    build_rss(articles)
    build_static()
    build_links()
    build_about()


@cli.command("new", short_help="新建文章")
@click.argument('filename')
@root_command
def generate_markdown(filename):
    tmp_str_list = []
    title = exact_filename(filename)
    public_date = date.today()
    data = {"title": title, "slug": slugify(title), "category": "draft", "tags": [],
            "date": public_date.strftime("%Y-%m-%d"), "status": "draft", "subtitle": ""}
    for key, val in data.items():
        tmp_str_list.append(f"{key}: {val}")
    meta_str = "\n".join(tmp_str_list)
    template = conf.DEFAULT_POST_TEMPLATE.format(meta_str).strip()
    parent_folder = conf.CONTENT_PATH.joinpath(conf.POST_FOLDER_NAME, public_date.strftime("%Y"))
    parent_folder.mkdir(parents=True, exist_ok=True)

    filename = parent_folder.joinpath(filename)
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
