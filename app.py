import streamlit as st
import joblib
import pandas as pd
import os
from scraper import scrape_instagram_profile

# ------------------------------
# PAGE CONFIGURATION
# ------------------------------
st.set_page_config(
    page_title="Fake Profile Detector",
    page_icon=" ",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------------------
# CUSTOM CSS FOR HERO SECTION AND STYLING
# ------------------------------
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hero Section */
    .hero-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 3rem 2rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
    }
    .hero-title {
        color: #ffffff;
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.25rem;
        font-weight: 400;
        margin-bottom: 1.5rem;
    }
    .hero-highlight {
        color: #38bdf8;
        font-weight: 600;
    }
    .hero-badge {
        background-color: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        padding: 0.25rem 1rem;
        border-radius: 100px;
        font-size: 0.875rem;
        font-weight: 500;
        display: inline-block;
        margin-bottom: 1rem;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }
    
    /* Card Styles */
    .card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    .card-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 1rem;
    }
    
    /* Result Cards */
    .result-card-fake {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border-left: 6px solid #dc2626;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    .result-card-real {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-left: 6px solid #16a34a;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    .result-label {
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        color: #64748b;
    }
    .result-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.25rem 0;
    }
    
    /* Metric Box */
    .metric-box {
        background-color: #f8fafc;
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid #e2e8f0;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white;
        font-weight: 600;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.2);
        transition: all 0.2s ease;
        width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.3);
        transform: translateY(-1px);
    }
    
    /* Radio Button Styling */
    .stRadio > div {
        background-color: #f8fafc;
        padding: 0.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: #f8fafc;
        border-radius: 8px;
    }
    
    /* Input Field */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        padding: 0.75rem 1rem;
        font-size: 1rem;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #f8fafc;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0 1rem 0;
        color: #94a3b8;
        font-size: 0.875rem;
        border-top: 1px solid #e2e8f0;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------
# LOAD MODEL AND SCALER (CACHED)
# ------------------------------
@st.cache_resource
def load_assets():
    model = None
    scaler = None
    feature_order = None
    
    if os.path.exists('model.pkl'):
        model = joblib.load('model.pkl')
    else:
        st.error("Model file 'model.pkl' not found. Please ensure it is in the project directory.")
    
    if os.path.exists('scaler.pkl'):
        scaler = joblib.load('scaler.pkl')
    else:
        st.warning("Scaler file 'scaler.pkl' not found. Predictions may be less accurate.")
    
    feature_order = [
        'profile pic',
        'nums/length username',
        'fullname words',
        'nums/length fullname',
        'name==username',
        'description length',
        'external URL',
        'private',
        '#posts',
        '#followers',
        '#follows'
    ]
    
    return model, scaler, feature_order

model, scaler, feature_order = load_assets()

