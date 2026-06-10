from __future__ import annotations

import os

import requests
import streamlit as st

_API_HOST = os.environ.get("FARMLENS_API_URL", "http://localhost:8000")
_API_BASE = f"{_API_HOST}/api/v1"
_HEALTH_URL = f"{_API_HOST}/health"
_TIMEOUT = 60

_LANGUAGES: dict[str, str] = {
    "हिन्दी": "hi",
    "English": "en",
    "ਪੰਜਾਬੀ": "pa",
    "मराठी": "mr",
    "తెలుగు": "te",
    "தமிழ்": "ta",
}
_STATES: list[str] = [
    "Uttar Pradesh",
    "Maharashtra",
    "Punjab",
    "Haryana",
    "Madhya Pradesh",
    "Rajasthan",
    "Gujarat",
    "Karnataka",
    "Andhra Pradesh",
    "Tamil Nadu",
]
_CITIES: dict[str, tuple[float, float]] = {
    "Delhi": (28.6139, 77.2090),
    "Lucknow": (26.8467, 80.9462),
    "Ludhiana": (30.9010, 75.8573),
    "Pune": (18.5204, 73.8567),
    "Bhopal": (23.2599, 77.4126),
    "Jaipur": (26.9124, 75.7873),
}


# ── API client ────────────────────────────────────────────────────────────────


def _post_chat(question: str, language: str) -> dict:
    """POST a text question to the /chat endpoint."""
    resp = requests.post(
        f"{_API_BASE}/chat",
        params={"question": question, "language": language},
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def _post_voice_chat(audio: bytes, language: str) -> dict:
    """POST recorded audio to the /voice-chat endpoint."""
    resp = requests.post(
        f"{_API_BASE}/voice-chat",
        params={"language": language},
        files={"audio": ("question.wav", audio, "audio/wav")},
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def _get_price(crop: str, state: str) -> dict:
    """GET mandi prices for a crop in a state."""
    resp = requests.get(
        f"{_API_BASE}/price", params={"crop": crop, "state": state}, timeout=_TIMEOUT
    )
    resp.raise_for_status()
    return resp.json()


def _get_weather(lat: float, lon: float) -> dict:
    """GET the weather advisory for coordinates."""
    resp = requests.get(f"{_API_BASE}/weather", params={"lat": lat, "lon": lon}, timeout=_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def _get_schemes(query: str) -> dict:
    """GET government schemes matching a query."""
    resp = requests.get(f"{_API_BASE}/schemes", params={"query": query}, timeout=_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def _backend_online() -> bool:
    """Return True if the backend health endpoint responds."""
    try:
        return requests.get(_HEALTH_URL, timeout=3).status_code == 200
    except requests.RequestException:
        return False


# ── UI rendering ──────────────────────────────────────────────────────────────


def _render_answer(data: dict) -> None:
    """Render a RAGResponse answer with optional sources."""
    st.success(data.get("answer", ""))
    sources = data.get("sources", [])
    if sources:
        with st.expander("स्रोत / Sources"):
            for src in sources:
                st.caption(f"{src.get('source', '')} — p.{src.get('page', '?')}")


def _render_text_tab(language: str) -> None:
    """Render the text-question tab."""
    question = st.text_input("अपना सवाल लिखें / Type your question")
    if st.button("पूछें / Ask", key="ask_text") and question:
        with st.spinner("सोच रहे हैं… / Thinking…"):
            try:
                _render_answer(_post_chat(question, language))
            except requests.RequestException as exc:
                st.error(f"बैकएंड त्रुटि / Backend error: {exc}")


def _render_voice_tab(language: str) -> None:
    """Render the voice-question tab."""
    st.caption("माइक से सवाल रिकॉर्ड करें / Record your question with the mic")
    audio = st.audio_input("रिकॉर्ड करें / Record")
    if audio is not None and st.button("भेजें / Send", key="ask_voice"):
        with st.spinner("सुन रहे हैं… / Listening…"):
            try:
                _render_answer(_post_voice_chat(audio.getvalue(), language))
            except requests.RequestException as exc:
                st.error(f"बैकएंड त्रुटि / Backend error: {exc}")


def _render_price_tool() -> None:
    """Render the mandi-price quick tool."""
    crop = st.text_input("फसल / Crop", value="गेहूं", key="price_crop")
    state = st.selectbox("राज्य / State", _STATES, key="price_state")
    if st.button("भाव देखें / Get price", key="btn_price") and crop:
        try:
            data = _get_price(crop, state)
            for rec in data.get("records", []):
                st.write(f"{rec['market']}: ₹{rec['modal_price']} ({rec['arrival_date']})")
        except requests.RequestException as exc:
            st.error(f"त्रुटि / Error: {exc}")


def _render_weather_tool() -> None:
    """Render the weather-advisory quick tool."""
    city = st.selectbox("शहर / City", list(_CITIES), key="weather_city")
    if st.button("मौसम देखें / Get weather", key="btn_weather"):
        lat, lon = _CITIES[city]
        try:
            data = _get_weather(lat, lon)
            verdict = "✅ सुरक्षित" if data.get("safe_to_spray") else "⚠️ असुरक्षित"
            st.write(f"{verdict} — {data.get('spray_advisory', '')}")
        except requests.RequestException as exc:
            st.error(f"त्रुटि / Error: {exc}")


def _render_schemes_tool() -> None:
    """Render the government-schemes quick tool."""
    query = st.text_input("खोजें / Search", value="insurance", key="scheme_q")
    if st.button("योजनाएँ / Schemes", key="btn_scheme") and query:
        try:
            data = _get_schemes(query)
            for scheme in data.get("schemes", []):
                st.write(f"**{scheme['name_hi']}** — {scheme['benefit']}")
        except requests.RequestException as exc:
            st.error(f"त्रुटि / Error: {exc}")


def _render_tools_tab() -> None:
    """Render the structured data tools (price, weather, schemes)."""
    st.subheader("भाव / Mandi price")
    _render_price_tool()
    st.subheader("मौसम / Weather")
    _render_weather_tool()
    st.subheader("योजनाएँ / Schemes")
    _render_schemes_tool()


def _render_sidebar() -> str:
    """Render the sidebar and return the selected language code."""
    st.sidebar.header("सेटिंग्स / Settings")
    label = st.sidebar.selectbox("भाषा / Language", list(_LANGUAGES))
    if _backend_online():
        st.sidebar.success("बैकएंड ऑनलाइन / Backend online")
    else:
        st.sidebar.error("बैकएंड बंद / Backend offline — start the API first")
    return _LANGUAGES[label]


def main() -> None:
    """Run the FarmLens Streamlit UI."""
    st.set_page_config(page_title="FarmLens", page_icon="🌾", layout="centered")
    st.title("FarmLens — किसान सहायक")
    st.caption("आवाज़ या टेक्स्ट से खेती के सवाल पूछें / Ask farming questions by voice or text")
    language = _render_sidebar()
    text_tab, voice_tab, tools_tab = st.tabs(["💬 टेक्स्ट / Text", "🎙️ आवाज़ / Voice", "📊 टूल्स / Tools"])
    with text_tab:
        _render_text_tab(language)
    with voice_tab:
        _render_voice_tab(language)
    with tools_tab:
        _render_tools_tab()


if __name__ == "__main__":
    main()
