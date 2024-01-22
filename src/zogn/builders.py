import datetime
import shutil
import os
from csscompressor import compress
from copy import deepcopy
from pathlib import Path

import dateutil.tz
from feedgen.feed import FeedGenerator
from jinja2 import Environment, FileSystemLoader

from zogn import conf

from zogn.parsers import parse_category, parse_tag, MyMarkdown, content2markdown, POST_DATA

env = Environment(loader=FileSystemLoader(conf.THEME_PATH / conf.TEMPLATES_FOLDER))


def copy_img_files(source_folder, destination_folder):
    # 确保目标文件夹存在
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # 遍历源文件夹中的文件
    for file in source_folder.glob("**/*.webp"):
        print(file.as_posix())

    # for filename in os.listdir(source_folder):
    #     print(filename)
    #     source_path = os.path.join(source_folder, filename)
    #
    #     # 检查文件是否是.webp文件
    #     if filename.lower().endswith('.webp') and os.path.isfile(source_path):
    #         destination_path = os.path.join(destination_folder, filename)
    #         shutil.copy2(source_path, destination_path)


def build_article(articles):
    for article in articles:
        html = render_to_html("post/detail.html", article=article)
        path_prefix = conf.HTML_OUTPUT_PATH.joinpath(conf.POST_HTML_FOLDER_NAME)
        path_prefix.mkdir(parents=True, exist_ok=True)
        save_path = path_prefix.joinpath(article["slug"] + ".html")
        writer(save_path, html)


def build_category(articles):
    category_dict = parse_category(articles)
    for category_name, articles in category_dict.items():
        html = render_to_html("post/category.html", articles=articles, category_name=category_name)
        path_prefix = conf.HTML_OUTPUT_PATH.joinpath("category")
        path_prefix.mkdir(parents=True, exist_ok=True)
        save_path = path_prefix.joinpath(category_name + ".html")
        writer(save_path, html)


def build_tags(articles):
    tags_dict = parse_tag(articles)
    for tag_name, articles in tags_dict.items():
        html = render_to_html("post/tag.html", articles=articles, tag_name=tag_name)
        path_prefix = conf.HTML_OUTPUT_PATH.joinpath("tag")
        path_prefix.mkdir(parents=True, exist_ok=True)
        save_path = path_prefix.joinpath(tag_name + ".html")
        writer(save_path, html)


def build_all_tags(articles):
    tags = parse_tag(articles)
    tags = [{"name": name, "count": len(articles)} for name, articles in tags.items()]
    html = render_to_html("tags.html", tags=tags)
    save_path = conf.HTML_OUTPUT_PATH.joinpath("tags.html")
    writer(save_path, html)


def build_about():
    about_path = conf.CONTENT_PATH / "about.md"
    with open(about_path, "r", encoding="utf-8") as f:
        body = content2markdown(f.read())
    html = render_to_html("about.html", body=body)
    save_path = conf.HTML_OUTPUT_PATH.joinpath("about.html")
    writer(save_path, html)


def build_links():
    html = render_to_html("links.html")
    save_path = conf.HTML_OUTPUT_PATH.joinpath("links.html")
    writer(save_path, html)


def build_sitemap(articles):
    article_tags = []
    [article_tags.append(tag) for article in articles for tag in article["tags"] if tag not in article_tags]
    categories = []
    [categories.append(article["category"]) for article in articles if article["category"] not in categories]
    today = datetime.date.today()

    html = render_to_html("sitemap.xml", articles=articles, tags=article_tags, categories=categories,
                          today=today)
    save_path = conf.HTML_OUTPUT_PATH.joinpath("sitemap.xml")
    writer(save_path, html)


