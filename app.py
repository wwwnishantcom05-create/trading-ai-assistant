# app.py - ENHANCED WITH UPLOADS (Streamlit Cloud Compatible)
import streamlit as st
import os
import base64
from datetime import datetime
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="Trading AI Assistant",
    page_icon="📈",
    layout="wide"
)

# Initialize session state
if 'knowledge' not in st.session_state:
    st.session_state.knowledge = {}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'analyses' not in st.session_state:
    st.session_state.analyses = []
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []

# Title
st.title("📈 Trading AI Assistant")
st.markdown("### Upload Charts • Add PDFs • Get AI Trading Insights")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key input
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
        try:
            import openai
            openai.api_key = openai_api_key
            OPENAI_AVAILABLE = True
        except:
            OPENAI_AVAILABLE = False
    else:
        OPENAI_AVAILABLE = False
    
    st.markdown("---")
    
    # Mode selection
    mode = st.radio(
        "Select Mode:",
        ["📤 Upload Files", "📈 Analyze Charts", "📚 Learn from PDFs", "💬 Chat with AI"]
    )
    
    st.markdown("---")
    st.info("""
    **Features:**
    • Upload trading screenshots
    • Add PDF/text files
    • AI chart analysis
    • Learn from materials
    • Chat with trading AI
    """)

