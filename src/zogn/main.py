import os
import re

from zogn.builders import build_article, build_category, build_about, build_sitemap, writer, build_static, \
    build_index, build_tags, build_all_tags, build_rss, build_links, build_archives
import click
from datetime import date, datetime
from slugify import slugify

from zogn.parsers import check_repeat_slug
from zogn.server import app
from zogn import conf
import functools
import shutil

pattern = r'(\d{4}年\d{2}月\d{2}日\s周[一二三四五六日].*?)\n(.*?)(?=\d{4}年\d{2}月\d{2}日|\Z)'
meta_pattern = r'(\d{4}年\d{2}月\d{2}日)\s(周[一二三四五六日])\s·(.*?)\s·|(\d{4}年\d{2}月\d{2}日)\s(周[一二三四五六日])'

DAYOFWEEK = {
    "周一": "Mon",
    "周二": "Tue",
    "周三": "Wed",
    "周四": "Thu",
    "周五": "Fri",
    "周六": "Sat",
    "周日": "Sun",
}


# meta_pattern = r'(\d{4}年\d{2}月\d{2}日)\s(周[一二三四五六日])'


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

    check_repeat_slug()

    articles = conf.POST_DATA["articles"]

    build_article(articles)
    build_sitemap(articles)
    build_category(articles)
    build_tags(articles)
    build_all_tags(articles)
    build_index(articles)
    build_rss(articles)
    build_archives(articles)
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
    parent_folder = conf.CONTENT_PATH.joinpath(conf.POST_SOURCE_FOLDER_NAME, public_date.strftime("%Y"))
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


@cli.command("load", short_help="加载日志")
@click.argument("filepath")
def init_command(filepath):
    text = open(filepath, "r").read()
    matches = re.findall(pattern, text, re.DOTALL)
    for match in matches:
        daily_meta, content = match
        # content = content.replace('\n', '\n\n')
        daily_metas = re.search(meta_pattern, daily_meta.strip())
        daily_date, daily_day, daily_weather, _daily_date, _daily_day = daily_metas.groups()
        if _daily_day is None:
            article_date = daily_date
            article_day = daily_day
            article_weather = daily_weather
        else:
            article_date = _daily_date
            article_day = _daily_day
            article_weather = daily_weather

        article_date = datetime.strptime(article_date, "%Y年%m月%d日")
        daily_title = article_date.strftime("%Y%m%d")

        tmp_str_list = []
        embedded_data = {"title": daily_title, "slug": daily_title, "category": "日常", "status": "public",
                         "date": article_date.strftime("%Y-%m-%d"), "day": article_day, "tag": [],
                         "weather": article_weather if article_weather else ""}
        for key, val in embedded_data.items():
            tmp_str_list.append(f"{key}: {val}")
        meta_str = "\n".join(tmp_str_list)
        template = conf.DEFAULT_POST_TEMPLATE.format(meta_str).strip()
        template += "\n" + content
        parent_folder = conf.DAILY_PATH.joinpath(article_date.strftime("%Y"), article_date.strftime("%Y%m"))
        parent_folder.mkdir(parents=True, exist_ok=True)

        filename = parent_folder.joinpath(daily_title)
        writer(f'{filename}.md', template)


@cli.command("server", short_help="本地预览")
@root_command
def server_command():
    check_repeat_slug()
    app.run(port=9999, debug=True)


if __name__ == '__main__':
    cli()
