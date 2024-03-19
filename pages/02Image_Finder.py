"""Image Finder"""

import os
import base64

import streamlit as st

from lib import constants
from lib import utils

st.header("Image Finder 🔎", divider=True)

for data_storage in [
    constants.DATA_LOCATION,
    constants.VECTOR_LOCATION,
    constants.FILE_LOCATION,
]:
    if not os.path.exists(data_storage):
        os.mkdir(data_storage)

source_window = st.sidebar.empty()
image_window = st.empty()

with source_window:
    with st.form("image", clear_on_submit=False, border=False):
        query = st.text_input("Search by text")
        image = st.file_uploader(
            "Search by image", accept_multiple_files=False, type=["jpg", "png"]
        )
        n_results = st.slider("Max number of results:", 1, 5, 1, 1)
        submitted = st.form_submit_button("Search")

if image:
    base64_encoded_image = base64.b64encode(image.getvalue()).decode("utf-8")
    payload = utils.format_content_for_titan_mm_embed(
        base64_encoded_image=base64_encoded_image
    )
    image_embedding = utils.generate_embeddings(payload)["embedding"]

found_images = None
if submitted:
    with st.spinner("Searching..."):
        if query and image:
            st.sidebar.warning("Search by text or image not both.")
        elif query:
            found_images = utils.find_similar_image(
                query_texts=[query], n_results=n_results
            )
        elif image:
            found_images = utils.find_similar_image(
                query_embeddings=[image_embedding], n_results=n_results
            )
        else:
            st.sidebar.warning("Search by text or image.")


if found_images is not None:
    if found_images:
        for found_image in found_images:
            st.image(found_image[1])
            st.write(
                f"Name: {found_image[0]}, Path: {found_image[1]}, Distance: {found_image[2]}"
            )
    else:
        st.write("No similar images are found!")