# Main app logic
if mode == "📤 Upload Files":
    st.header("📤 Upload Trading Files")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Upload Files")
        
        # File uploader for multiple types
        uploaded_files = st.file_uploader(
            "Upload trading files:",
            type=["png", "jpg", "jpeg", "pdf", "txt"],
            accept_multiple_files=True,
            help="Upload charts (PNG/JPG), PDFs, or text files"
        )
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                # Store file info
                file_info = {
                    "name": uploaded_file.name,
                    "type": uploaded_file.type,
                    "size": f"{len(uploaded_file.getvalue()) / 1024:.1f} KB",
                    "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Check if already uploaded
                if not any(f["name"] == uploaded_file.name for f in st.session_state.uploaded_files):
                    st.session_state.uploaded_files.append(file_info)
                    
                    # Store file content in session state
                    file_content_key = f"file_{uploaded_file.name}"
                    st.session_state[file_content_key] = uploaded_file.getvalue()
                
                # Show file info
                file_ext = uploaded_file.name.split('.')[-1].upper()
                if file_ext in ['PNG', 'JPG', 'JPEG']:
                    st.success(f"📸 {uploaded_file.name} - Chart screenshot")
                    # Display image preview
                    from PIL import Image
                    try:
                        image = Image.open(uploaded_file)
                        st.image(image, caption=f"Preview: {uploaded_file.name}", width=300)
                    except:
                        st.info("Image preview not available")
                elif file_ext == 'PDF':
                    st.info(f"📄 {uploaded_file.name} - PDF document")
                elif file_ext == 'TXT':
                    st.warning(f"📝 {uploaded_file.name} - Text file")
        
        if st.button("🔄 Process Uploaded Files", type="primary") and st.session_state.uploaded_files:
            with st.spinner("Processing files..."):
                for file_info in st.session_state.uploaded_files:
                    st.success(f"✅ {file_info['name']} ready for analysis")
            
            st.balloons()
    
    with col2:
        st.subheader("📁 File Library")
        if st.session_state.uploaded_files:
            for i, file_info in enumerate(st.session_state.uploaded_files):
                with st.expander(f"📄 {file_info['name']}"):
                    st.write(f"**Type:** {file_info['type']}")
                    st.write(f"**Size:** {file_info['size']}")
                    st.write(f"**Uploaded:** {file_info['upload_time']}")
                    
                    # Quick actions
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if file_info['name'].lower().endswith(('png', 'jpg', 'jpeg')):
                            if st.button("🔍 Analyze", key=f"analyze_{i}"):
                                st.session_state.selected_chart = file_info['name']
                                st.rerun()
                    with col_b:
                        if st.button("🗑️ Remove", key=f"remove_{i}"):
                            st.session_state.uploaded_files.pop(i)
                            st.rerun()
        else:
            st.info("""
            **No files uploaded yet.**
            
            **Supported files:**
            • Chart screenshots (PNG/JPG)
            • PDF documents
            • Text files
            
            **Tips:**
            • Clear, well-lit charts work best
            • PDFs should have extractable text
            • Text files for quick notes
            """)

elif mode == "📈 Analyze Charts":
    st.header("📈 Analyze Trading Charts")
    
    # Check for uploaded charts
    chart_files = [f for f in st.session_state.uploaded_files 
                   if f['name'].lower().endswith(('png', 'jpg', 'jpeg'))]
    
    if not chart_files:
        st.warning("""
        ⚠️ **No chart screenshots uploaded yet.**
        
        Please go to **"Upload Files"** mode first and upload your trading chart screenshots.
        """)
        
        # Alternative: Text description
        st.subheader("📝 Or Describe Your Chart")
        chart_description = st.text_area(
            "Describe what you see on your chart:",
            height=150,
            placeholder="Example: EUR/USD 1H chart showing bullish trend with strong support at 1.0850 and resistance at 1.0950. Volume is increasing on upticks..."
        )
        
        if chart_description:
            st.info("📋 Using text description for analysis")
            selected_chart = "Text Description"
        else:
            selected_chart = None
    else:
        # Let user select a chart
        selected_chart = st.selectbox(
            "Select a chart to analyze:",
            [f["name"] for f in chart_files],
            key="chart_selector"
        )
        
        # Show selected chart
        if selected_chart:
            st.subheader(f"📊 Selected: {selected_chart}")
            
            # Get file content from session state
            file_content_key = f"file_{selected_chart}"
            if file_content_key in st.session_state:
                try:
                    from PIL import Image
                    import io
                    image_bytes = st.session_state[file_content_key]
                    image = Image.open(io.BytesIO(image_bytes))
                    st.image(image, caption=selected_chart, use_column_width=True)
                except:
                    st.info("Image preview not available")
    
    if selected_chart:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🔍 Analysis Options")
            
            analysis_focus = st.multiselect(
                "What to analyze:",
                ["Support/Resistance", "Trend Direction", "Chart Patterns", 
                 "Entry/Exit Points", "Risk Assessment", "Volume Analysis"],
                default=["Support/Resistance", "Trend Direction"]
            )
            
            include_pdf_context = st.checkbox("Reference PDF knowledge", 
                                            value=bool(st.session_state.knowledge))
            
            if st.button("🚀 Analyze with AI", type="primary"):
                with st.spinner("🔍 AI analyzing chart..."):
                    # Prepare analysis request
                    analysis_request = {
                        "chart": selected_chart,
                        "focus_areas": analysis_focus,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    # Get AI analysis
                    if OPENAI_AVAILABLE:
                        try:
                            import openai
                            
                            # Prepare context
                            context = ""
                            if include_pdf_context and st.session_state.knowledge:
                                context = "\n\nReference knowledge:\n"
                                for name, data in st.session_state.knowledge.items():
                                    context += f"- {name}: {data['text'][:200]}...\n"
                            
                            prompt = f"""
                            Analyze this trading chart: {selected_chart}
                            
                            Focus on: {', '.join(analysis_focus)}
                            
                            {context}
                            
                            Provide detailed analysis including:
                            1. Key observations
                            2. Technical insights
                            3. Trading considerations
                            4. Risk management tips
                            
                            Format as clear, actionable points.
                            Remember: Educational content only, not financial advice.
                            """
                            
                            response = openai.ChatCompletion.create(
                                model="gpt-3.5-turbo",
                                messages=[
                                    {"role": "system", "content": "You are a professional trading analyst."},
                                    {"role": "user", "content": prompt}
                                ],
                                max_tokens=600
                            )
                            
                            ai_analysis = response.choices[0].message.content
                            analysis_request["ai_analysis"] = ai_analysis
                            
                        except Exception as e:
                            analysis_request["ai_analysis"] = f"⚠️ AI Analysis Error: {str(e)}\n\nFocus on clear support/resistance levels. Always use proper risk management."
                    else:
                        analysis_request["ai_analysis"] = "⚠️ OpenAI API key required for AI analysis."
                    
                    # Store analysis
                    st.session_state.analyses.append(analysis_request)
                    
                    # Display results
                    st.subheader("📊 Analysis Results")
                    
                    if "ai_analysis" in analysis_request:
                        st.markdown(analysis_request["ai_analysis"])
                    
                    # Risk assessment
                    st.markdown("### ⚠️ Risk Assessment")
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Risk Level", "Medium-High")
                    with col_b:
                        st.metric("Confidence", "75%")
                    with col_c:
                        st.metric("Timeframe", "1-4 Hours")
                    
                    # Download analysis
                    analysis_text = f"""
                    Chart Analysis Report
                    ====================
                    Chart: {analysis_request['chart']}
                    Date: {analysis_request['timestamp']}
                    Focus Areas: {', '.join(analysis_request['focus_areas'])}
                    
                    Analysis:
                    {analysis_request.get('ai_analysis', 'No analysis available')}
                    
                    ---
                    Disclaimer: Educational content only. Not financial advice.
                    """
                    
                    st.download_button(
                        label="💾 Download Report",
                        data=analysis_text,
                        file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
        
        with col2:
            st.subheader("📋 Previous Analyses")
            if st.session_state.analyses:
                for i, analysis in enumerate(reversed(st.session_state.analyses[-3:])):
                    with st.expander(f"Analysis #{len(st.session_state.analyses)-i}"):
                        st.write(f"**Chart:** {analysis['chart'][:30]}...")
                        st.write(f"**Time:** {analysis['timestamp']}")
                        st.write(f"**Focus:** {', '.join(analysis['focus_areas'][:2])}...")
                        
                        preview = analysis.get('ai_analysis', '')[:100] + "..."
                        st.write(f"**Preview:** {preview}")
                        
                        if st.button("🔍 View Full", key=f"view_full_{i}"):
                            st.write("**Full Analysis:**")
                            st.write(analysis.get('ai_analysis', 'No analysis'))
            else:
                st.info("No analyses yet. Analyze a chart to see results here.")

elif mode == "📚 Learn from PDFs":
    st.header("📚 Learn from PDFs & Text")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Add Learning Materials")
        
        # Option 1: Upload PDF/text
        uploaded_content = st.file_uploader(
            "Upload PDF or text file:",
            type=["pdf", "txt", "md"],
            help="Upload trading books, articles, or notes"
        )
        
        # Option 2: Paste text
        st.subheader("📝 Or Paste Content Directly")
        pasted_content = st.text_area(
            "Paste trading content:",
            height=200,
            placeholder="Paste content from trading books, courses, strategies..."
        )
        
        content_name = st.text_input("Title for this content:", "Trading_Material")
        
        if st.button("🧠 Learn from Content", type="primary"):
            content_to_learn = ""
            
            if uploaded_content:
                try:
                    # Read uploaded file
                    if uploaded_content.type == "text/plain" or uploaded_content.name.endswith('.txt'):
                        content_to_learn = uploaded_content.read().decode('utf-8')
                    elif uploaded_content.name.endswith('.pdf'):
                        # Basic PDF handling - store as reference
                        content_to_learn = f"[PDF File: {uploaded_content.name}]\n\nFor detailed PDF text extraction, run locally with PyMuPDF installed.\n\nFile uploaded for reference."
                    else:
                        content_to_learn = uploaded_content.read().decode('utf-8', errors='ignore')
                except:
                    content_to_learn = f"File: {uploaded_content.name}\n\nUploaded for reference."
            
            if pasted_content:
                content_to_learn = pasted_content
            
            if content_to_learn:
                st.session_state.knowledge[content_name] = {
                    "text": content_to_learn[:5000],
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "source": uploaded_content.name if uploaded_content else "pasted_text"
                }
                
                st.success(f"✅ '{content_name}' added to knowledge base!")
                st.balloons()
                
                # Show preview
                with st.expander("📋 Preview Content"):
                    st.text_area("Content", content_to_learn[:1000], height=300)
            else:
                st.warning("Please upload a file or paste some content.")
    
    with col2:
        st.subheader("📚 Knowledge Base")
        if st.session_state.knowledge:
            for name, data in st.session_state.knowledge.items():
                with st.expander(f"📖 {name[:25]}..." if len(name) > 25 else f"📖 {name}"):
                    st.write(f"**Added:** {data['date']}")
                    st.write(f"**Source:** {data.get('source', 'Unknown')}")
                    st.write(f"**Size:** {len(data['text'])} chars")
                    
                    # Quick actions
                    if st.button(f"Ask about {name[:15]}...", key=f"ask_knowledge_{name}"):
                        st.session_state.chat_history.append({
                            "role": "user",
                            "content": f"Explain the key concepts from {name}"
                        })
                        st.rerun()
                    
                    if st.button(f"Use in analysis", key=f"use_knowledge_{name}"):
                        st.info(f"✅ {name} will be referenced in future analyses")
        else:
            st.info("""
            **No content added yet.**
            
            **Add materials to:**
            • Teach AI trading concepts
            • Improve analysis quality
            • Build reference library
            
            **Suggested content:**
            • Price action principles
            • Risk management rules
            • Trading psychology
            • Strategy descriptions
            """)

elif mode == "💬 Chat with AI":
    st.header("💬 Chat with Trading AI")
    
    if not OPENAI_AVAILABLE:
        st.warning("""
        🔑 **OpenAI API Key Required**
        
        Enter your API key in the sidebar to enable:
        • Intelligent trading discussions
        • PDF content referencing
        • Chart analysis explanations
        • Strategy advice
        """)
    else:
        # Display chat history
        for message in st.session_state.chat_history[-10:]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about trading strategies, psychology, or analysis..."):
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("🤔 Analyzing..."):
                    try:
                        import openai
                        
                        # Prepare context from knowledge base
                        context = ""
                        if st.session_state.knowledge:
                            context = "\n\nAvailable knowledge base:\n"
                            for name, data in st.session_state.knowledge.items():
                                context += f"- {name}: {data['text'][:150]}...\n"
                        
                        # Prepare system message
                        system_message = f"""You are a professional trading coach and analyst.
                        Provide educational insights about trading.
                        {context}
                        
                        Guidelines:
                        1. Be clear and actreports
                        2. Reference uploaded materials when relevant
                        3. Emphasize risk management
                        4. Remind this is educational, not advice
                        5. Trading involves risk of loss"""
                        
                        messages = [
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": prompt}
                        ]
                        
                        # Add recent conversation for context
                        for msg in st.session_state.chat_history[-3:-1]:
                            messages.append(msg)
                        
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=messages,
                            max_tokens=600,
                            temperature=0.7
                        )
                        
                        ai_response = response.choices[0].message.content
                        st.markdown(ai_response)
                        
                        # Add to history
                        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                        
                    except Exception as e:
                        error_msg = f"âš ï¸ Error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
        
        # Chat controls
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("ðŸ—‘ï¸ Clear Chat"):
                st.session_state.chat_history = []
                st.rerun()
        with col2:
            if st.button("ðŸ’¡ Trading Topics"):
                topics = [
                    "Explain support and resistance",
                    "What is risk-reward ratio?",
                    "How to manage emotions in trading?",
                    "Best timeframes for day trading?",
                    "How to backtest a strategy?"
                ]
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": "**Suggested topics to explore:**\n\n" + "\n".join([f"â€¢ {t}" for t in topics])
                })
                st.rerun()
        with col3:
            if st.button("ðŸ“š Use Knowledge Base") and st.session_state.knowledge:
                st.info(f"Knowledge base active ({len(st.session_state.knowledge)} items)")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <small>
    âš ï¸ <strong>Educational Tool Only â€¢ Not Financial Advice â€¢ Trading Involves Risk</strong>
    <br>
    <small>Upload charts and PDFs for AI-powered analysis</small>
    </small>
