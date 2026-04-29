import base64
import streamlit as st
from supabase import create_client
import streamlit.components.v1 as components
import datetime
from PIL import Image
import io
from barcode import Code128
from barcode.writer import ImageWriter




# ---------------------------
# SUPABASE CONFIG
# ---------------------------
SUPABASE_URL = "https://faepxvomqitkrwrmvqkw.supabase.co"
SUPABASE_KEY = "sb_publishable_TRUzAINeAbQ1Jf5bL8qofg_0FlGMin6"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="DTDC Booking", layout="centered")
st.title("📦 DTDC Booking")




# ---------------------------
# IMAGE COMPRESS
# ---------------------------
def compress_image(uploaded_file):
    img = Image.open(uploaded_file)
    img = img.resize((800, 800))

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=30)

    return buffer.getvalue()



# ---------------------------
# GET logo
# ---------------------------

def get_logo_base64():
    with open("logo.png", "rb") as f:
        return base64.b64encode(f.read()).decode()


# ---------------------------
# GET barcode
# ---------------------------

def generate_barcode_base64(cn):
    buffer = io.BytesIO()
    barcode = Code128(cn, writer=ImageWriter())
    barcode.write(buffer, {"module_height": 15, "module_width": 0.3,"write_text": False})
    return base64.b64encode(buffer.getvalue()).decode()    



# ---------------------------
# GET NEXT CN
# ---------------------------
def get_next_cn(customer):
    res = supabase.table("consignment_no") \
        .select("*") \
        .eq("customer_name", customer) \
        .is_("used_date", None) \
        .limit(1) \
        .execute()

    if res.data:
        return res.data[0]["consignment_no"]
    return ""




# ---------------------------
# MARK USED
# ---------------------------
def mark_used(cn):
    supabase.table("consignment_no") \
        .update({"used_date": str(datetime.datetime.now())}) \
        .eq("consignment_no", cn) \
        .execute()





# ---------------------------
# HTML BILL (DTDC STYLE 🔥)
# ---------------------------
def generate_html_bill(cn, sender, receiver, pincode, content):

    return f"""
    <html>
    <body style="font-family: Arial; border:2px solid black; padding:10px;">
    
    <h2>DTDC EXPRESS LIMITED</h2>

    <table border="1" width="100%" cellspacing="0" cellpadding="5">
        <tr>
            <td><b>Consignor</b><br>{sender}</td>
            <td><b>Consignee</b><br>{receiver}</td>
        </tr>
        <tr>
            <td>Pincode: {pincode}</td>
            <td>Content: {content}</td>
        </tr>
    </table>

    <h3 style="text-align:center;">AWB No: {cn}</h3>

    <div style="text-align:center; margin-top:20px;">
        <button onclick="window.print()">🖨️ Print</button>
    </div>

    <p style="text-align:center; margin-top:20px;">
    THIS DOCUMENT IS NOT A TAX INVOICE
    </p>

    </body>
    </html>
    """


def generate_html_bill1(cn, sender_name, sender_addr, sender_phone,
                       receiver_name, receiver_addr, receiver_phone,
                       content, value, pieces, weight, dim,
                       origin="TRICHY", dest="DELHI", product="STD EXP-S"):

  
    barcode_base64 = generate_barcode_base64(cn)
    logo_base64 = get_logo_base64()

    return f"""
<html>
    <head>
    
    <style>
        body {{
            font-family: Arial;
            margin:0;
            padding:0;
        }}

        .container {{
            border:2px solid black;
            width:100%;
            box-sizing: border-box;
        }}

        table {{
            width:100%;
            border-collapse: collapse;
            table-layout: fixed;
        }}

        td {{
            border:1px solid black;
            padding:5px;
            font-size:12px;
        }}

        .logo {{
            width:100px;
        }}

        .center {{
            text-align:center;
        }}

        .big {{
            font-size:18px;
            font-weight:bold;
        }}

        @media print {{
            button {{
                display:none;
            }}
        }}
        </style>
        </head>

        <body>

    <div class="container">
    <table>
        <tr>
            <td width="50%">
                <img src="data:image/png;base64,{logo_base64}" class="logo"><br>
                DTDC Express Limited<br>
                Regd. Office No. 3, Victoria Road<br>
                Bengaluru - 560047
            </td>

            <td width="25%">
                Origin: <b>{origin}</b><br><br>
                PRODUCT: <b>{product}</b>
            </td>

            <td width="25%">
                Dest: <b>{dest}</b><br><br>
                Type: <b>NON-DOCUMENT</b><br><br>
                Date: {datetime.datetime.now().strftime("%a %b %d %Y")}
            </td>
        </tr>
    </table>


    <table>
        <tr>
            <td width="50%">
            Consignor's Name: <b>{sender_name}</b><br>
            Consignor's Address: {sender_addr}<br>
            Phone: {sender_phone}
            </td>

            <td width="50%">
            Consignee's Name: <b>{receiver_name}</b><br>
            Consignee's Address: {receiver_addr}<br>
            Phone: {receiver_phone}
            </td>
        </tr>
    </table>

    <table>
        <tr>
            <td width="50%">
                Content: {content}<br>
                Value: {value}<br>
                Pieces: {pieces}<br>
                Weight: {weight}
            </td>

            <td width="50%">
                <!-- 🔥 REAL BARCODE -->
                <img src="data:image/png;base64,{barcode_base64}" style="display:block;margin:auto;width:80%;height:50px;">
                <div class="center big">AWB No: {cn}</div>
            </td>

        </tr>
    </table>

    <table>
        <tr>
            <td width="50%">
                Declaration text...
                <br><br>
                <b>Sender Signature</b>
            </td>

            <td width="50%" class="center big">
                Risk Surcharge
            </td>
        </tr>
    </table>    

    <table>
        <tr>
            <td class="center">
                https://www.dtdc.in | +91-9606911811
            </td>
        </tr>
    </table>

    <table>
        <tr>
            <td class="center">
                THIS DOCUMENT IS NOT A TAX INVOICE
            </td>
        </tr>
    </table>

    </div>

    <div style="text-align:center;margin-top:10px;">
    <button onclick="window.print()">🖨️ Print</button>
    </div>

    </body>
</html>
"""


