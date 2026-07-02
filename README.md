# 🎬 Smart Movie Recommendation System (MovieLens + TMDB)

## Overview
A **content‑based movie recommender** built on the MovieLens dataset. It uses **TF‑IDF** on genre tags and cleaned title words, then computes **cosine similarity** to find movies similar to a chosen title. The web interface is built with **Streamlit**, and movie posters/details are fetched live from **TMDB**.

## Repository Structure
| File | Purpose |
|---|---|
| `movies.csv` | MovieLens‑style dataset (`movieId,title,genres`). |
| `recommender.py` | Core recommendation logic – TF‑IDF vectorisation and similarity computation. |
| `tmdb_client.py` | Wrapper around TMDB API to retrieve poster, overview and rating. |
| `app.py` | Streamlit front‑end – search box, results grid, and TMDB display. |
| `requirements.txt` | Python dependencies. |
| `.env` | Stores your TMDB API token as `TMDB_API_TOKEN` (keep secret!). |
| `.gitignore` | Excludes `.env` and other artefacts. |

## ⚠️ TMDB API Token
Your TMDB token should be stored in a file named `.env`:
```
TMDB_API_TOKEN=your_token_here
```
Do **not** commit `.env` to a public repository. The `.gitignore` already excludes it.

## Setup & Run
```bash
# (optional) create a virtual environment
python -m venv venv
# Windows activation
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py
```
The app will be available at `http://localhost:8501`.

## Using a Full MovieLens Dataset
Replace the provided `movies.csv` with the full dataset (e.g., `ml-latest-small` with ~9k movies or `ml-25m` with ~62k movies). Ensure the CSV retains the three columns `movieId,title,genres`. No code changes are required.

## How It Works
1. **Genres** (`Adventure|Animation|Comedy`) are turned into space‑separated tokens and heavily weighted.
2. **Title words** are cleaned and added as a lighter signal.
3. `TfidfVectorizer` creates a vector for each movie.
4. `cosine_similarity` scores similarity between movies.
5. For the selected movie, the top‑N similar movies are returned.
6. `tmdb_client.py` looks up each recommended movie’s poster, overview and rating from TMDB **for display only**.

## Extending the Project
- **Hybrid Recommendation**: Combine this content‑based model with collaborative filtering using MovieLens `ratings.csv`.
- **Direct TMDB Mapping**: Use `links.csv` (MovieLens) to map `movieId` → `tmdbId` for precise TMDB look‑ups.
- **Alternative Front‑ends**: Import `MovieRecommender` into a Flask or FastAPI backend and serve results via REST.
- **Deployment**: Deploy to Streamlit Community Cloud – add your TMDB token as a secret in the cloud dashboard.

## License
This project is provided for educational purposes. Feel free to adapt and extend it.
