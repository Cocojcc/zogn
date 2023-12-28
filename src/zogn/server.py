from flask import Flask, Response, send_from_directory
from zogn.parsers import parse_article, parse_sitemap, parse_category, parse_about, parse_index, SLUG_TO_PATH, \
    parse_tag, load_all_articles
from zogn.builders import render_to_html, build_rss, Pagination
from zogn import conf

import datetime

app = Flask(__name__,
            template_folder=conf.TEMPLATES_FOLDER,
            static_folder=conf.STATIC_FOLDER,
            )

app.config["img_folder_path"] = conf.IMAGE_PATH


@app.route("/")
def index():
    articles = parse_index()
    paginator = Pagination(articles, 10, page_tag="index")
    return render_to_html("index.html", articles=paginator.paginate(1), page=paginator)
    # return render_to_html("index.html", articles=articles)


@app.route("/<slug>")
def detail(slug):
    if slug == "favicon.ico":
        return "", 404
    article_path = SLUG_TO_PATH[f'{slug}']
    metadata = parse_article(article_path)
    return render_to_html("post/detail.html", article=metadata)


@app.route("/img/<path:path>")
def img(path):
    return send_from_directory(conf.IMAGE_PATH, path)


@app.route("/index-page-<int:page>")
def page(page):
    articles = parse_index()
    paginator = Pagination(articles, 10, page_tag="index")
    return render_to_html("index.html", articles=paginator.paginate(page), page=paginator)


@app.route("/category/<name>")
def category(name):
    categories = parse_category(load_all_articles())
    articles = categories.get(name) or []
    return render_to_html("post/category.html", articles=articles, category_name=name)


@app.route("/tag/<name>")
def tag(name):
    tags = parse_tag(load_all_articles())
    articles = tags.get(name) or []
    return render_to_html("post/tag.html", articles=articles, tag_name=name)


@app.route("/about")
def about():
    body = parse_about()
    return render_to_html("about.html", body=body)


@app.route("/archives")
def archives():
    articles = parse_index()
    return render_to_html("archives.html", articles=articles)


@app.route("/links")
def links():
    return render_to_html("links.html")


@app.route("/tags")
def tags():
    tags = parse_tag(load_all_articles())
    tags = [{"name": name, "count": len(articles)} for name, articles in tags.items()]
    return render_to_html("tags.html", tags=tags)


@app.route("/sitemap.xml")
def sitemap():
    articles = parse_sitemap()
    article_tags = []
    [article_tags.append(tag) for article in articles for tag in article["tags"] if tag not in article_tags]

    categories = []
    [categories.append(article["category"]) for article in articles if article["category"] not in categories]
    today = datetime.date.today()
    xml = render_to_html("sitemap.xml", articles=articles, tags=article_tags, categories=categories,
                         today=today)
    return Response(xml, mimetype="application/xml")


@app.route("/feed.xml")
def rss():
    articles = parse_sitemap()
    fg = build_rss(articles)
    xml = fg.rss_str()
    return Response(xml, mimetype="application/xml")


if __name__ == '__main__':
    app.run(port=9999, debug=True, host="0.0.0.0")
