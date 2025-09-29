import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests, io, zipfile, os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

# ------------------------------
# 1. Gemini Setup (Text Generation)
# ------------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

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

# ------------------------------
# 3. Brand Kit Generation
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

            # Show text output in UI
            st.subheader("📝 Brand Identity Text")
            st.write(brand_text)

            # --- (B) Generate AI Logo with Hugging Face FLUX ---
            st.subheader("🎨 Generated Logo")
            logo_prompt = f"Minimal modern logo design for {brand_name}, {vibe} style, {industry} brand identity, vector graphic, clean lines"

            HF_API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-Krea-dev"
            headers = {"Authorization": f"Bearer {st.secrets['HF_API_KEY']}"}

            def query(payload):
                response = requests.post(HF_API_URL, headers=headers, json=payload)
                if response.status_code != 200:
                    st.error(f"Error {response.status_code}: {response.text}")
                    return None
                return response.content

            image_bytes = query({"inputs": logo_prompt})
            logo_img = None
            if image_bytes:
                logo_img = Image.open(io.BytesIO(image_bytes))
                st.image(logo_img, caption="AI-Generated Logo", use_container_width=True)

            # --- (C) Generate a Color Palette (Simple Example) ---
            st.subheader("🎨 Suggested Color Palette")
            colors = ["#FF5733", "#33C1FF", "#75FF33", "#FFC733", "#9D33FF"]  # placeholder colors
            cols = st.columns(len(colors))
            for idx, col in enumerate(cols):
                col.markdown(f"<div style='background-color:{colors[idx]}; width:80px; height:40px; border-radius:5px'></div>", unsafe_allow_html=True)

            # --- (D) Create a Professional PDF Brand Guide ---
            pdf_path = f"{brand_name}_brand_guide.pdf"
            c = canvas.Canvas(pdf_path, pagesize=letter)

            # Cover Page
            if logo_img:
                img_bytes = io.BytesIO()
                logo_img.save(img_bytes, format="PNG")
                img_bytes.seek(0)
                c.drawImage(ImageReader(img_bytes), 200, 600, width=200, height=200)

            c.setFont("Helvetica-Bold", 22)
            c.drawCentredString(300, 550, f"Brand Guide: {brand_name}")

            c.setFont("Helvetica", 14)
            c.drawCentredString(300, 520, f"Industry: {industry}")
            c.drawCentredString(300, 500, f"Vibe: {vibe}")
            c.showPage()

            # Content Page
            c.setFont("Helvetica-Bold", 18)
            c.drawString(50, 750, "Brand Identity")

            y = 720
            c.setFont("Helvetica", 12)
            for section in brand_text.split("\n"):
                c.drawString(50, y, section.strip())
                y -= 20

            c.save()

            # --- (E) Package Everything into a ZIP File ---
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "a") as zip_file:
                zip_file.writestr("brand_text.txt", brand_text)
                if logo_img:
                    img_bytes = io.BytesIO()
                    logo_img.save(img_bytes, format="PNG")
                    zip_file.writestr("logo.png", img_bytes.getvalue())
                zip_file.write(pdf_path, os.path.basename(pdf_path))

            st.success("✅ Brand Kit Generated!")
            st.download_button("📥 Download Brand Kit (ZIP)",
                               zip_buffer.getvalue(),
                               file_name=f"{brand_name}_kit.zip")