# ------------------------------
# HERO SECTION
# ------------------------------
st.markdown("""
<div class="hero-container">
    <div class="hero-badge">AI-POWERED DETECTION</div>
    <div class="hero-title">Verify Social Media Authenticity</div>
    <div class="hero-subtitle">
        Instantly analyze Instagram profiles to distinguish 
        <span class="hero-highlight">genuine accounts</span> from 
        <span class="hero-highlight">bots and fake profiles</span> using advanced machine learning.
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------
# MAIN CONTENT AREA
# ------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<p class="card-title">Start Analysis</p>', unsafe_allow_html=True)
    
    # Input method selection
    input_method = st.radio(
        "Choose input method:",
        ["Automatic Scraping (Enter URL)", "Manual Data Entry (Fallback)"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    features_dict = None
    
    if input_method == "Automatic Scraping (Enter URL)":
        url = st.text_input(
            "Instagram Profile URL",
            placeholder="https://www.instagram.com/username/",
            label_visibility="collapsed"
        )
        st.caption("Enter a public Instagram profile URL. Scraping takes 3-5 seconds.")
        
        if st.button("Analyze Profile"):
            if not url:
                st.warning("Please enter a valid Instagram URL.")
            else:
                with st.spinner("Scraping profile data... Please wait."):
                    try:
                        features_dict = scrape_instagram_profile(url)
                        st.success("Profile data extracted successfully.")
                    except Exception as e:
                        st.error(f"Scraping failed: {str(e)}")
                        st.info("Try the Manual Data Entry option instead.")
    
    else:
        st.markdown("### Manual Profile Data Entry")
        st.caption("Enter the profile statistics manually if scraping is blocked.")
        
        manual_col1, manual_col2 = st.columns(2)
        
        with manual_col1:
            profile_pic = st.selectbox(
                "Profile Picture",
                options=[1, 0],
                format_func=lambda x: "Custom Image" if x == 1 else "Default Avatar"
            )
            username_input = st.text_input("Username", value="example_user")
            fullname_input = st.text_input("Full Name", value="Example Name")
            fullname_words = st.number_input("Words in Full Name", min_value=0, max_value=20, value=len(fullname_input.split()))
            name_equals_username = st.checkbox("Name equals Username")
            description_length = st.number_input("Bio Length (characters)", min_value=0, max_value=500, value=50)
        
        with manual_col2:
            external_url = st.selectbox(
                "External URL Present",
                options=[1, 0],
                format_func=lambda x: "Yes" if x == 1 else "No"
            )
            private = st.selectbox(
                "Private Account",
                options=[1, 0],
                format_func=lambda x: "Yes" if x == 1 else "No"
            )
            posts = st.number_input("Number of Posts", min_value=0, max_value=100000, value=100)
            followers = st.number_input("Number of Followers", min_value=0, max_value=10000000, value=1000)
            follows = st.number_input("Number of Following", min_value=0, max_value=100000, value=500)
        
        if st.button("Analyze Manual Entry"):
            # Calculate derived features from manual inputs
            username = username_input
            username_length = len(username)
            nums_username = sum(c.isdigit() for c in username)
            nums_length_username = nums_username / username_length if username_length > 0 else 0.0
            
            fullname = fullname_input
            fullname_len = len(fullname)
            nums_fullname = sum(c.isdigit() for c in fullname)
            nums_length_fullname = nums_fullname / fullname_len if fullname_len > 0 else 0.0
            
            features_dict = {
                'profile pic': profile_pic,
                'nums/length username': nums_length_username,
                'fullname words': fullname_words,
                'nums/length fullname': nums_length_fullname,
                'name==username': 1 if name_equals_username else 0,
                'description length': description_length,
                'external URL': external_url,
                'private': private,
                '#posts': posts,
                '#followers': followers,
                '#follows': follows
            }
            st.success("Manual data prepared for analysis.")
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<p class="card-title">How It Works</p>', unsafe_allow_html=True)
    st.markdown("""
    <div style="color: #334155; line-height: 1.6;">
        <p style="margin-bottom: 1rem;">
            <span style="font-weight: 600; color: #0f172a;">1. Data Collection</span><br>
            We analyze 11 key profile features including follower ratios, bio completeness, and username patterns.
        </p>
        <p style="margin-bottom: 1rem;">
            <span style="font-weight: 600; color: #0f172a;">2. Machine Learning</span><br>
            A Random Forest classifier trained on thousands of verified real and fake accounts.
        </p>
        <p>
            <span style="font-weight: 600; color: #0f172a;">3. Instant Verdict</span><br>
            Receive a confidence score indicating the likelihood the account is authentic.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show model status in sidebar
    if model:
        st.success("Model loaded and ready.")
    else:
        st.error("Model not loaded.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------
# DISPLAY PREDICTION RESULTS
# ------------------------------
if features_dict is not None and model is not None:
    st.markdown("---")
    st.markdown("## Analysis Results")
    
    # Convert to DataFrame with correct column order
    input_df = pd.DataFrame([features_dict])[feature_order]
    
    # Apply scaling if available
    if scaler is not None:
        input_scaled = scaler.transform(input_df)
    else:
        input_scaled = input_df
    
    # Make prediction
    prediction = model.predict(input_scaled)[0]
    probabilities = model.predict_proba(input_scaled)[0]
    
    # Confidence scores
    confidence_real = probabilities[0] * 100
    confidence_fake = probabilities[1] * 100
    
    # Display result card
    if prediction == 1:
        st.markdown(f"""
        <div class="result-card-fake">
            <div class="result-label">Prediction</div>
            <div class="result-value" style="color: #dc2626;">FAKE / BOT</div>
            <div style="font-size: 1.1rem; margin-top: 0.5rem; color: #7f1d1d;">
                Confidence: {confidence_fake:.1f}%
            </div>
            <p style="margin-top: 1rem; color: #7f1d1d;">
                This account exhibits patterns consistent with automated or fake profiles.
                Suspicious indicators may include unusual follower ratios, minimal bio content,
                or numeric username patterns.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="result-card-real">
            <div class="result-label">Prediction</div>
            <div class="result-value" style="color: #16a34a;">AUTHENTIC</div>
            <div style="font-size: 1.1rem; margin-top: 0.5rem; color: #14532d;">
                Confidence: {confidence_real:.1f}%
            </div>
            <p style="margin-top: 1rem; color: #14532d;">
                This account appears to be a genuine human profile. The analyzed features
                fall within normal ranges for authentic social media accounts.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display extracted features in expander
    with st.expander("View Extracted Feature Values"):
        feature_df = pd.DataFrame([features_dict]).T
        feature_df.columns = ['Value']
        st.dataframe(feature_df, use_container_width=True)
        
        # Show probability breakdown
        proba_df = pd.DataFrame({
            'Class': ['Real', 'Fake'],
            'Probability': [f"{confidence_real:.2f}%", f"{confidence_fake:.2f}%"]
        })
        st.dataframe(proba_df, use_container_width=True, hide_index=True)

# ------------------------------
# FOOTER
# ------------------------------
st.markdown("""
<div class="footer">
    <p>Fake Social Media Profile Detection | Powered by Machine Learning</p>
    <p style="margin-top: 0.5rem; font-size: 0.8rem;">
        This tool analyzes publicly available profile metadata. Results are probabilistic and should be interpreted as guidance.
    </p>
</div>
""", unsafe_allow_html=True)
