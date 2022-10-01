import datetime
import shutil

import dateutil.tz
from feedgen.feed import FeedGenerator
from jinja2 import Environment, FileSystemLoader

from zogn import conf

from zogn.parsers import parse_category, parse_sitemap, load_all_articles, parse_index, parse_tag, MyMarkdown, \
    content2markdown

env = Environment(loader=FileSystemLoader(conf.THEME_PATH / conf.TEMPLATES_FOLDER))

SLUG_TO_PATH = {}


def build_article(articles):
    for article in articles:
        html = render_to_html("post/detail.html", article=article)
        path_prefix = conf.HTML_OUTPUT_PATH.joinpath(conf.POST_FOLDER_NAME, article["year"])
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


# def build_links():
#     html = render_to_html("links.html", links=conf.LINKS)
#     save_path = conf.HTML_OUTPUT_PATH.joinpath("links.html")
#     writer(save_path, html)


def build_sitemap(articles):
    html = render_to_html("sitemap.xml", articles=articles)
    save_path = conf.HTML_OUTPUT_PATH.joinpath("sitemap.xml")
    writer(save_path, html)


def build_static():
    static = conf.HTML_OUTPUT_PATH.joinpath("static")
    if static.exists():
        shutil.rmtree(static)
    shutil.copytree(conf.STATIC_FOLDER, static)


def build_index(articles):
    html = render_to_html("index.html", articles=articles)
    save_path = conf.HTML_OUTPUT_PATH.joinpath("index.html")
    writer(save_path, html)

    # pagination_num = 10
    #
    # paginator = Pagination(articles, pagination_num)
    # page_count = paginator.page_count
    #
    # for i in range(1, page_count + 1):
    #     html = render_to_html("index.html", articles=paginator.paginate(i), page=paginator)
    #     if i == 1:
    #         save_path = conf.HTML_OUTPUT_PATH.joinpath("index.html")
    #     else:
    #         save_path = conf.HTML_OUTPUT_PATH.joinpath(f"index-{i}.html")
    #     writer(save_path, html)


class Pagination:

    def __init__(self, articles: list, limit: int, current_page=1):
        self.articles = articles
        self.limit = limit

        page_count, tmp = divmod(len(articles), limit)
        if tmp: page_count += 1

        self.page_count = page_count
        self.current_page = current_page

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
        else:
            return f"/page-{self.current_page - 1}.html"

    @property
    def next_page_path(self):
        return f"/page-{self.current_page + 1}.html" if self.has_next else None


def build_rss(articles):
    """
    生成 RSS Feed
    """
    fg = FeedGenerator()
    fg.id('https://2dosth.com')
    fg.title('2dosth')
    fg.author({'name': 'JChen', 'email': 'intbleem@gmail.com'})
    fg.link(href='https://2dosth.com', rel='alternate')
    fg.description(conf.SITE_SETTINGS.get('SITE_DESCRIPTION'))
    articles.sort(key=lambda x: x["date"], reverse=False)
    for index, item in enumerate(articles):
        fe = fg.add_entry()
        fe.id(item['slug'])
        fe.title(item['title'])
        fe.pubDate(datetime.datetime.combine(item['date'], datetime.datetime.min.time(), tzinfo=dateutil.tz.tzutc()))
        fe.content(item['body'])
        fe.link(href=f"{conf.SITE_SETTINGS.get('SITE_URL')}{item['url']}")
    fg.rss_file(conf.HTML_OUTPUT_PATH.joinpath('feed.xml').as_posix())
    return fg


def render_to_html(template, **kwargs):
    template = env.get_template(template)
    html = template.render(**conf.SITE_SETTINGS, **kwargs)
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
