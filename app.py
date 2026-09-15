import streamlit as st

# --- 1. PAGE CONFIGURATION & PREMIUM MULTI-COLOR STYLING ---
st.set_page_config(
    page_title="HyperLocal 3-Hour Delivery Platform",
    page_icon="🚀",
    layout="wide",
)

# Custom CSS for Multi-color, Dark Glassmorphism, & No-Flicker Aesthetic
st.markdown(
    """
    <style>
    /* Main Background & Font */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Glowing Multi-color Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 15px;
    }
    
    /* Gradient Headings */
    h1, h2, h3 {
        background: linear-gradient(90deg, #ec4899, #8b5cf6, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Hide Streamlit Default Header/Footer for clean single-page look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)

# --- 2. INITIALIZE SESSION STATE (Data Persistence without Flicker) ---
if "wallet_balance" not in st.session_state:
    st.session_state.wallet_balance = 600.0  # Default advance balance

if "shop_active" not in st.session_state:
    st.session_state.shop_active = True  # Shop active/inactive status

if "products" not in st.session_state:
    st.session_state.products = [
        {"name": "Wireless Earbuds", "price": 1200, "shop": "Sharma Electronics"},
        {"name": "Organic Atta (10kg)", "price": 450, "shop": "Gupta Kirana"},
        {
            "name": "Smart Watch (Luxury)",
            "price": 15000,
            "shop": "Pan-India Hub",
        },
    ]


# --- 3. SINGLE-PAGE TOP NAVIGATION BAR (No Page Reload / No Flicker) ---
st.markdown(
    "<h1 style='text-align: center;'>⚡ HyperLocal 3-Hour Delivery Platform</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #94a3b8;'>Any item from ₹1 to ₹10 Lakhs"
    " delivered across Pan-India under 3 hours!</p>",
    unsafe_allow_html=True,
)

# Custom single-page tab selection using radio buttons styled horizontally
nav_mode = st.radio(
    "Select View Mode",
    ["🛒 Customer View", "🏪 Shopkeeper Panel", "💳 Wallet & Admin Audit"],
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown("---")

# =========================================================================
# VIEW 1: CUSTOMER VIEW (Browse, Search, and Strict Online Payment via Direct QR)
# =========================================================================
if nav_mode == "🛒 Customer View":
  st.subheader("🛍️ Universal Marketplace (Pan-India & 3-Hour Delivery)")

  col1, col2 = st.columns([2, 1])
  with col1:
    search_query = st.text_input(
        "🔍 Search anything (from ₹1 to ₹10 Lakhs):",
        placeholder="Type product name...",
    )
  with col2:
    location_pin = st.text_input("📍 Enter Pin Code:", value="110001")

  st.markdown("### Available Products (Live Stock)")

  # Filter products based on search
  filtered_products = [
      p
      for p in st.session_state.products
      if search_query.lower() in p["name"].lower()
  ]

  if not filtered_products:
    st.info("No products found matching your search.")
  else:
    for idx, prod in enumerate(filtered_products):
      with st.container():
        st.markdown(
            f"""
                <div class="metric-card">
                    <h4>{prod['name']}</h4>
                    <p><b>Price:</b> ₹{prod['price']:,} | <b>Seller:</b> {prod['shop']}</p>
                    <p style="color: #10b981; font-size: 14px;">✔ 3-Hour Delivery Available | 100% Online Secure Payment</p>
                </div>
                """,
            unsafe_allow_html=True,
        )

        # Checkout / Order button
        if st.button(f"Buy Now (₹{prod['price']:,})", key=f"buy_{idx}"):
          commission = prod["price"] * 0.03  # 3% Commission rule

          # Check if shopkeeper has enough wallet balance for commission deduction
          if st.session_state.shop_active:
            if st.session_state.wallet_balance >= commission:
              # Deduct commission from wallet and process order
              st.session_state.wallet_balance -= commission
              st.success(
                  f"🎉 Order placed successfully! Direct QR payment sent to"
                  f" shopkeeper. Platform 3% Commission (₹{commission:.2f})deducted"
                  " from shopkeeper's wallet."
              )
            else:
              st.error(
                  f"❌ Order Failed! Shopkeeper's wallet balance (₹{st.session_state.wallet_balance})"
                  f" is too low to cover the required 3% commission (₹{commission:.2f})."
                  " Ask shopkeeper to recharge wallet."
              )
          else:
            st.warning(
                "⚠️ This shop is currently INACTIVE (Offline). Order cannot be"
                " processed."
            )

# =========================================================================
# VIEW 2: SHOPKEEPER PANEL (Active/Inactive Toggle & Auto-Menu Adder)
# =========================================================================
elif nav_mode == "🏪 Shopkeeper Panel":
  st.subheader("🏪 Shopkeeper Control Panel")

  col_a, col_b = st.columns(2)

  with col_a:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("### 🎛️ Shop Status Toggle")
    # Active / Inactive Toggle Switch
    active_status = st.toggle(
        "Online / Active Status", value=st.session_state.shop_active
    )
    st.session_state.shop_active = active_status

    if st.session_state.shop_active:
      st.success("Your shop is LIVE and visible to customers!")
    else:
      st.error("Your shop is currently OFFLINE (Inactive).")
    st.markdown("</div>", unsafe_allow_html=True)

  with col_b:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("### 💰 Advance Wallet Balance")
    st.metric(
        label="Current Wallet Balance",
        value=f"₹{st.session_state.wallet_balance:.2f}",
    )
    if st.session_state.wallet_balance < 500:
      st.warning(
          "⚠️ Warning: Balance below ₹500! Top-up required to stay active."
      )
    else:
      st.success("✔ Wallet balance is safe for order processing.")
    st.markdown("</div>", unsafe_allow_html=True)

  # Auto Product Adder Section
  st.markdown("### ➕ Add New Product to Menu Instantly")
  with st.form("add_product_form"):
    new_p_name = st.text_input("Product Name (e.g., Grocery item or 10Lakh item)")
    new_p_price = st.number_input(
        "Product Price (₹)", min_value=1, max_value=1000000, value=500
    )
    submit_product = st.form_submit_button("Add Product Live")

    if submit_product and new_p_name:
      st.session_state.products.append(
          {
              "name": new_p_name,
              "price": new_p_price,
              "shop": "My Local Shop",
          }
      )
      st.success(
          f"Product '{new_p_name}' added successfully and is now live for"
          " customers!"
      )

# =========================================================================
# VIEW 3: WALLET RECHARGE & ADMIN AUDIT
# =========================================================================
elif nav_mode == "💳 Wallet & Admin Audit":
  st.subheader("💳 Wallet Recharge & Commission Management")

  st.markdown(
      """
    <div class="metric-card">
        <h4>How Wallet & 3% Commission Works:</h4>
        <ul>
            <li><b>Strict Online Payments:</b> No Cash on Delivery (COD). Customers pay directly via Shopkeeper's QR.</li>
            <li><b>3% Commission Rule:</b> On every order, 3% app commission is auto-deducted from the shopkeeper's advance wallet.</li>
            <li><b>Minimum Balance Limit:</b> If wallet balance drops below ₹500 or is less than the required order commission, the order will be locked/rejected automatically.</li>
        </ul>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # Quick Wallet Top-up Simulation for Shopkeeper
  st.markdown("### Top-up Advance Wallet")
  recharge_amount = st.number_input(
      "Enter Recharge Amount (₹)", min_value=100, max_value=50000, value=1000
  )
  if st.button("Recharge Wallet Now"):
    st.session_state.wallet_balance += recharge_amount
    st.success(
        f"Successfully added ₹{recharge_amount} to your wallet! New Balance:"
        f" ₹{st.session_state.wallet_balance:.2f}"
    )
