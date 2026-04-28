import streamlit as st
from supabase import create_client
import datetime
import base64
from PIL import Image
import io
import requests

# ---------------------------
# SUPABASE CONFIG
# ---------------------------
SUPABASE_URL = "https://faepxvomqitkrwrmvqkw.supabase.co/rest/v1/"
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
    return None

# ---------------------------
# MARK USED
# ---------------------------
def mark_used(cn):
    supabase.table("consignment_no") \
        .update({"used_date": str(datetime.datetime.now())}) \
        .eq("consignment_no", cn) \
        .execute()

# ---------------------------
# UI
# ---------------------------
customer = st.selectbox("Customer", ["CUS1", "CUS2", "CUS3"])

cn_auto = get_next_cn(customer)

st.success(f"Auto CN: {cn_auto}")

barcode = st.text_input("Scan / Enter CN")

if barcode:
    cn = barcode
else:
    cn = cn_auto

# ---------------------------
# INPUTS
# ---------------------------
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

    # ---------------------------
    # COMPRESS + UPLOAD PHOTO
    # ---------------------------
    photo_url = ""

    if photo:
        compressed = compress_image(photo)

        supabase.storage.from_("photos").upload(
            f"{cn}.jpg",
            compressed
        )

        photo_url = f"{SUPABASE_URL}/storage/v1/object/public/photos/{cn}.jpg"

    # ---------------------------
    # PDF GENERATE (HTML)
    # ---------------------------
    html = f"""
    <h3>DTDC BILL</h3>
    CN: {cn}<br>
    Sender: {sender_phone}<br>
    Receiver: {receiver_phone}<br>
    Pincode: {pincode}<br>
    Content: {content}
    """

    pdf_bytes = html.encode()

    supabase.storage.from_("bills").upload(
        f"{cn}.pdf",
        pdf_bytes
    )

    # ---------------------------
    # SAVE RECORD
    # ---------------------------
    supabase.table("record").insert({
        "consignment": cn,
        "customer": customer,
        "sender_phone": sender_phone,
        "receiver_phone": receiver_phone,
        "pincode": pincode,
        "content": content
    }).execute()

    # ---------------------------
    # MARK USED
    # ---------------------------
    mark_used(cn)

    # ---------------------------
    # PRINT (OPTIONAL)
    # ---------------------------
    if print_required:
        try:
            requests.post("https://your-print-api/print", json={"cn": cn})
        except:
            pass

    st.success(f"Done ✅ {cn}")

    st.experimental_rerun()
