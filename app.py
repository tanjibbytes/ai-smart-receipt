import streamlit as st
from fpdf import FPDF
import os

# ১. পেজ সেটআপ ও থিম
st.set_page_config(page_title="Smart-Receipt Pro", page_icon="📄", layout="wide")

# ==========================================
# 🌐 ল্যাঙ্গুয়েজ ডিকশনারি (Translations Dictionary)
# ==========================================
translations = {
    "English": {
        "lang_label": "🌐 Choose Language / ভাষা নির্বাচন করুন:",
        "main_title": "⚡ Smart-Receipt Pro Dashboard",
        "subtitle": "Create professional business invoices and track billing instantly.",
        "shop_settings": "🔐 Shop Settings",
        "biz_name_lbl": "Business Name",
        "biz_email_lbl": "Business Email",
        "biz_phone_lbl": "Business Mobile",
        "upload_logo_lbl": "Upload Shop Logo (PNG)",
        "save_profile_btn": "💾 Save Profile Settings",
        "save_success": "✅ Settings Saved Successfully!",
        "cust_header": "👤 Customer Information",
        "cust_name": "Full Name",
        "cust_phone": "Phone Number",
        "cust_addr": "Delivery Address",
        "order_header": "🛒 Order Items (Max 5)",
        "item_lbl": "Item",
        "qty_lbl": "Qty",
        "price_lbl": "Price (TK)",
        "billing_header": "💳 Billing & Summary",
        "del_charge_lbl": "Delivery Charge (TK)",
        "pay_method_lbl": "Payment Method",
        "paid_lbl": "Paid Amount / Advance (TK)",
        "total_bill_metric": "Total Bill (TK)",
        "items_metric": "Items:",
        "due_metric": "Due / COD Amount",
        "remaining_metric": "- Remaining",
        "status_metric": "Payment Status",
        "fully_paid_metric": "FULLY PAID",
        "success_metric": "Success",
        "actions_header": "📄 Actions",
        "generate_btn": "✨ Generate & Download PDF Memo",
        "error_name": "Please enter a Customer Name before generating the invoice!",
        "download_ready_btn": "📥 Click here to Save PDF",
        # PDF Specific
        "pdf_title": "CASH RECEIPT / INVOICE",
        "pdf_method": "Method:",
        "pdf_cust_name": "Customer Name:",
        "pdf_mobile": "Mobile:",
        "pdf_address": "Address:",
        "pdf_th_item": "Item Description",
        "pdf_th_qty": "Qty",
        "pdf_th_price": "Unit Price",
        "pdf_th_total": "Total Price",
        "pdf_subtotal": "Subtotal:",
        "pdf_delivery": "Delivery Charge:",
        "pdf_total_amount": "Total Amount:",
        "pdf_paid_amount": "Paid Amount:",
        "pdf_due_amount": "Due Amount (COD):",
        "pdf_status_paid": "Status: FULLY PAID"
    },
    "বাংলা": {
        "lang_label": "🌐 Choose Language / ভাষা নির্বাচন করুন:",
        "main_title": "⚡ স্মার্ট-রিসিট প্রো ড্যাশবোর্ড",
        "subtitle": "প্রফেশনাল ক্যাশ মেমো তৈরি করুন এবং নিমেষেই হিসাব রাখুন।",
        "shop_settings": "🔐 শপের সেটিংস (Shop Settings)",
        "biz_name_lbl": "প্রতিষ্ঠানের নাম",
        "biz_email_lbl": "প্রতিষ্ঠানের ইমেইল",
        "biz_phone_lbl": "মোবাইল নম্বর",
        "upload_logo_lbl": "শপের লোগো আপলোড করুন (PNG)",
        "save_profile_btn": "💾 প্রোফাইল সেভ করুন",
        "save_success": "✅ সেটিংস সফলভাবে সেভ হয়েছে!",
        "cust_header": "👤 গ্রাহকের তথ্যাদি (Customer Info)",
        "cust_name": "পূর্ণ নাম",
        "cust_phone": "ফোন নম্বর",
        "cust_addr": "ডেলিভারি ঠিকানা",
        "order_header": "🛒 প্রোডাক্টের বিবরণ (সর্বোচ্চ ৫টি)",
        "item_lbl": "প্রোডাক্ট",
        "qty_lbl": "পরিমাণ",
        "price_lbl": "মূল্য (টাকা)",
        "billing_header": "💳 বিলিং এবং সামারি",
        "del_charge_lbl": "ডেলিভারি চার্জ (টাকা)",
        "pay_method_lbl": "পেমেন্ট মাধ্যম",
        "paid_lbl": "অগ্রিম পরিশোধ / অ্যাডভান্স (টাকা)",
        "total_bill_metric": "সর্বমোট বিল",
        "items_metric": "প্রোডাক্টের মোট দাম:",
        "due_metric": "বাকি / ক্যাশ অন ডেলিভারি",
        "remaining_metric": "- অবশিষ্ট",
        "status_metric": "পেমেন্টের অবস্থা",
        "fully_paid_metric": "পুরোপুরি পরিশোধিত",
        "success_metric": "সফল",
        "actions_header": "📄 অ্যাকশন",
        "generate_btn": "✨ মেমো তৈরি ও পিডিএফ ডাউনলোড করুন",
        "error_name": "অনুগ্রহ করে মেমো তৈরি করার আগে গ্রাহকের নাম লিখুন!",
        "download_ready_btn": "📥 পিডিএফ-টি সেভ করতে এখানে ক্লিক করুন",
        # PDF Specific
        "pdf_title": "ক্যাশ রিসিট / ইনভয়েস",
        "pdf_method": "মাধ্যম:",
        "pdf_cust_name": "গ্রাহকের নাম:",
        "pdf_mobile": "মোবাইল:",
        "pdf_address": "ঠিকানা:",
        "pdf_th_item": "প্রোডাক্টের বিবরণ",
        "pdf_th_qty": "পরিমাণ",
        "pdf_th_price": "একক মূল্য",
        "pdf_th_total": "মোট মূল্য",
        "pdf_subtotal": "উপ-মোট:",
        "pdf_delivery": "ডেলিভারি চার্জ:",
        "pdf_total_amount": "সর্বমোট বিল:",
        "pdf_paid_amount": "পরিশোধিত টাকা:",
        "pdf_due_amount": "অবশিষ্ট টাকা (COD):",
        "pdf_status_paid": "অবস্থা: সম্পূর্ণ পরিশোধিত"
    }
}

