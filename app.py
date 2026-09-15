import streamlit as st
import pandas as pd
import numpy as np

# 1. Page Configuration
st.set_page_config(
    page_title="Enterprise Streamlit Dashboard",
    page_layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS Styling
st.markdown("""
    <style>
    .stApp {
        background-color: #F8FAFC;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] { 
        height: 48px; 
        background: linear-gradient(135deg, #F1F5F9, #E2E8F0); 
        border-radius: 10px 10px 0px 0px;
        padding-left: 20px;
        padding-right: 20px;
        font-weight: 600;
        color: #334155;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3B82F6, #1D4ED8) !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar & Mock Authentication
st.sidebar.title("🔐 Access Control")
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.sidebar.error("Invalid Credentials (Try admin / admin123)")
    st.stop()
else:
    st.sidebar.success("Logged in as Admin")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.title("🎛️ Navigation Panel")
selected_option = st.sidebar.radio(
    "Go to", 
    ["Dashboard", "Data Analytics & Filters", "File Uploader", "Feedback", "Settings"]
)

# 4. Main Body Content Based on Sidebar Navigation
if selected_option == "Dashboard":
    st.title("📊 Executive Performance Dashboard")
    st.write("Welcome back! Yahan aapke business ke key metrics hain.")
    
    # Metrics Row
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Revenue", value="$54,200", delta="+10.4%")
    col2.metric(label="Active Users", value="1,820", delta="+15%")
    col3.metric(label="Bounce Rate", value="2.1%", delta="-0.8%")
    
    st.markdown("---")
    
    # Sample Multi-Series Chart
    st.subheader("📈 Growth Trend Analysis")
    chart_data = pd.DataFrame(
        np.random.randn(20, 2),
        columns=['This Year', 'Last Year']
    )
    st.line_chart(chart_data)

elif selected_option == "Data Analytics & Filters":
    st.title("📁 Advanced Data Analytics & Filtering")
    st.write("Apne dataset ko filter karein aur insights dekhein.")
    
    # Sample DataFrame with more rows
    df = pd.DataFrame({
        'Task': ['Design UI', 'Database Setup', 'API Integration', 'Testing', 'Deployment', 'Documentation'],
        'Status': ['Completed', 'In Progress', 'Pending', 'Pending', 'Completed', 'In Progress'],
        'Hours': [15, 25, 10, 8, 12, 18],
        'Priority': ['High', 'High', 'Medium', 'Low', 'High', 'Medium']
    })
    
    # Interactive Filter widget
    selected_status = st.multiselect(
        "Filter by Status", 
        options=df['Status'].unique(), 
        default=df['Status'].unique()
    )
    
    filtered_df = df[df['Status'].isin(selected_status)]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Bar Chart for Filtered Hours
    if not filtered_df.empty:
        st.subheader("📊 Hours Spent per Task")
        st.bar_chart(filtered_df.set_index('Task')['Hours'])
    
    # Download Button Feature
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv_data,
        file_name='filtered_analytics.csv',
        mime='text/csv'
    )

elif selected_option == "File Uploader":
    st.title("📂 Dataset Uploader & Visualizer")
    st.write("Apni khud ki CSV file upload karein.")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        user_df = pd.read_csv(uploaded_file)
        st.success("File successfully loaded!")
        st.subheader("Data Preview")
        st.dataframe(user_df.head(), use_container_width=True)
        
        st.subheader("Summary Statistics")
        st.write(user_df.describe())
    else:
        st.info("Test karne ke liye koi bhi CSV file upload karein.")

elif selected_option == "Feedback":
    st.title("💬 User Feedback Form")
    with st.form("feedback_form"):
        user_name = st.text_input("Aapka Naam")
        user_email = st.text_input("Email Address")
        rating = st.slider("Rating (1 to 5)", 1, 5, 5)
        comments = st.text_area("Apna Feedback Likhein")
        
        submitted = st.form_submit_button("Submit Feedback")
        
        if submitted:
            if user_name and comments:
                st.success(f"Shukriya {user_name}! Aapka feedback successfully save ho gaya hai.")
            else:
                st.warning("Kripya Naam aur Comments fields zaroor bharein.")

elif selected_option == "Settings":
    st.title("⚙️ System Settings")
    st.write("Application configurations manage karein.")
    
    dark_mode = st.toggle("Enable Dark Theme Preview")
    email_alerts = st.checkbox("Enable Daily Email Reports", value=True)
    
    if st.button("Save Configurations"):
        st.success("Settings updated successfully!")