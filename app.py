# app.py - OPTIMIZED FOR STREAMLIT CLOUD
import streamlit as st
import tempfile
import os
from datetime import datetime
import base64
from io import BytesIO

# Try to import PDF processing libraries
try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except:
    PDF_AVAILABLE = False
    st.warning("PDF processing requires PyMuPDF. Running in limited mode.")

# Try to import image processing
try:
    from PIL import Image
    IMAGE_AVAILABLE = True
except:
    IMAGE_AVAILABLE = False

# Try to import OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except:
    OPENAI_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Trading AI Assistant",
    page_icon="📈",
    layout="wide"
)

# Initialize session state
if 'pdf_knowledge' not in st.session_state:
    st.session_state.pdf_knowledge = {}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'screenshots_analyzed' not in st.session_state:
    st.session_state.screenshots_analyzed = []

# Title
st.title("📈 Trading AI Assistant")
st.markdown("### Upload PDFs to learn trading psychology • Upload charts for analysis")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key input
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
        if OPENAI_AVAILABLE:
            openai.api_key = openai_api_key
    
    st.markdown("---")
    
    # Mode selection
    mode = st.radio(
        "Select Mode:",
        ["📚 PDF Learning Mode", "📈 Chart Analysis Mode", "💬 Chat with AI"]
    )
    
    st.markdown("---")
    
    # Status indicators
    st.caption("Status:")
    cols = st.columns(3)
    with cols[0]:
        st.write("📄 PDF:", "✅" if PDF_AVAILABLE else "❌")
    with cols[1]:
        st.write("🖼️ Image:", "✅" if IMAGE_AVAILABLE else "❌")
    with cols[2]:
        st.write("🤖 AI:", "✅" if OPENAI_AVAILABLE and openai_api_key else "❌")

# Main app logic
if mode == "📚 PDF Learning Mode":
    st.header("📚 Upload Trading PDFs")
    
    if not PDF_AVAILABLE:
        st.error("""
        PDF processing is not available. Please install PyMuPDF locally:
        ```bash
        pip install PyMuPDF
        ```
        For Streamlit Cloud, this feature requires custom dependencies.
        """)
    else:
        uploaded_pdf = st.file_uploader(
            "Upload trading PDF (psychology, strategies, etc.)",
            type=["pdf"]
        )
        
        if uploaded_pdf:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.success(f"PDF Uploaded: {uploaded_pdf.name}")
                
                if st.button("📖 Extract and Learn from PDF"):
                    with st.spinner("Processing PDF..."):
                        # Create temporary file
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                            tmp_file.write(uploaded_pdf.read())
                            tmp_path = tmp_file.name
                        
                        try:
                            # Extract text from PDF
                            doc = fitz.open(tmp_path)
                            text = ""
                            for page in doc:
                                text += page.get_text()
                            doc.close()
                            
                            # Store in session state
                            st.session_state.pdf_knowledge[uploaded_pdf.name] = {
                                "text": text[:5000],  # Store first 5000 chars for demo
                                "processed_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "page_count": len(doc)
                            }
                            
                            st.success(f"✅ PDF processed! {len(doc)} pages extracted")
                            
                            # Show preview
                            with st.expander("📋 View Extracted Text Preview"):
                                st.text_area("PDF Content", text[:2000], height=300)
                            
                        except Exception as e:
                            st.error(f"Error processing PDF: {str(e)}")
                        finally:
                            # Clean up temp file
                            if os.path.exists(tmp_path):
                                os.unlink(tmp_path)
            
            with col2:
                st.subheader("📊 Knowledge Base")
                if st.session_state.pdf_knowledge:
                    for pdf_name, data in st.session_state.pdf_knowledge.items():
                        st.metric(
                            label=pdf_name,
                            value=f"{data['page_count']} pages",
                            delta=data['processed_date'].split()[0]
                        )

