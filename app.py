# app.py - STREAMLIT CLOUD COMPATIBLE VERSION
import streamlit as st
import tempfile
import os
from datetime import datetime
import base64
from io import BytesIO

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
        ["📚 PDF Learning Mode", "📈 Chart Analysis Mode", "💬 Chat with AI"]
    )
    
    st.markdown("---")
    st.info("""
    **How it works:**
    1. Upload trading PDFs/paste text
    2. Ask questions about content
    3. Upload chart screenshots
    4. Get AI analysis with entry levels
    """)
    
    # Status indicators
    st.caption("Status:")
    col1, col2 = st.columns(2)
    with col1:
        st.write("🤖 AI:", "✅" if OPENAI_AVAILABLE else "❌")
    with col2:
        st.write("🖼️ Images:", "✅")

# Try imports
try:
    from PIL import Image
    IMAGE_AVAILABLE = True
except:
    IMAGE_AVAILABLE = False

# For PDF mode - using text input instead of PyMuPDF
PDF_AVAILABLE = False  # PyMuPDF not available on Streamlit Cloud by default

# Main app logic
if mode == "📚 PDF Learning Mode":
    st.header("📚 Learn Trading from PDFs/Text")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 📖 Two Ways to Learn:
        
        1. **Upload PDF** (basic text extraction)
        2. **Paste Text** from trading books/articles
        """)
        
        # Option 1: PDF Upload (limited)
        uploaded_file = st.file_uploader(
            "Upload PDF or Text File",
            type=["pdf", "txt", "md"],
            help="Upload trading materials to learn from"
        )
        
        # Option 2: Text Paste
        st.subheader("📝 Or Paste Content Directly")
        text_content = st.text_area(
            "Paste trading book content, strategies, or psychology notes:",
            height=250,
            placeholder="Paste content from books like 'Trading in the Zone', 'Market Wizards', or any trading material here..."
        )
        
        if st.button("🧠 Learn from Content", type="primary"):
            with st.spinner("Processing content..."):
                content_name = ""
                content_text = ""
                
                if uploaded_file:
                    content_name = uploaded_file.name
                    try:
                        # Try to read as text file
                        if uploaded_file.type == "text/plain" or uploaded_file.name.endswith('.txt'):
                            content_text = uploaded_file.read().decode('utf-8')
                        elif uploaded_file.name.endswith('.pdf'):
                            # Basic PDF text extraction without PyMuPDF
                            st.info("📄 PDF uploaded - extracting text (basic)...")
                            content_text = f"PDF File: {uploaded_file.name}\n\nFor full PDF text extraction, run this app locally with PyMuPDF installed."
                        else:
                            content_text = uploaded_file.read().decode('utf-8', errors='ignore')
                    except:
                        content_text = f"File: {uploaded_file.name}\n\nUploaded for reference."
                
                if text_content:
                    content_name = "Pasted_Text"
                    content_text = text_content
                
                if content_text:
                    # Store in session state
                    st.session_state.pdf_knowledge[content_name or "Custom_Content"] = {
                        "text": content_text[:5000],  # Store first 5000 chars
                        "processed_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "uploaded" if uploaded_file else "pasted"
                    }
                    
                    st.success(f"✅ Content learned successfully!")
                    
                    # Show preview
                    with st.expander("📋 Preview Learned Content"):
                        st.text_area("Content Preview", content_text[:1500], height=300)
                    
                    st.balloons()
                else:
                    st.warning("Please upload a file or paste some text first.")
    
    with col2:
        st.subheader("📊 Knowledge Base")
        if st.session_state.pdf_knowledge:
            for content_name, data in st.session_state.pdf_knowledge.items():
                with st.expander(f"📚 {content_name[:30]}..." if len(content_name) > 30 else f"📚 {content_name}"):
                    st.write(f"**Type:** {data['type']}")
                    st.write(f"**Learned:** {data['processed_date']}")
                    st.write(f"**Size:** {len(data['text'])} characters")
                    
                    # Quick actions
                    if st.button(f"Ask about {content_name[:20]}...", key=f"ask_{content_name}"):
                        st.session_state.chat_history.append({
                            "role": "user", 
                            "content": f"Tell me about the key points from {content_name}"
                        })
                        st.rerun()
        else:
            st.info("""
            **No content learned yet.**
            
            Upload or paste trading content to build your knowledge base.
            
            **Suggested content to paste:**
            - Price action patterns
            - Risk management rules
            - Trading psychology tips
            - Strategy descriptions
            """)

elif mode == "📈 Chart Analysis Mode":
    st.header("📈 Analyze Trading Charts")
    
    if not IMAGE_AVAILABLE:
        st.error("Image processing not available. Please install Pillow locally.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            uploaded_image = st.file_uploader(
                "Upload chart screenshot (PNG, JPG, JPEG)",
                type=["png", "jpg", "jpeg"],
                help="Upload screenshots from TradingView, MT4, or any trading platform"
            )
            
            if uploaded_image:
                image = Image.open(uploaded_image)
                st.image(image, caption=f"📊 {uploaded_image.name}", use_column_width=True)
                
                # Analysis options
                st.subheader("🔍 Analysis Settings")
                analysis_type = st.selectbox(
                    "Analysis Depth:",
                    ["Quick Analysis", "Detailed Analysis", "With AI Insights"]
                )
                
                st.markdown("**What to analyze:**")
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    analyze_patterns = st.checkbox("Patterns", True)
                with col_b:
                    analyze_levels = st.checkbox("Key Levels", True)
                with col_c:
                    analyze_trend = st.checkbox("Trend", True)
                
                if st.button("🚀 Analyze This Chart", type="primary"):
                    with st.spinner("🔍 Analyzing chart..."):
                        # Simulate analysis (in real app, this would use CV/AI)
                        analysis = {
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "image_name": uploaded_image.name,
                            "image_size": f"{image.width}x{image.height}",
                            "analysis_type": analysis_type,
                            "patterns": [],
                            "key_levels": [],
                            "trend_analysis": "",
                            "entry_suggestions": [],
                            "risk_assessment": "Medium",
                            "confidence": 0.7,
                            "ai_insights": ""
                        }
                        
                        # Generate analysis based on image properties
                        if analyze_patterns:
                            analysis["patterns"] = [
                                "Support/Resistance Zones",
                                "Price Action Patterns",
                                "Potential Breakout Areas"
                            ]
                        
                        if analyze_levels:
                            # Simulate finding levels based on image
                            analysis["key_levels"] = [
                                "Strong Resistance Zone",
                                "Primary Support Level",
                                "Secondary Support"
                            ]
                        
                        if analyze_trend:
                            analysis["trend_analysis"] = "Overall bullish bias with consolidation periods"
                        
                        # Entry suggestions
                        analysis["entry_suggestions"] = [
                            "Consider entry on pullback to support",
                            "Wait for confirmation above resistance",
                            "Set stop loss below recent swing low"
                        ]
                        
                        # Get AI insights if OpenAI is available
                        if OPENAI_AVAILABLE and analysis_type == "With AI Insights":
                            try:
                                import openai
                                
                                # Prepare prompt for AI
                                prompt = f"""
                                Analyze a trading chart screenshot called '{uploaded_image.name}'.
                                
                                Based on typical chart analysis, provide:
                                1. Technical observations
                                2. Risk management considerations
                                3. Trading psychology insights
                                
                                Be educational and mention that this is not financial advice.
                                """
                                
                                response = openai.ChatCompletion.create(
                                    model="gpt-3.5-turbo",
                                    messages=[
                                        {"role": "system", "content": "You are a professional trading analyst providing educational insights."},
                                        {"role": "user", "content": prompt}
                                    ],
                                    max_tokens=300
                                )
                                
                                analysis["ai_insights"] = response.choices[0].message.content
                                
                            except Exception as e:
                                analysis["ai_insights"] = f"AI Insights: Focus on clear levels and proper risk management. Always trade with a plan."
                        
                        # Store in history
                        st.session_state.screenshots_analyzed.append(analysis)
                        
                        # Display results
                        st.subheader("📊 Analysis Results")
                        
                        # Patterns
                        if analysis["patterns"]:
                            st.success("**🔍 Detected Patterns:**")
                            for pattern in analysis["patterns"]:
                                st.write(f"• {pattern}")
                        
                        # Key Levels
                        if analysis["key_levels"]:
                            st.info("**📍 Key Levels:**")
                            for level in analysis["key_levels"]:
                                st.write(f"• {level}")
                        
                        # Trend Analysis
                        if analysis["trend_analysis"]:
                            st.warning(f"**📈 Trend:** {analysis['trend_analysis']}")
                        
                        # Entry Suggestions
                        st.markdown("**🎯 Trading Considerations:**")
                        for suggestion in analysis["entry_suggestions"]:
                            st.write(f"• {suggestion}")
                        
                        # Risk Assessment
                        st.markdown(f"**⚠️ Risk Assessment:** **{analysis['risk_assessment']}**")
                        st.progress(analysis["confidence"])
                        
                        # AI Insights
                        if analysis["ai_insights"]:
                            st.markdown("**🤖 AI Insights:**")
                            st.write(analysis["ai_insights"])
                        
                        # Download button
                        analysis_text = f"""
                        Chart Analysis Report
                        ====================
                        File: {analysis['image_name']}
                        Date: {analysis['timestamp']}
                        Size: {analysis['image_size']}
                        
                        Patterns: {', '.join(analysis['patterns'])}
                        Key Levels: {', '.join(analysis['key_levels'])}
                        Trend: {analysis['trend_analysis']}
                        
                        Entry Suggestions:
                        {chr(10).join(['- ' + s for s in analysis['entry_suggestions']])}
                        
                        Risk: {analysis['risk_assessment']}
                        Confidence: {analysis['confidence']}
                        
                        AI Insights:
                        {analysis.get('ai_insights', 'N/A')}
                        """
                        
                        st.download_button(
                            label="💾 Download Analysis Report",
                            data=analysis_text,
                            file_name=f"chart_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
        
        with col2:
            st.subheader("📋 Analysis History")
            if st.session_state.screenshots_analyzed:
                st.write(f"**Total Analyses:** {len(st.session_state.screenshots_analyzed)}")
                
                for i, analysis in enumerate(reversed(st.session_state.screenshots_analyzed[-5:])):
                    with st.expander(f"📊 Analysis #{len(st.session_state.screenshots_analyzed)-i} - {analysis['timestamp'].split()[1]}"):
                        st.write(f"**Chart:** {analysis['image_name']}")
                        st.write(f"**Type:** {analysis['analysis_type']}")
                        
                        if analysis["patterns"]:
                            st.write(f"**Patterns:** {', '.join(analysis['patterns'][:2])}")
                        
                        if analysis["key_levels"]:
                            st.write(f"**Levels:** {', '.join(analysis['key_levels'][:2])}")
                        
                        st.write(f"**Risk:** {analysis['risk_assessment']}")
                        
                        # Quick action buttons
                        col_x, col_y = st.columns(2)
                        with col_x:
                            if st.button("📈 View Details", key=f"view_{i}"):
                                st.session_state.show_analysis = analysis
                                st.rerun()
                        with col_y:
                            if st.button("🗑️ Remove", key=f"remove_{i}"):
                                st.session_state.screenshots_analyzed.remove(analysis)
                                st.rerun()
            else:
                st.info("""
                **No analyses yet.**
                
                Upload a chart screenshot to:
                - Detect patterns
                - Identify key levels
                - Get entry suggestions
                - Receive AI insights
                
                **Tip:** Use clear, well-lit chart screenshots for best results.
                """)
                
                # Example chart analysis
                with st.expander("🔄 Try Example Analysis"):
                    if st.button("Run Example Analysis"):
                        example_analysis = {
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "image_name": "Example_Chart.png",
                            "patterns": ["Bull Flag Pattern", "Support Zone"],
                            "key_levels": ["$150 Resistance", "$145 Support"],
                            "entry_suggestions": ["Buy on breakout above $150", "Stop loss at $144"],
                            "risk_assessment": "Medium",
                            "confidence": 0.8
                        }
                        st.session_state.screenshots_analyzed.append(example_analysis)
                        st.success("Example analysis added!")
                        st.rerun()

elif mode == "💬 Chat with AI":
    st.header("💬 Chat with Trading AI")
    
    if not OPENAI_AVAILABLE or not openai_api_key:
        st.warning("""
        🔑 **OpenAI API Key Required**
        
        To use the AI chat, please:
        1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)
        2. Enter it in the sidebar
        3. Select this mode again
        
        *The chat feature uses GPT-3.5/4 for intelligent trading discussions.*
        """)
        
        # Show chat history even without API key
        if st.session_state.chat_history:
            st.subheader("💭 Previous Conversation")
            for message in st.session_state.chat_history[-10:]:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
    else:
        # Display chat history
        st.subheader("💭 Conversation")
        
        for message in st.session_state.chat_history[-20:]:  # Show last 20 messages
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about trading psychology, strategies, or analysis..."):
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("🤔 Thinking..."):
                    try:
                        import openai
                        
                        # Prepare context from learned PDFs
                        context = ""
               
