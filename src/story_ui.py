"""Consistent, accessible interpretation layout."""
from __future__ import annotations
import html
import streamlit as st
def render_story(story: dict, label: str):
    with st.container(border=True):
        st.markdown('#### What this figure tells us · '+label)
        st.markdown('**Finding:** '+story['headline'])
        st.write(story['evidence'])
        st.markdown('**How a business might use this:** '+story['decision'])
        st.caption('Interpretation boundary: '+story['caution'])
