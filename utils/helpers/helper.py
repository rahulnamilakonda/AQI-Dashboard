import streamlit as st


def markdown(markdown: str, unsafe_allow_html=True):
    st.markdown(markdown, unsafe_allow_html=unsafe_allow_html)