# ==========================================
# 🔘 ল্যাঙ্গুয়েজ সিলেক্টর টগল (শীর্ষে বসানো হলো)
# ==========================================
selected_lang = st.radio(
    translations["English"]["lang_label"], 
    ["English", "বাংলা"], 
    horizontal=True
)
t = translations[selected_lang]

# Custom CSS for premium look
st.markdown("""
    <style>
    .main-title {
        font-size: 32px;
        font-weight: bold;
        color: #4F46E5;
        margin-bottom: 5px;
    }
    .subtitle {
        font-size: 16px;
        color: #6B7280;
        margin-bottom: 25px;
    }
    .section-header {
        font-size: 20px;
        font-weight: 600;
        color: #1F2937;
        margin-top: 15px;
        margin-bottom: 15px;
        border-left: 4px solid #4F46E5;
        padding-left: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ২. সেশন স্টেট ব্যাকআপ (Auto-Save-এর জন্য)
if 'biz_name' not in st.session_state:
    st.session_state['biz_name'] = "My Clothing Brand"
if 'biz_email' not in st.session_state:
    st.session_state['biz_email'] = "info@mybrand.com"
if 'biz_phone' not in st.session_state:
    st.session_state['biz_phone'] = "+880 1711-XXXXXX"
if 'logo_path' not in st.session_state:
    st.session_state['logo_path'] = None

# ৩. পিডিএফ জেনারেটর ক্লাস
class CustomReceiptPDF(FPDF):
    def __init__(self, b_name, b_email, b_phone, b_logo_path=None):
        super().__init__()
        self.b_name = b_name
        self.b_email = b_email
        self.b_phone = b_phone
        self.b_logo_path = b_logo_path

    def header(self):
        if self.b_logo_path and os.path.exists(self.b_logo_path):
            self.image(self.b_logo_path, x=90, y=10, w=30)
            self.ln(35)
        else:
            self.ln(10)
            
        self.set_font('Helvetica', 'B', 20)
        self.cell(0, 10, self.b_name.upper(), ln=True, align='C')
        self.set_font('Helvetica', '', 10)
        self.cell(0, 5, f"Email: {self.b_email}  |  Mobile: {self.b_phone}", ln=True, align='C')
        self.ln(5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, 'Thank you for shopping with us! Powered by Smart-Receipt Pro.', align='C')

def generate_pdf(filename, b_info, c_info, products_list, del_charge, payment_method, paid_amount):
    pdf = CustomReceiptPDF(b_info['name'], b_info['email'], b_info['phone'], b_info['logo'])
    pdf.add_page()
    
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(100, 10, t["pdf_title"], border=0)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(90, 10, f"{t['pdf_method']} {payment_method}", border=0, ln=True, align='R')
    pdf.ln(5)
    
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 7, f"{t['pdf_cust_name']} {c_info['name']}", ln=True)
    pdf.cell(0, 7, f"{t['pdf_mobile']} {c_info['phone']}", ln=True)
    pdf.cell(0, 7, f"{t['pdf_address']} {c_info['address']}", ln=True)
    
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(100, 10, t["pdf_th_item"], border=0)
    pdf.cell(30, 10, t["pdf_th_qty"], border=0, align='C')
    pdf.cell(30, 10, t["pdf_th_price"], border=0, align='R')
    pdf.cell(30, 10, t["pdf_th_total"], border=0, ln=True, align='R')
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)
    
    subtotal = 0
    pdf.set_font('Helvetica', '', 11)
    for p in products_list:
        if p['name'].strip() != "":
            item_total = p['price'] * p['qty']
            subtotal += item_total
            pdf.cell(100, 10, p['name'], border=0)
            pdf.cell(30, 10, str(p['qty']), border=0, align='C')
            pdf.cell(30, 10, f"{p['price']} TK", border=0, align='R')
            pdf.cell(30, 10, f"{item_total} TK", border=0, ln=True, align='R')
    
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    total_bill = subtotal + del_charge
    due_amount = total_bill - paid_amount
    
    pdf.cell(160, 8, t["pdf_subtotal"], border=0, align='R')
    pdf.cell(30, 8, f"{subtotal} TK", border=0, ln=True, align='R')
    
    pdf.cell(160, 8, t["pdf_delivery"], border=0, align='R')
    pdf.cell(30, 8, f"{del_charge} TK", border=0, ln=True, align='R')
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(160, 8, t["pdf_total_amount"], border=0, align='R')
    pdf.cell(30, 8, f"{total_bill} TK", border=0, ln=True, align='R')
    
    pdf.set_text_color(0, 128, 0)
    pdf.cell(160, 8, t["pdf_paid_amount"], border=0, align='R')
    pdf.cell(30, 8, f"{paid_amount} TK", border=0, ln=True, align='R')
    
    if due_amount > 0:
        pdf.set_text_color(255, 0, 0)
        pdf.cell(160, 8, t["pdf_due_amount"], border=0, align='R')
        pdf.cell(30, 8, f"{due_amount} TK", border=0, ln=True, align='R')
    else:
        pdf.set_text_color(0, 128, 0)
        pdf.cell(160, 8, t["pdf_status_paid"], border=0, ln=True, align='R')
        
    pdf.set_text_color(0, 0, 0)
    pdf.output(filename)

# ৪. সাইডবার সেটিংস (Auto-Save functionality সহ)
st.sidebar.markdown(f"### {t['shop_settings']}")
input_biz_name = st.sidebar.text_input(t["biz_name_lbl"], st.session_state['biz_name'])
input_biz_email = st.sidebar.text_input(t["biz_email_lbl"], st.session_state['biz_email'])
input_biz_phone = st.sidebar.text_input(t["biz_phone_lbl"], st.session_state['biz_phone'])

uploaded_logo = st.sidebar.file_uploader(t["upload_logo_lbl"], type=["png"])

if st.sidebar.button(t["save_profile_btn"], type="secondary"):
    st.session_state['biz_name'] = input_biz_name
    st.session_state['biz_email'] = input_biz_email
    st.session_state['biz_phone'] = input_biz_phone
    
    if uploaded_logo:
        logo_path = "saved_logo.png"
        with open(logo_path, "wb") as f:
            f.write(uploaded_logo.getbuffer())
        st.session_state['logo_path'] = logo_path
        
    st.sidebar.success(t["save_success"])

# ৫. মূল অ্যাপ ইন্টারফেস
st.markdown(f'<div class="main-title">{t["main_title"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="subtitle">{t["subtitle"]}</div>', unsafe_allow_html=True)

# কাস্টমার ইনফো সেকশন
st.markdown(f'<div class="section-header">{t["cust_header"]}</div>', unsafe_allow_html=True)
c_col1, c_col2, c_col3 = st.columns(3)
with c_col1:
    v_name = st.text_input(t["cust_name"], placeholder="e.g. Rahat Rahman")
with c_col2:
    v_phone = st.text_input(t["cust_phone"], placeholder="e.g. 017XXXXXXXX")
with c_col3:
    v_addr = st.text_input(t["cust_addr"], placeholder="e.g. Sylhet, Bangladesh")

st.write("")

# প্রোডাক্ট এবং পেমেন্ট সেকশন মিক্সড করা (Side-by-Side Setup)
col_left, col_right = st.columns([5, 4])

with col_left:
    st.markdown(f'<div class="section-header">{t["order_header"]}</div>', unsafe_allow_html=True)
    products_list = []
    sub_total_calc = 0
    
    for i in range(1, 6):
        p_col1, p_col2, p_col3 = st.columns([3, 1, 1.5])
        with p_col1:
            p_name = st.text_input(f"{t['item_lbl']} {i}", key=f"p{i}_name", placeholder=f"Product name...")
        with p_col2:
            p_qty = st.number_input(t["qty_lbl"], min_value=1, value=1, step=1, key=f"p{i}_qty")
        with p_col3:
            p_price = st.number_input(t["price_lbl"], min_value=0, value=0, step=50, key=f"p{i}_price")
        
        if p_name.strip() != "":
            products_list.append({'name': p_name, 'qty': p_qty, 'price': p_price})
            sub_total_calc += (p_price * p_qty)

with col_right:
    st.markdown(f'<div class="section-header">{t["billing_header"]}</div>', unsafe_allow_html=True)
    
    pay_col1, pay_col2 = st.columns(2)
    with pay_col1:
        del_charge = st.number_input(t["del_charge_lbl"], min_value=0, value=60, step=10)
        pay_options = ["Cash on Delivery (COD)", "bKash", "Nagad", "Rocket"] if selected_lang == "English" else ["ক্যাশ অন ডেলিভারি (COD)", "বিকাশ", "নগদ", "রকেট"]
        pay_method = st.selectbox(t["pay_method_lbl"], options=pay_options)
    with pay_col2:
        paid_tk = st.number_input(t["paid_lbl"], min_value=0, value=0, step=50)
    
    st.write("")
    grand_total_calc = sub_total_calc + del_charge
    final_due_calc = grand_total_calc - paid_tk
    
    # লাইভ প্রিভিউ কার্ড (Live Preview Metrics Cards)
    m_col1, m_col2 = st.columns(2)
    m_col1.metric(label=t["total_bill_metric"], value=f"{grand_total_calc} TK", delta=f"{t['items_metric']} {sub_total_calc} TK")
    
    if final_due_calc > 0:
        m_col2.metric(label=t["due_metric"], value=f"{final_due_calc} TK", delta=t["remaining_metric"], delta_color="inverse")
    else:
        m_col2.metric(label=t["status_metric"], value=t["fully_paid_metric"], delta=t["success_metric"], delta_color="normal")

st.markdown("---")

# ডাউনলোড সেকশন
st.markdown(f'<div class="section-header">{t["actions_header"]}</div>', unsafe_allow_html=True)
if st.button(t["generate_btn"], type="primary", use_container_width=True):
    if v_name.strip() == "":
        st.error(t["error_name"])
    else:
        # সেশন স্টেট থেকে সেভ করা শপ ডাটা নেওয়া হচ্ছে
        b_info = {
            'name': st.session_state['biz_name'], 
            'email': st.session_state['biz_email'], 
            'phone': st.session_state['biz_phone'], 
            'logo': st.session_state['logo_path']
        }
        c_info = {'name': v_name, 'phone': v_phone, 'address': v_addr}
        
        pdf_filename = f"Receipt_{v_name.replace(' ', '_')}.pdf"
        generate_pdf(pdf_filename, b_info, c_info, products_list, del_charge, pay_method, paid_tk)
        
        with open(pdf_filename, "rb") as file:
            st.download_button(
                label=t["download_ready_btn"],
                data=file,
                file_name=pdf_filename,
                mime="application/pdf",
                use_container_width=True
            )