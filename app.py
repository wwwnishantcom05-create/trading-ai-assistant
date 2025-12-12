# app.py - MINIMAL VERSION FOR STREAMLIT CLOUD
import streamlit as st
import os
from datetime import datetime

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

# Title
st.title("📈 Trading AI Assistant")
st.markdown("### Learn Trading • Analyze Charts • Get AI Insights")

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
        ["📚 Learn Trading", "📈 Chart Analysis", "💬 Chat with AI"]
    )
    
    st.markdown("---")
    st.info("""
    **Features:**
    1. Learn from trading content
    2. Get chart analysis
    3. AI-powered insights
    """)

# Main app logic
if mode == "📚 Learn Trading":
    st.header("📚 Learn Trading Concepts")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Add Trading Knowledge")
        
        # Text input for learning
        content = st.text_area(
            "Enter trading concepts, strategies, or psychology notes:",
            height=200,
            placeholder="Paste content from trading books, courses, or articles..."
        )
        
        content_name = st.text_input("Title for this content:", "Trading_Notes")
        
        if st.button("💾 Save for AI Learning", type="primary") and content:
            st.session_state.knowledge[content_name] = {
                "text": content[:3000],
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.success(f"✅ '{content_name}' saved! AI can now reference this.")
            st.balloons()
        
        # Quick content templates
        with st.expander("📋 Quick Templates"):
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Price Action Basics"):
                    st.session_state.knowledge["Price_Action_Basics"] = {
                        "text": "Price action trading focuses on reading raw price movements without indicators. Key concepts: support/resistance, trend lines, candlestick patterns, breakouts, and reversals.",
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.success("Price action basics loaded!")
            
            with col_b:
                if st.button("Risk Management"):
                    st.session_state.knowledge["Risk_Management"] = {
                        "text": "Risk management rules: 1. Risk only 1-2% per trade 2. Use stop losses 3. Maintain positive risk-reward ratios 4. Diversify positions 5. Keep a trading journal.",
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.success("Risk management loaded!")
    
    with col2:
        st.subheader("📊 Knowledge Base")
        if st.session_state.knowledge:
            for name, data in st.session_state.knowledge.items():
                with st.expander(f"📖 {name}"):
                    st.write(f"**Saved:** {data['date']}")
                    st.write(f"**Preview:** {data['text'][:200]}...")
                    if st.button(f"Ask about {name}", key=f"ask_{name}"):
                        st.session_state.chat_history.append({
                            "role": "user",
                            "content": f"Explain {name} in detail"
                        })
                        st.rerun()
        else:
            st.info("""
            **No content saved yet.**
            
            Add trading knowledge to:
            - Teach the AI
            - Get better responses
            - Build your learning base
            """)

elif mode == "📈 Chart Analysis":
    st.header("📈 Trading Chart Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Chart Input")
        
        # Option 1: Describe the chart
        chart_description = st.text_area(
            "Describe your chart:",
            height=150,
            placeholder="Example: EUR/USD 1H chart showing bullish trend with support at 1.0850 and resistance at 1.0950..."
        )
        
        # Option 2: Upload image (optional)
        uploaded_file = st.file_uploader(
            "Or upload chart image (optional):",
            type=["png", "jpg", "jpeg"]
        )
        
        if uploaded_file:
            st.image(uploaded_file, caption="Uploaded Chart", width=300)
        
        analysis_type = st.selectbox(
            "Analysis Type:",
            ["Technical Analysis", "Entry/Exit Points", "Risk Assessment", "Full Analysis"]
        )
        
        if st.button("🔍 Analyze Chart", type="primary"):
            with st.spinner("Analyzing..."):
                # Create analysis entry
                analysis = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "description": chart_description or f"Chart Image: {uploaded_file.name if uploaded_file else 'No description'}",
                    "type": analysis_type,
                    "ai_analysis": ""
                }
                
                # Get AI analysis if OpenAI is available
                if OPENAI_AVAILABLE and (chart_description or uploaded_file):
                    try:
                        import openai
                        
                        prompt = f"""
                        Analyze this trading scenario:
                        
                        {chart_description if chart_description else "User uploaded a chart image for analysis."}
                        
                        Provide {analysis_type.lower()} focusing on:
                        1. Key observations
                        2. Trading considerations
                        3. Risk management
                        4. Educational insights
                        
                        Format as clear, actionable points.
                        Remember: This is educational only, not financial advice.
                        """
                        
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "You are a professional trading analyst providing educational insights."},
                                {"role": "user", "content": prompt}
                            ],
                            max_tokens=400
                        )
                        
                        analysis["ai_analysis"] = response.choices[0].message.content
                        
                    except Exception as e:
                        analysis["ai_analysis"] = f"AI Analysis: Focus on clear support/resistance levels. Manage risk appropriately. Trading involves risk."
                
                # Store analysis
                st.session_state.analyses.append(analysis)
                
                # Display results
                st.subheader("📊 Analysis Results")
                
                if analysis["ai_analysis"]:
                    st.markdown(analysis["ai_analysis"])
                else:
                    st.info("""
                    **Manual Analysis Guidelines:**
                    
                    1. **Identify Trend:** Up, down, or sideways
                    2. **Key Levels:** Support and resistance
                    3. **Patterns:** Chart patterns if visible
                    4. **Volume:** Consider volume if data available
                    5. **Risk:** Always use stop losses
                    
                    *Enable OpenAI API for AI-powered analysis*
                    """)
                
                # Risk meter
                st.markdown("**⚠️ Risk Level:** Medium-High (trading always involves risk)")
                st.progress(0.6)
    
    with col2:
        st.subheader("📋 Analysis History")
        if st.session_state.analyses:
            for i, analysis in enumerate(reversed(st.session_state.analyses[-5:])):
                with st.expander(f"Analysis #{len(st.session_state.analyses)-i}"):
                    st.write(f"**Time:** {analysis['timestamp']}")
                    st.write(f"**Type:** {analysis['type']}")
                    st.write(f"**Chart:** {analysis['description'][:100]}...")
                    
                    if analysis["ai_analysis"]:
                        st.write("**AI Insights:**")
                        st.write(analysis["ai_analysis"][:200] + "...")
                    
                    col_x, col_y = st.columns(2)
                    with col_x:
                        if st.button("View Full", key=f"view_{i}"):
                            st.write("**Full Analysis:**")
                            st.write(analysis["ai_analysis"] or "No AI analysis available.")
                    with col_y:
                        if st.button("Delete", key=f"delete_{i}"):
                            st.session_state.analyses.remove(analysis)
                            st.rerun()
        else:
            st.info("""
            **No analyses yet.**
            
            Describe a chart or upload an image to get analysis.
            
            **Example descriptions:**
            - "Bullish trend with strong support"
            - "Range-bound market between two levels"
            - "Breakout above resistance with volume"
            """)

