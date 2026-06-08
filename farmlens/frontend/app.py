from __future__ import annotations

import streamlit as st


def main() -> None:
    """Run the FarmLens Streamlit UI."""
    st.set_page_config(page_title="FarmLens", page_icon="🌾", layout="centered")
    st.title("FarmLens — किसान सहायक")
    st.write("Coming soon: voice and text farming advisory in Hindi.")


if __name__ == "__main__":
    main()
