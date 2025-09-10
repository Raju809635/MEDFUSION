import streamlit as st
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import io

st.title("🔍 OCR Test - MedFusion")

st.markdown("### Test OCR functionality with your PDF")

uploaded_file = st.file_uploader("Upload a scanned PDF for OCR", type=['pdf'])

if uploaded_file is not None:
    st.success("✅ PDF uploaded successfully!")
    
    if st.button("🔍 Extract Text with OCR"):
        try:
            with st.spinner("Processing PDF with OCR..."):
                # Convert PDF to images
                images = convert_from_bytes(uploaded_file.getvalue())
                
                extracted_text = ""
                for page_num, image in enumerate(images):
                    # Use OCR to extract text
                    page_text = pytesseract.image_to_string(image, config='--psm 6')
                    if page_text.strip():
                        extracted_text += f"--- Page {page_num + 1} ---\n{page_text}\n\n"
                
                if extracted_text.strip():
                    st.success("✅ OCR extraction successful!")
                    st.markdown("### 📄 Extracted Text:")
                    st.text_area("OCR Results", extracted_text, height=400)
                else:
                    st.warning("⚠️ No text could be extracted from the PDF")
                    
        except Exception as e:
            error_msg = str(e)
            if "poppler" in error_msg.lower():
                st.error("❌ Poppler not installed!")
                st.markdown("""
                **To install Poppler:**
                1. Download from: https://github.com/oschwartz10612/poppler-windows/releases/
                2. Extract to: `C:\\poppler`
                3. Add to PATH: `C:\\poppler\\bin`
                4. Restart your computer
                """)
            else:
                st.error(f"❌ OCR Error: {error_msg}")

st.markdown("---")
st.info("💡 This is a test page to verify OCR functionality. Once working, your main app will have full OCR support!")
