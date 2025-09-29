import streamlit as st
from huggingface_hub import InferenceClient
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
import os

# Hugging Face API token (put your key in secrets or env variable)
HF_TOKEN = os.getenv("HF_TOKEN")

# Initialize Hugging Face client
image_client = InferenceClient("black-forest-labs/FLUX.1-Krea-dev", token=HF_TOKEN)
text_client = InferenceClient("google/gemma-2-2b-it", token=HF_TOKEN)

st.title("🎨 AI Brand Identity Creator")

# --- Inputs ---
brand_name = st.text_input("Enter your Brand Name:")
slogan = st.text_input("Enter your Slogan:")
theme_color = st.color_picker("Pick your Theme Color:", "#0000FF")
brand_style = st.selectbox("Choose Brand Style:", ["Modern", "Minimalist", "Playful", "Luxury", "Futuristic"])

if st.button("Generate Brand Kit"):
    if not brand_name:
        st.warning("Please enter a brand name")
    else:
        with st.spinner("✨ Creating your brand identity..."):

            # --- Generate Logo ---
            logo_prompt = f"Minimal {brand_style} logo design for brand '{brand_name}', theme color {theme_color}, with slogan '{slogan}'. Flat vector style."
            try:
                image_bytes = image_client.text_to_image(logo_prompt)
                logo_img = ImageReader(io.BytesIO(image_bytes))
                st.image(image_bytes, caption="Generated Logo", use_column_width=True)
            except Exception as e:
                st.error(f"Logo generation failed: {e}")
                logo_img = None

            # --- Generate Copy (text content) ---
            copy_prompt = f"""
            Create branding content for a company named {brand_name} with slogan '{slogan}'.
            Theme color: {theme_color}, Style: {brand_style}.
            Include:
            1. About Us (short paragraph).
            2. Tagline suggestions (3).
            3. Social media post examples (2).
            """
            try:
                copy_response = text_client.text_generation(copy_prompt, max_new_tokens=500)
                copy_text = copy_response.generated_text
                st.text_area("Generated Branding Copy:", copy_text, height=300)
            except Exception as e:
                st.error(f"Text generation failed: {e}")
                copy_text = "Brand copy could not be generated."

            # --- Generate PDF Brand Kit ---
            pdf_buffer = io.BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=A4)
            width, height = A4

            c.setFont("Helvetica-Bold", 20)
            c.drawString(50, height - 50, f"{brand_name} - Brand Identity Kit")

            if logo_img:
                c.drawImage(logo_img, 50, height - 250, width=200, height=200, mask="auto")

            c.setFont("Helvetica", 12)
            text_object = c.beginText(50, height - 300)
            for line in copy_text.split("\n"):
                text_object.textLine(line)
            c.drawText(text_object)

            c.save()
            pdf_buffer.seek(0)

            st.download_button(
                "📥 Download Brand Kit PDF",
                data=pdf_buffer,
                file_name=f"{brand_name}_brand_kit.pdf",
                mime="application/pdf"
            )
