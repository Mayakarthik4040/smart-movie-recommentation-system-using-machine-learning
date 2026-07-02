"""
Content-Based Movie Recommendation Engine (MovieLens format)
---------------------------------------------------------------
Expects a CSV with columns: movieId, title, genres
  - title contains the release year in parentheses, e.g. "Toy Story (1995)"
  - genres are pipe-separated, e.g. "Adventure|Animation|Comedy"

Uses TF-IDF on genres (heavily weighted) + cleaned title words, then
Cosine Similarity to find the most similar movies to a given title.
"""

import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

YEAR_PATTERN = re.compile(r"\s*\((\d{4})\)\s*$")
ARTICLE_SUFFIX_PATTERN = re.compile(r"^(.*),\s*(The|A|An)$", re.IGNORECASE)


def extract_year(title: str):
    match = YEAR_PATTERN.search(title)
    return int(match.group(1)) if match else None


def clean_title(title: str) -> str:
    """Remove the year suffix, e.g. 'Toy Story (1995)' -> 'Toy Story'"""
    return YEAR_PATTERN.sub("", title).strip()


def display_title(title: str) -> str:
    """
    Reorder 'American President, The (1995)' -> 'The American President (1995)'
    for nicer display and better TMDB search matching.
    """
    year = extract_year(title)
    base = clean_title(title)
    match = ARTICLE_SUFFIX_PATTERN.match(base)
    if match:
        base = f"{match.group(2)} {match.group(1)}".strip()
    return f"{base} ({year})" if year else base


class MovieRecommender:
    def __init__(self, csv_path: str = "movies.csv"):
        self.df = pd.read_csv(csv_path)
        self._prepare_data()

    def _prepare_data(self):
        self.df["genres"] = self.df["genres"].fillna("(no genres listed)")

        self.df["year"] = self.df["title"].apply(extract_year)
        self.df["clean_title"] = self.df["title"].apply(clean_title)
        self.df["display_title"] = self.df["title"].apply(display_title)

        # Genre list as space-separated tokens (pipe -> space), heavily
        # weighted since genres are the strongest signal in this dataset.
        genre_tokens = self.df["genres"].str.replace("|", " ", regex=False)

        # Title words add a light secondary signal (helps franchises like
        # "Toy Story" / "Toy Story 2" cluster together).
        self.df["tags"] = (
            (genre_tokens + " ") * 4 + self.df["clean_title"]
        ).str.lower()

        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.tfidf_matrix = self.vectorizer.fit_transform(self.df["tags"])
        # Removed precomputing full similarity matrix to save memory; will compute on demand.

        # Lookup by the ORIGINAL title (as stored in the CSV) since that's
        # what dropdowns/search will select against.
        self.title_to_index = pd.Series(
            self.df.index, index=self.df["title"].str.lower()
        )

    def all_titles(self):
        """Return original titles, sorted by their nicer display form."""
        return self.df.sort_values("display_title")["title"].tolist()

    def search_titles(self, query: str, limit: int = 25):
        """Case-insensitive substring search over titles (handles 'The X' too)."""
        q = query.strip().lower()
        if not q:
            return self.all_titles()[:limit]
        mask = (
            self.df["title"].str.lower().str.contains(q, regex=False)
            | self.df["display_title"].str.lower().str.contains(q, regex=False)
        )
        matches = self.df[mask].sort_values("display_title")
        return matches["title"].tolist()[:limit]

    def get_movie(self, title: str):
        key = title.strip().lower()
        if key not in self.title_to_index:
            return None
        return self.df.iloc[self.title_to_index[key]]

    def recommend(self, title: str, top_n: int = 5):
        """
        Return the top_n most similar movies to `title`.
        Returns a DataFrame with title, clean_title, display_title, genres,
        year, similarity_score — or None if the title isn't found.
        """
        key = title.strip().lower()
        if key not in self.title_to_index:
            return None

        idx = self.title_to_index[key]
        # Compute cosine similarity of the target movie with all others on the fly to avoid huge memory usage.
        # Using sparse matrix operations; result is a 1D array.
        similarities = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix[idx])
        # Flatten and enumerate
        sim_scores = list(enumerate(similarities.ravel()))
        # Exclude the movie itself and sort
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = [s for s in sim_scores if s[0] != idx][:top_n]

        movie_indices = [i for i, _ in sim_scores]
        results = self.df.iloc[movie_indices][
            ["title", "clean_title", "display_title", "genres", "year"]
        ].copy()
        results["similarity_score"] = [round(score, 3) for _, score in sim_scores]
        return results.reset_index(drop=True)


if __name__ == "__main__":
    rec = MovieRecommender("movies.csv")
    print("Sample titles:", rec.all_titles()[:5])
    print()
    test_title = "Toy Story (1995)"
    print(f"Recommendations for '{test_title}':")
    print(rec.recommend(test_title, top_n=5)[["display_title", "genres", "similarity_score"]])
    print()
    print("Search 'ace':", rec.search_titles("ace"))