elif mode == "💬 Chat with AI":
    st.header("💬 Trading AI Chat")
    
    if not OPENAI_AVAILABLE:
        st.warning("""
        🔑 **OpenAI API Key Required**
        
        To chat with the AI:
        1. Get API key from [OpenAI](https://platform.openai.com)
        2. Enter it in the sidebar
        3. Start chatting!
        """)
        
        # Show conversation history even without API
        if st.session_state.chat_history:
            st.subheader("Recent Conversation")
            for message in st.session_state.chat_history[-5:]:
                role_icon = "👤" if message["role"] == "user" else "🤖"
                st.markdown(f"**{role_icon} {message['role'].title()}:**")
                st.write(message["content"])
                st.markdown("---")
    else:
        # Display chat
        st.subheader("Conversation")
        
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about trading..."):
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        import openai
                        
                        # Prepare context from saved knowledge
                        context = ""
                        if st.session_state.knowledge:
                            context = "Reference knowledge: " + "; ".join([
                                f"{name}: {data['text'][:100]}..." 
                                for name, data in st.session_state.knowledge.items()
                            ])
                        
                        # Prepare messages
                        messages = [
                            {
                                "role": "system", 
                                "content": f"""You are a professional trading coach. 
                                Provide educational insights about trading psychology, 
                                technical analysis, and risk management.
                                {context}
                                Always remind that this is educational, not financial advice."""
                            },
                            {"role": "user", "content": prompt}
                        ]
                        
                        # Add recent conversation context
                        for msg in st.session_state.chat_history[-4:-1]:
                            messages.append(msg)
                        
                        # Get response
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
                        error_msg = f"Error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
        
        # Chat controls
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat"):
                st.session_state.chat_history = []
                st.rerun()
        with col2:
            if st.button("💡 Example Questions"):
                examples = [
                    "What is the 1% risk rule?",
                    "How to identify support and resistance?",
                    "Explain trend following strategies",
                    "What is trading psychology?",
                    "How to create a trading plan?"
                ]
                st.info("Try asking: " + " | ".join(examples[:3]))

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <small>
    ⚠️ <strong>Educational Tool Only</strong> • Not Financial Advice • Trading Involves Risk
    </small>
</div>
""", unsafe_allow_html=True)

# Help section
with st.expander("🆘 Need Help?"):
    st.markdown("""
    ### **Quick Start:**
    
    1. **Get OpenAI Key:**
       - Visit: https://platform.openai.com/api-keys
       - Create free account
       - Generate API key
    
    2. **Enter Key** in sidebar
    
    3. **Start Using:**
       - **Learn Mode:** Add trading knowledge
       - **Analysis Mode:** Describe/upload charts
       - **Chat Mode:** Ask trading questions
    
    ### **For Developers:**
    ```bash
    # Local setup
    pip install streamlit openai
    streamlit run app.py
    ```
    
    ### **Source Code:**
    GitHub: https://github.com/wwwnishantom05-create/trading-ai-assistant
    """)

# Add some styling
st.markdown("""
<style>
    .stButton button {
        width: 100%;
        margin: 5px 0;
    }
    .css-1d391kg {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)