# ---------------------------
# UI
# ---------------------------
customer = st.selectbox("Customer", ["CUS1", "CUS2", "CUS3"])

cn_auto = get_next_cn(customer)
st.success(f"Auto CN: {cn_auto}")



# ---------------------------
# BARCODE SCANNER 🔥
# ---------------------------

st.subheader("📷 Barcode Scanner")

scan_value = components.html("""
<div id="reader" style="width:100%"></div>

<script src="https://unpkg.com/html5-qrcode"></script>

<script>
function sendToStreamlit(value){
    window.parent.postMessage({
        type: "streamlit:setComponentValue",
        value: value
    }, "*");
}

function onScanSuccess(decodedText) {
    sendToStreamlit(decodedText);
}

let scanner = new Html5Qrcode("reader");

scanner.start(
    { facingMode: "environment" },
    {
        fps: 10,
        qrbox: { width: 250, height: 120 },
        formatsToSupport: [Html5QrcodeSupportedFormats.CODE_128]
    },
    onScanSuccess
);
</script>
""", height=300)

# 👉 இதுதான் important
if scan_value:
    st.success(f"Scanned: {scan_value}")
    st.session_state["cn"] = scan_value
    cn_auto =  scan_value


scanned_value = st.text_input("Paste scanned value here")

barcode = st.text_input("Or Enter CN manually", value=cn_auto)

cn = scanned_value if scanned_value else barcode






sender_phone = st.text_input("Sender Phone")
receiver_phone = st.text_input("Receiver Phone")
pincode = st.text_input("Pincode")
content = st.text_input("Content")

photo = st.file_uploader("Upload Photo")
print_required = st.checkbox("Print")

# ---------------------------
# SUBMIT
# ---------------------------
if st.button("Submit"):

    if not sender_phone:
        st.error("Sender phone required")
        st.stop()

    # PHOTO SAVE
    if photo:
        compressed = compress_image(photo)
        supabase.storage.from_("photos").upload(f"{cn}.jpg", compressed)

    # SAVE RECORD
    supabase.table("record").insert({
        "consignment": cn,
        "customer": customer,
        "sender_phone": sender_phone,
        "receiver_phone": receiver_phone,
        "pincode": pincode,
        "content": content
    }).execute()

    mark_used(cn)

    st.success(f"Donee ✅ {cn}")

    # ---------------------------
    # BILL SHOW (MOBILE FRIENDLY 🔥)
    # ---------------------------
    #html = generate_html_bill(cn, sender_phone, receiver_phone, pincode, content)

    html = generate_html_bill1("c22121","harish","trichy","1234567890",
                             "rajesh","delhi","0987654321","Sample Content", "1000", 1, 10, "10x10x10" ,"TRICHY","DELHI","STD EXP-S");

    

    st.components.v1.html(html, height=600)

    # ---------------------------
    # DOWNLOAD
    # ---------------------------
    st.download_button(
        "📄 Download Bill",
        html,
        file_name=f"{cn}.html"
    )

    # ---------------------------
    # RELOAD FIX 🔥
    # ---------------------------
    st.experimental_rerun()
