import shutil

import markdown
from jinja2 import Environment, FileSystemLoader
from zogn import conf

from zogn.parsers import parse_tag, parse_sitemap, load_all_articles, parse_index

env = Environment(loader=FileSystemLoader(conf.THEME_PATH / conf.TEMPLATES_FOLDER))

SLUG_TO_PATH = {}


def build_article():
    articles = load_all_articles()
    for article in articles:
        html = render_to_html("post/detail.html", article=article)
        pre_dirs = list(set(conf.CONTENT_PATH.parts) ^ set(conf.POST_PATH.parts))
        path_prefix = conf.HTML_OUTPUT_PATH.joinpath("/".join(pre_dirs))
        path_prefix.mkdir(parents=True, exist_ok=True)
        save_path = path_prefix.joinpath(article["slug"] + ".html")
        writer(save_path, html)


def build_tags():
    tags_dict = parse_tag()
    for tag_name, articles in tags_dict.items():
        html = render_to_html("post/tag.html", articles=articles, tag_name=tag_name)
        path_prefix = conf.HTML_OUTPUT_PATH.joinpath("tag")
        path_prefix.mkdir(parents=True, exist_ok=True)
        save_path = path_prefix.joinpath(tag_name + ".html")
        writer(save_path, html)


def build_about():
    about_path = conf.CONTENT_PATH / "about.md"
    with open(about_path, "r", encoding="utf-8") as f:
        body = markdown.markdown(f.read(), extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
        ])
    html = render_to_html("about.html", body=body)
    save_path = conf.HTML_OUTPUT_PATH.joinpath("about.html")
    writer(save_path, html)


def build_links():
    html = render_to_html("links.html", links=conf.LINKS)
    save_path = conf.HTML_OUTPUT_PATH.joinpath("links.html")
    writer(save_path, html)


def build_sitemap():
    articles = parse_sitemap()
    html = render_to_html("sitemap.xml", articles=articles)
    save_path = conf.HTML_OUTPUT_PATH.joinpath("sitemap.xml")
    writer(save_path, html)


def build_static():
    static = conf.HTML_OUTPUT_PATH.joinpath("static")
    if static.exists():
        shutil.rmtree(static)
    shutil.copytree(conf.STATIC_FOLDER, static)


def build_all_tags():
    tags = parse_tag()
    tags = [{"name": name, "count": len(articles)} for name, articles in tags.items()]
    html = render_to_html("tags.html", tags=tags)
    save_path = conf.HTML_OUTPUT_PATH.joinpath("tags.html")
    writer(save_path, html)


def build_index():
    articles = parse_index()
    html = render_to_html("index.html", articles=articles)
    save_path = conf.HTML_OUTPUT_PATH.joinpath("index.html")
    writer(save_path, html)


def render_to_html(template, **kwargs):
    template = env.get_template(template)
    html = template.render(**conf.SITE_SETTINGS, **kwargs)
    return html


def writer(filepath, html):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
