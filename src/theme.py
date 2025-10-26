# src/theme.py
from pathlib import Path
import streamlit as st

def apply_theme(theme: str = "light") -> None:
    """
    Loads the CSS file corresponding to the selected theme ('light' or 'dark')
    from the assets directory and injects it into the Streamlit app.
    """

    # Normalize theme input (anything other than "dark" becomes "light")
    theme_name = "dark" if theme == "dark" else "light"

    # The CSS files are expected to be in assets/
    css_path = Path("assets") / f"{theme_name}.css"

    if not css_path.exists():
        st.warning(f"⚠️ Theme file not found: {css_path}")
        return

    try:
        css_content = css_path.read_text(encoding="utf-8")
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading theme '{theme_name}': {e}")

