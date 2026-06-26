import streamlit as st
from fpdf import FPDF
import google.generativeai as genai
import json
import os
import re

# ১. পেজ সেটআপ
st.set_page_config(page_title="AI Smart-Receipt Pro", page_icon="📄", layout="wide")

# ২. এআই কনফিগারেশন
try:
    GENAI_API_KEY = st.secrets["GENAI_API_KEY"]
    genai.configure(api_key=GENAI_API_KEY)
except Exception as e:
    st.error("API Key not configured in Secrets! Please check settings.")

def extract_customer_info_with_ai(raw_message):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    You are an expert order management AI. Analyze the following online shopping order message from Bangladesh and extract details.
    
    Instructions:
    1. Extract Customer Name, Phone, and Address. 
    2. Identify all products mentioned. Extract up to 5 distinct products.
    3. For each product, extract its name (clean and readable), quantity (default to 1 if not mentioned), and price (default to 0 if not mentioned).
    
    Message: "{raw_message}"
    
    Return ONLY a raw JSON object matching this structure, with no markdown formatting, no ```json tags, and no extra text:
    {{
        "name": "Customer Name",
        "phone": "Phone Number",
        "address": "Delivery Address",
        "products": [
            {{"name": "Product Name 1", "qty": 1, "price": 0}},
            {{"name": "Product Name 2", "qty": 2, "price": 450}}
        ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        text_data = response.text.strip()
        
        # ক্লিনিং: যদি এআই ভুল করে কোনো ব্যাকটিক বা ```json ব্লক দেয় তা কেটে ফেলা
        if "```" in text_data:
            text_data = re.sub(r'```[a-zA-Z]*', '', text_data).strip()
            
        data = json.loads(text_data)
        return data
    except Exception as e:
        # ব্যাকআপ সলিউশন: কোনো কারণে ফেল করলে ক্র্যাশ করবে না
        phone_match = re.search(r'(01[3-9]\d{8})', raw_message)
        return {
            "name": "Customer Name",
            "phone": phone_match.group(1).strip() if phone_match else "N/A",
            "address": "Please type address manually",
            "products": []
        }

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
        self.cell(0, 10, 'Thank you for shopping with us! Powered by AI Smart-Receipt.', align='C')

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

# ৪. সাইডবার সেটিংস
st.sidebar.title("🔐 Shop Profile Settings")
biz_name = st.sidebar.text_input("Business Name", "My Clothing Brand")
biz_email = st.sidebar.text_input("Business Email", "info@mybrand.com")
biz_phone = st.sidebar.text_input("Business Mobile", "+880 1711-XXXXXX")

uploaded_logo = st.sidebar.file_uploader("Upload Shop Logo (PNG)", type=["png"])
logo_path = "temp_logo.png" if uploaded_logo else None
if uploaded_logo:
    with open(logo_path, "wb") as f:
        f.write(uploaded_logo.getbuffer())

# ৫. মূল অ্যাপ
st.title("📄 AI Smart-Receipt & Social Dispatcher Pro")
st.write("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📥 Input Area")
    fb_message = st.text_area(
        "কাস্টমারের মেসেজটি এখানে পেস্ট করুন:", 
        placeholder="Example: Name: Ahmed, Phone: 01711223344, Addr: Sylhet. 2ta Black T-Shirt and 1ta Blue Jeans.",
        height=120
    )
    del_charge = st.number_input("Delivery Charge (TK)", min_value=0, value=60, step=10)
    pay_method = st.selectbox("Payment Method", options=["Cash on Delivery (COD)", "bKash", "Nagad", "Rocket"])
    paid_tk = st.number_input("Paid Amount / Advance (TK)", min_value=0, value=0, step=50)

with col2:
    st.subheader("🚀 AI Generated Output")
    if st.button("Process Message & Generate PDF", type="primary"):
        if fb_message.strip() == "":
            st.error("Please paste a message first!")
        else:
            with st.spinner("AI is reading the message and separating products..."):
                ai_data = extract_customer_info_with_ai(fb_message)
            st.success("AI extraction complete!")
            
            # সেশন স্টেটে ডেটা সেভ করা যাতে রিফ্রেশে চলে না যায়
            st.session_state['c_name'] = ai_data.get('name', '')
            st.session_state['c_phone'] = ai_data.get('phone', '')
            st.session_state['c_addr'] = ai_data.get('address', '')
            st.session_state['ai_products'] = ai_data.get('products', [])

if 'c_name' in st.session_state:
    st.write("---")
    st.subheader("📝 Verify Details & Order Items")
    
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        v_name = st.text_input("Customer Name", st.session_state['c_name'])
        v_phone = st.text_input("Phone", st.session_state['c_phone'])
    with c_col2:
        v_addr = st.text_input("Address", st.session_state['c_addr'])

    st.write("#### 🛒 Products in this Order (Max 5)")
    products_list = []
    
    ai_extracted_prods = st.session_state.get('ai_products', [])
    sub_total_calc = 0
    
    for i in range(1, 6):
        p_col1, p_col2, p_col3 = st.columns([2, 1, 1])
        
        # ডিফল্ট ব্ল্যাঙ্ক ভ্যালু সেটআপ
        ai_p_name = ""
        ai_p_qty = 1
        ai_p_price = 0
        
        # যদি এআই ওই নির্দিষ্ট ইনডেক্সের জন্য কোনো প্রোডাক্ট পেয়ে থাকে
        if len(ai_extracted_prods) >= i:
            ai_p_name = ai_extracted_prods[i-1].get('name', '')
            ai_p_qty = ai_extracted_prods[i-1].get('qty', 1)
            try:
                ai_p_price = int(ai_extracted_prods[i-1].get('price', 0))
            except:
                ai_p_price = 0
        
        with p_col1:
            p_name = st.text_input(f"Product {i} Name", value=ai_p_name, key=f"p{i}_name", placeholder=f"Product {i} name...")
        with p_col2:
            p_qty = st.number_input(f"Product {i} Qty", min_value=1, value=int(ai_p_qty) if ai_p_qty else 1, step=1, key=f"p{i}_qty")
        with p_col3:
            p_price = st.number_input(f"Product {i} Price (TK)", min_value=0, value=int(ai_p_price), step=50, key=f"p{i}_price")
        
        if p_name.strip() != "":
            products_list.append({'name': p_name, 'qty': p_qty, 'price': p_price})
            sub_total_calc += (p_price * p_qty)

    grand_total_calc = sub_total_calc + del_charge
    final_due_calc = grand_total_calc - paid_tk
    
    st.write("---")
    st.write(f"**Total Bill:** {grand_total_calc} TK | **Paid:** {paid_tk} TK")
    if final_due_calc > 0:
        st.error(f"⚠️ **Due (Cash on Delivery):** {final_due_calc} TK")
    else:
        st.success("✅ **Status:** FULLY PAID")

    if st.button("Generate & Download PDF Memo", type="secondary"):
        b_info = {'name': biz_name, 'email': biz_email, 'phone': biz_phone, 'logo': logo_path}
        c_info = {'name': v_name, 'phone': v_phone, 'address': v_addr}
        
        pdf_filename = f"Receipt_{v_name.replace(' ', '_')}.pdf"
        generate_pdf(pdf_filename, b_info, c_info, products_list, del_charge, pay_method, paid_tk)
        
        with open(pdf_filename, "rb") as file:
            st.download_button(
                label="📥 Click here to Save PDF",
                data=file,
                file_name=pdf_filename,
                mime="application/pdf"
            )