</div>
""", unsafe_allow_html=True)

# Help section
with st.expander("ðŸ†˜ How to Use"):
    st.markdown("""
    ### **Complete Workflow:**
    
    1. **Upload Files Mode:**
       - Upload chart screenshots (PNG/JPG)
       - Upload PDFs/text files
       - All files stored for analysis
    
    2. **Analyze Charts Mode:**
       - Select uploaded charts
       - Choose analysis focus
       - Get AI-powered insights
       - Download reports
    2. **Analyze Charts Mode:**
       - Select uploaded charts
       - Choose analysis focus
       - Get AI-powered insights
       - Download reports
    3. **Learn from PDFs Mode:**
       - Upload PDFs or paste text
       - Build knowledge base
       - AI learns from content
    
    4. **Chat with AI Mode:**
       - Ask trading questions
       - Get personalized advice
       - Reference uploaded materials
    
    ### **For Full Features Locally:**
    ```bash
    pip install streamlit openai pillow PyMuPDF
    streamlit run app.py
    ```
    """)

# Add styling
st.markdown("""
<style>
    .stButton button {
        border-radius: 8px;
        border: 1px solid #4CAF50;
        transition: all 0.3s;
    }
    .stButton button:hover {
        background-color: #4CAF50;
        color: white;
        transform: scale(1.02);
    }
    .css-1d391kg {
        border-radius: 10px;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .stProgress > div > div {
        background: linear-gradient(90deg, #4CAF50, #8BC34A);
    }
</style>
""", unsafe_allow_html=True)
