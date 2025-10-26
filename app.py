# app.py — UI for Chatbot Project (Italian Restautrant)
from __future__ import annotations
from typing import Optional
import os, sys
import streamlit as st
import html

# Load environment variables from .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Make local modules importable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from src import queries
from src.anthropic_llm import AnthropicLLM

from src.i18n import STR

# Streamlit page setup
st.set_page_config(page_title="Trattoria AI", page_icon="🍝", layout="wide")

# Allow theme to persist via URL query parameter (?theme=light|dark)
qp = st.query_params
if "theme" in qp and qp["theme"] in ("light", "dark"):
    st.session_state.theme = qp["theme"]

from src.theme import apply_theme

# Session defaults
if "lang" not in st.session_state: st.session_state.lang = "ελ"
if "theme" not in st.session_state: st.session_state.theme = "light"
if "messages" not in st.session_state: st.session_state.messages = []
if "customer" not in st.session_state: st.session_state.customer = "guest"
if "order_id" not in st.session_state: st.session_state.order_id = 1
if "llm" not in st.session_state: st.session_state.llm = None

# Allow language to persist via URL query parameter (?lang=ελ|en)
qp = st.query_params
if "lang" in qp and qp["lang"] in ("ελ", "en"):
    if qp["lang"] != st.session_state.lang:
        st.session_state.lang = qp["lang"]

# Resolved dictionary for current language
S = STR[st.session_state.lang]

# Brand header (logo) at the top of the app
def brand_header():
    logo_path = "assets/logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=300)
    else:
        st.warning("⚠️ Logo not found at assets/logo.png")

# Apply theme and render brand area
apply_theme(st.session_state.theme)
S = STR[st.session_state.lang]
brand_header()

st.markdown('<a id="top"></a>', unsafe_allow_html=True)

# ---------- Helpers ----------
def page_title(icon: str, text: str):
    """Consistent page section header with icon."""
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;margin:8px 0 4px 0;">'
        f'<span style="font-size:26px">{icon}</span>'
        f'<h1 style="font-family:\'Playfair Display\',serif;font-weight:700;margin:0;font-size:28px;">{text}</h1>'
        f'</div>', unsafe_allow_html=True
    )

def get_llm() -> Optional[AnthropicLLM]:
    """Lazy-instantiates the Anthropic LLM client based on environment configuration."""
    if st.session_state.llm is None:
        key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            st.warning(S["llm_missing"])
            return None
        st.session_state.llm = AnthropicLLM(api_key=key)
    return st.session_state.llm

def render_cart_view():
    """Cart tab: read-only snapshot from DB excluding paid items."""
    try:
        rec = queries.receipt(
            int(st.session_state.order_id),
            item_names=None,
            include_paid=False,
            include_status=True
        )
        items = rec.get("items", [])
        total = float(rec.get("total", 0.0))
    except Exception as e:
        st.error(f"Σφάλμα φόρτωσης καλαθιού: {e}")
        return

    c1, c2 = st.columns(2)
    with c1: st.metric(S["items"], len(items))
    with c2: st.metric(S["total"], f"{total:.2f}")

    if not items:
        st.caption(S["not_found"])
    else:
        for it in items:
            status_info = f" ({it.get('status')})" if "status" in it else ""
            st.write(f"- {it['item name']} — €{float(it['item value']):.2f}{status_info}")

# Tabs
tab_chat, tab_menu, tab_cart, tab_settings = st.tabs(
    [f"🗨️ {S['chat']}", f"📖 {S['menu']}", f"🛒 {S['cart']}", f"⚙️ {S['settings']}"]
)

# ================= CHAT =================
with tab_chat:
    page_title("💬", S["chat_header"])

    # Reset button aligned to the right
    right = st.columns([23, 1])[1]
    with right:
        if st.button("🔄", key="reset_chat_btn"):
            st.session_state.messages = []
            st.rerun()

    # Immutable context badge with order and customer
    st.markdown(
        f'<span class="badge">{S.get("context_badge","Order")}: '
        f'<b>#{int(st.session_state.order_id)}</b> — {st.session_state.customer}</span>',
        unsafe_allow_html=True
    )

    # Message history (user / assistant)
    with st.container():
        for role, text in st.session_state.messages:
            with st.chat_message(role):
                st.markdown(text)

    # Chat input anchored at bottom of the tab
    user_msg = st.chat_input("…", key="chat_input_main")
    if user_msg:
        st.session_state.messages.append(("user", user_msg))
        context = f"My order_id is {int(st.session_state.order_id)} and my name is {st.session_state.customer}."
        llm = get_llm()
        if llm:
            try:
                reply = llm.query(user_msg, chat_history=[{"role": "user", "content": context}])
            except Exception as e:
                reply = f"Error: {e}"
        else:
            reply = S.get("llm_missing", "LLM missing.")
        st.session_state.messages.append(("assistant", reply))
        st.rerun()

    # Back to top Button
    st.markdown('<a href="#top" class="to-top" title="Back to top">↑</a>', unsafe_allow_html=True)


