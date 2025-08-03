import streamlit as st
import pickle
import pandas as pd
import requests

# 🔍 Fetch poster, rating, and trailer
def fetch_movie_details(movie_id):
    try:
        url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=c5bc106f802c0f36cbd2c908033891e9&language=en-US&append_to_response=videos'
        response = requests.get(url, timeout=5)
        data = response.json()
        poster_path = data.get('poster_path')
        rating = data.get('vote_average', 'N/A')
        overview = data.get('overview', '')
        homepage = f"https://www.themoviedb.org/movie/{movie_id}"

        # Trailer fetch
        trailer_url = ""
        for video in data.get("videos", {}).get("results", []):
            if video["type"] == "Trailer" and video["site"] == "YouTube":
                trailer_url = f"https://www.youtube.com/watch?v={video['key']}"
                break

        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w200{poster_path}"
            return poster_url, rating, trailer_url, overview[:150] + "...", homepage
        else:
            return None, None, None, None, None

    except Exception as e:
        return None, None, None, None, None

# 🔁 Recommend movies
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]
    sorted_movies = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:]

    results = []
    for i in sorted_movies:
        movie_id = movies.iloc[i[0]].movie_id
        title = movies.iloc[i[0]].title
        poster, rating, trailer, overview, link = fetch_movie_details(movie_id)

        if poster:
            results.append({
                "title": title,
                "poster": poster,
                "rating": rating,
                "trailer": trailer,
                "overview": overview,
                "link": link
            })

        if len(results) == 10:
            break
    return results

movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align:center;'>🎬Movie Recommendation System</h1>", unsafe_allow_html=True)

selected_movie = st.selectbox("Choose a movie you like:", movies['title'].values)

if st.button("Recommend"):
    results = recommend(selected_movie)

    if not results:
        st.warning("No recommendations with posters found.")
    else:
        for row in range(0, len(results), 5):
            cols = st.columns(5)
            for i, col in enumerate(cols):
                if row + i < len(results):
                    movie = results[row + i]
                    with col:
                        st.image(movie['poster'], use_container_width=True)
                        st.markdown(f"<h5 style='text-align:center'>{movie['title']}</h5>", unsafe_allow_html=True)
                        st.markdown(f"<p style='text-align:center'>⭐ {movie['rating']}/10</p>", unsafe_allow_html=True)
                        if movie["trailer"]:
                            st.markdown(f"<p style='text-align:center'><a href='{movie['trailer']}' target='_blank'>▶️ Trailer</a></p>", unsafe_allow_html=True)
                        st.markdown(f"<p style='text-align:center'><a href='{movie['link']}' target='_blank'>ℹ️ More Info</a></p>", unsafe_allow_html=True)
