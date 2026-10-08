import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

st.set_page_config(page_title="Road Watch | Accident Risk Predictor", page_icon="🚦",
                   layout="wide", initial_sidebar_state="expanded")

import os  # noqa: E402


def _conflicted_files(base):
    """Files that still contain Git merge-conflict markers (a broken pull/merge)."""
    bad = []
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in (".git", "venv", ".venv", "__pycache__", "node_modules")]
        for name in files:
            if name.endswith((".py", ".csv", ".toml", ".txt")):
                path = os.path.join(root, name)
                try:
                    with open(path, encoding="utf-8", errors="ignore") as fh:
                        lines = fh.read().splitlines()
                except OSError:
                    continue
                if any(x.startswith("<<<<<<<") for x in lines) and any(x.startswith(">>>>>>>") for x in lines):
                    bad.append(os.path.relpath(path, base))
    return bad


_bad = _conflicted_files(os.path.dirname(os.path.abspath(__file__)))
if _bad:
    st.error("These files contain Git merge-conflict markers (<<<<<<<, =======, >>>>>>>): "
             + ", ".join(_bad) + ". Replace them with the clean copies from the original zip, "
             "commit and push again, then reboot the app.")
    st.stop()

from roadwatch.theme import inject_css, sidebar_brand  # noqa: E402

inject_css()
sidebar_brand()

pages = [
    st.Page("views/home.py", title="Open Road", icon="🛣️", default=True),
    st.Page("views/predict.py", title="Risk Check", icon="🚦"),
    st.Page("views/explore.py", title="Traffic Data", icon="📊"),
    st.Page("views/performance.py", title="Model Report", icon="🎯"),
    st.Page("views/road_rules.py", title="Rules of the Road", icon="📜"),
    st.Page("views/about.py", title="About", icon="ℹ️"),
]
st.navigation(pages).run()
