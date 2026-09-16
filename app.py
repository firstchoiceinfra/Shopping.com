import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import io
from datetime import datetime

# Safe Plotly Import with Fallback
try:
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# 1. Database Setup & Initialization
def init_db():
    conn = sqlite3.connect('app_database.db')
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, rating INTEGER, comments TEXT, timestamp TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, task_name TEXT, status TEXT, hours INTEGER, priority TEXT, timestamp TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, timestamp TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, brand TEXT, price REAL, stock INTEGER, category TEXT, description TEXT, features TEXT, image_url TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, items TEXT, subtotal REAL, gst_amount REAL, total_amount REAL, timestamp TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, phone TEXT, total_purchases REAL, joined_date TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS support_tickets (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, subject TEXT, description TEXT, status TEXT, timestamp TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS discussions (id INTEGER PRIMARY KEY AUTOINCREMENT, author TEXT, message TEXT, timestamp TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_roles (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, status TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS notifications (id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT, category TEXT, timestamp TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS team_notes (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, author TEXT, timestamp TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance (id INTEGER PRIMARY KEY AUTOINCREMENT, emp_name TEXT, date TEXT, status TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS payroll (id INTEGER PRIMARY KEY AUTOINCREMENT, emp_name TEXT, basic_salary REAL, bonus REAL, total_payout REAL, month TEXT)''')

    # Seed products if empty
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ("Wireless Mouse", "LogiTech", 1999.00, 50, "Electronics", "Ergonomic wireless mouse with smooth tracking.", "2.4GHz Wireless, 1000 DPI, Long Battery", "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=300"),
            ("Mechanical Keyboard", "Razer", 5999.00, 3, "Electronics", "RGB mechanical gaming keyboard with blue switches.", "RGB Backlit, Clicky Switches, Anti-ghosting", "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=300"),
            ("Gaming Headset", "HyperX", 3799.00, 25, "Electronics", "Immersive sound gaming headset with comfy earcups.", "7.1 Surround Sound, Noise Cancelling Mic", "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=300"),
            ("Notebook", "Classmate", 399.00, 100, "Stationery", "High quality ruled pages notebook for office and college.", "200 Pages, Hardbound, Acid-free paper", "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300"),
            ("Coffee Mug", "Starbucks", 850.00, 4, "Lifestyle", "Ceramic coffee mug for your daily brew.", "Microwave Safe, 350ml Capacity", "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=300")
        ]
        cursor.executemany("INSERT INTO products (name, brand, price, stock, category, description, features, image_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", sample_products)
        conn.commit()

    cursor.execute("SELECT COUNT(*) FROM user_roles")
    if cursor.fetchone()[0] == 0:
        sample_roles = [("admin", "Administrator", "Active"), ("manager_john", "Project Manager", "Active"), ("dev_sara", "Developer", "Active")]
        cursor.executemany("INSERT INTO user_roles (username, role, status) VALUES (?, ?, ?)", sample_roles)
        conn.commit()
        
    conn.close()

init_db()

def log_activity(action_text, notif_category="System"):
    conn = sqlite3.connect('app_database.db')
    cursor = conn.cursor()
    t_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO audit_logs (action, timestamp) VALUES (?, ?)", (action_text, t_time))
    cursor.execute("INSERT INTO notifications (message, category, timestamp) VALUES (?, ?, ?)", (action_text, notif_category, t_time))
    conn.commit()
    conn.close()

# Initialize State
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "lang" not in st.session_state:
    st.session_state.lang = "English"

trans = {
    "English": {
        "dashboard": "Executive Performance Dashboard",
        "store": "Online Product Store",
        "cart": "Shopping Cart & GST Checkout",
        "nav": "Navigation Panel",
        "welcome": "Welcome back! Here are your live database metrics."
    },
    "Hindi": {
        "dashboard": "एग्जीक्यूटिव परफॉरमेंस डैशबोर्ड",
        "store": "ऑनलाइन प्रोडक्ट स्टोर",
        "cart": "शॉपिंग कार्ट और जीएसटी चेकआउट",
        "nav": "नेविगेशन पैनल",
        "welcome": "वापस स्वागत है! यहाँ आपके लाइव डेटाबेस मेट्रिक्स हैं।"
    }
}
t = trans[st.session_state.lang]

# High-Contrast Color Palette Definition
if st.session_state.dark_mode:
    bg_color = "#0B0F19"
    card_bg = "#1E293B"
    text_color = "#F8FAFC"
    sidebar_bg = "#111827"
    sidebar_text = "#F8FAFC"
    input_bg = "#334155"
    input_text = "#FFFFFF"
    table_bg = "#1E293B"
    table_text = "#FFFFFF"
else:
    bg_color = "#FFF7ED"       # Clean soft light orange background
    card_bg = "#FFFFFF"        # Pure white cards for maximum contrast
    text_color = "#1E293B"     # Deep dark slate text for crisp readability
    sidebar_bg = "#F1F5F9"     # Clean soft light gray sidebar
    sidebar_text = "#0F172A"   # Dark high-contrast sidebar text
    input_bg = "#FFFFFF"       # White input background
    input_text = "#0F172A"     # Deep dark text inside inputs so it's clearly visible
    table_bg = "#FFFFFF"
    table_text = "#0F172A"

st.markdown(f"""
    <style>
    .stApp {{ 
        background-color: {bg_color}; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
        color: {text_color}; 
    }}
    section[data-testid="stSidebar"] {{ 
        background-color: {sidebar_bg} !important; 
        color: {sidebar_text} !important; 
        border-right: 1px solid #E2E8F0;
    }}
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] div {{ 
        color: {sidebar_text} !important; 
        font-weight: 500;
    }}
    /* High-Contrast Inputs & Select Boxes */
    input, textarea, select {{ 
        background-color: {input_bg} !important; 
        color: {input_text} !important; 
        border: 1px solid #CBD5E1 !important;
        border-radius: 6px !important;
    }}
    div[data-baseweb="input"] input, div[data-baseweb="select"] div {{ 
        background-color: {input_bg} !important; 
        color: {input_text} !important; 
    }}
    /* Buttons Styling */
    .stButton > button {{ 
        background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%) !important; 
        color: white !important; 
        border-radius: 8px !important; 
        font-weight: bold !important; 
        border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }}
    div[data-testid="stFormSubmitButton"] > button {{ 
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important; 
        color: white !important; 
        font-weight: bold !important;
    }}
    div[data-testid="stDownloadButton"] > button {{ 
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%) !important; 
        color: white !important; 
        font-weight: bold !important;
    }}
    /* Cards & Containers */
    .kanban-card, .product-card, .note-card {{ 
        background-color: {card_bg}; 
        padding: 18px; 
        border-radius: 10px; 
        margin-bottom: 15px; 
        border-left: 6px solid #2575fc; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        color: {text_color}; 
    }}
    /* Tables & DataFrames */
    .stDataFrame, .stTable {{ 
        background-color: {table_bg} !important; 
        color: {table_text} !important; 
    }}
    div[data-testid="stDataFrame"] div {{ 
        color: {table_text} !important; 
    }}
    </style>
""", unsafe_allow_html=True)

if "cart" not in st.session_state:
    st.session_state.cart = {}

# Sidebar Authentication & Language
st.sidebar.title("🔐 Access Control")
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.session_state.current_user = "admin"
            st.session_state.user_role = "Administrator"
            st.rerun()
        else:
            st.sidebar.error("Use admin / admin123")
    st.stop()
else:
    st.sidebar.success(f"User: {st.session_state.current_user}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

st.sidebar.markdown("---")
lang_choice = st.sidebar.selectbox("🌐 Language / भाषा", ["English", "Hindi"], index=0 if st.session_state.lang=="English" else 1)
if lang_choice != st.session_state.lang:
    st.session_state.lang = lang_choice
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.title(f"🎛️ {t['nav']}")
selected_option = st.sidebar.radio(
    "Go to", 
    [
        "Dashboard", 
        "🔔 Notifications Center",
        "📌 Team Collaboration Notes",
        "💬 Live Team Chat Board",
        "🎧 Support Helpdesk Tickets",
        "👥 Employee Attendance & Payroll",
        "🔍 Global Master Search", 
        "🛍️ E-Commerce Store", 
        "🛠️ Manage & Edit Products",
        "🛒 Shopping Cart & GST Checkout", 
        "📦 Order History & Tax Invoices",
        "👥 Customer CRM & Directory",
        "👥 User Roles & Permissions",
        "Database Analytics & Sales", 
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

# Navigation Options Implementation
if selected_option == "Dashboard":
    st.title(f"📊 {t['dashboard']}")
    st.write(t['welcome'])
    conn = sqlite3.connect('app_database.db')
    t_count = pd.read_sql_query("SELECT COUNT(*) as total FROM tasks", conn)['total'].iloc[0]
    total_products = pd.read_sql_query("SELECT COUNT(*) as total FROM products", conn)['total'].iloc[0]
    total_orders = pd.read_sql_query("SELECT COUNT(*) as total FROM orders", conn)['total'].iloc[0]
    conn.close()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Tasks", t_count)
    col2.metric("Products", total_products)
    col3.metric("Orders", total_orders)

elif selected_option == "🔔 Notifications Center":
    st.title("🔔 Notifications Center")
    conn = sqlite3.connect('app_database.db')
    notif_df = pd.read_sql_query("SELECT * FROM notifications ORDER BY id DESC", conn)
    conn.close()
    for _, row in notif_df.iterrows():
        st.info(f"**[{row['category']}]** {row['message']} — *{row['timestamp']}*")

elif selected_option == "📌 Team Collaboration Notes":
    st.title("📌 Team Notes")
    with st.form("note"):
        title = st.text_input("Title")
        content = st.text_area("Content")
        if st.form_submit_button("Publish"):
            conn = sqlite3.connect('app_database.db')
            conn.cursor().execute("INSERT INTO team_notes (title, content, author, timestamp) VALUES (?, ?, ?, ?)",
                                  (title, content, st.session_state.current_user, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
            st.success("Published!")
            st.rerun()

elif selected_option == "💬 Live Team Chat Board":
    st.title("💬 Live Team Chat")
    with st.form("chat"):
        msg = st.text_input("Message")
        if st.form_submit_button("Send"):
            conn = sqlite3.connect('app_database.db')
            conn.cursor().execute("INSERT INTO discussions (author, message, timestamp) VALUES (?, ?, ?)",
                                  (st.session_state.current_user, msg, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
            st.rerun()
    conn = sqlite3.connect('app_database.db')
    for _, c in pd.read_sql_query("SELECT * FROM discussions ORDER BY id DESC", conn).iterrows():
        st.info(f"**{c['author']}**: {c['message']} — *{c['timestamp']}*")
    conn.close()

elif selected_option == "🎧 Support Helpdesk Tickets":
    st.title("🎧 Support Ticketing System")
    with st.form("tick"):
        cust = st.text_input("Customer Name")
        subj = st.text_input("Subject")
        desc = st.text_area("Description")
        if st.form_submit_button("Submit"):
            conn = sqlite3.connect('app_database.db')
            conn.cursor().execute("INSERT INTO support_tickets (customer_name, subject, description, status, timestamp) VALUES (?, ?, ?, 'Open', ?)",
                                  (cust, subj, desc, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
            st.success("Ticket raised!")
            st.rerun()

elif selected_option == "👥 Employee Attendance & Payroll":
    st.title("👥 Employee Attendance & Payroll Management")
    tab1, tab2 = st.tabs(["Attendance", "Payroll"])
    with tab1:
        with st.form("att"):
            emp = st.text_input("Employee Name")
            stat = st.selectbox("Status", ["Present", "Absent", "Half-Day"])
            if st.form_submit_button("Mark Attendance"):
                conn = sqlite3.connect('app_database.db')
                conn.cursor().execute("INSERT INTO attendance (emp_name, date, status) VALUES (?, ?, ?)",
                                      (emp, datetime.now().strftime("%Y-%m-%d"), stat))
                conn.commit()
                conn.close()
                st.success("Attendance marked!")
        conn = sqlite3.connect('app_database.db')
        st.dataframe(pd.read_sql_query("SELECT * FROM attendance", conn), use_container_width=True)
        conn.close()
    with tab2:
        with st.form("pay"):
            emp_p = st.text_input("Staff Name")
            basic = st.number_input("Basic Salary (₹)", value=25000.0)
            bonus = st.number_input("Bonus (₹)", value=2000.0)
            if st.form_submit_button("Generate Payslip"):
                total = basic + bonus
                conn = sqlite3.connect('app_database.db')
                conn.cursor().execute("INSERT INTO payroll (emp_name, basic_salary, bonus, total_payout, month) VALUES (?, ?, ?, ?, ?)",
                                      (emp_p, basic, bonus, total, datetime.now().strftime("%B %Y")))
                conn.commit()
                conn.close()
                st.success(f"Payslip generated! Total Payout: ₹{total:,.2f}")
        conn = sqlite3.connect('app_database.db')
        st.dataframe(pd.read_sql_query("SELECT * FROM payroll", conn), use_container_width=True)
        conn.close()

elif selected_option == "🔍 Global Master Search":
    st.title("🔍 Global Master Search")
    q = st.text_input("Search keyword...")
    if q:
        conn = sqlite3.connect('app_database.db')
        df = pd.read_sql_query("SELECT * FROM products", conn)
        conn.close()
        st.dataframe(df[df.apply(lambda row: row.astype(str).str.contains(q, case=False).any(), axis=1)], use_container_width=True)

elif selected_option == "🛍️ E-Commerce Store":
    st.title(f"🛍️ {t['store']}")
    conn = sqlite3.connect('app_database.db')
    prods = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    cols = st.columns(3)
    for i, row in prods.iterrows():
        with cols[i % 3]:
            st.markdown(f"""
                <div class="product-card">
                    <h3>{row['name']}</h3>
                    <p><b>Brand:</b> {row['brand']}</p>
                    <p><b>Price:</b> ₹{row['price']:,.2f}</p>
                    <p><b>Stock:</b> {row['stock']}</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Add to Cart", key=f"pc_{row['id']}"):
                st.session_state.cart[row['id']] = st.session_state.cart.get(row['id'], 0) + 1
                st.success("Added!")

elif selected_option == "🛠️ Manage & Edit Products":
    st.title("🛠️ Manage Inventory")
    with st.form("add_p"):
        name = st.text_input("Name")
        brand = st.text_input("Brand")
        price = st.number_input("Price (₹)", value=1000.0)
        stock = st.number_input("Stock", value=10)
        if st.form_submit_button("Add"):
            conn = sqlite3.connect('app_database.db')
            conn.cursor().execute("INSERT INTO products (name, brand, price, stock, category, description, features, image_url) VALUES (?, ?, ?, ?, 'General', 'Desc', 'Feat', '')",
                                  (name, brand, price, stock))
            conn.commit()
            conn.close()
            st.success("Added!")
            st.rerun()

elif selected_option == "🛒 Shopping Cart & GST Checkout":
    st.title(f"🛒 {t['cart']}")
    if st.session_state.cart:
        conn = sqlite3.connect('app_database.db')
        prods = pd.read_sql_query("SELECT * FROM products", conn)
        conn.close()
        subtotal = 0.0
        items = []
        for pid, qty in st.session_state.cart.items():
            r = prods[prods['id'] == pid].iloc[0]
            sub = r['price'] * qty
            subtotal += sub
            items.append({"Product": r['name'], "Price": r['price'], "Qty": qty, "Subtotal": sub})
        st.dataframe(pd.DataFrame(items), use_container_width=True)
        gst = subtotal * 0.18
        total = subtotal + gst
        st.markdown(f"### Subtotal: ₹{subtotal:,.2f} | GST (18%): ₹{gst:,.2f} | **Total: ₹{total:,.2f}**")
        c_name = st.text_input("Customer Name", value="Test User")
        if st.button("Place Order"):
            conn = sqlite3.connect('app_database.db')
            conn.cursor().execute("INSERT INTO orders (customer_name, items, subtotal, gst_amount, total_amount, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                                  (c_name, str(items), subtotal, gst, total, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
            st.success("Order Placed!")
            st.session_state.cart = {}
            st.rerun()
    else:
        st.info("Cart is empty.")

elif selected_option == "📦 Order History & Tax Invoices":
    st.title("📦 Order History & Invoices")
    conn = sqlite3.connect('app_database.db')
    orders = pd.read_sql_query("SELECT * FROM orders", conn)
    conn.close()
    if not orders.empty:
        st.dataframe(orders, use_container_width=True)

elif selected_option == "👥 Customer CRM & Directory":
    st.title("👥 Customer CRM")
    conn = sqlite3.connect('app_database.db')
    st.dataframe(pd.read_sql_query("SELECT * FROM customers", conn), use_container_width=True)
    conn.close()

elif selected_option == "👥 User Roles & Permissions":
    st.title("👥 User Roles")
    conn = sqlite3.connect('app_database.db')
    st.dataframe(pd.read_sql_query("SELECT * FROM user_roles", conn), use_container_width=True)
    conn.close()

elif selected_option == "Database Analytics & Sales":
    st.title("📊 Sales Analytics")
    conn = sqlite3.connect('app_database.db')
    orders = pd.read_sql_query("SELECT * FROM orders", conn)
    conn.close()
    if not orders.empty:
        if HAS_PLOTLY:
            fig = px.bar(orders, x='id', y='total_amount', title="Order-wise Revenue Breakdown (₹)", color='total_amount')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.bar_chart(orders.set_index('id')['total_amount'])
    else:
        st.info("No data for analytics yet.")

elif selected_option == "Task Manager (CRUD)":
    st.title("📝 Task Manager")
    with st.form("t_add"):
        t_name = st.text_input("Task Name")
        if st.form_submit_button("Add Task"):
            conn = sqlite3.connect('app_database.db')
            conn.cursor().execute("INSERT INTO tasks (task_name, status, hours, priority, timestamp) VALUES (?, 'Pending', 5, 'Medium', ?)",
                                  (t_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
            st.success("Task added!")
            st.rerun()
    conn = sqlite3.connect('app_database.db')
    st.dataframe(pd.read_sql_query("SELECT * FROM tasks", conn), use_container_width=True)
    conn.close()

elif selected_option == "Kanban Board":
    st.title("📌 Kanban Board")
    conn = sqlite3.connect('app_database.db')
    t = pd.read_sql_query("SELECT * FROM tasks", conn)
    conn.close()
    if not t.empty:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("### Pending")
            for _, r in t[t['status'] == 'Pending'].iterrows():
                st.markdown(f"<div class='kanban-card'><b>{r['task_name']}</b></div>", unsafe_allow_html=True)
        with c2:
            st.markdown("### In Progress")
            for _, r in t[t['status'] == 'In Progress'].iterrows():
                st.markdown(f"<div class='kanban-card'><b>{r['task_name']}</b></div>", unsafe_allow_html=True)
        with c3:
            st.markdown("### Completed")
            for _, r in t[t['status'] == 'Completed'].iterrows():
                st.markdown(f"<div class='kanban-card'><b>{r['task_name']}</b></div>", unsafe_allow_html=True)

elif selected_option == "File Uploader":
    st.title("📂 Dataset Uploader")
    f = st.file_uploader("Upload CSV", type="csv")
    if f:
        st.dataframe(pd.read_csv(f), use_container_width=True)

elif selected_option == "Feedback":
    st.title("💬 Feedback")
    with st.form("fb"):
        name = st.text_input("Name")
        com = st.text_area("Comments")
        if st.form_submit_button("Submit"):
            conn = sqlite3.connect('app_database.db')
            conn.cursor().execute("INSERT INTO feedback (name, email, rating, comments, timestamp) VALUES (?, 'test@test.com', 5, ?, ?)",
                                  (name, com, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
            st.success("Feedback submitted!")

elif selected_option == "View Saved Feedback":
    st.title("📋 Saved Feedbacks")
    conn = sqlite3.connect('app_database.db')
    st.dataframe(pd.read_sql_query("SELECT * FROM feedback", conn), use_container_width=True)
    conn.close()

elif selected_option == "Reports & Export":
    st.title("📥 Reports Export")
    conn = sqlite3.connect('app_database.db')
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        pd.read_sql_query("SELECT * FROM tasks", conn).to_excel(writer, sheet_name='Tasks', index=False)
        pd.read_sql_query("SELECT * FROM products", conn).to_excel(writer, sheet_name='Products', index=False)
    conn.close()
    st.download_button("Download Excel Report", data=out.getvalue(), file_name="report.xlsx")

elif selected_option == "Audit Logs":
    st.title("🛡️ Audit Logs")
    conn = sqlite3.connect('app_database.db')
    st.dataframe(pd.read_sql_query("SELECT * FROM audit_logs ORDER BY id DESC", conn), use_container_width=True)
    conn.close()

elif selected_option == "Settings":
    st.title("⚙️ Settings & Database Backup")
    dm = st.toggle("Enable Dark Theme", value=st.session_state.dark_mode)
    if dm != st.session_state.dark_mode:
        st.session_state.dark_mode = dm
        st.rerun()
        
    st.markdown("---")
    st.subheader("💾 Database Backup & Restore")
    with open("app_database.db", "rb") as f:
        st.download_button("Download Database Backup (.db)", data=f, file_name="app_database_backup.db")
        
    up_db = st.file_uploader("Restore Database (.db file)", type="db")
    if up_db:
        with open("app_database.db", "wb") as f:
            f.write(up_db.getbuffer())
        st.success("Database restored successfully! Please restart the app.")