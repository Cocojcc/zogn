from xml.etree import ElementTree as etree

import yaml
from markdown import Markdown
from markdown.inlinepatterns import LinkInlineProcessor, IMAGE_LINK_RE

from zogn.conf import CONTENT_PATH, POST_PATH, POST_FOLDER_NAME

SLUG_TO_PATH = {}


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


def content2markdown(content):
    md = MyMarkdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
    ])
    content = md.convert(content)
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
    metadata["category"] = {"name": category, "url": f"/category/{category}.html"}
    tags = metadata.pop("tags")
    metadata["tags"] = [{"name": tag, "url": f"/tag/{tag}.html"} for tag in tags]

    metadata["tdk_category"] = category
    metadata["tdk_tags"] = category
    return metadata


def load_all_articles():
    articles = []
    for p in POST_PATH.rglob("**/*.md"):
        with p.open("r", encoding="utf-8") as f:
            metadata, content = parse_markdown(f)
            if metadata["status"] == "draft":
                continue
            metadata["body"] = content2markdown(content)
            metadata["year"] = p.parts[-2]
            metadata["url"] = f'/{POST_FOLDER_NAME}/{metadata["year"]}/{metadata["slug"]}.html'
            metadata = refactor_metadata_tags_and_category(metadata)

            articles.append(metadata)
            SLUG_TO_PATH[f"{metadata['year']}/{metadata['slug']}"] = p.as_posix()

    articles.sort(key=lambda x: x["date"], reverse=True)
    return articles


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
