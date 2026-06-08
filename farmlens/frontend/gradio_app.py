from __future__ import annotations

import gradio as gr


def answer(question: str) -> str:
    """Placeholder answer function for the Gradio demo."""
    return "Coming soon."


def create_demo() -> gr.Blocks:
    """Create the FarmLens Gradio demo interface."""
    with gr.Blocks(title="FarmLens") as demo:
        gr.Markdown("# FarmLens — किसान सहायक")
        question = gr.Textbox(label="अपना सवाल पूछें / Ask your question")
        output = gr.Textbox(label="उत्तर / Answer")
        gr.Button("पूछें / Ask").click(answer, inputs=question, outputs=output)
    return demo


if __name__ == "__main__":
    demo = create_demo()
    demo.launch()
