"""Cached loaders shared by every page."""
import streamlit as st

from roadwatch import pipeline as P


@st.cache_resource(show_spinner="Warming up the engine...")
def get_bundle():
    return P.get_bundle()


@st.cache_data(show_spinner=False)
def get_plot_data():
    return P.load_plot_frame()
