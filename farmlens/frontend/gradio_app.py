from __future__ import annotations

import gradio as gr

from farmlens.core.config import get_settings
from farmlens.core.exceptions import FarmLensException
from farmlens.features.mandi.service import MandiService
from farmlens.features.rag.pipeline import RAGPipeline
from farmlens.features.schemes.service import SchemeService
from farmlens.features.weather.service import WeatherService

# Single in-process instances (this app calls services directly — no HTTP layer).
_settings = get_settings()
_rag = RAGPipeline(_settings)
_mandi = MandiService(_settings)
_weather = WeatherService(_settings)
_schemes = SchemeService()


def answer_question(question: str) -> str:
    """Answer a farming question via RAG, initialising the pipeline on first use."""
    if not question.strip():
        return "कृपया अपना सवाल लिखें।"
    try:
        if not _rag.is_ready:
            _rag.initialize()
        response = _rag.answer(question)
    except FarmLensException as exc:
        return f"उत्तर देने में समस्या हुई: {exc}"
    sources = "\n".join(f"• {s.source} (पृष्ठ {s.page})" for s in response.sources)
    return f"{response.answer}\n\n— स्रोत —\n{sources}" if sources else response.answer


def get_price(crop: str, state: str) -> str:
    """Look up live mandi prices for a crop in a state."""
    try:
        result = _mandi.get_price(crop, state)
    except FarmLensException as exc:
        return f"भाव लाने में समस्या: {exc}"
    rows = [f"{r.market}: ₹{r.modal_price} ({r.arrival_date})" for r in result.records]
    return "\n".join(rows) if rows else "कोई भाव नहीं मिला।"


def get_weather(lat: float, lon: float) -> str:
    """Get a spray advisory for the given coordinates."""
    try:
        result = _weather.get_advisory(lat, lon)
    except FarmLensException as exc:
        return f"मौसम लाने में समस्या: {exc}"
    safe = "हाँ" if result.safe_to_spray else "नहीं"
    return f"{result.location}\n{result.spray_advisory}\nछिड़काव सुरक्षित: {safe}"


def find_schemes(query: str) -> str:
    """Find government schemes relevant to the query."""
    try:
        result = _schemes.find_schemes(query)
    except FarmLensException as exc:
        return f"योजनाएँ लाने में समस्या: {exc}"
    return "\n\n".join(f"📋 {s.name_hi}\n{s.description_hi}" for s in result.schemes)


def _chat_tab() -> None:
    """Build the RAG question-answer tab."""
    question = gr.Textbox(label="आपका सवाल", placeholder="गेहूं में पीला रतुआ रोग कैसे रोकें?")
    answer = gr.Textbox(label="उत्तर", lines=8)
    gr.Button("पूछें").click(answer_question, inputs=question, outputs=answer)


def _price_tab() -> None:
    """Build the mandi price tab."""
    crop = gr.Textbox(label="फसल", placeholder="गेहूं")
    state = gr.Textbox(label="राज्य", placeholder="Punjab")
    out = gr.Textbox(label="भाव", lines=6)
    gr.Button("भाव देखें").click(get_price, inputs=[crop, state], outputs=out)


def _weather_tab() -> None:
    """Build the weather / spray-advisory tab."""
    lat = gr.Number(label="Latitude", value=28.61)
    lon = gr.Number(label="Longitude", value=77.21)
    out = gr.Textbox(label="मौसम सलाह", lines=4)
    gr.Button("मौसम देखें").click(get_weather, inputs=[lat, lon], outputs=out)


def _schemes_tab() -> None:
    """Build the government-schemes tab."""
    query = gr.Textbox(label="विषय", placeholder="फसल बीमा")
    out = gr.Textbox(label="योजनाएँ", lines=8)
    gr.Button("खोजें").click(find_schemes, inputs=query, outputs=out)


def create_demo() -> gr.Blocks:
    """Build the FarmLens Gradio demo (chat + tool tabs)."""
    with gr.Blocks(title="FarmLens") as demo:
        gr.Markdown("# 🌾 FarmLens — किसान सहायक\nहिंदी में खेती से जुड़े सवाल पूछें।")
        with gr.Tab("सवाल-जवाब"):
            _chat_tab()
        with gr.Tab("मंडी भाव"):
            _price_tab()
        with gr.Tab("मौसम"):
            _weather_tab()
        with gr.Tab("योजनाएँ"):
            _schemes_tab()
    return demo


if __name__ == "__main__":
    create_demo().launch(server_name="0.0.0.0", server_port=7860)
