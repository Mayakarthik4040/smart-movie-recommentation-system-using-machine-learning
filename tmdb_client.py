
import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()  # reads TMDB_API_TOKEN from a local .env file

TMDB_API_TOKEN = os.environ.get("TMDB_API_TOKEN", "")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w342"

HEADERS = {
    "Authorization": f"Bearer {TMDB_API_TOKEN}",
    "accept": "application/json",
}

_ARTICLE_SUFFIX = re.compile(r"^(.*),\s*(The|A|An)$")


def _reorder_title(title: str) -> str:
    
    m = _ARTICLE_SUFFIX.match(title.strip())
    if m:
        base, article = m.groups()
        return f"{article} {base}"
    return title


def fetch_movie_details(title: str, year: int | None = None):
    
    if not TMDB_API_TOKEN:
        return None

    query_title = _reorder_title(title)
    params = {"query": query_title}
    if year:
        params["year"] = year

    try:
        resp = requests.get(
            f"{TMDB_BASE_URL}/search/movie",
            headers=HEADERS,
            params=params,
            timeout=6,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])

        # If searching with year returns nothing, retry without it
        if not results and year:
            params.pop("year")
            resp = requests.get(
                f"{TMDB_BASE_URL}/search/movie",
                headers=HEADERS,
                params=params,
                timeout=6,
            )
            resp.raise_for_status()
            results = resp.json().get("results", [])

        if not results:
            return None

        movie = results[0]
        poster_path = movie.get("poster_path")
        return {
            "poster_url": f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else None,
            "overview": movie.get("overview", ""),
            "rating": movie.get("vote_average"),
            "tmdb_id": movie.get("id"),
        }
    except requests.RequestException:
        return None
