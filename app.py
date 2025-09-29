import streamlit as st
import google.generativeai as genai
from PIL import Image
import io, zipfile, os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from huggingface_hub import InferenceClient

# ------------------------------
# 1. Gemini Setup (Text Generation)
# ------------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# ------------------------------
# 2. Hugging Face Setup (Image Generation)
# ------------------------------
HF_TOKEN = st.secrets["HF_API_KEY"]
image_client = InferenceClient("black-forest-labs/FLUX.1-Krea-dev", token=HF_TOKEN)

# ------------------------------
# 3. Streamlit UI
# ------------------------------
st.set_page_config(page_title="AI Brand Identity Creator", page_icon="🎨", layout="centered")
st.title("🎨 AI Brand Identity Creator")
st.write("Generate a complete brand kit (logo, tagline, mission, and brand guide) instantly with AI.")

# User Inputs
brand_name = st.text_input("Enter your Brand Name")
industry = st.text_input("Enter your Industry")
vibe = st.selectbox("Select your Brand Vibe", ["Luxury", "Fun", "Eco-Friendly", "Minimalist", "Techy"])
theme_color = st.color_picker("Pick your brand's theme color", "#000000")

# ------------------------------
# 4. Brand Kit Generation
# ------------------------------
if st.button("🚀 Generate Brand Kit"):
    if not brand_name or not industry:
        st.warning("⚠️ Please enter brand name and industry before generating.")
    else:
        with st.spinner("✨ Creating your brand kit... please wait"):

            # --- (A) Generate Brand Text Assets with Gemini ---
            text_prompt = f"""
            You are a brand strategist. Create a branding kit for a {vibe} brand.
            Brand Name: {brand_name}
            Industry: {industry}
            Provide:
            - A catchy tagline
            - A 2–3 sentence mission statement
            - A short brand story (4–5 sentences)
            """
            model = genai.GenerativeModel("gemini-2.5-flash")
            text_response = model.generate_content(text_prompt)
            brand_text = text_response.text

            st.subheader("📝 Brand Identity Text")
            st.write(brand_text)

            # --- (B) Generate AI Logo with FLUX ---
            st.subheader("🎨 Generated Logo")
            logo_img = None
            logo_prompt = (
                f"Minimal modern logo design for {brand_name}, {vibe} style, {industry} brand identity, "
                f"vector graphic, clean lines, primary color {theme_color}"
            )
            try:
                logo_img = image_client.text_to_image(logo_prompt)
                st.image(logo_img, caption=f"AI-Generated Logo ({theme_color})", use_container_width=True)
            except Exception as e:
                st.error(f"Image generation failed: {e}")

            # --- (C) Create a PDF Brand Guide with logo ---
            pdf_path = f"{brand_name}_brand_guide.pdf"
            c = canvas.Canvas(pdf_path, pagesize=letter)
            c.setFont("Helvetica-Bold", 18)
            c.drawString(100, 750, f"Brand Guide: {brand_name}")

            c.setFont("Helvetica", 12)
            c.drawString(100, 720, f"Industry: {industry}")
            c.drawString(100, 700, f"Vibe: {vibe}")
            c.drawString(100, 680, f"Theme Color: {theme_color}")
            c.drawString(100, 660, "---------------------------------------")

            # Add Logo to PDF
            if logo_img:
                img_bytes = io.BytesIO()
                logo_img.save(img_bytes, format="PNG")
                img_bytes.seek(0)
                c.drawImage(ImageReader(img_bytes), 100, 450, width=200, height=200)

            # Add Brand Text
            text_obj = c.beginText(100, 420)
            for line in brand_text.split("\n"):
                text_obj.textLine(line)
            c.drawText(text_obj)

            c.save()

            # --- (D) Package Everything into a ZIP File ---
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "a") as zip_file:
                zip_file.writestr("brand_text.txt", brand_text)
                if logo_img:
                    img_bytes = io.BytesIO()
                    logo_img.save(img_bytes, format="PNG")
                    zip_file.writestr("logo.png", img_bytes.getvalue())
                zip_file.write(pdf_path, os.path.basename(pdf_path))

            st.success("✅ Brand Kit Generated!")
            st.download_button(
                "📥 Download Brand Kit (ZIP)",
                zip_buffer.getvalue(),
                file_name=f"{brand_name}_kit.zip"
            )
