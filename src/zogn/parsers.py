from xml.etree import ElementTree as etree

import yaml, re
import mistune
from bs4 import BeautifulSoup

from mistune import HTMLRenderer, escape_html, escape

from itertools import groupby
from operator import itemgetter

from markdown import Markdown
from markdown.inlinepatterns import LinkInlineProcessor, IMAGE_LINK_RE

from zogn.conf import (CONTENT_PATH, POST_PATH, POST_SOURCE_FOLDER_NAME, POST_HTML_FOLDER_NAME, SITE_SETTINGS,
                       POST_DATA, SLUG_TO_PATH)


class ImageInlineProcessor(LinkInlineProcessor):
    """ Return a img element from the given match. """

    def handleMatch(self, m, data):
        text, index, handled = self.getText(data, m.end(0))
        if not handled:
            return None, None, None

        src, title, index, handled = self.getLink(data, index)
        if not handled:
            return None, None, None

        # 让图片居中显示
        p = etree.Element("div")
        p.set("style", "text-align:center")
        el = etree.SubElement(p, "img")

        def sub_relative_identifier(a):
            start = 0
            end = 0
            pattern = re.compile("(\.\.)+?")
            for i in pattern.finditer(a):
                end = i.end()
            if start + end:
                return a[end:]
            return a

        src = sub_relative_identifier(src)
        el.set("src", src)
        if title is not None:
            el.set("title", title)

        el.set("data-src", src)
        return p, m.start(0), index


class MyMarkdown(Markdown):

    def build_parser(self):
        super().build_parser()
        self.inlinePatterns.register(ImageInlineProcessor(IMAGE_LINK_RE, self), 'image_link', 150)
        return self


class MyRenderer(HTMLRenderer):
    def paragraph(self, text):
        if "<br>" in text:
            return '<p>' + text + '</p><br>\n'
        return '<p>' + text + '</p>\n'


def content2markdown(content):
    # 使用正则表达式匹配四个连续的换行符，并在替换时将其中的三个替换为 \n<br>\n
    pattern = re.compile(r'(\n{4})')

    # 定义替换函数，使用捕获组中的内容进行替换
    def replace_newlines(match):
        return '\n<br>\n' + match.group(1)[:1]

    # 使用 re.sub() 函数进行替换，传入替换函数和输入字符串
    content = re.sub(pattern, replace_newlines, content)

    # md = MyMarkdown(extensions=[
    #     'markdown.extensions.extra',
    #     'markdown.extensions.codehilite',
    # ])
    # content = md.convert(content)

    #
    # # content = mistune.html(content)
    #
    # markdown = mistune.create_markdown(escape=False, hard_wrap=True)
    # use this renderer instance

    markdown = mistune.Markdown(renderer=MyRenderer(escape=False))
    content = markdown(content)
    return content


def parse_markdown(file):
    frontmatter, content = "", ""
    firstline = file.readline().strip()
    remained = file.read().strip()
    if firstline == "---":
        frontmatter, remained = remained.split("---", maxsplit=1)
        content = remained.strip()
    else:
        content = "\n\n".join([firstline, remained])
    metadata = yaml.load(frontmatter, Loader=yaml.FullLoader) or {}
    return metadata, content


def refactor_metadata_tags_and_category(metadata):
    # 计算文章的分类和标签链接
    category = metadata.pop("category")
    metadata["category"] = {"name": category, "url": f"/category/{category}"}
    tags = metadata.pop("tags")
    metadata["tags"] = [{"name": tag, "url": f"/tag/{tag}"} for tag in tags]

    metadata["tdk_category"] = category
    metadata["tdk_tags"] = tags
    return metadata


