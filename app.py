# app.py — UI for Chatbot Project (Italian Restautrant)
from __future__ import annotations
from typing import Optional
import os, sys
import streamlit as st
import streamlit.components.v1 as components
import html
import threading

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

# Initialize background services (order reset + status daemon) once per process
@st.cache_resource(show_spinner=False)
def start_background_services():
    queries.finalize_previous_orders()

    stop_event = threading.Event()

    def worker():
        while not stop_event.is_set():
            try:
                queries.refresh_order_statuses()
            except Exception as exc:
                print(f"[order-status-daemon] {exc}")
            stop_event.wait(30)

    thread = threading.Thread(target=worker, name="order-status-daemon", daemon=True)
    thread.start()
    return stop_event

# Session defaults
if "lang" not in st.session_state: st.session_state.lang = "en"
if "theme" not in st.session_state: st.session_state.theme = "light"
if "messages" not in st.session_state: st.session_state.messages = []
if "customer" not in st.session_state: st.session_state.customer = "guest"
if "order_id" not in st.session_state: st.session_state.order_id = 1
if "table_number" not in st.session_state: st.session_state.table_number = 1
if "llm" not in st.session_state: st.session_state.llm = None
if "initial_greeting_sent" not in st.session_state: st.session_state.initial_greeting_sent = False

# Allow language to persist via URL query parameter (?lang=ελ|en)
qp = st.query_params
if "lang" in qp and qp["lang"] in ("ελ", "en"):
    if qp["lang"] != st.session_state.lang:
        st.session_state.lang = qp["lang"]

# Resolved dictionary for current language
S = STR[st.session_state.lang]

# Brand header (logo) at the top of the app
def brand_header():
    col1, col2 = st.columns([3, 1])
    with col1:
        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            st.image(logo_path, width=200)  # Reduced from 300 to 200
        else:
            st.warning("⚠️ Logo not found at assets/logo.png")
    with col2:
        # Table selector dropdown
        selected_table = st.selectbox(
            S["table"],
            options=list(range(1, 11)),
            index=st.session_state.table_number - 1,
            key="table_selector",
            label_visibility="collapsed"  # Hide label to save space
        )
        st.caption(f"{S['table']}: {selected_table}")  # Show table info as caption
        if selected_table != st.session_state.table_number:
            st.session_state.table_number = selected_table
            st.session_state.order_id = selected_table  # Each table corresponds to an order_id
            st.session_state.messages = []  # Clear messages when switching tables
            st.session_state.initial_greeting_sent = False
            st.rerun()

# Apply theme and render brand area
apply_theme(st.session_state.theme)
S = STR[st.session_state.lang]

start_background_services()

# Compact header wrapper
st.markdown('<div class="compact-header">', unsafe_allow_html=True)
brand_header()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<a id="top"></a>', unsafe_allow_html=True)

# ---------- Helpers ----------
def page_title(icon: str, text: str):
    """Consistent page section header with icon."""
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:8px;margin:4px 0 2px 0;">'
        f'<span style="font-size:20px">{icon}</span>'
        f'<h1 style="font-family:\'Playfair Display\',serif;font-weight:700;margin:0;font-size:22px;">{text}</h1>'
        f'</div>', unsafe_allow_html=True
    )


def build_chat_context() -> str:
    """Returns a base context message for the LLM without personal names."""
    order_id = int(st.session_state.order_id)
    table_no = int(st.session_state.table_number)
    order_summary = "No current items in this order."
    try:
        receipt = queries.receipt(order_id=order_id, include_paid=True, include_status=True)
        items = receipt.get("items", [])
        if items:
            lines = [
                f"  • order_item_id {entry['order_item_id']}: {entry['item name']} x{entry['quantity']} (status: {entry.get('status', 'pending')})"
                for entry in items
            ]
            order_summary = "Current order items:\n" + "\n".join(lines)
    except Exception:
        # Silently ignore DB issues; the LLM will rely on tools instead
        pass

    return (
        "You are Trattoria AI, a helpful restaurant assistant. "
        f"The guest is seated at table {table_no}, which maps to order_id {order_id}. "
        "Use that order_id when referencing or updating their cart. "
        f"{order_summary} "
        "Answer concisely about menu items, orders, specials, and customer requests."
    )


