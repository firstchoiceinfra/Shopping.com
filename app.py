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
    
    # Tasks Table
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
            brand TEXT,
            price REAL,
            stock INTEGER,
            category TEXT,
            description TEXT,
            features TEXT,
            image_url TEXT
        )
    ''')
    
    # E-Commerce Orders Table (With GST breakdown)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            items TEXT,
            subtotal REAL,
            gst_amount REAL,
            total_amount REAL,
            timestamp TEXT
        )
    ''')
    
    # Customer CRM Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            total_purchases REAL,
            joined_date TEXT
        )
    ''')
    
    # Support Tickets Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS support_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            subject TEXT,
            description TEXT,
            status TEXT,
            timestamp TEXT
        )
    ''')
    
    # Real-Time Discussion Board Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS discussions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT,
            message TEXT,
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
    
    # Seed default products if empty
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
    cursor.execute("INSERT INTO audit_logs (action, timestamp) VALUES (?, ?)", (action_text, t_time))
    cursor.execute("INSERT INTO notifications (message, category, timestamp) VALUES (?, ?, ?)", (action_text, notif_category, t_time))
    conn.commit()
    conn.close()

# Initialize Theme State
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

bg_color = "#0F172A" if st.session_state.dark_mode else "#FFF7ED"
card_bg = "#1E293B" if st.session_state.dark_mode else "#FFFFFF"
text_color = "#F8FAFC" if st.session_state.dark_mode else "#334155"

sidebar_bg = "#1E293B" if st.session_state.dark_mode else "#F1F5F9"
sidebar_text = "#FFFFFF" if st.session_state.dark_mode else "#1E293B"

