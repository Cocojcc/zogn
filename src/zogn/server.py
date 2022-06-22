from flask import Flask
from zogn.parsers import parse_article, parse_sitemap, parse_category, parse_about, parse_index, SLUG_TO_PATH
from zogn.builders import render_to_html
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
    categories = parse_category()
    articles = categories.get(name) or []
    return render_to_html("post/category.html", articles=articles)


@app.route("/about.html")
def about():
    body = parse_about()
    return render_to_html("about.html", body=body)


@app.route("/links.html")
def links():
    return render_to_html("links.html", links=conf.LINKS)


@app.route("/sitemap.xml")
def sitemap():
    articles = parse_sitemap()
    return render_to_html("sitemap.xml", articles=articles)


if __name__ == '__main__':
    app.run(port=9999, debug=True)
