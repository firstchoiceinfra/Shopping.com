import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import io
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
    
    # Tasks Table for CRUD & Kanban
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
    
    # Activity Audit Logs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            timestamp TEXT
        )
    ''')
    
    # E-Commerce Products Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            stock INTEGER,
            category TEXT
        )
    ''')
    
    # E-Commerce Orders Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            items TEXT,
            total_amount REAL,
            timestamp TEXT
        )
    ''')
    
    # User Roles Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            role TEXT,
            status TEXT
        )
    ''')
    
    # Notifications Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT,
            category TEXT,
            timestamp TEXT
        )
    ''')
    
    # Team Notes Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            author TEXT,
            timestamp TEXT
        )
    ''')
    
    # Seed default products if table is empty
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ("Wireless Mouse", 25.99, 50, "Electronics"),
            ("Mechanical Keyboard", 79.99, 30, "Electronics"),
            ("Gaming Headset", 49.99, 25, "Electronics"),
            ("Notebook", 4.99, 100, "Stationery"),
            ("Coffee Mug", 12.50, 40, "Lifestyle")
        ]
        cursor.executemany("INSERT INTO products (name, price, stock, category) VALUES (?, ?, ?, ?)", sample_products)
        conn.commit()

    # Seed default roles if empty
    cursor.execute("SELECT COUNT(*) FROM user_roles")
    if cursor.fetchone()[0] == 0:
        sample_roles = [
            ("admin", "Administrator", "Active"),
            ("manager_john", "Project Manager", "Active"),
            ("dev_sara", "Developer", "Active")
        ]
        cursor.executemany("INSERT INTO user_roles (username, role, status) VALUES (?, ?, ?)", sample_roles)
        conn.commit()
        
    conn.close()

init_db()

def log_activity(action_text, notif_category="System"):
    conn = sqlite3.connect('app_database.db')
    cursor = conn.cursor()
    t_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Insert into Audit Logs
    cursor.execute("INSERT INTO audit_logs (action, timestamp) VALUES (?, ?)", (action_text, t_time))
    
    # Insert into Notifications
    cursor.execute("INSERT INTO notifications (message, category, timestamp) VALUES (?, ?, ?)", (action_text, notif_category, t_time))
    
    conn.commit()
    conn.close()