table_bg = "#1E293B" if st.session_state.dark_mode else "#FFFFFF"
table_text = "#FFFFFF" if st.session_state.dark_mode else "#000000"
input_bg = "#334155" if st.session_state.dark_mode else "#FFFFFF"
input_text = "#FFFFFF" if st.session_state.dark_mode else "#000000"

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
    }}
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] div {{
        color: {sidebar_text} !important;
    }}
    .stButton > button {{
        background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15) !important;
        transition: all 0.3s ease-in-out;
    }}
    .stButton > button:hover {{
        background: linear-gradient(135deg, #2575fc 0%, #6a11cb 100%) !important;
        color: white !important;
        transform: translateY(-2px);
    }}
    div[data-testid="stFormSubmitButton"] > button {{
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important;
        color: white !important;
    }}
    div[data-testid="stDownloadButton"] > button {{
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%) !important;
        color: white !important;
    }}
    input, textarea, select {{
        background-color: {input_bg} !important;
        color: {input_text} !important;
    }}
    div[data-baseweb="input"] input {{
        background-color: {input_bg} !important;
        color: {input_text} !important;
    }}
    div[data-baseweb="select"] div {{
        background-color: {input_bg} !important;
        color: {input_text} !important;
    }}
    .kanban-card, .product-card, .note-card {{
        background-color: {card_bg};
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 10px;
        border-left: 5px solid #3B82F6;
        color: {text_color};
    }}
    .stDataFrame, .stTable {{
        background-color: {table_bg};
        color: {table_text};
    }}
    div[data-testid="stDataFrame"] div {{
        color: {table_text} !important;
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

# Sidebar & Mock Authentication
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
            log_activity("Admin logged in successfully.", "Auth")
            st.rerun()
        elif username == "manager" and password == "manager123":
            st.session_state.logged_in = True
            st.session_state.current_user = "manager_john"
            st.session_state.user_role = "Project Manager"
            log_activity("Manager logged in successfully.", "Auth")
            st.rerun()
        else:
            st.sidebar.error("Try admin/admin123 or manager/manager123")
    st.stop()
else:
    st.sidebar.success(f"Logged in as {st.session_state.current_user} ({st.session_state.user_role})")
    if st.sidebar.button("Logout"):
        log_activity("User logged out.", "Auth")
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
        "💬 Live Team Chat Board",
        "🎧 Support Helpdesk Tickets",
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

# Main Navigation Logic
if selected_option == "Dashboard":
    st.title("📊 Executive Performance Dashboard")
    conn = sqlite3.connect('app_database.db')
    t_count = pd.read_sql_query("SELECT COUNT(*) as total FROM tasks", conn)['total'].iloc[0]
    completed_tasks = pd.read_sql_query("SELECT COUNT(*) as total FROM tasks WHERE status = 'Completed'", conn)['total'].iloc[0]
    total_products = pd.read_sql_query("SELECT COUNT(*) as total FROM products", conn)['total'].iloc[0]
    total_orders = pd.read_sql_query("SELECT COUNT(*) as total FROM orders", conn)['total'].iloc[0]
    low_stock = pd.read_sql_query("SELECT COUNT(*) as total FROM products WHERE stock < 5", conn)['total'].iloc[0]
    open_tickets = pd.read_sql_query("SELECT COUNT(*) as total FROM support_tickets WHERE status = 'Open'", conn)['total'].iloc[0]
    conn.close()
    
    if low_stock > 0:
        st.warning(f"⚠️ **Inventory Alert:** {low_stock} products are running low on stock (< 5 units)!")
    if open_tickets > 0:
        st.info(f"🎧 **Support Desk:** {open_tickets} customer support tickets are currently open.")
        
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Tasks", t_count)
    col2.metric("Products", total_products)
    col3.metric("Orders", total_orders)
    col4.metric("Open Tickets", open_tickets)
    
    st.markdown("---")
    progress = int((completed_tasks / t_count) * 100) if t_count > 0 else 0
    st.progress(progress, text=f"Project Milestone Completion: {progress}%")

elif selected_option == "🔔 Notifications Center":
    st.title("🔔 Real-Time Notifications Center")
    conn = sqlite3.connect('app_database.db')
    notif_df = pd.read_sql_query("SELECT * FROM notifications ORDER BY id DESC", conn)
    conn.close()
    if st.button("Clear Notifications"):
        conn = sqlite3.connect('app_database.db')
        conn.cursor().execute("DELETE FROM notifications")
        conn.commit()
        conn.close()
        st.rerun()
    for _, row in notif_df.iterrows():
        st.info(f"**[{row['category']}]** {row['message']} — *{row['timestamp']}*")

elif selected_option == "📌 Team Collaboration Notes":
    st.title("📌 Team Collaboration Notes")
    with st.form("note_form"):
        title = st.text_input("Title")
        content = st.text_area("Content")
        if st.form_submit_button("Post Note"):
            conn = sqlite3.connect('app_database.db')
            conn.cursor().execute("INSERT INTO team_notes (title, content, author, timestamp) VALUES (?, ?, ?, ?)",
                                  (title, content, st.session_state.current_user, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
            st.success("Note published!")
            st.rerun()
    conn = sqlite3.connect('app_database.db')
    notes = pd.read_sql_query("SELECT * FROM team_notes ORDER BY id DESC", conn)
    conn.close()
    for _, r in notes.iterrows():
        st.markdown(f"<div class='note-card'><h4>{r['title']}</h4><p>{r['content']}</p><small>By {r['author']} at {r['timestamp']}</small></div>", unsafe_allow_html=True)

elif selected_option == "💬 Live Team Chat Board":
    st.title("💬 Real-Time Team Chat")
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
    chats = pd.read_sql_query("SELECT * FROM discussions ORDER BY id DESC", conn)
    conn.close()
    for _, c in chats.iterrows():
        st.info(f"**{c['author']}**: {c['message']} — *{c['timestamp']}*")

elif selected_option == "🎧 Support Helpdesk Tickets":
    st.title("🎧 Customer Support Ticketing System")
    with st.form("ticket_form"):
        cust = st.text_input("Customer Name")
        subj = st.text_input("Subject / Issue")
        desc = st.text_area("Detailed Description")
        if st.form_submit_button("Raise Ticket"):
            conn = sqlite3.connect('app_database.db')
            conn.cursor().execute("INSERT INTO support_tickets (customer_name, subject, description, status, timestamp) VALUES (?, ?, ?, 'Open', ?)",
                                  (cust, subj, desc, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
            st.success("Support ticket registered successfully!")
            st.rerun()
    
    st.markdown("---")
    st.subheader("Manage Active Support Tickets")
    conn = sqlite3.connect('app_database.db')
    tickets = pd.read_sql_query("SELECT * FROM support_tickets", conn)
    conn.close()
    if not tickets.empty:
        st.dataframe(tickets, use_container_width=True)
        t_id = st.selectbox("Select Ticket ID to Update Status", options=tickets['id'].tolist())
        new_stat = st.selectbox("New Status", ["Open", "In Progress", "Resolved"])
        if st.button("Update Ticket Status"):
            conn = sqlite3.connect('app_database.db')
            conn.cursor().execute("UPDATE support_tickets SET status = ? WHERE id = ?", (new_stat, t_id))
            conn.commit()
            conn.close()
            st.success("Ticket status updated!")
            st.rerun()
    else:
        st.info("No active support tickets.")

elif selected_option == "🔍 Global Master Search":
    st.title("🔍 Global Database Search")
    q = st.text_input("Keyword search...")
    if q:
        conn = sqlite3.connect('app_database.db')
        p = pd.read_sql_query("SELECT * FROM products", conn)
        t = pd.read_sql_query("SELECT * FROM tasks", conn)
        conn.close()
        st.subheader("Products Match")
        st.dataframe(p[p.apply(lambda row: row.astype(str).str.contains(q, case=False).any(), axis=1)], use_container_width=True)
        st.subheader("Tasks Match")
        st.dataframe(t[t.apply(lambda row: row.astype(str).str.contains(q, case=False).any(), axis=1)], use_container_width=True)

elif selected_option == "🛍️ E-Commerce Store":
    st.title("🛍️ Online Product Store (With Barcodes & QR codes)")
    conn = sqlite3.connect('app_database.db')
    prods = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    
    cols = st.columns(3)
    for i, row in prods.iterrows():
        with cols[i % 3]:
            img = row['image_url'] if row['image_url'] else "https://via.placeholder.com/300"
            st.markdown(f"""
                <div class="product-card">
                    <img src="{img}" style="width:100%; height:140px; object-fit:cover; border-radius:6px;">
                    <h3>{row['name']}</h3>
                    <p><b>Brand:</b> {row['brand']} | <b>SKU-BARCODE:</b> SKU-{row['id']:03d}</p>
                    <p><b>Price:</b> ₹{row['price']:,.2f}</p>
                    <p><b>Stock:</b> {row['stock']}</p>
                    <p>{row['description']}</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Add to Cart", key=f"p_{row['id']}"):
                st.session_state.cart[row['id']] = st.session_state.cart.get(row['id'], 0) + 1
                st.success(f"Added {row['name']} to cart!")

elif selected_option == "🛠️ Manage & Edit Products":
    st.title("🛠️ Product Inventory Management")
    if st.session_state.user_role != "Administrator":
        st.error("Access Denied: Only Administrators can add or edit inventory items.")
    else:
        with st.form("add_prod"):
            name = st.text_input("Name")
            brand = st.text_input("Brand")
            price = st.number_input("Price (₹)", value=500.0)
            stock = st.number_input("Stock", value=10)
            cat = st.text_input("Category")
            desc = st.text_area("Description")
            feats = st.text_input("Features")
            img = st.text_input("Image URL")
            if st.form_submit_button("Add Product"):
                conn = sqlite3.connect('app_database.db')
                conn.cursor().execute("INSERT INTO products (name, brand, price, stock, category, description, features, image_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                      (name, brand, price, stock, cat, desc, feats, img))
                conn.commit()
                conn.close()
                st.success("Product added successfully!")
                st.rerun()

elif selected_option == "🛒 Shopping Cart & GST Checkout":
    st.title("🛒 Shopping Cart & GST Tax Calculator")
    if st.session_state.cart:
        conn = sqlite3.connect('app_database.db')
        prods = pd.read_sql_query("SELECT * FROM products", conn)
        conn.close()
        
        items, subtotal = [], 0.0
        for pid, qty in st.session_state.cart.items():
            r = prods[prods['id'] == pid].iloc[0]
            sub = r['price'] * qty
            subtotal += sub
            items.append({"Product": f"{r['name']} ({r['brand']})", "Price": r['price'], "Qty": qty, "Subtotal": sub})
            
        st.dataframe(pd.DataFrame(items), use_container_width=True)
        
        # Calculate 18% GST (CGST 9% + SGST 9%)
        gst = subtotal * 0.18
        cgst = gst / 2
        sgst = gst / 2
        grand_total = subtotal + gst
        
        st.markdown(f"""
            **Subtotal:** ₹{subtotal:,.2f}  
            **CGST (9%):** ₹{cgst:,.2f}  
            **SGST (9%):** ₹{sgst:,.2f}  
            ### **Grand Total (Incl. GST): ₹{grand_total:,.2f}**
        """)
        
        c_name = st.text_input("Customer Name", value="Admin User")
        c_email = st.text_input("Email", value="admin@shop.com")
        c_phone = st.text_input("Phone", value="9876543210")
        
        if st.button("Confirm Order & Generate Tax Invoice"):
            conn = sqlite3.connect('app_database.db')
            cur = conn.cursor()
            item_str = ", ".join([f"{i['Product']} (x{i['Qty']})" for i in items])
            cur.execute("INSERT INTO orders (customer_name, items, subtotal, gst_amount, total_amount, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                        (c_name, item_str, subtotal, gst, grand_total, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            # CRM update
            cur.execute("SELECT id, total_purchases FROM customers WHERE name = ?", (c_name,))
            cm = cur.fetchone()
            if cm:
                cur.execute("UPDATE customers SET total_purchases = ? WHERE id = ?", (cm[1] + grand_total, cm[0]))
            else:
                cur.execute("INSERT INTO customers (name, email, phone, total_purchases, joined_date) VALUES (?, ?, ?, ?, ?)",
                            (c_name, c_email, c_phone, grand_total, datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            conn.close()
            log_activity(f"Order placed by {c_name} for ₹{grand_total:,.2f} (GST Included)", "Store")
            st.success("Order confirmed successfully!")
            st.session_state.cart = {}
            st.rerun()
    else:
        st.info("Cart is empty.")

elif selected_option == "📦 Order History & Tax Invoices":
    st.title("📦 Orders & Professional GST Invoices")
    conn = sqlite3.connect('app_database.db')
    orders = pd.read_sql_query("SELECT * FROM orders", conn)
    conn.close()
    if not orders.empty:
        st.dataframe(orders, use_container_width=True)
        oid = st.selectbox("Select Order ID for Tax Invoice", options=orders['id'].tolist())
        o = orders[orders['id'] == oid].iloc[0]
        
        inv = f"""
        ==================================================
                 OFFICIAL GST TAX INVOICE                 
        ==================================================
        Invoice No: GST-INV-{o['id']:04d}
        Date: {o['timestamp']}
        Customer: {o['customer_name']}
        --------------------------------------------------
        Items Purchased:
        {o['items']}
        --------------------------------------------------
        Subtotal:     ₹{o['subtotal']:,.2f}
        GST (18%):    ₹{o['gst_amount']:,.2f}
        --------------------------------------------------
        Grand Total:  ₹{o['total_amount']:,.2f}
        ==================================================
              Thank you for shopping with us!             
        ==================================================
        """
        st.text_area("Invoice Format", value=inv, height=220)
        st.download_button("Download GST Invoice", data=inv, file_name=f"gst_invoice_{o['id']}.txt")
    else:
        st.info("No order history found.")

elif selected_option == "👥 Customer CRM & Directory":
    st.title("👥 Customer CRM Suite")
    conn = sqlite3.connect('app_database.db')
    c_df = pd.read_sql_query("SELECT * FROM customers", conn)
    conn.close()
    if not c_df.empty:
        st.dataframe(c_df, use_container_width=True)
    else:
        st.info("No customers recorded yet.")

elif selected_option == "👥 User Roles & Permissions":
    st.title("👥 RBAC Security & Roles")
    conn = sqlite3.connect('app_database.db')
    r_df = pd.read_sql_query("SELECT * FROM user_roles", conn)
    conn.close()
    st.dataframe(r_df, use_container_width=True)

elif selected_option == "Database Analytics & Sales":
    st.title("📊 Sales & Revenue Analytics")
    conn = sqlite3.connect('app_database.db')
    o = pd.read_sql_query("SELECT * FROM orders", conn)
    conn.close()
    if not o.empty:
        st.bar_chart(o.set_index('id')['total_amount'])
    else:
        st.info("No sales data available.")

elif selected_option == "Task Manager (CRUD)":
    st.title("📝 Task Manager")
    with st.form("task"):
        t_name = st.text_input("Task Name")
        stat = st.selectbox("Status", ["Pending", "In Progress", "Completed"])
        hrs = st.number_input("Hours", value=5)
        pri = st.selectbox("Priority", ["Low", "Medium", "High"])
        if st.form_submit_button("Add Task"):
            conn = sqlite3.connect('app_database.db')
            conn.cursor().execute("INSERT INTO tasks (task_name, status, hours, priority, timestamp) VALUES (?, ?, ?, ?, ?)",
                                  (t_name, stat, hrs, pri, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
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
    st.title("💬 Feedback Form")
    with st.form("fb"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        rating = st.slider("Rating", 1, 5, 5)
        com = st.text_area("Comments")
        if st.form_submit_button("Submit"):
            conn = sqlite3.connect('app_database.db')
            conn.cursor().execute("INSERT INTO feedback (name, email, rating, comments, timestamp) VALUES (?, ?, ?, ?, ?)",
                                  (name, email, rating, com, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
            st.success("Feedback saved!")

elif selected_option == "View Saved Feedback":
    st.title("📋 Saved Feedbacks")
    conn = sqlite3.connect('app_database.db')
    st.dataframe(pd.read_sql_query("SELECT * FROM feedback", conn), use_container_width=True)
    conn.close()

elif selected_option == "Reports & Export":
    st.title("📥 Multi-Sheet Enterprise Export")
    conn = sqlite3.connect('app_database.db')
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        pd.read_sql_query("SELECT * FROM tasks", conn).to_excel(writer, sheet_name='Tasks', index=False)
        pd.read_sql_query("SELECT * FROM products", conn).to_excel(writer, sheet_name='Products', index=False)
        pd.read_sql_query("SELECT * FROM orders", conn).to_excel(writer, sheet_name='Orders', index=False)
    conn.close()
    st.download_button("Download Master Excel Report", data=out.getvalue(), file_name="master_report.xlsx")

elif selected_option == "Audit Logs":
    st.title("🛡️ Audit Logs")
    conn = sqlite3.connect('app_database.db')
    st.dataframe(pd.read_sql_query("SELECT * FROM audit_logs ORDER BY id DESC", conn), use_container_width=True)
    conn.close()

elif selected_option == "Settings":
    st.title("⚙️ Settings")
    dm = st.toggle("Enable Dark Theme", value=st.session_state.dark_mode)
    if dm != st.session_state.dark_mode:
        st.session_state.dark_mode = dm
        st.rerun()
