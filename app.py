import streamlit as st
from PIL import Image
import io, zipfile, os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from huggingface_hub import InferenceClient

# ------------------------------
# 1. Hugging Face Setup
# ------------------------------
HF_TOKEN = st.secrets["HF_API_KEY"]

# Hugging Face models (free)
IMAGE_MODEL = "stabilityai/stable-diffusion-2-1-base"
TEXT_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

# Clients
image_client = InferenceClient(IMAGE_MODEL, token=HF_TOKEN)
text_client = InferenceClient(TEXT_MODEL, token=HF_TOKEN)

# ------------------------------
# 2. Streamlit UI
# ------------------------------
st.set_page_config(page_title="AI Brand Identity Creator", page_icon="🎨", layout="centered")
st.title("🎨 AI Brand Identity Creator")
st.write("Generate a complete brand kit (logo, tagline, mission, and brand guide) instantly with AI.")

# User Inputs
brand_name = st.text_input("Enter your Brand Name")
industry = st.text_input("Enter your Industry")
vibe = st.selectbox("Select your Brand Vibe", ["Luxury", "Fun", "Eco-Friendly", "Minimalist", "Techy"])
theme_color = st.color_picker("Pick a theme color for your brand", "#FF5733")

# ------------------------------
# 3. Brand Kit Generation
# ------------------------------
if st.button("🚀 Generate Brand Kit"):
    if not brand_name or not industry:
        st.warning("⚠️ Please enter brand name and industry before generating.")
    else:
        with st.spinner("✨ Creating your brand kit... please wait"):

            # --- (A) Generate Brand Text Assets ---
            copy_prompt = f"""
            You are a professional brand strategist. Create a branding kit for a {vibe} brand.
            Brand Name: {brand_name}
            Industry: {industry}
            Provide:
            - A catchy tagline
            - A 2–3 sentence mission statement
            - A short brand story (4–5 sentences)
            """

            try:
                copy_response = text_client.text_generation(
                    prompt=copy_prompt,
                    max_new_tokens=400,
                    temperature=0.7
                )
                brand_text = copy_response
            except Exception as e:
                st.error(f"Text generation failed: {e}")
                brand_text = "Error: No branding text generated."

            # Show text output
            st.subheader("📝 Brand Identity Text")
            st.write(brand_text)

            # --- (B) Generate AI Logo ---
            st.subheader("🎨 Generated Logo")
            logo_prompt = f"Minimal modern logo design for {brand_name}, {vibe} style, {industry} industry, theme color {theme_color}, flat vector, clean lines"

            try:
                image_bytes = image_client.text_to_image(prompt=logo_prompt)
                logo_img = Image.open(io.BytesIO(image_bytes))
                st.image(logo_img, caption="AI-Generated Logo", use_container_width=True)
            except Exception as e:
                st.error(f"Logo generation failed: {e}")
                logo_img = None

            # --- (C) Color Palette ---
            st.subheader("🎨 Suggested Color Palette")
            colors = [theme_color, "#33C1FF", "#75FF33", "#FFC733", "#9D33FF"]
            cols = st.columns(len(colors))
            for idx, col in enumerate(cols):
                col.markdown(
                    f"<div style='background-color:{colors[idx]}; width:80px; height:40px; border-radius:5px'></div>",
                    unsafe_allow_html=True
                )

            # --- (D) Create PDF Guide ---
            pdf_path = f"{brand_name}_brand_guide.pdf"
            c = canvas.Canvas(pdf_path, pagesize=letter)
            c.setFont("Helvetica-Bold", 18)
            c.drawString(100, 750, f"Brand Guide: {brand_name}")

            # Insert logo in PDF if available
            if logo_img:
                img_reader = ImageReader(logo_img)
                c.drawImage(img_reader, 100, 600, width=120, height=120, mask='auto')

            c.setFont("Helvetica", 12)
            c.drawString(100, 570, f"Industry: {industry}")
            c.drawString(100, 550, f"Vibe: {vibe}")
            c.drawString(100, 530, f"Theme Color: {theme_color}")
            c.drawString(100, 510, "---------------------------------------")

            text_obj = c.beginText(100, 490)
            for line in brand_text.split("\n"):
                text_obj.textLine(line)
            c.drawText(text_obj)
            c.save()

            # --- (E) Package Everything ---
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "a") as zip_file:
                # Save branding text
                zip_file.writestr("brand_text.txt", brand_text)
                # Save logo
                if logo_img:
                    img_bytes = io.BytesIO()
                    logo_img.save(img_bytes, format="PNG")
                    zip_file.writestr("logo.png", img_bytes.getvalue())
                # Save PDF
                zip_file.write(pdf_path, os.path.basename(pdf_path))

            st.success("✅ Brand Kit Generated!")
            st.download_button(
                "📥 Download Brand Kit (ZIP)",
                zip_buffer.getvalue(),
                file_name=f"{brand_name}_kit.zip"
            )
