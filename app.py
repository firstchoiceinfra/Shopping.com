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
selected_option = st.sidebar.radio("Navigation", ["Dashboard", "Data Analytics", "Settings"])

st.sidebar.markdown("---")
st.sidebar.info("Aap yahan se apne app ke controls manage kar sakte hain.")

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
    st.title("📁 Data Analytics & Table")
    st.write("Yahan aap apne datasets ko view aur filter kar sakte hain.")
    
    # Sample DataFrame
    df = pd.DataFrame({
        'Task': ['Design UI', 'Database Setup', 'API Integration', 'Testing'],
        'Status': ['Completed', 'In Progress', 'Pending', 'Pending'],
        'Hours': [15, 25, 10, 8]
    })
    
    st.dataframe(df, use_container_width=True)

elif selected_option == "Settings":
    st.title("⚙️ Application Settings")
    st.write("Apni preferences yahan configure karein.")
    
    dark_mode = st.toggle("Enable Dark Theme Preview")
    notifications = st.checkbox("Receive Email Notifications", value=True)
    
    if st.button("Save Changes"):
        st.success("Settings saved successfully!")
