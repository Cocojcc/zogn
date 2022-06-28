import markdown
import yaml

from zogn.conf import CONTENT_PATH, POST_PATH

SLUG_TO_PATH = {}


def content2markdown(content):
    content = markdown.markdown(content, extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
    ])
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


def load_all_articles():
    articles = []
    for p in POST_PATH.rglob("*.md"):
        with p.open("r", encoding="utf-8") as f:
            metadata, content = parse_markdown(f)
            if metadata["status"] == "draft":
                continue
            metadata["body"] = content2markdown(content)
            articles.append(metadata)
            SLUG_TO_PATH[metadata["slug"]] = p.as_posix()
    articles.sort(key=lambda x: x["date"], reverse=True)
    return articles


def parse_index():
    return load_all_articles()


def parse_article(path):
    with open(path, "r", encoding="utf-8") as f:
        metadata, content = parse_markdown(f)
    content = markdown.markdown(content, extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
    ])
    metadata["body"] = content2markdown(content)
    return metadata


def parse_sitemap():
    articles = load_all_articles()
    return articles


def parse_category():
    categories_dict = {}
    articles = load_all_articles()
    for article in articles:
        category_name = article["category"]
        categories_dict.setdefault(category_name, []).append(article)
    return categories_dict


def parse_tag():
    tags_dict = {}
    articles = load_all_articles()
    for article in articles:
        tags = article["tags"]
        for tag_name in tags:
            tags_dict.setdefault(tag_name, []).append(article)
    return tags_dict


def parse_about():
    about_path = CONTENT_PATH / "about.md"
    with open(about_path, "r", encoding="utf-8") as f:
        body = content2markdown(f.read())
    return body