# ================= MENU =================
with tab_menu:
    page_title("📖", S["menu_header"])

    # Filters (type + categories)
    colf, colc = st.columns([1, 2])
    with colf:
        type_sel = st.selectbox(S["type"], [S["all"], S["foods"], S["drinks"]], key="menu_type_sel")
        is_food = None if type_sel == S["all"] else (type_sel == S["foods"])

    # Fetch categories based on chosen type
    try:
        cats_resp = queries.getCategories(is_food=is_food)
        categories = cats_resp.get("categories", [])
    except Exception as e:
        st.error(e)
        categories = []

    with colc:
        chosen_cats = st.multiselect(S["categories"], options=categories, default=[], key="menu_cats_ms")

    # Price range
    colp1, colp2 = st.columns(2)
    with colp1:
        min_price = st.number_input(S["min_price"], min_value=0.0, step=0.5, value=0.0, key="menu_min_price")
    with colp2:
        max_price = st.number_input(S["max_price"], min_value=0.0, step=0.5, value=0.0, key="menu_max_price")

    # Include / Exclude ingredients
    coli, cole = st.columns(2)
    with coli:
        must_include = [
            s.strip() for s in st.text_input(S["must_include"], "", key="menu_must_include").split(",") if s.strip()
        ]
    with cole:
        must_exclude = [
            s.strip() for s in st.text_input(S["must_exclude"], "", key="menu_must_exclude").split(",") if s.strip()
        ]

    # Query menu items (based on user filters)
    try:
        menu_resp = queries.getMenu(
            is_food=is_food,
            category=chosen_cats or None,
            min_price=min_price if min_price > 0 else None,
            max_price=max_price if max_price > 0 else None,
            must_include=must_include or None,
            must_exclude=must_exclude or None
        )
        items = menu_resp.get("items", [])
    except Exception as e:
        st.error(e)
        items = []


    # Render items (using a pure HTML grid to avoid widget artifacts between tabs)
    if not items:
        st.info(S["not_found"])
    else:
        parts = ['<div class="menu-grid2">']
        for it in items:
            title = html.escape(it.get("food", "Item"))
            desc  = html.escape(it.get("description") or "")
            price = float(it.get("price", 0.0))
            ing   = it.get("ingredients") or []
            ing_text = f"{S['ingredients']}: " + ", ".join(ing) if ing else ""
            ing_text = html.escape(ing_text)

            desc_html = f'<div class="desc">{desc}</div>' if desc else ''
            ing_html  = f'<div class="ing" style="margin-top:8px;opacity:.85;font-size:13px;">{ing_text}</div>' if ing_text else ''

            parts.append(
                '<div class="menu-card">'
                f'<div class="title">{title}</div>'
                f'{desc_html}'
                f'<span class="price">€ {price:.2f}</span>'
                f'{ing_html}'
                '</div>'
            )
        parts.append('</div>')
        st.markdown("".join(parts), unsafe_allow_html=True)

    st.markdown('<a href="#top" class="to-top" title="Back to top">↑</a>', unsafe_allow_html=True)


# ================= CART (read-only) =================
with tab_cart:
    page_title("🛒", S["cart_header"])
    render_cart_view()

# ================= SETTINGS =================
with tab_settings:
    page_title("⚙️", S["settings_header"])
    col1, col2 = st.columns(2)

    # Customer and order settings (persist in session)
    with col1:
        st.session_state.customer = st.text_input(
            S["customer"], value=st.session_state.customer, key="settings_customer"
        )
        st.session_state.order_id = st.number_input(
            S["order_id"], min_value=1, step=1, value=int(st.session_state.order_id), key="settings_order_id"
        )

    # Language and theme controls; both persist in URL for durability across browser refresh
    with col2:
        lang = st.radio(
            S["language"], ["ελ", "en"],
            index=0 if st.session_state.lang == "ελ" else 1,
            key="lang_radio_top"
        )
        if lang != st.session_state.lang:
            st.session_state.lang = lang
            st.query_params["lang"] = lang
            if "theme" in st.session_state:
                st.query_params["theme"] = st.session_state.theme
            st.rerun()

        theme_label = st.radio(
            S["theme"], [S["light"], S["dark"]],
            index=0 if st.session_state.theme == "light" else 1,
            key="theme_radio_top"
        )
        new_theme = "light" if theme_label == S["light"] else "dark"
        if new_theme != st.session_state.theme:
            st.session_state.theme = new_theme
            st.query_params["theme"] = new_theme
            st.rerun()
