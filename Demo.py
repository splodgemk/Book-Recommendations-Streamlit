import streamlit as st
import numpy as np
import pandas as pd

import requests
from PIL import Image
from io import BytesIO


corr_matrix = np.load("correlation_matrix.npy")
rating_utility_matrix = pd.read_csv("rating_utility_matrix.csv")
rating_utility_matrix.drop("user_id", axis=1, inplace=True)

def recommend(title,similarity):
    books = rating_utility_matrix.columns
    books_list = list(books)
    book_index = books_list.index(title)
    corr_title = corr_matrix[book_index]
    recommendations = list(books[(corr_title < 1.0) & (corr_title > similarity)])
    return recommendations

def get_book_cover(title):
    response = requests.get(f"http://openlibrary.org/search.json?title={title}")
    if response.status_code == 200:
        data = response.json()
        if data['num_found'] > 0:
            cover_id = data['docs'][0].get('cover_i', None)
            if cover_id:
                cover_url = f"http://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
                return cover_url
    return None

def clean_book_title(title):
    chars_to_remove = '\/[]()#'
    translation_table = str.maketrans('', '', chars_to_remove)
    return title.translate(translation_table)

def is_valid_image(url):
    try:
        response = requests.get(url)
        Image.open(BytesIO(response.content))
        return True
    except UnidentifiedImageError:
        return False


st.set_page_config(
	page_title="Book Recommendations",
	page_icon = ":📖:"
)


#st.write(rating_utility_matrix.columns)

st.subheader("Book recommnendation app 📖")
st.write("A small collaborative recommnendation system made using data from good reads.")

covers = st.toggle("Display Book covers")
book_title = st.selectbox("Select a book title: ",rating_utility_matrix.columns )
similarity = st.slider("Pick how similar the recommendations should be:", 0.2,0.9,0.8)


if book_title:
    st.header(f"Searching for books similar to: {book_title}")
    if covers:
        cleaned_title = clean_book_title(book_title)
        cover_url = get_book_cover(cleaned_title)
        if cover_url and is_valid_image(cover_url):
            response = requests.get(cover_url)
            image = Image.open(BytesIO(response.content))
            st.image(image, caption=cleaned_title)
        else:
            st.write('Book cover not found.')

st.divider()

recommendations = recommend(book_title, similarity)

if recommendations[0] == book_title:
    recommendations.remove(recommendations[0])


st.header("Recommendations:")
if len(recommendations) == 0:
    st.write("No books found. Try lowering the similarity slider.")
else:
    st.write(f"Found {len(recommendations)} titles.")



with st.spinner("Searching book shelves..."):
    for book in reversed(recommendations):
        if book != book_title:
            st.write(book)
        if covers:
            cover_url = get_book_cover(book)
            if cover_url and is_valid_image(cover_url):
                response = requests.get(cover_url)
                image = Image.open(BytesIO(response.content))
                st.image(image, caption=book)
            else:
                st.write('Book cover not found.')
    