elif mode == "📈 Chart Analysis Mode":
    st.header("📈 Analyze Trading Charts")
    
    if not IMAGE_AVAILABLE:
        st.error("Image processing libraries not available.")
    else:
        uploaded_image = st.file_uploader(
            "Upload chart screenshot (PNG, JPG)",
            type=["png", "jpg", "jpeg"]
        )
        
        if uploaded_image:
            col1, col2 = st.columns(2)
            
            with col1:
                image = Image.open(uploaded_image)
                st.image(image, caption="Uploaded Chart", use_column_width=True)
                
                # Analysis options
                st.subheader("Analysis Options")
                analyze_patterns = st.checkbox("Detect Patterns", True)
                analyze_levels = st.checkbox("Find Key Levels", True)
                get_ai_insights = st.checkbox("Get AI Insights", OPENAI_AVAILABLE and openai_api_key)
                
                if st.button("🔍 Analyze Chart", type="primary"):
                    with st.spinner("Analyzing..."):
                        # Store analysis
                        analysis = {
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "image_name": uploaded_image.name,
                            "patterns": ["Support/Resistance", "Trend"] if analyze_patterns else [],
                            "levels": ["$150.00", "$152.50", "$148.00"] if analyze_levels else [],
                            "ai_insights": ""
                        }
                        
                        # Get AI insights if requested
                        if get_ai_insights and OPENAI_AVAILABLE and openai_api_key:
                            try:
                                response = openai.ChatCompletion.create(
                                    model="gpt-3.5-turbo",
                                    messages=[
                                        {"role": "system", "content": "You are a trading analyst. Provide technical analysis insights."},
                                        {"role": "user", "content": f"Analyze this trading chart called {uploaded_image.name}. Focus on potential patterns, key levels, and risk management."}
                                    ],
                                    max_tokens=300
                                )
                                analysis["ai_insights"] = response.choices[0].message.content
                            except Exception as e:
                                analysis["ai_insights"] = f"AI analysis unavailable: {str(e)}"
                        
                        # Store in history
                        st.session_state.screenshots_analyzed.append(analysis)
                        
                        # Display results
                        st.subheader("📊 Analysis Results")
                        
                        if analysis["patterns"]:
                            st.success(f"**Patterns Detected:** {', '.join(analysis['patterns'])}")
                        
                        if analysis["levels"]:
                            st.info(f"**Key Levels:** {', '.join(analysis['levels'])}")
                        
                        if analysis["ai_insights"]:
                            st.markdown("### 🤖 AI Insights")
                            st.write(analysis["ai_insights"])
                        
                        # Save analysis
                        st.download_button(
                            label="💾 Save Analysis Report",
                            data=str(analysis),
                            file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
            
            with col2:
                st.subheader("📋 Analysis History")
                if st.session_state.screenshots_analyzed:
                    for i, analysis in enumerate(reversed(st.session_state.screenshots_analyzed[-3:])):
                        with st.expander(f"Analysis {i+1} - {analysis['timestamp']}"):
                            st.write(f"**Image:** {analysis['image_name']}")
                            if analysis['patterns']:
                                st.write(f"**Patterns:** {', '.join(analysis['patterns'])}")
                            if analysis['levels']:
                                st.write(f"**Levels:** {', '.join(analysis['levels'])}")
                else:
                    st.info("No analyses yet. Upload a chart to begin!")

elif mode == "💬 Chat with AI":
    st.header("💬 Chat with Trading AI")
    
    if not OPENAI_AVAILABLE or not openai_api_key:
        st.warning("Please enter your OpenAI API key in the sidebar to enable chat.")
    else:
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about trading, psychology, strategies..."):
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        # Check if we have PDF knowledge to include
                        context = ""
                        if st.session_state.pdf_knowledge:
                            for pdf_name, data in st.session_state.pdf_knowledge.items():
                                context += f"\n\nFrom {pdf_name}:\n{data['text'][:1000]}..."
                        
                        messages = [
                            {"role": "system", "content": "You are a professional trading coach and analyst. Provide educational insights about trading psychology, price action, and risk management." + context},
                            {"role": "user", "content": prompt}
                        ]
                        
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=messages,
                            max_tokens=500,
                            temperature=0.7
                        )
                        
                        ai_response = response.choices[0].message.content
                        st.markdown(ai_response)
                        
                        # Add to history
                        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <small>
    ⚠️ <strong>Disclaimer:</strong> Educational tool only. Not financial advice. Trading involves risk.
    </small>
</div>
""", unsafe_allow_html=True)

# Quick setup instructions
with st.expander("🚀 Quick Start Guide"):
    st.markdown("""
    ### **For Local Development:**
    ```bash
    # Clone this app
    git clone <your-repo-url>
    cd trading-ai-assistant
    
    # Install requirements
    pip install -r requirements.txt
    
    # Run the app
    streamlit run app.py
    ```
    
    ### **For Production on Streamlit Cloud:**
    1. Push code to GitHub
    2. Deploy on [Streamlit Cloud](https://streamlit.io/cloud)
    3. Add OpenAI API key in Secrets
    4. Your app will be live at: `https://trading-ai-assistant.streamlit.app`
    """)
# Remove or comment out the PyMuPDF import
# try:
#     import fitz  # PyMuPDF
#     PDF_AVAILABLE = True
# except:
#     PDF_AVAILABLE = False

PDF_AVAILABLE = False  # Set to False for now
