from flask import Flask, Response
from zogn.parsers import parse_article, parse_sitemap, parse_category, parse_about, parse_index, SLUG_TO_PATH, parse_tag, load_all_articles
from zogn.builders import render_to_html, build_rss
from zogn import conf

app = Flask(__name__,
            template_folder=conf.TEMPLATES_FOLDER,
            static_folder=conf.STATIC_FOLDER
            )


@app.route("/")
def index():
    articles = parse_index()
    return render_to_html("index.html", articles=articles)


@app.route("/post/<slug>.html")
def detail(slug):
    article_path = SLUG_TO_PATH[slug]
    metadata = parse_article(article_path)
    return render_to_html("post/detail.html", article=metadata)


@app.route("/category/<name>.html")
def category(name):
    categories = parse_category(load_all_articles())
    articles = categories.get(name) or []
    return render_to_html("post/category.html", articles=articles, category_name=name)


@app.route("/tag/<name>.html")
def tag(name):
    tags = parse_tag(load_all_articles())
    articles = tags.get(name) or []
    return render_to_html("post/tag.html", articles=articles, tag_name=name)


@app.route("/about.html")
def about():
    body = parse_about()
    return render_to_html("about.html", body=body)


@app.route("/links.html")
def links():
    return render_to_html("links.html", links=conf.LINKS)


@app.route("/tags.html")
def tags():
    tags = parse_tag(load_all_articles())
    tags = [{"name": name, "count": len(articles)} for name, articles in tags.items()]
    return render_to_html("tags.html", tags=tags)


@app.route("/sitemap.xml")
def sitemap():
    articles = parse_sitemap()
    xml = render_to_html("sitemap.xml", articles=articles)
    return Response(xml, mimetype="application/xml")


@app.route("/feed.xml")
def rss():
    articles = parse_sitemap()
    fg = build_rss(articles)
    xml = fg.rss_str()
    return Response(xml, mimetype="application/xml")


if __name__ == '__main__':
    app.run(port=9999, debug=True, host="0.0.0.0")