def load_all_articles():
    articles = []

    for p in POST_PATH.rglob("**/*.md"):
        with p.open("r", encoding="utf-8") as f:
            metadata, content = parse_markdown(f)
            if metadata["status"] == "draft":
                continue
            metadata["body"] = content2markdown(content)
            metadata["abstract"] = content2markdown(extract_abstract(content, 200))
            metadata["content"] = content
            # metadata["year"] = p.parts[-2]
            # metadata["url"] = f'/{POST_FOLDER_NAME}/{metadata["year"]}/{metadata["slug"]}.html'
            metadata["url"] = f'/{POST_HTML_FOLDER_NAME}/{metadata["slug"]}' if POST_HTML_FOLDER_NAME else f'/{metadata["slug"]}'
            metadata = refactor_metadata_tags_and_category(metadata)
            articles.append(metadata)

            SLUG_TO_PATH[f"{metadata['slug']}"] = p.as_posix()

    articles.sort(key=lambda x: x["date"], reverse=True)
    return articles


def extract_abstract(content, length):
    content = content.replace("#", "")
    if len(content.strip()) <= length:
        return content
    return content[:length] + "……"


def check_repeat_slug():
    TMP_SLUGS = {}
    for p in POST_PATH.rglob("**/*.md"):
        with p.open("r", encoding="utf-8") as f:
            metadata, content = parse_markdown(f)
            if metadata['slug'] in TMP_SLUGS:
                raise RuntimeError(f"存在重复的slug；{metadata['slug']}")

            TMP_SLUGS[f"{metadata['slug']}"] = p.as_posix()


def parse_index():
    return load_all_articles()


def parse_article(path):
    with open(path, "r", encoding="utf-8") as f:
        metadata, content = parse_markdown(f)
    metadata["body"] = content2markdown(content)
    metadata["content"] = content
    return refactor_metadata_tags_and_category(metadata)


def parse_sitemap():
    articles = load_all_articles()
    return articles


def parse_archive(articles):
    grouped_data = {}
    sorted_articles = sorted(articles, key=itemgetter('date'))
    for year, group in groupby(sorted_articles, key=lambda x: x['date'].year):
        grouped_data[year] = list(group)

    return grouped_data


def parse_category(articles):
    categories_dict = {}
    for article in articles:
        category_name = article["category"]["name"]
        categories_dict.setdefault(category_name, []).append(article)
    return categories_dict


def parse_tag(articles):
    tags_dict = {}
    for article in articles:
        tags = article["tags"]
        for tag in tags:
            tags_dict.setdefault(tag["name"], []).append(article)
    return tags_dict


def parse_about():
    about_path = CONTENT_PATH / "about.md"
    with open(about_path, "r", encoding="utf-8") as f:
        body = content2markdown(f.read())
    return body


def find_previous_and_next(current, articles):
    index = articles.index(current)

    # 获取上一个文件
    previous_article = articles[index - 1] if index > 0 else None

    # 获取下一个文件
    next_article = articles[index + 1] if index < len(articles) - 1 else None

    return previous_article, next_article


def load_all_data():
    articles = load_all_articles()

    for i, article in enumerate(articles):
        prev_article, next_article = find_previous_and_next(article, articles)
        if i == 0:
            article["next_article"] = {"slug": next_article["slug"], "title": next_article["title"]}
        elif i == len(articles) - 1:
            article["prev_article"] = {"slug": prev_article["slug"], "title": prev_article["title"]}
        else:
            article["prev_article"] = {"slug": prev_article["slug"], "title": prev_article["title"]}
            article["next_article"] = {"slug": next_article["slug"], "title": next_article["title"]}

    # 分类
    categories = parse_category(articles)
    categories_count = sorted([{"name": category, "count": len(_)} for category, _ in categories.items()],
                              key=lambda x: x["count"], reverse=True)

    # 标签
    tags = parse_tag(articles)
    tags_count = sorted([{"name": tag, "count": len(_)} for tag, _ in tags.items()],
                        key=lambda x: x["count"], reverse=True)

    # 归档
    archives = parse_archive(articles)
    archives_count = sorted([{"name": year, "count": len(_)} for year, _ in archives.items()],
                            key=lambda x: x["name"], reverse=True)

    result = {
        "articles": articles, "categories": categories, "tags": tags, "archives": archives,
        "total": {
            "category": categories_count, "tag": tags_count, "archive": archives_count
        },
    }

    POST_DATA.update(**result)
    return result
