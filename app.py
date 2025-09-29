import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests, io, zipfile, os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# ------------------------------
# 1. Gemini Setup (Text Generation)
# ------------------------------
# You need to set your Gemini API key as a secret in Streamlit Cloud:
# st.secrets["GEMINI_API_KEY"]
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


            # --- (B) Generate AI Logo (Stable Diffusion from Hugging Face API) ---
            st.subheader("🎨 Generated Logo")
            logo_prompt = f"Minimal modern logo design for {brand_name}, {vibe} style, {industry} brand identity, vector graphic, clean lines"
            
            # Hugging Face Inference API endpoint (Stable Diffusion)
            HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
            headers = {"Authorization": f"Bearer {st.secrets['HF_API_KEY']}"}
            
            def query(payload):
                response = requests.post(HF_API_URL, headers=headers, json=payload)
                return response.content
            
            image_bytes = query({"inputs": logo_prompt})
            logo_img = Image.open(io.BytesIO(image_bytes))
            st.image(logo_img, caption="AI-Generated Logo", use_container_width=True)


            # --- (C) Generate a Color Palette (Simple Example) ---
            st.subheader("🎨 Suggested Color Palette")
            colors = ["#FF5733", "#33C1FF", "#75FF33", "#FFC733", "#9D33FF"]  # placeholder colors
            cols = st.columns(len(colors))
            for idx, col in enumerate(cols):
                col.markdown(f"<div style='background-color:{colors[idx]}; width:80px; height:40px; border-radius:5px'></div>", unsafe_allow_html=True)


            # --- (D) Create a PDF Brand Guide ---
            pdf_path = f"{brand_name}_brand_guide.pdf"
            c = canvas.Canvas(pdf_path, pagesize=letter)
            c.setFont("Helvetica-Bold", 18)
            c.drawString(100, 750, f"Brand Guide: {brand_name}")
            
            c.setFont("Helvetica", 12)
            c.drawString(100, 720, f"Industry: {industry}")
            c.drawString(100, 700, f"Vibe: {vibe}")
            c.drawString(100, 680, "---------------------------------------")
            
            text_obj = c.beginText(100, 650)
            for line in brand_text.split("\n"):
                text_obj.textLine(line)
            c.drawText(text_obj)
            c.save()


            # --- (E) Package Everything into a ZIP File ---
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "a") as zip_file:
                # Save brand text
                zip_file.writestr("brand_text.txt", brand_text)
                # Save logo image
                img_bytes = io.BytesIO()
                logo_img.save(img_bytes, format="PNG")
                zip_file.writestr("logo.png", img_bytes.getvalue())
                # Save PDF guide
                zip_file.write(pdf_path, os.path.basename(pdf_path))

            st.success("✅ Brand Kit Generated!")
            st.download_button("📥 Download Brand Kit (ZIP)", 
                               zip_buffer.getvalue(), 
                               file_name=f"{brand_name}_kit.zip")