# 2. Page Configuration
st.set_page_config(
    page_title="Enterprise E-Commerce & Dashboard",
    page_layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Theme State
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# Dynamic CSS Styling based on Theme Choice
bg_color = "#0F172A" if st.session_state.dark_mode else "#F8FAFC"
card_bg = "#1E293B" if st.session_state.dark_mode else "#FFFFFF"
text_color = "#F8FAFC" if st.session_state.dark_mode else "#334155"

st.markdown(f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: {text_color};
    }}
    .kanban-card, .product-card, .note-card {{
        background-color: {card_bg};
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 10px;
        border-left: 5px solid #3B82F6;
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    .stTabs [data-baseweb="tab"] {{ 
        height: 48px; 
        background: linear-gradient(135deg, #F1F5F9, #E2E8F0); 
        border-radius: 10px 10px 0px 0px;
        padding-left: 20px;
        padding-right: 20px;
        font-weight: 600;
        color: #334155;
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, #3B82F6, #1D4ED8) !important;
        color: white !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Initialize Cart
if "cart" not in st.session_state:
    st.session_state.cart = {}

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
            log_activity("Admin logged in successfully.", "Auth")
            st.rerun()
        else:
            st.sidebar.error("Invalid Credentials (Try admin / admin123)")
    st.stop()
else:
    st.sidebar.success("Logged in as Admin")
    if st.sidebar.button("Logout"):
        log_activity("Admin logged out.", "Auth")
        st.session_state.logged_in = False
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.title("🎛️ Navigation Panel")
selected_option = st.sidebar.radio(
    "Go to", 
    [
        "Dashboard", 
        "🔔 Notifications Center",
        "📌 Team Collaboration Notes",
        "🔍 Global Master Search", 
        "🛍️ E-Commerce Store", 
        "🛒 Shopping Cart", 
        "📦 Order History",
        "👥 User Roles & Permissions",
        "Database Analytics", 
        "Task Manager (CRUD)", 
        "Kanban Board", 
        "File Uploader", 
        "Feedback", 
        "View Saved Feedback", 
        "Reports & Export", 
        "Audit Logs", 
        "Settings"
    ]
)

# 4. Main Body Content Based on Sidebar Navigation
if selected_option == "Dashboard":
    st.title("📊 Executive Performance Dashboard")
    st.write("Welcome back! Yahan aapke live database metrics aur store statistics hain.")
    
    conn = sqlite3.connect('app_database.db')
    t_count_df = pd.read_sql_query("SELECT COUNT(*) as total FROM tasks", conn)
    completed_df = pd.read_sql_query("SELECT COUNT(*) as total FROM tasks WHERE status = 'Completed'", conn)
    f_count_df = pd.read_sql_query("SELECT COUNT(*) as total FROM feedback", conn)
    p_count_df = pd.read_sql_query("SELECT COUNT(*) as total FROM products", conn)
    o_count_df = pd.read_sql_query("SELECT COUNT(*) as total FROM orders", conn)
    conn.close()
    
    total_tasks = t_count_df['total'].iloc[0] if not t_count_df.empty else 0
    completed_tasks = completed_df['total'].iloc[0] if not completed_df.empty else 0
    total_feedbacks = f_count_df['total'].iloc[0] if not f_count_df.empty else 0
    total_products = p_count_df['total'].iloc[0] if not p_count_df.empty else 0
    total_orders = o_count_df['total'].iloc[0] if not o_count_df.empty else 0
    
    progress_val = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Total Tasks", value=total_tasks)
    col2.metric(label="Store Products", value=total_products)
    col3.metric(label="Total Orders", value=total_orders)
    col4.metric(label="Feedbacks", value=total_feedbacks)
    
    st.markdown("---")
    st.subheader("🎯 Overall Project Completion Milestone")
    st.progress(progress_val, text=f"Project Progress: {progress_val}% Completed")
    
    st.markdown("---")
    st.subheader("📈 General Growth Overview")
    chart_data = pd.DataFrame(np.random.randn(20, 2), columns=['This Year', 'Last Year'])
    st.line_chart(chart_data)

elif selected_option == "🔔 Notifications Center":
    st.title("🔔 Real-Time Notifications Center")
    st.write("Yahan aapko system ke sabhi recent alerts aur activities ki live feed milegi.")
    
    conn = sqlite3.connect('app_database.db')
    notif_df = pd.read_sql_query("SELECT * FROM notifications ORDER BY id DESC", conn)
    conn.close()
    
    col_clear, col_refresh = st.columns([1, 4])
    with col_clear:
        if st.button("Clear All Notifications"):
            conn = sqlite3.connect('app_database.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notifications")
            conn.commit()
            conn.close()
            st.success("All notifications cleared!")
            st.rerun()
            
    if not notif_df.empty:
        st.markdown("---")
        for _, row in notif_df.iterrows():
            st.info(f"**[{row['category']}]** {row['message']} — *{row['timestamp']}*")
    else:
        st.info("Abhi koi naya notification nahi hai.")

elif selected_option == "📌 Team Collaboration Notes":
    st.title("📌 Team Collaboration & Sticky Notes")
    st.write("Aap aur aapke team members yahan important announcements aur notes share kar sakte hain.")
    
    with st.form("add_note_form"):
        st.subheader("Create New Team Note")
        note_title = st.text_input("Note Title")
        note_content = st.text_area("Note Description / Content")
        note_author = st.text_input("Author Name", value="Admin")
        
        submit_note = st.form_submit_button("Publish Note")
        if submit_note:
            if note_title and note_content:
                conn = sqlite3.connect('app_database.db')
                cursor = conn.cursor()
                t_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("INSERT INTO team_notes (title, content, author, timestamp) VALUES (?, ?, ?, ?)", (note_title, note_content, note_author, t_time))
                conn.commit()
                conn.close()
                log_activity(f"New team note published by {note_author}: {note_title}", "Notes")
                st.success("Note published successfully!")
                st.rerun()
            else:
                st.warning("Kripya title aur content dono bharein.")
                
    st.markdown("---")
    st.subheader("📋 Active Team Notes Board")
    conn = sqlite3.connect('app_database.db')
    notes_df = pd.read_sql_query("SELECT * FROM team_notes ORDER BY id DESC", conn)
    conn.close()
    
    if not notes_df.empty:
        for _, row in notes_df.iterrows():
            st.markdown(f"""
                <div class="note-card">
                    <h4>📌 {row['title']}</h4>
                    <p>{row['content']}</p>
                    <small><b>Author:</b> {row['author']} | <b>Posted on:</b> {row['timestamp']}</small>
                </div>
            """, unsafe_allow_html=True)
            
        note_ids = notes_df['id'].tolist()
        selected_note_id = st.selectbox("Select Note ID to Delete", options=note_ids)
        if st.button("Delete Selected Note"):
            conn = sqlite3.connect('app_database.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM team_notes WHERE id = ?", (selected_note_id,))
            conn.commit()
            conn.close()
            log_activity(f"Deleted note ID: {selected_note_id}", "Notes")
            st.success("Note deleted successfully!")
            st.rerun()
    else:
        st.info("No team notes available yet.")

elif selected_option == "🔍 Global Master Search":
    st.title("🔍 Global Database Search Bar")
    st.write("Poore database (Tasks, Products, Orders, aur Feedback) mein ek sath keyword search karein.")
    
    search_term = st.text_input("Enter search keyword (e.g., Mouse, Admin, Completed):")
    
    if search_term:
        conn = sqlite3.connect('app_database.db')
        tasks_df = pd.read_sql_query("SELECT * FROM tasks", conn)
        products_df = pd.read_sql_query("SELECT * FROM products", conn)
        orders_df = pd.read_sql_query("SELECT * FROM orders", conn)
        feedback_df = pd.read_sql_query("SELECT * FROM feedback", conn)
        conn.close()
        
        st.subheader("📌 Matching Tasks")
        if not tasks_df.empty:
            matched_tasks = tasks_df[tasks_df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
            st.dataframe(matched_tasks, use_container_width=True)
            
        st.subheader("🛍️ Matching Products")
        if not products_df.empty:
            matched_prods = products_df[products_df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
            st.dataframe(matched_prods, use_container_width=True)
            
        st.subheader("📦 Matching Orders")
        if not orders_df.empty:
            matched_orders = orders_df[orders_df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
            st.dataframe(matched_orders, use_container_width=True)
            
        st.subheader("💬 Matching Feedbacks")
        if not feedback_df.empty:
            matched_fb = feedback_df[feedback_df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
            st.dataframe(matched_fb, use_container_width=True)
    else:
        st.info("Kripya upar search bar mein koi keyword type karein.")

elif selected_option == "🛍️ E-Commerce Store":
    st.title("🛍️ Online Product Store")
    st.write("Browse products available in the database and add them to your shopping cart.")
    
    conn = sqlite3.connect('app_database.db')
    products_df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    
    if not products_df.empty:
        cols = st.columns(3)
        for index, row in products_df.iterrows():
            col = cols[index % 3]
            with col:
                st.markdown(f"""
                    <div class="product-card">
                        <h3>{row['name']}</h3>
                        <p><b>Category:</b> {row['category']}</p>
                        <p><b>Price:</b> ${row['price']:.2f}</p>
                        <p><b>Stock Available:</b> {row['stock']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Add to Cart", key=f"prod_{row['id']}"):
                    p_id = row['id']
                    if p_id in st.session_state.cart:
                        st.session_state.cart[p_id] += 1
                    else:
                        st.session_state.cart[p_id] = 1
                    st.success(f"Added {row['name']} to cart!")
    else:
        st.info("No products found in database.")

elif selected_option == "🛒 Shopping Cart":
    st.title("🛒 Your Shopping Cart")
    st.write("Review your selected items and proceed to checkout.")
    
    if st.session_state.cart:
        conn = sqlite3.connect('app_database.db')
        products_df = pd.read_sql_query("SELECT * FROM products", conn)
        conn.close()
        
        cart_items = []
        total_price = 0.0
        
        for p_id, qty in st.session_state.cart.items():
            product_row = products_df[products_df['id'] == p_id]
            if not product_row.empty:
                p_name = product_row['name'].values[0]
                p_price = product_row['price'].values[0]
                subtotal = p_price * qty
                total_price += subtotal
                cart_items.append({"ID": p_id, "Product": p_name, "Price": p_price, "Quantity": qty, "Subtotal": subtotal})
                
        cart_df = pd.DataFrame(cart_items)
        st.dataframe(cart_df, use_container_width=True)
        st.markdown(f"### Total Amount: ${total_price:.2f}")
        
        col_clear, col_checkout = st.columns(2)
        with col_clear:
            if st.button("Clear Cart"):
                st.session_state.cart = {}
                st.rerun()
                
        with col_checkout:
            customer_name_input = st.text_input("Customer Name for Order", value="Admin User")
            if st.button("Place Order Now"):
                conn = sqlite3.connect('app_database.db')
                cursor = conn.cursor()
                items_summary = ", ".join([f"{row['Product']} (x{row['Quantity']})" for row in cart_items])
                t_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute(
                    "INSERT INTO orders (customer_name, items, total_amount, timestamp) VALUES (?, ?, ?, ?)",
                    (customer_name_input, items_summary, total_price, t_time)
                )
                conn.commit()
                conn.close()
                
                log_activity(f"New order placed by {customer_name_input} for ${total_price:.2f}", "Store")
                st.success("Order placed successfully! Recorded in database.")
                st.session_state.cart = {}
                st.rerun()
    else:
        st.info("Your shopping cart is empty. Visit the 'E-Commerce Store' tab to add products.")

elif selected_option == "📦 Order History":
    st.title("📦 Customer Orders History")
    st.write("View all completed e-commerce transactions.")
    
    conn = sqlite3.connect('app_database.db')
    orders_df = pd.read_sql_query("SELECT * FROM orders", conn)
    conn.close()
    
    if not orders_df.empty:
        st.dataframe(orders_df, use_container_width=True)
    else:
        st.info("No orders found in the database yet.")

elif selected_option == "👥 User Roles & Permissions":
    st.title("👥 User Roles & Permissions Management")
    st.write("Manage staff roles and user access privileges.")
    
    with st.form("add_role_form"):
        st.subheader("Add New Team Member Role")
        new_user = st.text_input("Username")
        new_role = st.selectbox("Assign Role", ["Administrator", "Project Manager", "Developer", "Customer Support"])
        new_status = st.selectbox("Status", ["Active", "Inactive"])
        
        submit_role = st.form_submit_button("Save User Role")
        if submit_role:
            if new_user:
                conn = sqlite3.connect('app_database.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO user_roles (username, role, status) VALUES (?, ?, ?)", (new_user, new_role, new_status))
                conn.commit()
                conn.close()
                log_activity(f"Added role for user: {new_user}", "Admin")
                st.success(f"User {new_user} added with role {new_role}!")
            else:
                st.warning("Kripya username enter karein.")
                
    st.markdown("---")
    st.subheader("📋 Current User Roles Directory")
    conn = sqlite3.connect('app_database.db')
    roles_df = pd.read_sql_query("SELECT * FROM user_roles", conn)
    conn.close()
    if not roles_df.empty:
        st.dataframe(roles_df, use_container_width=True)
    else:
        st.info("No user roles configured.")

elif selected_option == "Database Analytics":
    st.title("📊 Live Database Analytics & Insights")
    st.write("Yahan aapke saved tasks, products, aur feedback ka visual breakdown dikh raha hai.")
    
    conn = sqlite3.connect('app_database.db')
    tasks_df = pd.read_sql_query("SELECT * FROM tasks", conn)
    feedback_df = pd.read_sql_query("SELECT * FROM feedback", conn)
    products_df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    
    if not tasks_df.empty:
        st.subheader("📌 Tasks Count by Status")
        status_counts = tasks_df['status'].value_counts()
        st.bar_chart(status_counts)
        
    if not products_df.empty:
        st.markdown("---")
        st.subheader("🛍️ Product Price Distribution")
        st.bar_chart(products_df.set_index('name')['price'])
        
    if not feedback_df.empty:
        st.markdown("---")
        st.subheader("⭐ User Feedback Rating Distribution")
        rating_counts = feedback_df['rating'].value_counts().sort_index()
        st.bar_chart(rating_counts)

elif selected_option == "Task Manager (CRUD)":
    st.title("📝 Project Task Manager (Advanced Search & CRUD)")
    
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
                log_activity(f"Added new task: {t_name}", "Tasks")
                st.success(f"Task '{t_name}' successfully added!")
            else:
                st.warning("Kripya Task Name zaroor bharein.")

    st.markdown("---")
    st.subheader("📋 Search & Manage Database Tasks")
    
    conn = sqlite3.connect('app_database.db')
    tasks_df = pd.read_sql_query("SELECT * FROM tasks", conn)
    conn.close()
    
    if not tasks_df.empty:
        search_query = st.text_input("🔍 Search Task by Name")
        if search_query:
            tasks_df = tasks_df[tasks_df['task_name'].str.contains(search_query, case=False, na=False)]
            
        st.dataframe(tasks_df, use_container_width=True)
        
        if not tasks_df.empty:
            task_ids = tasks_df['id'].tolist()
            selected_id_to_delete = st.selectbox("Select Task ID to Delete", options=task_ids)
            if st.button("Delete Selected Task"):
                conn = sqlite3.connect('app_database.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tasks WHERE id = ?", (selected_id_to_delete,))
                conn.commit()
                conn.close()
                log_activity(f"Deleted task ID: {selected_id_to_delete}", "Tasks")
                st.success(f"Task ID {selected_id_to_delete} deleted successfully!")
                st.rerun()
    else:
        st.info("Koi task database mein available nahi hai.")

elif selected_option == "Kanban Board":
    st.title("📌 Project Kanban Board")
    st.write("Aapke saare tasks status ke mutabiq columns mein display ho rahe hain.")
    
    conn = sqlite3.connect('app_database.db')
    tasks_df = pd.read_sql_query("SELECT * FROM tasks", conn)
    conn.close()
    
    if not tasks_df.empty:
        col_pending, col_progress, col_completed = st.columns(3)
        
        with col_pending:
            st.markdown("### ⏳ Pending")
            pending_tasks = tasks_df[tasks_df['status'] == 'Pending']
            for _, row in pending_tasks.iterrows():
                st.markdown(f"""
                    <div class="kanban-card" style="border-left-color: #EF4444;">
                        <strong>{row['task_name']}</strong><br>
                        <small>Priority: {row['priority']} | Hours: {row['hours']}h</small>
                    </div>
                """, unsafe_allow_html=True)
                
        with col_progress:
            st.markdown("### 🔄 In Progress")
            progress_tasks = tasks_df[tasks_df['status'] == 'In Progress']
            for _, row in progress_tasks.iterrows():
                st.markdown(f"""
                    <div class="kanban-card" style="border-left-color: #F59E0B;">
                        <strong>{row['task_name']}</strong><br>
                        <small>Priority: {row['priority']} | Hours: {row['hours']}h</small>
                    </div>
                """, unsafe_allow_html=True)
                
        with col_completed:
            st.markdown("### ✅ Completed")
            completed_tasks = tasks_df[tasks_df['status'] == 'Completed']
            for _, row in completed_tasks.iterrows():
                st.markdown(f"""
                    <div class="kanban-card" style="border-left-color: #10B981;">
                        <strong>{row['task_name']}</strong><br>
                        <small>Priority: {row['priority']} | Hours: {row['hours']}h</small>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Kanban board ke liye pehle 'Task Manager' se kuch tasks add karein.")

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
                log_activity(f"New feedback received from {user_name}", "Feedback")
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

elif selected_option == "Reports & Export":
    st.title("📥 Enterprise Reports & Multi-Sheet Export")
    st.write("Yahan se aap poore database ka data ek hi Excel workbook mein download kar sakte hain.")
    
    conn = sqlite3.connect('app_database.db')
    tasks_export = pd.read_sql_query("SELECT * FROM tasks", conn)
    feedback_export = pd.read_sql_query("SELECT * FROM feedback", conn)
    logs_export = pd.read_sql_query("SELECT * FROM audit_logs", conn)
    products_export = pd.read_sql_query("SELECT * FROM products", conn)
    orders_export = pd.read_sql_query("SELECT * FROM orders", conn)
    roles_export = pd.read_sql_query("SELECT * FROM user_roles", conn)
    notif_export = pd.read_sql_query("SELECT * FROM notifications", conn)
    notes_export = pd.read_sql_query("SELECT * FROM team_notes", conn)
    conn.close()
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        tasks_export.to_excel(writer, sheet_name='Tasks', index=False)
        feedback_export.to_excel(writer, sheet_name='Feedback', index=False)
        products_export.to_excel(writer, sheet_name='Products', index=False)
        orders_export.to_excel(writer, sheet_name='Orders', index=False)
        roles_export.to_excel(writer, sheet_name='User Roles', index=False)
        notif_export.to_excel(writer, sheet_name='Notifications', index=False)
        notes_export.to_excel(writer, sheet_name='Team Notes', index=False)
        logs_export.to_excel(writer, sheet_name='Audit Logs', index=False)
    excel_data = output.getvalue()
    
    st.download_button(
        label="📥 Download Complete Enterprise Report (.xlsx)",
        data=excel_data,
        file_name='enterprise_master_report.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

elif selected_option == "Audit Logs":
    st.title("🛡️ System Audit & Activity Logs")
    st.write("Yahan aap application ki recent activity aur admin actions track kar sakte hain.")
    
    conn = sqlite3.connect('app_database.db')
    logs_df = pd.read_sql_query("SELECT * FROM audit_logs ORDER BY id DESC", conn)
    conn.close()
    
    if not logs_df.empty:
        st.dataframe(logs_df, use_container_width=True)
    else:
        st.info("Abhi tak koi activity log record nahi hui hai.")

elif selected_option == "Settings":
    st.title("⚙️ System Settings")
    
    dark_mode_toggle = st.toggle("Enable Dark Theme Mode", value=st.session_state.dark_mode)
    if dark_mode_toggle != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode_toggle
        st.rerun()
        
    if st.button("Save Configurations"):
        log_activity("System settings updated.", "Settings")
        st.success("Settings updated successfully!")
