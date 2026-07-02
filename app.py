


import streamlit as st
from recommender import MovieRecommender
from tmdb_client import fetch_movie_details

st.set_page_config(page_title="Smart Movie Recommender", page_icon="🎬", layout="wide")


@st.cache_resource
def load_recommender():
    return MovieRecommender("movies.csv")


@st.cache_data(show_spinner=False, ttl=60 * 60)
def get_movie_details(clean_title: str, year):
    return fetch_movie_details(clean_title, year)


rec = load_recommender()

st.title("🎬 Smart Movie Recommendation System")
st.caption("Content-based filtering on genres (TF-IDF + Cosine Similarity) · Posters via TMDB")

st.markdown("---")

search = st.text_input("🔎 Search for a movie by name", "")
if search:
    options = rec.search_titles(search, limit=25)
else:
    options = rec.all_titles()[:300]  # cap the dropdown for very large datasets

if not options:
    st.warning("No movies matched your search. Try a different title.")
else:
    col1, col2 = st.columns([3, 1])
    with col1:
        movie = st.selectbox("Pick a movie:", options)
    with col2:
        top_n = st.number_input("How many?", min_value=3, max_value=15, value=5, step=1)

    if st.button("🔍 Recommend Similar Movies", type="primary"):
        results = rec.recommend(movie, top_n=top_n)

        if results is None:
            st.error("Sorry, that movie isn't in the database.")
        else:
            st.markdown(f"### Because you liked **{movie}**, you might enjoy:")

            cols = st.columns(min(len(results), 5))
            for i, row in results.iterrows():
                details = get_movie_details(row["clean_title"], row["year"])
                col = cols[i % len(cols)]
                with col:
                    if details and details.get("poster_url"):
                        st.image(details["poster_url"], use_container_width=True)
                    else:
                        st.markdown(
                            "<div style='height:220px;display:flex;align-items:center;"
                            "justify-content:center;background:#eee;border-radius:8px;'>"
                            "🎞️ No poster</div>",
                            unsafe_allow_html=True,
                        )
                    st.markdown(f"**{row['title']}**")
                    st.caption(row["genres"].replace("|", " · "))
                    st.caption(f"Match: {row['similarity_score']*100:.0f}%")
                    if details and details.get("rating"):
                        st.caption(f"⭐ {details['rating']:.1f}/10 on TMDB")
                    if details and details.get("overview"):
                        with st.expander("Overview"):
                            st.write(details["overview"])

st.markdown("---")
with st.expander("ℹ️ How this works"):
    st.write(
       
    )

st.caption("Swap `movies.csv` for your full MovieLens file — same columns (movieId, title, genres), no code changes needed.")
