import streamlit as st
import pandas as pd
import numpy as np

# 1. Page Configuration
st.set_page_config(
    page_title="Advanced Streamlit Dashboard",
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

# 3. Sidebar Configuration
st.sidebar.title("🎛️ Control Panel")
selected_option = st.sidebar.radio(
    "Navigation", 
    ["Dashboard", "Data Analytics", "File Uploader", "Feedback", "Settings"]
)

st.sidebar.markdown("---")
st.sidebar.info("Aap yahan se alag-alag modules ke beech switch kar sakte hain.")

# 4. Main Body Content Based on Sidebar
if selected_option == "Dashboard":
    st.title("📊 Executive Dashboard")
    st.write("Yahan aapke key metrics aur quick summaries display hongi.")
    
    # Metrics Row
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Revenue", value="$45,200", delta="+8.2%")
    col2.metric(label="Active Users", value="1,420", delta="+12%")
    col3.metric(label="Conversion Rate", value="3.4%", delta="-0.5%")
    
    st.markdown("---")
    
    # Sample Chart
    st.subheader("📈 Performance Overview")
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['A', 'B', 'C']
    )
    st.line_chart(chart_data)

elif selected_option == "Data Analytics":
    st.title("📁 Data Analytics & Export")
    st.write("Yahan aap apne dataset ko view kar sakte hain aur CSV file mein download bhi kar sakte hain.")
    
    # Sample DataFrame
    df = pd.DataFrame({
        'Task': ['Design UI', 'Database Setup', 'API Integration', 'Testing'],
        'Status': ['Completed', 'In Progress', 'Pending', 'Pending'],
        'Hours': [15, 25, 10, 8]
    })
    
    st.dataframe(df, use_container_width=True)
    
    # Download Button Feature
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data as CSV",
        data=csv_data,
        file_name='analytics_report.csv',
        mime='text/csv'
    )

elif selected_option == "File Uploader":
    st.title("📂 Upload Your Dataset")
    st.write("Apna khud ka CSV file upload karein aur quick analysis dekhein.")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        user_df = pd.read_csv(uploaded_file)
        st.success("File successfully uploaded!")
        st.subheader("Data Preview")
        st.dataframe(user_df.head(), use_container_width=True)
        
        st.subheader("Basic Statistics")
        st.write(user_df.describe())
    else:
        st.info("Kripya test karne ke liye ek CSV file upload karein.")

elif selected_option == "Feedback":
    st.title("💬 User Feedback Form")
    st.write("Apna anubhav hamare sath share karein.")
    
    with st.form("feedback_form"):
        user_name = st.text_input("Aapka Naam")
        user_email = st.text_input("Email Address")
        rating = st.slider("Rating (1 to 5)", 1, 5, 5)
        comments = st.text_area("Apna Feedback Likhein")
        
        submitted = st.form_submit_button("Submit Feedback")
        
        if submitted:
            if user_name and comments:
                st.success(f"Shukriya {user_name}! Aapka feedback successfully submit ho gaya hai.")
            else:
                st.warning("Kripya Naam aur Comments fields zaroor bharein.")

elif selected_option == "Settings":
    st.title("⚙️ Application Settings")
    st.write("Apni preferences yahan configure karein.")
    
    dark_mode = st.toggle("Enable Dark Theme Preview")
    notifications = st.checkbox("Receive Email Notifications", value=True)
    
    if st.button("Save Changes"):
        st.success("Settings saved successfully!")