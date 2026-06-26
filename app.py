import streamlit as st
from fpdf import FPDF
import os

# ১. পেজ সেটআপ ও থিম
st.set_page_config(page_title="Smart-Receipt Pro", page_icon="📄", layout="wide")

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
    pdf.cell(100, 10, 'CASH RECEIPT / INVOICE', border=0)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(90, 10, f"Method: {payment_method}", border=0, ln=True, align='R')
    pdf.ln(5)
    
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 7, f"Customer Name: {c_info['name']}", ln=True)
    pdf.cell(0, 7, f"Mobile: {c_info['phone']}", ln=True)
    pdf.cell(0, 7, f"Address: {c_info['address']}", ln=True)
    
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(100, 10, 'Item Description', border=0)
    pdf.cell(30, 10, 'Qty', border=0, align='C')
    pdf.cell(30, 10, 'Unit Price', border=0, align='R')
    pdf.cell(30, 10, 'Total Price', border=0, ln=True, align='R')
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
    
    pdf.cell(160, 8, 'Subtotal:', border=0, align='R')
    pdf.cell(30, 8, f"{subtotal} TK", border=0, ln=True, align='R')
    
    pdf.cell(160, 8, 'Delivery Charge:', border=0, align='R')
    pdf.cell(30, 8, f"{del_charge} TK", border=0, ln=True, align='R')
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(160, 8, 'Total Amount:', border=0, align='R')
    pdf.cell(30, 8, f"{total_bill} TK", border=0, ln=True, align='R')
    
    pdf.set_text_color(0, 128, 0)
    pdf.cell(160, 8, 'Paid Amount:', border=0, align='R')
    pdf.cell(30, 8, f"{paid_amount} TK", border=0, ln=True, align='R')
    
    if due_amount > 0:
        pdf.set_text_color(255, 0, 0)
        pdf.cell(160, 8, 'Due Amount (COD):', border=0, align='R')
        pdf.cell(30, 8, f"{due_amount} TK", border=0, ln=True, align='R')
    else:
        pdf.set_text_color(0, 128, 0)
        pdf.cell(160, 8, 'Status: FULLY PAID', border=0, ln=True, align='R')
        
    pdf.set_text_color(0, 0, 0)
    pdf.output(filename)

# ৪. সাইডবার সেটিংস (Auto-Save functionality সহ)
st.sidebar.markdown("### 🔐 Shop Settings")
input_biz_name = st.sidebar.text_input("Business Name", st.session_state['biz_name'])
input_biz_email = st.sidebar.text_input("Business Email", st.session_state['biz_email'])
input_biz_phone = st.sidebar.text_input("Business Mobile", st.session_state['biz_phone'])

uploaded_logo = st.sidebar.file_uploader("Upload Shop Logo (PNG)", type=["png"])

if st.sidebar.button("💾 Save Profile Settings", type="secondary"):
    st.session_state['biz_name'] = input_biz_name
    st.session_state['biz_email'] = input_biz_email
    st.session_state['biz_phone'] = input_biz_phone
    
    if uploaded_logo:
        logo_path = "saved_logo.png"
        with open(logo_path, "wb") as f:
            f.write(uploaded_logo.getbuffer())
        st.session_state['logo_path'] = logo_path
        
    st.sidebar.success("✅ Settings Saved Successfully!")

# ৫. মূল অ্যাপ ইন্টারফেস
st.markdown('<div class="main-title">⚡ Smart-Receipt Pro Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Create professional business invoices and track billing instantly.</div>', unsafe_allow_html=True)

# কাস্টমার ইনফো সেকশন
st.markdown('<div class="section-header">👤 Customer Information</div>', unsafe_allow_html=True)
c_col1, c_col2, c_col3 = st.columns(3)
with c_col1:
    v_name = st.text_input("Full Name", placeholder="e.g. Rahat Rahman")
with c_col2:
    v_phone = st.text_input("Phone Number", placeholder="e.g. 017XXXXXXXX")
with c_col3:
    v_addr = st.text_input("Delivery Address", placeholder="e.g. Sylhet, Bangladesh")

st.write("")

# প্রোডাক্ট এবং পেমেন্ট সেকশন মিক্সড করা (Side-by-Side Setup)
col_left, col_right = st.columns([5, 4])

with col_left:
    st.markdown('<div class="section-header">🛒 Order Items (Max 5)</div>', unsafe_allow_html=True)
    products_list = []
    sub_total_calc = 0
    
    for i in range(1, 6):
        p_col1, p_col2, p_col3 = st.columns([3, 1, 1.5])
        with p_col1:
            p_name = st.text_input(f"Item {i}", key=f"p{i}_name", placeholder=f"Product name...")
        with p_col2:
            p_qty = st.number_input(f"Qty", min_value=1, value=1, step=1, key=f"p{i}_qty")
        with p_col3:
            p_price = st.number_input(f"Price (TK)", min_value=0, value=0, step=50, key=f"p{i}_price")
        
        if p_name.strip() != "":
            products_list.append({'name': p_name, 'qty': p_qty, 'price': p_price})
            sub_total_calc += (p_price * p_qty)

with col_right:
    st.markdown('<div class="section-header">💳 Billing & Summary</div>', unsafe_allow_html=True)
    
    pay_col1, pay_col2 = st.columns(2)
    with pay_col1:
        del_charge = st.number_input("Delivery Charge (TK)", min_value=0, value=60, step=10)
        pay_method = st.selectbox("Payment Method", options=["Cash on Delivery (COD)", "bKash", "Nagad", "Rocket"])
    with pay_col2:
        paid_tk = st.number_input("Paid Amount / Advance (TK)", min_value=0, value=0, step=50)
    
    st.write("")
    grand_total_calc = sub_total_calc + del_charge
    final_due_calc = grand_total_calc - paid_tk
    
    # লাইভ প্রিভিউ কার্ড (Live Preview Metrics Cards)
    m_col1, m_col2 = st.columns(2)
    m_col1.metric(label="Total Bill (TK)", value=f"{grand_total_calc} TK", delta=f"Items: {sub_total_calc} TK")
    
    if final_due_calc > 0:
        m_col2.metric(label="Due / COD Amount", value=f"{final_due_calc} TK", delta="- Remaining", delta_color="inverse")
    else:
        m_col2.metric(label="Payment Status", value="FULLY PAID", delta="Success", delta_color="normal")

st.markdown("---")

# ডাউনলোড সেকশন
st.markdown('<div class="section-header">📄 Actions</div>', unsafe_allow_html=True)
if st.button("✨ Generate & Download PDF Memo", type="primary", use_container_width=True):
    if v_name.strip() == "":
        st.error("Please enter a Customer Name before generating the invoice!")
    else:
        # সেশন স্টেট থেকে সেভ করা শপ ডাটা নেওয়া হচ্ছে
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
                label="📥 Click here to Save PDF",
                data=file,
                file_name=pdf_filename,
                mime="application/pdf",
                use_container_width=True
            )