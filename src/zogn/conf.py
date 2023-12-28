from pathlib import Path
import toml
from datetime import date

BASE_DIR = Path.cwd()

CONTENT_FOLDER_NAME = "content"
POST_SOURCE_FOLDER_NAME = "post"
HTML_FOLDER_NAME = "docs"
THEME_FOLDER_NAME = "themes"
IMAGE_FOLDER_NAME = "img"

POST_HTML_FOLDER_NAME = ""


CONTENT_PATH = BASE_DIR / CONTENT_FOLDER_NAME
POST_PATH = CONTENT_PATH / POST_SOURCE_FOLDER_NAME
HTML_OUTPUT_PATH = BASE_DIR / HTML_FOLDER_NAME
THEME_PATH = BASE_DIR / THEME_FOLDER_NAME
IMAGE_PATH = BASE_DIR / IMAGE_FOLDER_NAME

DEFAULT_POST_TEMPLATE = """\n
---
{}
---
"""

TOML_TEMPLATE = '''\n
SITE_NAME = "ZOROZ.ME"
SITE_LOGO_NAME = "ZOROZ.ME"
SITE_COPYRIGHT_NAME = "ZOROZ"
SITE_KEYWORDS = "zo9n,node,vue,Python,Django,backend,blog,web,random thoughts,coding"
SITE_DESCRIPTION = "This is a salted fish coder developed website which mainly records and shares coding notes, random thoughts."
SITE_URL = "https://zo9n.com"

STATIC_FOLDER = "default/static"
TEMPLATES_FOLDER = "default/templates"

LINKS = [
]

ANALYTICS_CODE = ""
'''

# 加载外部环境变量
CONF_PATH = BASE_DIR.joinpath("settings.toml")
try:
    settings = toml.load(CONF_PATH)
except:
    settings = {}

STATIC_FOLDER = THEME_PATH.joinpath(settings.get("STATIC_FOLDER", ""))
TEMPLATES_FOLDER = THEME_PATH.joinpath(settings.get("TEMPLATES_FOLDER", ""))
PAGINATION_NUM = settings.get("PAGINATION_NUM")
SITE_SETTINGS = {
    "SITE_NAME": settings.get("SITE_NAME"),
    "SITE_LOGO_NAME": settings.get("SITE_LOGO_NAME"),
    "SITE_COPYRIGHT_NAME": settings.get("SITE_COPYRIGHT_NAME"),
    "SITE_KEYWORDS": settings.get("SITE_KEYWORDS"),
    "SITE_DESCRIPTION": settings.get("SITE_DESCRIPTION"),
    "SITE_URL": settings.get("SITE_URL"),
    "CURRENT_YEAR": date.today().year,
    "ANALYTICS_CODE": settings.get("ANALYTICS_CODE"),
    "LINKS": settings.get("LINKS"),
    "STATIC_FOLDER": STATIC_FOLDER,
    "TEMPLATES_FOLDER": TEMPLATES_FOLDER,

}
