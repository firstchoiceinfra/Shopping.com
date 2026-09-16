import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import sqlite3
import io
import math
import json
import plotly.express as px
from datetime import datetime

# ============================================================
# CONFIG
# ============================================================
st.set_page_config(page_title="LocalBazaar - Har Gali Ka Bazaar", page_icon="🛍️", layout="wide")

COMMISSION_RATE = 0.03  # 3% platform commission, deducted from shopkeeper wallet
DB_PATH = "app_database.db"

# ============================================================
# DATABASE SETUP
# ============================================================
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # ---- Core marketplace tables ----
    cur.execute('''CREATE TABLE IF NOT EXISTS shopkeepers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        shop_name TEXT,
        owner_name TEXT,
        phone TEXT,
        area TEXT,
        city TEXT,
        lat REAL,
        lon REAL,
        wallet_balance REAL DEFAULT 0,
        free_delivery_threshold REAL DEFAULT 500,
        is_active INTEGER DEFAULT 1,
        created_at TEXT
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS customers_acc (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        full_name TEXT,
        phone TEXT,
        default_lat REAL,
        default_lon REAL,
        default_address TEXT,
        created_at TEXT
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        shopkeeper_id INTEGER,
        name TEXT,
        brand TEXT,
        category TEXT,
        mrp REAL,
        price REAL,
        stock INTEGER,
        description TEXT,
        features TEXT,
        image_url TEXT,
        created_at TEXT
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_group TEXT,
        customer_name TEXT,
        customer_lat REAL,
        customer_lon REAL,
        shopkeeper_id INTEGER,
        shop_name TEXT,
        items TEXT,
        distance_km REAL,
        subtotal REAL,
        delivery_charge REAL,
        gst_amount REAL,
        commission_amount REAL,
        total_amount REAL,
        status TEXT,
        timestamp TEXT
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS wallet_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        shopkeeper_id INTEGER,
        txn_type TEXT,
        amount REAL,
        balance_after REAL,
        note TEXT,
        timestamp TEXT
    )''')

    # ---- Legacy / supporting tables kept from original app ----
    cur.execute('''CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, rating INTEGER, comments TEXT, timestamp TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, task_name TEXT, status TEXT, hours INTEGER, priority TEXT, timestamp TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, timestamp TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS support_tickets (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, subject TEXT, description TEXT, status TEXT, timestamp TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS discussions (id INTEGER PRIMARY KEY AUTOINCREMENT, author TEXT, message TEXT, timestamp TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS notifications (id INTEGER PRIMARY KEY AUTOINCREMENT, message TEXT, category TEXT, timestamp TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS team_notes (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, author TEXT, timestamp TEXT)''')

    conn.commit()

    # ---- Seed a demo admin + demo shopkeepers so the app is usable immediately ----
    cur.execute("SELECT COUNT(*) FROM shopkeepers")
    if cur.fetchone()[0] == 0:
        demo_shops = [
            ("kirana_mumbai", "shop123", "Sharma Kirana Store", "Ramesh Sharma", "9820000001",
             "Andheri West", "Mumbai", 19.1358, 72.8267, 1000.0, 500.0, 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ("electro_mumbai", "shop123", "Patel Electronics", "Kiran Patel", "9820000002",
             "Andheri East", "Mumbai", 19.1197, 72.8697, 1500.0, 1000.0, 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ("kirana_nagpur", "shop123", "Deshmukh General Store", "Vinod Deshmukh", "9420000003",
             "Sitabuldi", "Nagpur", 21.1466, 79.0849, 800.0, 500.0, 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ]
        cur.executemany('''INSERT INTO shopkeepers
            (username, password, shop_name, owner_name, phone, area, city, lat, lon, wallet_balance, free_delivery_threshold, is_active, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''', demo_shops)
        conn.commit()

        shop_ids = pd.read_sql_query("SELECT id, city FROM shopkeepers", conn)
        mumbai_ids = shop_ids[shop_ids['city'] == 'Mumbai']['id'].tolist()
        nagpur_ids = shop_ids[shop_ids['city'] == 'Nagpur']['id'].tolist()

        demo_products = []
        mumbai_catalog = [
            ("Basmati Rice 5kg", "India Gate", "Grocery", 650, 599, 40, "Premium long grain basmati rice.", "5kg pack, Aged rice, Extra long grain", "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=300"),
            ("Toor Dal 1kg", "Tata Sampann", "Grocery", 180, 165, 60, "Unpolished toor dal, rich in protein.", "1kg pack, Unpolished, High protein", "https://images.unsplash.com/photo-1614961233913-a5113a4a34ed?w=300"),
            ("Sunflower Oil 1L", "Fortune", "Grocery", 165, 152, 35, "Refined sunflower oil for daily cooking.", "1L pouch, Low cholesterol, Rich in Vitamin E", "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=300"),
            ("Wireless Mouse", "Logitech", "Electronics", 1999, 1799, 15, "Ergonomic wireless mouse with smooth tracking.", "2.4GHz Wireless, 1000 DPI, Long Battery", "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=300"),
        ]
        electro_catalog = [
            ("Mechanical Keyboard", "Razer", "Electronics", 6999, 5999, 8, "RGB mechanical gaming keyboard with blue switches.", "RGB Backlit, Clicky Switches, Anti-ghosting", "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=300"),
            ("Gaming Headset", "HyperX", "Electronics", 4299, 3799, 12, "Immersive sound gaming headset with comfy earcups.", "7.1 Surround Sound, Noise Cancelling Mic", "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=300"),
            ("LED Bulb 9W", "Philips", "Electronics", 199, 149, 100, "Long lasting energy saving LED bulb.", "9W, Cool Daylight, 2 Yr Warranty", "https://images.unsplash.com/photo-1550985616-10810253b84d?w=300"),
        ]
        nagpur_catalog = [
            ("Orange Fresh 1kg", "Local Farm", "Grocery", 90, 70, 200, "Fresh Nagpur oranges, farm picked.", "1kg, Seasonal, Farm fresh", "https://images.unsplash.com/photo-1547514701-42782101795e?w=300"),
            ("Notebook 200pg", "Classmate", "Stationery", 60, 45, 150, "High quality ruled pages notebook.", "200 Pages, Hardbound, Acid-free paper", "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300"),
            ("Coffee Mug", "Borosil", "Lifestyle", 350, 299, 20, "Ceramic coffee mug for your daily brew.", "Microwave Safe, 350ml Capacity", "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=300"),
        ]

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for sid in mumbai_ids[:1]:
            for p in mumbai_catalog:
                demo_products.append((sid, *p, now))
        for sid in mumbai_ids[1:2]:
            for p in electro_catalog:
                demo_products.append((sid, *p, now))
        for sid in nagpur_ids:
            for p in nagpur_catalog:
                demo_products.append((sid, *p, now))

        cur.executemany('''INSERT INTO products
            (shopkeeper_id, name, brand, category, mrp, price, stock, description, features, image_url, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)''', demo_products)
        conn.commit()

    conn.close()

init_db()

def log_activity(action_text, category="System"):
    conn = get_conn()
    cur = conn.cursor()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("INSERT INTO audit_logs (action, timestamp) VALUES (?, ?)", (action_text, ts))
    cur.execute("INSERT INTO notifications (message, category, timestamp) VALUES (?, ?, ?)", (action_text, category, ts))
    conn.commit()
    conn.close()

# ============================================================
# CORE BUSINESS LOGIC: distance, delivery charge, commission/wallet
# ============================================================
def haversine_km(lat1, lon1, lat2, lon2):
    """Real great-circle distance in km between two GPS points (same formula Google Maps uses for straight-line distance)."""
    if None in (lat1, lon1, lat2, lon2):
        return None
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))

def calc_delivery_charge(distance_km, free_threshold, subtotal):
    """₹20 within 1km, +₹10 for every additional km. Free if subtotal crosses shop's free-delivery threshold."""
    if free_threshold and free_threshold > 0 and subtotal >= free_threshold:
        return 0.0
    km_slab = max(1, math.ceil(distance_km if distance_km else 1))
    return float(10 + 10 * km_slab)

def eta_minutes(distance_km):
    """1 to 3 hours depending on distance, as requested."""
    if distance_km is None:
        return "1-3 hours"
    if distance_km <= 2:
        return "45-60 mins"
    elif distance_km <= 5:
        return "1-2 hours"
    else:
        return "2-3 hours"

def deduct_commission(shopkeeper_id, order_subtotal, conn):
    """Try to deduct 3% commission from shopkeeper wallet. Returns (success, commission_amount, new_balance)."""
    cur = conn.cursor()
    commission = round(order_subtotal * COMMISSION_RATE, 2)
    row = cur.execute("SELECT wallet_balance FROM shopkeepers WHERE id=?", (shopkeeper_id,)).fetchone()
    balance = row[0] if row else 0.0
    if balance >= commission:
        new_balance = round(balance - commission, 2)
        cur.execute("UPDATE shopkeepers SET wallet_balance=?, is_active=1 WHERE id=?", (new_balance, shopkeeper_id))
        cur.execute('''INSERT INTO wallet_transactions (shopkeeper_id, txn_type, amount, balance_after, note, timestamp)
                        VALUES (?,?,?,?,?,?)''',
                    (shopkeeper_id, "debit", commission, new_balance, "Order commission (3%)", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        return True, commission, new_balance
    else:
        cur.execute("UPDATE shopkeepers SET is_active=0 WHERE id=?", (shopkeeper_id,))
        return False, commission, balance

def refresh_shopkeeper_active_flags():
    """A shopkeeper is shown 'Active' only if wallet balance > 0; exact per-order check happens at checkout too."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE shopkeepers SET is_active = CASE WHEN wallet_balance > 0 THEN 1 ELSE 0 END")
    conn.commit()
    conn.close()

# ============================================================
# REAL BROWSER GPS LOCATION (navigator.geolocation - no API key needed)
# ============================================================
def capture_browser_location(key_prefix=""):
    """Injects JS that asks the browser for real GPS coordinates and pushes them into the URL
    query params, which Streamlit then reads. This is real device GPS/network location -
    the same permission prompt every maps app uses - no Google API key required."""
    components.html(f"""
        <script>
        function sendLoc(pos) {{
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            const url = new URL(window.parent.location.href);
            url.searchParams.set('{key_prefix}lat', lat);
            url.searchParams.set('{key_prefix}lon', lon);
            window.parent.history.replaceState({{}}, '', url);
            window.parent.location.reload();
        }}
        function sendErr(err) {{
            console.log('Geolocation error: ' + err.message);
        }}
        navigator.geolocation.getCurrentPosition(sendLoc, sendErr, {{enableHighAccuracy: true, timeout: 8000}});
        </script>
        <div style="font-size:12px;color:#94A3B8;">Requesting GPS permission from your browser...</div>
    """, height=30)

def get_query_location(key_prefix=""):
    try:
        params = st.query_params
        lat = params.get(f"{key_prefix}lat")
        lon = params.get(f"{key_prefix}lon")
    except Exception:
        params = st.experimental_get_query_params()
        lat = params.get(f"{key_prefix}lat", [None])[0]
        lon = params.get(f"{key_prefix}lon", [None])[0]
    if lat and lon:
        return float(lat), float(lon)
    return None, None

def clear_query_location(key_prefix=""):
    try:
        if f"{key_prefix}lat" in st.query_params:
            del st.query_params[f"{key_prefix}lat"]
        if f"{key_prefix}lon" in st.query_params:
            del st.query_params[f"{key_prefix}lon"]
    except Exception:
        pass

# ============================================================
# SESSION STATE
# ============================================================
defaults = {
    "dark_mode": False,
    "cart": {},
    "logged_in": False,
    "role": None,
    "current_user": None,
    "shopkeeper_id": None,
    "customer_lat": None,
    "customer_lon": None,
    "customer_address_label": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================================
# PREMIUM THEME (gradient, gold-on-indigo palette)
# ============================================================
PRIMARY_GRAD = "linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #C026D3 100%)"
GOLD = "#F59E0B"
bg_color = "#0B1120" if st.session_state.dark_mode else "#F8FAFC"
card_bg = "#151E32" if st.session_state.dark_mode else "#FFFFFF"
text_color = "#E2E8F0" if st.session_state.dark_mode else "#1E293B"
muted_color = "#94A3B8" if st.session_state.dark_mode else "#64748B"
sidebar_bg = "#0B1120" if st.session_state.dark_mode else "#111827"
border_color = "#293548" if st.session_state.dark_mode else "#E2E8F0"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap');
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
    h1, h2, h3 {{ font-family: 'Poppins', sans-serif; }}
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    section[data-testid="stSidebar"] {{ background: {sidebar_bg} !important; }}
    section[data-testid="stSidebar"] * {{ color: #F1F5F9 !important; }}
    .hero {{
        background: {PRIMARY_GRAD}; border-radius: 18px; padding: 28px 32px; color: white;
        margin-bottom: 22px; box-shadow: 0 10px 30px rgba(124,58,237,0.25);
    }}
    .hero h1 {{ margin: 0; font-size: 28px; font-weight: 800; }}
    .hero p {{ margin: 6px 0 0 0; opacity: 0.92; font-size: 14px; }}
    .premium-card {{
        background: {card_bg}; border: 1px solid {border_color}; border-radius: 16px;
        padding: 18px; margin-bottom: 16px; box-shadow: 0 4px 14px rgba(0,0,0,0.06);
        transition: transform .15s ease;
    }}
    .premium-card:hover {{ transform: translateY(-3px); }}
    .badge {{
        display:inline-block; padding: 3px 10px; border-radius: 999px; font-size: 11px; font-weight: 700;
    }}
    .badge-green {{ background:#DCFCE7; color:#166534; }}
    .badge-red {{ background:#FEE2E2; color:#991B1B; }}
    .badge-gold {{ background:#FEF3C7; color:#92400E; }}
    .price-tag {{ font-size: 20px; font-weight: 800; color: #7C3AED; }}
    .mrp-strike {{ text-decoration: line-through; color:{muted_color}; font-size: 13px; margin-left:6px; }}
    .stButton > button {{
        background: {PRIMARY_GRAD} !important; color: white !important; border: none !important;
        border-radius: 10px !important; font-weight: 700 !important; padding: 8px 18px !important;
    }}
    div[data-testid="stFormSubmitButton"] > button {{
        background: linear-gradient(135deg, #059669 0%, #10B981 100%) !important; color: white !important;
    }}
    div[data-testid="stDownloadButton"] > button {{
        background: linear-gradient(135deg, #F59E0B 0%, #F97316 100%) !important; color: white !important;
    }}
    .metric-chip {{
        background: {card_bg}; border-left: 4px solid {GOLD}; border-radius: 10px; padding: 12px 16px;
        margin-bottom: 10px;
    }}
</style>
""", unsafe_allow_html=True)

# ============================================================
# AUTH: Admin / Shopkeeper / Customer
# ============================================================
def do_login(role, username, password):
    conn = get_conn()
    cur = conn.cursor()
    if role == "Admin":
        if username == "admin" and password == "admin123":
            st.session_state.update(logged_in=True, role="Admin", current_user="admin")
            conn.close()
            return True
    elif role == "Shopkeeper":
        row = cur.execute("SELECT id, wallet_balance FROM shopkeepers WHERE username=? AND password=?",
                           (username, password)).fetchone()
        if row:
            st.session_state.update(logged_in=True, role="Shopkeeper", current_user=username, shopkeeper_id=row[0])
            conn.close()
            return True
    elif role == "Customer":
        row = cur.execute("SELECT id, default_lat, default_lon FROM customers_acc WHERE username=? AND password=?",
                           (username, password)).fetchone()
        if row:
            st.session_state.update(logged_in=True, role="Customer", current_user=username)
            if row[1] and row[2]:
                st.session_state.customer_lat, st.session_state.customer_lon = row[1], row[2]
            conn.close()
            return True
    conn.close()
    return False

st.sidebar.markdown("## 🛍️ LocalBazaar")
st.sidebar.caption("Har Gali Ka Apna Bazaar")

if not st.session_state.logged_in:
    st.sidebar.markdown("### 🔐 Login")
    role_choice = st.sidebar.selectbox("Main hoon:", ["Customer", "Shopkeeper", "Admin"])
    tabs_login, tabs_register = st.sidebar.tabs(["Login", "Naya Register"]) if role_choice != "Admin" else (st.sidebar.container(), None)

    if role_choice == "Admin":
        u = st.sidebar.text_input("Username", key="au")
        p = st.sidebar.text_input("Password", type="password", key="ap")
        if st.sidebar.button("Login as Admin"):
            if do_login("Admin", u, p):
                st.rerun()
            else:
                st.sidebar.error("Galat username/password. (demo: admin / admin123)")
        st.sidebar.info("Customer/Shopkeeper ke liye upar dropdown se select karein.")
    else:
        with tabs_login:
            u = st.text_input("Username", key=f"login_u_{role_choice}")
            p = st.text_input("Password", type="password", key=f"login_p_{role_choice}")
            if st.button(f"Login as {role_choice}", key=f"login_btn_{role_choice}"):
                if do_login(role_choice, u, p):
                    log_activity(f"{role_choice} '{u}' logged in.")
                    st.rerun()
                else:
                    st.error("Galat username ya password.")
            if role_choice == "Shopkeeper":
                st.caption("Demo shops: kirana_mumbai / electro_mumbai / kirana_nagpur — password: shop123")

        with tabs_register:
            if role_choice == "Shopkeeper":
                st.markdown("**Apni dukaan register karein**")
                r_user = st.text_input("Username", key="r_shop_user")
                r_pass = st.text_input("Password", type="password", key="r_shop_pass")
                r_shop = st.text_input("Shop ka naam", key="r_shop_name")
                r_owner = st.text_input("Aapka naam", key="r_owner_name")
                r_phone = st.text_input("Phone number", key="r_shop_phone")
                r_area = st.text_input("Area / Mohalla", key="r_shop_area")
                r_city = st.text_input("City", key="r_shop_city")
                st.caption("📍 Shop ki exact location GPS se lein (delivery distance isi se calculate hogi):")
                if st.button("📍 Use my current GPS location", key="shop_gps_btn"):
                    capture_browser_location(key_prefix="reg_")
                glat, glon = get_query_location(key_prefix="reg_")
                c1, c2 = st.columns(2)
                r_lat = c1.number_input("Latitude", value=glat if glat else 19.0760, format="%.6f", key="r_shop_lat")
                r_lon = c2.number_input("Longitude", value=glon if glon else 72.8777, format="%.6f", key="r_shop_lon")
                r_threshold = st.number_input("Kitne ₹ ke order par FREE delivery denge?", value=500.0, key="r_shop_thresh")
                st.caption("💰 Wallet: shuru mein 0 balance hoga. Order aane par 3% commission wallet se katega — top-up karke shop active rakhein.")
                if st.button("Register Shop", key="reg_shop_submit"):
                    if r_user and r_pass and r_shop:
                        conn = get_conn()
                        try:
                            conn.execute('''INSERT INTO shopkeepers
                                (username, password, shop_name, owner_name, phone, area, city, lat, lon, wallet_balance, free_delivery_threshold, is_active, created_at)
                                VALUES (?,?,?,?,?,?,?,?,?,0,?,0,?)''',
                                (r_user, r_pass, r_shop, r_owner, r_phone, r_area, r_city, r_lat, r_lon, r_threshold,
                                 datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                            conn.commit()
                            st.success("Shop register ho gayi! Ab login karke wallet top-up karein aur products add karein.")
                            log_activity(f"New shop registered: {r_shop}")
                        except sqlite3.IntegrityError:
                            st.error("Yeh username pehle se hai.")
                        conn.close()
                    else:
                        st.error("Username, password aur shop naam zaroori hai.")
            elif role_choice == "Customer":
                st.markdown("**Naya account banayein**")
                cu = st.text_input("Username", key="r_cust_user")
                cp = st.text_input("Password", type="password", key="r_cust_pass")
                cn = st.text_input("Aapka naam", key="r_cust_name")
                cph = st.text_input("Phone", key="r_cust_phone")
                if st.button("Register", key="reg_cust_submit"):
                    if cu and cp:
                        conn = get_conn()
                        try:
                            conn.execute('''INSERT INTO customers_acc (username, password, full_name, phone, created_at)
                                VALUES (?,?,?,?,?)''', (cu, cp, cn, cph, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                            conn.commit()
                            st.success("Account ban gaya! Ab login karein.")
                        except sqlite3.IntegrityError:
                            st.error("Yeh username pehle se hai.")
                        conn.close()
                    else:
                        st.error("Username aur password zaroori hai.")
    st.stop()
else:
    st.sidebar.success(f"👤 {st.session_state.current_user}  ·  {st.session_state.role}")
    if st.sidebar.button("Logout"):
        for k in ["logged_in", "role", "current_user", "shopkeeper_id"]:
            st.session_state[k] = defaults[k]
        st.rerun()

st.sidebar.markdown("---")
dm = st.sidebar.toggle("🌙 Dark Premium Theme", value=st.session_state.dark_mode)
if dm != st.session_state.dark_mode:
    st.session_state.dark_mode = dm
    st.rerun()
st.sidebar.markdown("---")

# ============================================================
# NAVIGATION (role-based)
# ============================================================
if st.session_state.role == "Customer":
    nav_options = ["🏠 Nearby Shops (Search)", "🛒 Cart & Checkout", "📦 My Orders", "👤 My Profile"]
elif st.session_state.role == "Shopkeeper":
    nav_options = ["📊 Shop Dashboard", "💰 Wallet & Commission", "🛠️ Manage Products", "📦 Orders Received"]
else:  # Admin
    nav_options = ["📊 Platform Overview", "🏪 All Shopkeepers", "📦 All Orders", "🛡️ Audit Logs", "📥 Reports & Export"]

selected_option = st.sidebar.radio("Navigation", nav_options)

st.markdown(f"""
<div class="hero">
    <h1>🛍️ LocalBazaar</h1>
    <p>Har gali ka apna bazaar — 1 rupaye se 5 lakh tak, 1-3 ghante mein delivery, seedha local dukaandar se.</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# CUSTOMER PAGES
# ============================================================
if st.session_state.role == "Customer":

    if selected_option == "🏠 Nearby Shops (Search)":
        st.subheader("📍 Aapki Location")
        loc_col1, loc_col2, loc_col3 = st.columns([2, 2, 3])
        with loc_col1:
            if st.button("📍 Use my real GPS location"):
                capture_browser_location(key_prefix="cust_")
        glat, glon = get_query_location(key_prefix="cust_")
        if glat and glon:
            st.session_state.customer_lat, st.session_state.customer_lon = glat, glon

        with loc_col2:
            manual = st.toggle("Manually set location", value=(st.session_state.customer_lat is None))
        with loc_col3:
            if st.session_state.customer_lat:
                st.success(f"📌 Location set: {st.session_state.customer_lat:.4f}, {st.session_state.customer_lon:.4f}")
            else:
                st.warning("Location set nahi hai — nearby shops aur delivery charge dikhane ke liye location zaroori hai.")

        if manual:
            mc1, mc2 = st.columns(2)
            m_lat = mc1.number_input("Latitude", value=st.session_state.customer_lat or 19.0760, format="%.6f")
            m_lon = mc2.number_input("Longitude", value=st.session_state.customer_lon or 72.8777, format="%.6f")
            if st.button("Set this location"):
                st.session_state.customer_lat, st.session_state.customer_lon = m_lat, m_lon
                st.rerun()

        st.markdown("---")
        refresh_shopkeeper_active_flags()
        search_q = st.text_input("🔍 Kya chahiye? (e.g. rice, mouse, notebook, oil...)")

        conn = get_conn()
        query = '''
            SELECT p.*, s.shop_name, s.area, s.city, s.lat as shop_lat, s.lon as shop_lon,
                   s.free_delivery_threshold, s.is_active
            FROM products p
            JOIN shopkeepers s ON p.shopkeeper_id = s.id
            WHERE s.is_active = 1 AND p.stock > 0
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()

        if search_q:
            df = df[df.apply(lambda r: search_q.lower() in str(r['name']).lower()
                              or search_q.lower() in str(r['brand']).lower()
                              or search_q.lower() in str(r['category']).lower(), axis=1)]

        if st.session_state.customer_lat and not df.empty:
            df['distance_km'] = df.apply(lambda r: haversine_km(
                st.session_state.customer_lat, st.session_state.customer_lon, r['shop_lat'], r['shop_lon']), axis=1)
            df = df.sort_values('distance_km')
        else:
            df['distance_km'] = None

        if df.empty:
            st.info("Koi product nahi mila. Search badal kar dekhein.")
        else:
            st.caption(f"{len(df)} products mile, sabse nazdeeki dukaan pehle dikhayi ja rahi hai.")
            cols = st.columns(3)
            for i, row in df.reset_index(drop=True).iterrows():
                with cols[i % 3]:
                    dist_txt = f"{row['distance_km']:.1f} km away" if pd.notnull(row['distance_km']) else "Set location to see distance"
                    eta = eta_minutes(row['distance_km']) if pd.notnull(row['distance_km']) else "1-3 hours"
                    disc = round(100 * (1 - row['price'] / row['mrp'])) if row['mrp'] else 0
                    st.markdown(f"""
                        <div class="premium-card">
                            <img src="{row['image_url']}" style="width:100%;height:140px;object-fit:cover;border-radius:10px;" onerror="this.style.display='none'"/>
                            <h4 style="margin:10px 0 2px 0;">{row['name']}</h4>
                            <div style="color:#64748B;font-size:12px;">{row['brand']} · {row['category']}</div>
                            <div style="margin-top:6px;">
                                <span class="price-tag">₹{row['price']:,.0f}</span>
                                <span class="mrp-strike">₹{row['mrp']:,.0f}</span>
                                <span class="badge badge-gold">{disc}% OFF</span>
                            </div>
                            <div style="margin-top:8px;font-size:12px;color:#64748B;">
                                🏪 {row['shop_name']} ({row['area']}, {row['city']})<br/>
                                📍 {dist_txt} &nbsp;|&nbsp; ⏱️ {eta}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"➕ Add to Cart", key=f"add_{row['id']}"):
                        st.session_state.cart[int(row['id'])] = st.session_state.cart.get(int(row['id']), 0) + 1
                        st.success("Cart mein add ho gaya!")

    elif selected_option == "🛒 Cart & Checkout":
        st.subheader("🛒 Aapka Cart")
        if not st.session_state.cart:
            st.info("Cart khali hai. Pehle 'Nearby Shops' se products add karein.")
        elif not st.session_state.customer_lat:
            st.warning("Checkout ke liye pehle 'Nearby Shops' page par apni location set karein.")
        else:
            conn = get_conn()
            prod_df = pd.read_sql_query('''
                SELECT p.*, s.shop_name, s.lat as shop_lat, s.lon as shop_lon,
                       s.free_delivery_threshold, s.is_active, s.wallet_balance
                FROM products p JOIN shopkeepers s ON p.shopkeeper_id = s.id
            ''', conn)
            conn.close()

            cart_df = prod_df[prod_df['id'].isin(st.session_state.cart.keys())].copy()
            cart_df['qty'] = cart_df['id'].apply(lambda pid: st.session_state.cart[pid])
            cart_df['line_total'] = cart_df['price'] * cart_df['qty']

            grand_total = 0.0
            order_plan = []  # one entry per shop

            for shop_id, group in cart_df.groupby('shopkeeper_id'):
                shop_name = group['shop_name'].iloc[0]
                shop_active = bool(group['is_active'].iloc[0])
                distance = haversine_km(st.session_state.customer_lat, st.session_state.customer_lon,
                                         group['shop_lat'].iloc[0], group['shop_lon'].iloc[0])
                subtotal = group['line_total'].sum()
                threshold = group['free_delivery_threshold'].iloc[0]
                delivery = calc_delivery_charge(distance, threshold, subtotal)
                gst = round(subtotal * 0.18, 2)
                total = round(subtotal + gst + delivery, 2)
                grand_total += total

                st.markdown(f"""
                    <div class="premium-card">
                        <h4>🏪 {shop_name} {'<span class="badge badge-green">Active</span>' if shop_active else '<span class="badge badge-red">Inactive - wallet low</span>'}</h4>
                        <div style="font-size:13px;color:#64748B;">📍 {distance:.1f} km away · ⏱️ {eta_minutes(distance)}</div>
                    </div>
                """, unsafe_allow_html=True)
                st.dataframe(group[['name', 'price', 'qty', 'line_total']].rename(
                    columns={'name': 'Product', 'price': 'Price', 'qty': 'Qty', 'line_total': 'Subtotal'}),
                    use_container_width=True, hide_index=True)
                dcol1, dcol2, dcol3, dcol4 = st.columns(4)
                dcol1.metric("Subtotal", f"₹{subtotal:,.2f}")
                dcol2.metric("Delivery", "FREE" if delivery == 0 else f"₹{delivery:,.2f}")
                dcol3.metric("GST (18%)", f"₹{gst:,.2f}")
                dcol4.metric("Shop Total", f"₹{total:,.2f}")
                if not shop_active:
                    st.error(f"⚠️ {shop_name} ka wallet balance commission ke liye kaafi nahi hai — yeh order abhi place nahi ho sakta.")

                order_plan.append(dict(shop_id=int(shop_id), shop_name=shop_name, items=group[['name', 'price', 'qty']].to_dict('records'),
                                        distance=distance, subtotal=subtotal, delivery=delivery, gst=gst, total=total, active=shop_active))

            st.markdown(f"### 🧾 Grand Total (sabhi shops): ₹{grand_total:,.2f}")

            if st.button("✅ Place Order(s)", type="primary"):
                conn = get_conn()
                order_group = datetime.now().strftime("OG%Y%m%d%H%M%S")
                placed, failed = [], []
                for plan in order_plan:
                    if not plan['active']:
                        failed.append(plan['shop_name'])
                        continue
                    ok, commission, new_bal = deduct_commission(plan['shop_id'], plan['subtotal'], conn)
                    if not ok:
                        failed.append(plan['shop_name'])
                        continue
                    conn.execute('''INSERT INTO orders
                        (order_group, customer_name, customer_lat, customer_lon, shopkeeper_id, shop_name, items,
                         distance_km, subtotal, delivery_charge, gst_amount, commission_amount, total_amount, status, timestamp)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                        (order_group, st.session_state.current_user, st.session_state.customer_lat, st.session_state.customer_lon,
                         plan['shop_id'], plan['shop_name'], json.dumps(plan['items']), plan['distance'], plan['subtotal'],
                         plan['delivery'], plan['gst'], commission, plan['total'], "Placed",
                         datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    placed.append(plan['shop_name'])
                conn.commit()
                conn.close()

                if placed:
                    st.success(f"Order place ho gaya: {', '.join(placed)}")
                    log_activity(f"Order placed by {st.session_state.current_user} at {', '.join(placed)}", "Order")
                    remaining_ids = cart_df[~cart_df['shopkeeper_id'].isin([o['shop_id'] for o in order_plan if o['shop_name'] in placed])]['id'].tolist()
                    st.session_state.cart = {pid: q for pid, q in st.session_state.cart.items() if pid in remaining_ids}
                if failed:
                    st.error(f"Yeh shops wallet-inactive hone ki wajah se order nahi le payi: {', '.join(failed)}. Un items ko cart se hataayein ya baad mein try karein.")
                if placed:
                    st.rerun()

    elif selected_option == "📦 My Orders":
        st.subheader("📦 Meri Orders")
        conn = get_conn()
        odf = pd.read_sql_query("SELECT * FROM orders WHERE customer_name=? ORDER BY id DESC",
                                 conn, params=(st.session_state.current_user,))
        conn.close()
        if odf.empty:
            st.info("Abhi tak koi order nahi hai.")
        else:
            for _, o in odf.iterrows():
                st.markdown(f"""
                    <div class="premium-card">
                        <b>🏪 {o['shop_name']}</b> &nbsp; <span class="badge badge-green">{o['status']}</span><br/>
                        <span style="font-size:12px;color:#64748B;">{o['timestamp']} · {o['distance_km']:.1f} km</span><br/>
                        Subtotal ₹{o['subtotal']:,.2f} + Delivery ₹{o['delivery_charge']:,.2f} + GST ₹{o['gst_amount']:,.2f}
                        = <b>₹{o['total_amount']:,.2f}</b>
                    </div>
                """, unsafe_allow_html=True)

    elif selected_option == "👤 My Profile":
        st.subheader("👤 Profile")
        st.write(f"**Username:** {st.session_state.current_user}")
        if st.session_state.customer_lat:
            st.write(f"**Saved location:** {st.session_state.customer_lat:.4f}, {st.session_state.customer_lon:.4f}")
        addr = st.text_input("Address label (e.g. Mumbai Ghar / Nagpur Parents Ghar)", value=st.session_state.customer_address_label)
        if st.button("Save address label"):
            st.session_state.customer_address_label = addr
            conn = get_conn()
            conn.execute("UPDATE customers_acc SET default_lat=?, default_lon=?, default_address=? WHERE username=?",
                         (st.session_state.customer_lat, st.session_state.customer_lon, addr, st.session_state.current_user))
            conn.commit()
            conn.close()
            st.success("Saved!")

# ============================================================
# SHOPKEEPER PAGES
# ============================================================
if st.session_state.role == "Shopkeeper":
    sk_id = st.session_state.shopkeeper_id
    conn = get_conn()
    sk = pd.read_sql_query("SELECT * FROM shopkeepers WHERE id=?", conn, params=(sk_id,)).iloc[0]
    conn.close()

    if selected_option == "📊 Shop Dashboard":
        st.subheader(f"🏪 {sk['shop_name']}")
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"<div class='metric-chip'><b>Wallet Balance</b><br/><span style='font-size:22px;'>₹{sk['wallet_balance']:,.2f}</span></div>", unsafe_allow_html=True)
        status_badge = "🟢 Active" if sk['is_active'] else "🔴 Inactive (top-up needed)"
        c2.markdown(f"<div class='metric-chip'><b>Status</b><br/><span style='font-size:22px;'>{status_badge}</span></div>", unsafe_allow_html=True)
        conn = get_conn()
        n_prod = pd.read_sql_query("SELECT COUNT(*) c FROM products WHERE shopkeeper_id=?", conn, params=(sk_id,))['c'].iloc[0]
        n_orders = pd.read_sql_query("SELECT COUNT(*) c FROM orders WHERE shopkeeper_id=?", conn, params=(sk_id,))['c'].iloc[0]
        revenue = pd.read_sql_query("SELECT COALESCE(SUM(subtotal),0) s FROM orders WHERE shopkeeper_id=?", conn, params=(sk_id,))['s'].iloc[0]
        conn.close()
        c3.markdown(f"<div class='metric-chip'><b>Products Listed</b><br/><span style='font-size:22px;'>{n_prod}</span></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='metric-chip'><b>Total Orders</b><br/><span style='font-size:22px;'>{n_orders}</span></div>", unsafe_allow_html=True)
        st.metric("Lifetime Revenue (subtotal)", f"₹{revenue:,.2f}")

        st.markdown("---")
        st.markdown("**📍 Shop Location** (delivery distance customers ko isi se dikhti hai)")
        if st.button("📍 Update to my current GPS location"):
            capture_browser_location(key_prefix="sk_")
        glat, glon = get_query_location(key_prefix="sk_")
        if glat and glon:
            conn = get_conn()
            conn.execute("UPDATE shopkeepers SET lat=?, lon=? WHERE id=?", (glat, glon, sk_id))
            conn.commit()
            conn.close()
            st.success(f"Location update ho gayi: {glat:.4f}, {glon:.4f}")
            clear_query_location(key_prefix="sk_")
        st.caption(f"Current: {sk['lat']:.4f}, {sk['lon']:.4f} · {sk['area']}, {sk['city']}")

        conn = get_conn()
        recent_orders = pd.read_sql_query("SELECT * FROM orders WHERE shopkeeper_id=? ORDER BY id DESC LIMIT 20", conn, params=(sk_id,))
        conn.close()
        if not recent_orders.empty:
            fig = px.bar(recent_orders.sort_values('id'), x='id', y='total_amount',
                         title="Recent Orders - Revenue", color='total_amount',
                         color_continuous_scale=['#C4B5FD', '#7C3AED'])
            st.plotly_chart(fig, use_container_width=True)

    elif selected_option == "💰 Wallet & Commission":
        st.subheader("💰 Wallet & Commission")
        st.info("Platform commission: har order ke subtotal ka **3%** aapke wallet se automatically kat jaata hai. "
                "Agar wallet mein paisa kam hai to naye order aane par dukaan 'Inactive' ho jaati hai — top-up karke wapas active karein.")
        c1, c2 = st.columns(2)
        c1.metric("Current Balance", f"₹{sk['wallet_balance']:,.2f}")
        c2.metric("Free Delivery Threshold", f"₹{sk['free_delivery_threshold']:,.2f}")

        with st.form("topup"):
            st.markdown("**💳 Wallet Top-up (demo — real payment gateway yahan integrate hoga)**")
            amt = st.number_input("Top-up Amount (₹)", min_value=50.0, value=500.0, step=50.0)
            if st.form_submit_button("Top-up Wallet"):
                conn = get_conn()
                cur = conn.cursor()
                new_bal = round(sk['wallet_balance'] + amt, 2)
                cur.execute("UPDATE shopkeepers SET wallet_balance=?, is_active=1 WHERE id=?", (new_bal, sk_id))
                cur.execute('''INSERT INTO wallet_transactions (shopkeeper_id, txn_type, amount, balance_after, note, timestamp)
                    VALUES (?,?,?,?,?,?)''', (sk_id, "credit", amt, new_bal, "Wallet top-up", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
                st.success(f"₹{amt:,.2f} add ho gaya! Naya balance: ₹{new_bal:,.2f}")
                st.rerun()

        st.markdown("**⚙️ Free Delivery Setting**")
        new_thresh = st.number_input("Is amount se upar ke order par FREE delivery", value=float(sk['free_delivery_threshold']))
        if st.button("Update threshold"):
            conn = get_conn()
            conn.execute("UPDATE shopkeepers SET free_delivery_threshold=? WHERE id=?", (new_thresh, sk_id))
            conn.commit()
            conn.close()
            st.success("Update ho gaya!")

        st.markdown("**📜 Wallet Transaction History**")
        conn = get_conn()
        wt = pd.read_sql_query("SELECT * FROM wallet_transactions WHERE shopkeeper_id=? ORDER BY id DESC", conn, params=(sk_id,))
        conn.close()
        st.dataframe(wt, use_container_width=True, hide_index=True)

    elif selected_option == "🛠️ Manage Products":
        st.subheader("🛠️ Apne Products Manage Karein")
        with st.form("add_product", clear_on_submit=True):
            st.markdown("**➕ Naya Product Add Karein**")
            p1, p2 = st.columns(2)
            name = p1.text_input("Product Name*")
            brand = p2.text_input("Brand")
            p3, p4 = st.columns(2)
            category = p3.text_input("Category (Grocery/Electronics/etc.)")
            image_url = p4.text_input("Image URL (optional)")
            p5, p6, p7 = st.columns(3)
            mrp = p5.number_input("MRP (₹)*", min_value=1.0, value=100.0)
            price = p6.number_input("Selling Price (₹)*", min_value=1.0, value=90.0)
            stock = p7.number_input("Stock Qty*", min_value=0, value=10)
            description = st.text_area("Description")
            features = st.text_input("Features / Specifications (comma separated)")
            if st.form_submit_button("Add Product"):
                if name and mrp and price:
                    conn = get_conn()
                    conn.execute('''INSERT INTO products
                        (shopkeeper_id, name, brand, category, mrp, price, stock, description, features, image_url, created_at)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
                        (sk_id, name, brand, category, mrp, price, stock, description, features, image_url,
                         datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                    conn.close()
                    st.success(f"'{name}' add ho gaya!")
                    log_activity(f"Product added: {name} by {st.session_state.current_user}")
                    st.rerun()
                else:
                    st.error("Name, MRP aur Price zaroori hai.")

        st.markdown("---")
        st.markdown("**📋 Aapke Products**")
        conn = get_conn()
        my_products = pd.read_sql_query("SELECT * FROM products WHERE shopkeeper_id=? ORDER BY id DESC", conn, params=(sk_id,))
        conn.close()
        if my_products.empty:
            st.info("Abhi koi product nahi hai.")
        else:
            for _, row in my_products.iterrows():
                with st.expander(f"{row['name']} — ₹{row['price']:,.0f} (Stock: {row['stock']})"):
                    e1, e2, e3 = st.columns(3)
                    n_price = e1.number_input("Price", value=float(row['price']), key=f"price_{row['id']}")
                    n_stock = e2.number_input("Stock", value=int(row['stock']), key=f"stock_{row['id']}")
                    if e3.button("Update", key=f"upd_{row['id']}"):
                        conn = get_conn()
                        conn.execute("UPDATE products SET price=?, stock=? WHERE id=?", (n_price, n_stock, row['id']))
                        conn.commit()
                        conn.close()
                        st.success("Updated!")
                        st.rerun()
                    if st.button("🗑️ Delete Product", key=f"del_{row['id']}"):
                        conn = get_conn()
                        conn.execute("DELETE FROM products WHERE id=?", (row['id'],))
                        conn.commit()
                        conn.close()
                        st.rerun()

    elif selected_option == "📦 Orders Received":
        st.subheader("📦 Orders Received")
        conn = get_conn()
        odf = pd.read_sql_query("SELECT * FROM orders WHERE shopkeeper_id=? ORDER BY id DESC", conn, params=(sk_id,))
        conn.close()
        if odf.empty:
            st.info("Abhi koi order nahi aaya.")
        else:
            for _, o in odf.iterrows():
                items = json.loads(o['items'])
                items_txt = ", ".join([f"{it['name']} x{it['qty']}" for it in items])
                st.markdown(f"""
                    <div class="premium-card">
                        <b>Order from {o['customer_name']}</b> &nbsp; <span class="badge badge-green">{o['status']}</span><br/>
                        <span style="font-size:13px;">{items_txt}</span><br/>
                        <span style="font-size:12px;color:#64748B;">{o['timestamp']} · {o['distance_km']:.1f} km · Commission paid: ₹{o['commission_amount']:,.2f}</span><br/>
                        Total: <b>₹{o['total_amount']:,.2f}</b>
                    </div>
                """, unsafe_allow_html=True)

# ============================================================
# ADMIN PAGES
# ============================================================
if st.session_state.role == "Admin":
    conn = get_conn()

    if selected_option == "📊 Platform Overview":
        st.subheader("📊 Platform Overview")
        n_shops = pd.read_sql_query("SELECT COUNT(*) c FROM shopkeepers", conn)['c'].iloc[0]
        n_active = pd.read_sql_query("SELECT COUNT(*) c FROM shopkeepers WHERE is_active=1", conn)['c'].iloc[0]
        n_orders = pd.read_sql_query("SELECT COUNT(*) c FROM orders", conn)['c'].iloc[0]
        total_commission = pd.read_sql_query("SELECT COALESCE(SUM(commission_amount),0) s FROM orders", conn)['s'].iloc[0]
        total_gmv = pd.read_sql_query("SELECT COALESCE(SUM(total_amount),0) s FROM orders", conn)['s'].iloc[0]

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.markdown(f"<div class='metric-chip'><b>Total Shops</b><br/><span style='font-size:20px;'>{n_shops}</span></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-chip'><b>Active Shops</b><br/><span style='font-size:20px;'>{n_active}</span></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-chip'><b>Total Orders</b><br/><span style='font-size:20px;'>{n_orders}</span></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='metric-chip'><b>GMV</b><br/><span style='font-size:20px;'>₹{total_gmv:,.0f}</span></div>", unsafe_allow_html=True)
        c5.markdown(f"<div class='metric-chip'><b>Platform Revenue</b><br/><span style='font-size:20px;'>₹{total_commission:,.0f}</span></div>", unsafe_allow_html=True)

        odf = pd.read_sql_query("SELECT * FROM orders ORDER BY id", conn)
        if not odf.empty:
            fig = px.bar(odf, x='id', y='total_amount', color='shop_name', title="Orders by Shop")
            st.plotly_chart(fig, use_container_width=True)

    elif selected_option == "🏪 All Shopkeepers":
        st.subheader("🏪 All Shopkeepers")
        sdf = pd.read_sql_query("SELECT id, shop_name, owner_name, area, city, wallet_balance, free_delivery_threshold, is_active FROM shopkeepers", conn)
        st.dataframe(sdf, use_container_width=True, hide_index=True)
        st.markdown("**Manual wallet adjustment (admin override)**")
        c1, c2, c3 = st.columns(3)
        pick_id = c1.number_input("Shopkeeper ID", min_value=1, step=1)
        adj_amt = c2.number_input("Amount to credit (₹)", value=0.0)
        if c3.button("Credit Wallet"):
            row = conn.execute("SELECT wallet_balance FROM shopkeepers WHERE id=?", (pick_id,)).fetchone()
            if row:
                new_bal = row[0] + adj_amt
                conn.execute("UPDATE shopkeepers SET wallet_balance=?, is_active=1 WHERE id=?", (new_bal, pick_id))
                conn.execute('''INSERT INTO wallet_transactions (shopkeeper_id, txn_type, amount, balance_after, note, timestamp)
                    VALUES (?,?,?,?,?,?)''', (pick_id, "credit", adj_amt, new_bal, "Admin adjustment", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                st.success("Wallet updated!")
                st.rerun()
            else:
                st.error("Shopkeeper ID nahi mila.")

    elif selected_option == "📦 All Orders":
        st.subheader("📦 All Orders")
        odf = pd.read_sql_query("SELECT * FROM orders ORDER BY id DESC", conn)
        st.dataframe(odf, use_container_width=True, hide_index=True)

    elif selected_option == "🛡️ Audit Logs":
        st.subheader("🛡️ Audit Logs")
        adf = pd.read_sql_query("SELECT * FROM audit_logs ORDER BY id DESC", conn)
        st.dataframe(adf, use_container_width=True, hide_index=True)

    elif selected_option == "📥 Reports & Export":
        st.subheader("📥 Reports & Export")
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as writer:
            pd.read_sql_query("SELECT * FROM orders", conn).to_excel(writer, sheet_name='Orders', index=False)
            pd.read_sql_query("SELECT * FROM shopkeepers", conn).to_excel(writer, sheet_name='Shopkeepers', index=False)
            pd.read_sql_query("SELECT * FROM products", conn).to_excel(writer, sheet_name='Products', index=False)
        st.download_button("⬇️ Download Full Excel Report", data=out.getvalue(), file_name="localbazaar_report.xlsx")

        st.markdown("---")
        st.subheader("💾 Database Backup")
        with open(DB_PATH, "rb") as f:
            st.download_button("⬇️ Download Database Backup (.db)", data=f, file_name="localbazaar_backup.db")

    conn.close()
