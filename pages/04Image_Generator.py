"""Image Generator"""

import io
import base64

import streamlit as st

from lib import constants
from lib import utils

st.header("Image Generator 🖨️", divider=True)

utils.setup_storage()

images = None

if "generated_images" not in st.session_state.keys():
    st.session_state["generated_images"] = None


prompt_window = st.sidebar.empty()
images_window = st.empty()


with prompt_window:
    with st.form("prompt", clear_on_submit=False, border=False):
        prompt = st.text_area("User prompt:")
        image_size = st.selectbox("Width, Height", options=constants.IMAGE_SIZE)
        cfg_scale = st.slider("CfgScale (randomness)", 1.1, 10.0, 8.0, 0.1, "%f")
        seed = st.slider("Seed (noise setting)", 0, 2147483646, 0, 1)
        image_numbers = st.select_slider(
            "Image numbers", options=constants.IMAGE_NUMBERS
        )
        submitted = st.form_submit_button("Generate")


with images_window:
    if prompt and submitted:
        with st.spinner("Generating images..."):
            image_settings = ()
            base64_encoded_images = utils.generate_images(
                prompt=prompt,
                number_of_images=image_numbers,
                cfg_scale=cfg_scale,
                width=image_size[0],
                height=image_size[1],
                seed=seed,
            )
            images = [
                io.BytesIO(base64.b64decode(image)) for image in base64_encoded_images
            ]
            st.session_state["generated_images"] = images
    with st.form("generated_image", clear_on_submit=False, border=False):
        if st.session_state["generated_images"] is not None:
            st.image(st.session_state["generated_images"])
        add_to_image_library = st.form_submit_button("Add to image library")

if st.session_state["generated_images"] is not None:
    if add_to_image_library:
        with st.spinner("Saving images..."):
            utils.add_images_to_library(st.session_state["generated_images"])
