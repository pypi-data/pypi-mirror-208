from typing import Any
from zoneinfo import ZoneInfo

from dateutil import parser
from dotenv import find_dotenv, load_dotenv
from start_github import Github

load_dotenv(find_dotenv())

CORPUS_URL = "https://api.github.com/repos/justmars/corpus-entities"
ARTICLES_URL = "https://api.github.com/repos/justmars/lawsql-articles"
gh = Github()  # type: ignore


def fetch_entities(path: str) -> list[dict[str, Any]]:
    if path not in ("members", "orgs"):
        raise Exception(f"Improper {path=}")
    url = f"{CORPUS_URL}/contents/{path}"
    if resp := gh.get(url):
        return resp.json()
    raise Exception(f"Could not fetch corpus entity: {url}")


def fetch_articles() -> list[dict[str, Any]]:
    """Get the github repository `/articles` files metadata. Each item
    in the response will look likeso:
    """
    url = f"{ARTICLES_URL}/contents/content"
    if resp := gh.get(url):
        return resp.json()
    raise Exception(f"Could not fetch articles content: {url}")


def fetch_article_date_modified(path: str) -> float:
    """Get the latest commit date of an article
    `path` to get its date last modified."""
    url = f"{ARTICLES_URL}/commits"
    params = {"path": path, "page": 1, "per_page": 1}
    if resp := gh.get(url=url, media_type="+json", params=params):
        return (
            parser.parse(resp.headers["date"])
            .astimezone(ZoneInfo("Asia/Manila"))
            .timestamp()
        )
    raise Exception(f"Could not fetch articles content: {url}")
