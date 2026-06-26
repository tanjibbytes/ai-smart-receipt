import streamlit as st
from fpdf import FPDF
import google.generativeai as genai
import json
import os

# ১. পেজ সেটআপ
st.set_page_config(page_title="AI Smart-Receipt Pro", page_icon="📄", layout="wide")

# ২. এআই কনফিগারেশন (স্ট্রিমলিট সিক্রেটস থেকে কি নেবে)
try:
    GENAI_API_KEY = st.secrets["GENAI_API_KEY"]
    genai.configure(api_key=GENAI_API_KEY)
except Exception as e:
    st.error("API Key not configured in Secrets! Please check settings.")

def extract_customer_info_with_ai(raw_message):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    You are an expert order management AI. Analyze the following Facebook/Instagram order message and extract the details in strict JSON format.
    Convert Banglish names or addresses to proper English if appropriate, but keep Bangladeshi context (e.g., Sylhet, Dhaka).
    
    Message: "{raw_message}"
    
    Output Format (Strictly return ONLY valid JSON, no markdown codeblocks, no extra text):
    {{
        "name": "Customer Name",
        "phone": "Phone Number",
        "address": "Full Delivery Address",
        "product": "Product Name and Size/Color details"
    }}
    """
    try:
        response = model.generate_content(prompt)
        text_data = response.text.strip()
        if text_data.startswith("```json"):
            text_data = text_data.replace("```json", "").replace("```", "").strip()
        data = json.loads(text_data)
        return data
    except Exception as e:
        return {
            "name": "Extraction Failed",
            "phone": "N/A",
            "address": "Please type manually",
            "product": "Please type manually"
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

def generate_pdf(filename, b_info, c_info, order_info):
    pdf = CustomReceiptPDF(b_info['name'], b_info['email'], b_info['phone'], b_info['logo'])
    pdf.add_page()
    
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, 'CASH RECEIPT / INVOICE', ln=True)
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 7, f"Customer Name: {c_info['name']}", ln=True)
    pdf.cell(0, 7, f"Mobile: {c_info['phone']}", ln=True)
    pdf.cell(0, 7, f"Address: {c_info['address']}", ln=True)
    
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(130, 10, 'Item Description', border=0)
    pdf.cell(60, 10, 'Price', border=0, ln=True, align='R')
    
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(130, 10, order_info['product'], border=0)
    pdf.cell(60, 10, f"{order_info['price']} TK", border=0, ln=True, align='R')
    
    pdf.cell(130, 10, 'Delivery Charge', border=0)
    pdf.cell(60, 10, f"{order_info['delivery']} TK", border=0, ln=True, align='R')
    
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    total_bill = order_info['price'] + order_info['delivery']
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(130, 10, 'Total Payable:', border=0)
    pdf.cell(60, 10, f"{total_bill} TK", border=0, ln=True, align='R')
    
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
st.write("ফেসবুক/ইনস্টাগ্রাম মেসেজ পেস্ট করে এক ক্লিকে পিডিএফ মেমো তৈরি করুন।")
st.write("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📥 Input Area")
    fb_message = st.text_area(
        "কাস্টমারের মেসেজটি এখানে পেস্ট করুন:", 
        placeholder="Example: Ami tanzim, Sylhet zindabazar thaki. 01712345678. Black Hoodie ta diben L size...",
        height=150
    )
    prod_price = st.number_input("Product Price (TK)", min_value=0, value=0, step=50)
    del_charge = st.radio("Delivery Charge (TK)", options=[60, 80, 120, 150], index=1)

with col2:
    st.subheader("🚀 AI Generated Output")
    if st.button("Process Message & Generate PDF", type="primary"):
        if fb_message.strip() == "":
            st.error("Please paste a message first!")
        else:
            with st.spinner("AI is reading the message..."):
                ai_data = extract_customer_info_with_ai(fb_message)
            
            st.success("AI extraction complete!")
            
            # এআই থেকে পাওয়া ডেটা এডিটেবল বক্সে দেখানো
            c_name = st.text_input("Customer Name", ai_data.get('name', ''))
            c_phone = st.text_input("Phone", ai_data.get('phone', ''))
            c_addr = st.text_input("Address", ai_data.get('address', ''))
            p_name = st.text_input("Product Details", ai_data.get('product', ''))
            
            b_info = {'name': biz_name, 'email': biz_email, 'phone': biz_phone, 'logo': logo_path}
            c_info = {'name': c_name, 'phone': c_phone, 'address': c_addr}
            order_info = {'product': p_name, 'price': prod_price, 'delivery': del_charge}
            
            pdf_filename = f"Receipt_{c_name.replace(' ', '_')}.pdf"
            generate_pdf(pdf_filename, b_info, c_info, order_info)
            
            with open(pdf_filename, "rb") as file:
                st.download_button(
                    label="📥 Download PDF Receipt",
                    data=file,
                    file_name=pdf_filename,
                    mime="application/pdf"
                )