def build_static():
    # static = conf.HTML_OUTPUT_PATH.joinpath("static")
    # if static.exists():
    #     shutil.rmtree(static)
    # shutil.copytree(conf.STATIC_FOLDER, static)

    # CSS file
    output_static = conf.HTML_OUTPUT_PATH.joinpath("static", "css")
    origin_static = conf.STATIC_FOLDER.joinpath("css")

    # 遍历源文件夹中的所有文件和子文件夹
    for root, dirs, files in os.walk(origin_static):
        # 构建目标文件夹中的相对路径
        destination_path = os.path.join(output_static, os.path.relpath(root, origin_static))

        # 确保目标文件夹中的子文件夹存在，如果不存在则创建
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)

        # 复制文件到目标文件夹
        for file in files:
            source_file_path = os.path.join(root, file)
            destination_file_path = os.path.join(destination_path, file)
            css = compress(open(source_file_path, "r", encoding="utf8").read())
            writer(destination_file_path, css)

    # JS file
    js_static = conf.HTML_OUTPUT_PATH.joinpath("static", "js")
    if js_static.exists():
        shutil.rmtree(js_static)
    shutil.copytree(conf.STATIC_FOLDER.joinpath("js"), js_static)

    # image file
    img = conf.HTML_OUTPUT_PATH.joinpath("img")
    if img.exists():
        shutil.rmtree(img)

    for file in conf.IMAGE_PATH.glob("**/*.webp"):
        output_index = file.parts.index("img")
        relative_path = Path(*file.parts[output_index:])
        target_path = conf.HTML_OUTPUT_PATH.joinpath(relative_path)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        shutil.copy2(file, target_path)

    # shutil.copytree(conf.IMAGE_PATH, img)
    # copy_img_files(conf.IMAGE_PATH, img)

    # ico file
    ico_file = conf.STATIC_FOLDER.joinpath("favicon.ico")
    if ico_file.exists():
        shutil.copy2(ico_file, conf.HTML_OUTPUT_PATH)


def build_index(articles):
    # html = render_to_html("index.html", articles=articles)
    # save_path = conf.HTML_OUTPUT_PATH.joinpath("index.html")
    # writer(save_path, html)

    pagination_num = conf.PAGINATION_NUM

    paginator = Pagination(articles, pagination_num, page_tag="index")
    page_count = paginator.page_count

    for i in range(1, page_count + 1):
        html = render_to_html("index.html", articles=paginator.paginate(i), page=paginator)
        if i == 1:
            save_path = conf.HTML_OUTPUT_PATH.joinpath("index.html")
        else:
            save_path = conf.HTML_OUTPUT_PATH.joinpath(f"index-page-{i}.html")
        writer(save_path, html)


def build_archives(articles):
    html = render_to_html("archives.html", articles=articles)
    save_path = conf.HTML_OUTPUT_PATH.joinpath("archives.html")
    writer(save_path, html)


class Pagination:

    def __init__(self, articles: list, limit: int, current_page=1, page_tag=None):
        self.articles = articles
        self.limit = limit

        page_count, tmp = divmod(len(articles), limit)
        if tmp: page_count += 1

        self.page_count = page_count
        self.current_page = current_page
        self.page_tag = page_tag

    @property
    def start(self):
        return (self.current_page - 1) * self.limit

    @property
    def end(self):
        return self.current_page * self.limit

    def paginate(self, page):
        self.current_page = page
        return self.articles[self.start:self.end]

    @property
    def has_prev(self):
        return self.current_page > 1

    @property
    def has_next(self):
        return self.current_page < self.page_count

    @property
    def prev_page_path(self):
        if self.current_page == 2:
            return "/"
        elif self.current_page == 1:
            return None
        else:
            return f"/{self.page_tag}-page-{self.current_page - 1}"

    @property
    def next_page_path(self):
        return f"/{self.page_tag}-page-{self.current_page + 1}" if self.has_next else None


def build_rss(articles):
    """
    生成 RSS Feed
    """
    articles = deepcopy(articles)

    fg = FeedGenerator()
    fg.id(conf.SITE_SETTINGS.get("SITE_URL"))
    fg.title(conf.SITE_SETTINGS.get("SITE_NAME"))
    fg.link(href=conf.SITE_SETTINGS.get("SITE_URL"), rel='alternate')
    fg.description(conf.SITE_SETTINGS.get('SITE_DESCRIPTION'))
    articles.sort(key=lambda x: x["date"], reverse=False)
    for index, item in enumerate(articles):
        fe = fg.add_entry()
        fe.id(str(item['slug']))
        fe.title(item['title'])
        fe.pubDate(datetime.datetime.combine(item['date'], datetime.datetime.min.time(), tzinfo=dateutil.tz.tzutc()))
        fe.content(item['body'])
        fe.link(href=f"{conf.SITE_SETTINGS.get('SITE_URL')}{item['url']}")
    fg.rss_file(conf.HTML_OUTPUT_PATH.joinpath('feed.xml').as_posix())
    return fg


def render_to_html(template, **kwargs):
    template = env.get_template(template)

    post_data = deepcopy(POST_DATA)
    post_data.update(**kwargs)

    html = template.render(**conf.SITE_SETTINGS, **post_data)
    return html


def writer(filepath, html):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)


def read_md(path):
    with open(path, "r") as f:
        md = MyMarkdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
        ])
        da = md.convert(f.read())
    return da
