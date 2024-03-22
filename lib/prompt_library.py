"""Crawl Anthropic prompt library"""

from typing import Dict

import streamlit as st
import requests
from bs4 import BeautifulSoup

URL = "https://docs.anthropic.com/claude"


@st.cache_data(show_spinner=False)
def crawl_contents(url: str) -> str:
    """Crawl contents from the given URL"""
    response = requests.get(url=url, timeout=5)
    contents = BeautifulSoup(response.content, "html.parser")
    return contents


@st.cache_data(show_spinner=False)
def crawl_prompt_list() -> Dict:
    """Get a list of Claude prompt library"""
    contents = crawl_contents(f"{URL}/prompt-library").select(".examples-grid a")
    prompts = {}
    for prompt in contents:
        href = prompt["href"]
        title = prompt.select_one(".icon-item-title").text
        description = prompt.select_one(".icon-item-desc").text.strip()
        prompts[title] = {"href": href, "description": description}
    return prompts


@st.cache_data(show_spinner=False)
def crawl_prompt(path: str) -> Dict:
    """Get a prompt details"""
    contents = crawl_contents(f"{URL}/{path}")
    prompt = {"system": "", "user": ""}
    system_prompt = contents.find("td", string="System")
    if system_prompt is not None:
        prompt["system"] = system_prompt.find_next("td").get_text()
    user_prompt = contents.find("td", string="User")
    if user_prompt is not None:
        prompt["user"] = user_prompt.find_next("td").get_text()
    return prompt