def ensure_initial_greeting():
    """Seed the conversation with a simple welcome message once per session."""
    if st.session_state.get("initial_greeting_sent"):
        return

    if st.session_state.messages:
        st.session_state.initial_greeting_sent = True
        return

    fallback = "Welcome to Trattoria AI! 👋\nI'm here to help with menu questions or orders.\nHow can I assist you today?"
    st.session_state.messages.append(("assistant", fallback))
    st.session_state.initial_greeting_sent = True


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
    """Cart tab: read-only snapshot from DB excluding only cancelled items."""
    try:
        rec = queries.receipt(
            int(st.session_state.order_id),
            item_names=None,
            include_paid=True,
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
    ensure_initial_greeting()

    # Message history (user / assistant) rendered via custom HTML for precise styling
    chat_container = st.container()
    chat_html_parts = ['<div class="chat-shell"><div class="chat-scroll">']

    for role, text in st.session_state.messages:
        safe_text = html.escape(text).replace("\n", "<br>")
        if role == "user":
            chat_html_parts.append(
                '<div class="chat-row chat-row-user">'
                f'<div class="chat-bubble chat-bubble-user">{safe_text}</div>'
                '</div>'
            )
        else:
            chat_html_parts.append(
                '<div class="chat-row chat-row-assistant">'
                f'<div class="chat-bubble chat-bubble-assistant">{safe_text}</div>'
                '</div>'
            )

    if st.session_state.get("waiting_for_response", False):
        chat_html_parts.append(
            '<div class="chat-row chat-row-assistant">'
            '<div class="chat-bubble chat-bubble-assistant typing-bubble">'
            '<div class="typing-indicator"><span></span><span></span><span></span></div>'
            '</div></div>'
        )

    chat_html_parts.append('</div></div>')
    chat_container.markdown("".join(chat_html_parts), unsafe_allow_html=True)

    components.html(
        """
        <script>
        const parentDocument = window.parent ? window.parent.document : document;
        const containers = parentDocument.querySelectorAll('.chat-shell .chat-scroll');
        const target = containers.length ? containers[containers.length - 1] : null;
        if (target) {
            setTimeout(() => {
                try {
                    target.scrollTo({ top: target.scrollHeight, behavior: 'smooth' });
                } catch (err) {
                    target.scrollTop = target.scrollHeight;
                }
            }, 50);
        }
        </script>
        """,
        height=0,
    )

    # Chat input anchored at bottom of the tab
    user_msg = st.chat_input(S["chat_placeholder"], key="chat_input_main")
    if user_msg:
        # Add user message immediately
        st.session_state.messages.append(("user", user_msg))
        st.session_state.waiting_for_response = True
        st.rerun()
    
    # Process LLM response if waiting
    if st.session_state.get("waiting_for_response", False):
        # Build full chat history from session messages
        chat_history = [{"role": "user", "content": build_chat_context()}]
        
        # Add all previous messages to chat history (exclude last one as it's the current user message)
        for role, text in st.session_state.messages[:-1]:
            chat_history.append({"role": role, "content": text})
        
        llm = get_llm()
        if llm:
            try:
                # Get the last user message
                last_user_msg = st.session_state.messages[-1][1]
                reply = llm.query(last_user_msg, chat_history=chat_history)
            except Exception as e:
                reply = f"Error: {e}"
        else:
            reply = S.get("llm_missing", "LLM missing.")
        
        st.session_state.messages.append(("assistant", reply))
        st.session_state.waiting_for_response = False
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
