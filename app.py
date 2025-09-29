import streamlit as st
import google.generativeai as genai
from diffusers import StableDiffusionPipeline
import torch
import os

# ---------------------------
# Configure Gemini API
# ---------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # set your key in terminal or .env
genai.configure(api_key=GEMINI_API_KEY)

# ---------------------------
# Load Stable Diffusion (Light Image Model)
# ---------------------------
@st.cache_resource
def load_image_model():
    model_id = "runwayml/stable-diffusion-v1-5"  # lightweight logo gen
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id, torch_dtype=torch.float16
    )
    pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")
    return pipe

# ---------------------------
# App UI
# ---------------------------
st.set_page_config(page_title="AI Business Idea Generator", layout="wide")
st.title("🚀 AI Startup Idea Builder")

# Sidebar input
with st.sidebar:
    st.header("⚙️ Customize Your Idea")
    niche = st.text_input("Business Niche", "food delivery")
    target = st.text_input("Target Audience", "college students")
    tone = st.selectbox("Tone", ["Professional", "Friendly", "Funny"])
    color_theme = st.color_picker("Pick a theme color", "#FF5733")
    generate_btn = st.button("✨ Generate Startup Idea")

# ---------------------------
# Main Logic
# ---------------------------
if generate_btn:
    # ---- Gemini Text Generation ----
    st.subheader("💡 Business Idea")
    model = genai.GenerativeModel("gemini-2.5-flash")
    text_prompt = (
        f"Generate a {tone.lower()} startup idea in the niche of {niche}, "
        f"targeted at {target}. Provide:\n"
        f"- A creative business name\n"
        f"- A catchy one-liner\n"
        f"- A short pitch (3-4 sentences)\n"
    )

    response = model.generate_content(text_prompt)
    st.write(response.text)

    # ---- Logo Generation ----
    st.subheader("🎨 AI Logo")
    img_pipe = load_image_model()
    image = img_pipe(f"Minimal startup logo for {niche}, theme color {color_theme}").images[0]
    st.image(image, caption="Generated Logo", use_column_width=True)
