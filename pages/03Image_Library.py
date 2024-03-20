"""Image Library"""

import os

import streamlit as st
from streamlit_image_select import image_select

from lib import constants
from lib import utils

st.header("Image Library 📚", divider=True)

for data_storage in [
    constants.DATA_LOCATION,
    constants.VECTOR_LOCATION,
    constants.FILE_LOCATION,
]:
    if not os.path.exists(data_storage):
        os.mkdir(data_storage)

source_window = st.sidebar.empty()
st.sidebar.divider()
preview_window = st.sidebar.empty()
images_window = st.empty()

images_in_library = utils.get_images_in_library()
selected_image = None

with source_window:
    with st.form("add_images", clear_on_submit=True, border=False):
        images = st.file_uploader(
            "Choose pictures", accept_multiple_files=True, type=["jpg", "png"]
        )
        add_submitted = st.form_submit_button("Add to image library")

if images and add_submitted:
    utils.add_images_to_library(images)
    images_in_library = utils.get_images_in_library()

with images_window:
    if images_in_library:
        selected_image = image_select(
            label="Click image to preview:",
            images=images_in_library,
            captions=[image.split("/")[-1] for image in images_in_library],
        )

with preview_window:
    if images_in_library:
        with st.form("delete_image", clear_on_submit=True, border=False):
            st.image(image=selected_image)
            delete_submitted = st.form_submit_button("Delete from image library")

if selected_image is not None and delete_submitted:
    utils.delete_image_from_library(selected_image)
    images_in_library = utils.get_images_in_library()
    st.rerun()
