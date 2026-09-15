import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime

# 1. Database Setup & Initialization
def init_db():
    conn = sqlite3.connect('app_database.db')
    cursor = conn.cursor()
    
    # Feedback Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            rating INTEGER,
            comments TEXT,
            timestamp TEXT
        )
    ''')
    
    # Tasks Table for CRUD
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT,
            status TEXT,
            hours INTEGER,
            priority TEXT,
            timestamp TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# 2. Page Configuration
st.set_page_config(
    page_title="Enterprise Streamlit Dashboard",
    page_layout="wide",
    initial_sidebar_state="expanded"
)

# 3. Custom CSS Styling
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

# 4. Sidebar & Mock Authentication
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
    ["Dashboard", "Database Analytics", "Task Manager (CRUD)", "File Uploader", "Feedback", "View Saved Feedback", "Settings"]
)

# 5. Main Body Content Based on Sidebar Navigation
if selected_option == "Dashboard":
    st.title("📊 Executive Performance Dashboard")
    st.write("Welcome back! Yahan aapke live database metrics hain.")
    
    # Fetch real counts from DB
    conn = sqlite3.connect('app_database.db')
    t_count_df = pd.read_sql_query("SELECT COUNT(*) as total FROM tasks", conn)
    f_count_df = pd.read_sql_query("SELECT COUNT(*) as total FROM feedback", conn)
    conn.close()
    
    total_tasks = t_count_df['total'].iloc[0] if not t_count_df.empty else 0
    total_feedbacks = f_count_df['total'].iloc[0] if not f_count_df.empty else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Database Tasks", value=total_tasks)
    col2.metric(label="Total Feedbacks Received", value=total_feedbacks)
    col3.metric(label="System Status", value="Online 🟢")
    
    st.markdown("---")
    st.subheader("📈 General Growth Overview")
    chart_data = pd.DataFrame(
        np.random.randn(20, 2),
        columns=['This Year', 'Last Year']
    )
    st.line_chart(chart_data)

elif selected_option == "Database Analytics":
    st.title("📊 Live Database Analytics & Insights")
    st.write("Yahan aapke saved tasks aur feedback ka visual breakdown dikh raha hai.")
    
    conn = sqlite3.connect('app_database.db')
    tasks_df = pd.read_sql_query("SELECT * FROM tasks", conn)
    feedback_df = pd.read_sql_query("SELECT * FROM feedback", conn)
    conn.close()
    
    if not tasks_df.empty:
        st.subheader("📌 Tasks Count by Status")
        status_counts = tasks_df['status'].value_counts()
        st.bar_chart(status_counts)
        
        st.subheader("⚡ Tasks Count by Priority")
        priority_counts = tasks_df['priority'].value_counts()
        st.bar_chart(priority_counts)
    else:
        st.info("Analytics ke liye pehle 'Task Manager' section se kuch tasks add karein.")
        
    if not feedback_df.empty:
        st.markdown("---")
        st.subheader("⭐ User Feedback Rating Distribution")
        rating_counts = feedback_df['rating'].value_counts().sort_index()
        st.bar_chart(rating_counts)

elif selected_option == "Task Manager (CRUD)":
    st.title("📝 Project Task Manager (Database Powered)")
    
    with st.form("add_task_form"):
        st.subheader("Add New Task")
        t_name = st.text_input("Task Name")
        t_status = st.selectbox("Status", ["Pending", "In Progress", "Completed"])
        t_hours = st.number_input("Estimated Hours", min_value=1, max_value=100, value=5)
        t_priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        
        submit_task = st.form_submit_button("Save Task to DB")
        
        if submit_task:
            if t_name:
                conn = sqlite3.connect('app_database.db')
                cursor = conn.cursor()
                t_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute(
                    "INSERT INTO tasks (task_name, status, hours, priority, timestamp) VALUES (?, ?, ?, ?, ?)",
                    (t_name, t_status, t_hours, t_priority, t_time)
                )
                conn.commit()
                conn.close()
                st.success(f"Task '{t_name}' successfully added!")
            else:
                st.warning("Kripya Task Name zaroor bharein.")

    st.markdown("---")
    st.subheader("📋 Current Tasks in Database")
    
    conn = sqlite3.connect('app_database.db')
    tasks_df = pd.read_sql_query("SELECT * FROM tasks", conn)
    conn.close()
    
    if not tasks_df.empty:
        st.dataframe(tasks_df, use_container_width=True)
        
        task_ids = tasks_df['id'].tolist()
        selected_id_to_delete = st.selectbox("Select Task ID to Delete", options=task_ids)
        if st.button("Delete Selected Task"):
            conn = sqlite3.connect('app_database.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (selected_id_to_delete,))
            conn.commit()
            conn.close()
            st.success(f"Task ID {selected_id_to_delete} deleted successfully!")
            st.rerun()
    else:
        st.info("Koi task database mein available nahi hai.")

elif selected_option == "File Uploader":
    st.title("📂 Dataset Uploader & Visualizer")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        user_df = pd.read_csv(uploaded_file)
        st.success("File successfully loaded!")
        st.dataframe(user_df.head(), use_container_width=True)
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
                conn = sqlite3.connect('app_database.db')
                cursor = conn.cursor()
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute(
                    "INSERT INTO feedback (name, email, rating, comments, timestamp) VALUES (?, ?, ?, ?, ?)",
                    (user_name, user_email, rating, comments, current_time)
                )
                conn.commit()
                conn.close()
                st.success(f"Shukriya {user_name}! Feedback saved.")
            else:
                st.warning("Kripya fields bharein.")

elif selected_option == "View Saved Feedback":
    st.title("📋 Saved Feedbacks from Database")
    conn = sqlite3.connect('app_database.db')
    feedback_df = pd.read_sql_query("SELECT * FROM feedback", conn)
    conn.close()
    if not feedback_df.empty:
        st.dataframe(feedback_df, use_container_width=True)
    else:
        st.info("Koi feedback nahi mila.")

elif selected_option == "Settings":
    st.title("⚙️ System Settings")
    st.toggle("Enable Dark Theme Preview")
    if st.button("Save Configurations"):
        st.success("Settings updated successfully!")