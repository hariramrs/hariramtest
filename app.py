import streamlit as st
import requests
import datetime

st.set_page_config(page_title="DTDC Booking", layout="centered")
st.title("📦 DTDC Booking Form")

# ---------------------------
# CONFIG
# ---------------------------
GET_CN_URL = "YOUR_GOOGLE_SCRIPT_GET_URL"
REMOVE_CN_URL = "YOUR_GOOGLE_SCRIPT_POST_URL"
SAVE_DATA_URL = "YOUR_EXISTING_GOOGLE_SCRIPT_URL"
PRINT_API_URL = "https://print.yourdomain.com/print"  # optional

# ---------------------------
# GET CN FROM GOOGLE SHEET
# ---------------------------
def get_cn(customer):
    try:
        res = requests.get(f"{GET_CN_URL}?customer={customer}")
        if res.text == "NONE":
            return None
        return res.text.strip()
    except:
        return None

# ---------------------------
# REMOVE USED CN
# ---------------------------
def remove_cn(customer):
    try:
        requests.post(REMOVE_CN_URL, json={"customer": customer})
    except:
        pass

# ---------------------------
# UI
# ---------------------------
customer = st.selectbox("Customer", ["-- Select --", "CUS1", "CUS2", "CUS3"])

if customer == "-- Select --":
    st.stop()

# ---------------------------
# GET CN PREVIEW
# ---------------------------
cn_preview = get_cn(customer)

if not cn_preview:
    st.error("No Consignment Number Available")
    st.stop()

st.success(f"Next CN: {cn_preview}")

# ---------------------------
# INPUTS
# ---------------------------
sender_phone = st.text_input("Sender Phone")
receiver_phone = st.text_input("Receiver Phone")
pincode = st.text_input("Pincode")
remarks = st.text_input("Remarks")
content = st.text_input("Content")

risk = st.selectbox("Risk", ["Owner Risk", "Carrier Risk", "No Risk"])
payment = st.selectbox("Payment", ["Cash", "Credit", "To Pay"])

photo = st.file_uploader("Upload Photo (optional)")

print_required = st.checkbox("🖨️ Print")

# ---------------------------
# SUBMIT
# ---------------------------
if st.button("Submit"):

    if not sender_phone.isdigit() or not receiver_phone.isdigit():
        st.error("Phone number invalid")
        st.stop()

    cn = cn_preview
    now = str(datetime.datetime.now())

    # ---------------------------
    # SAVE MAIN DATA (YOUR EXISTING SCRIPT)
    # ---------------------------
    try:
        requests.post(SAVE_DATA_URL, json={
            "time": now,
            "cn": cn,
            "customer": customer,
            "sender_phone": sender_phone,
            "receiver_phone": receiver_phone,
            "pincode": pincode,
            "remarks": remarks,
            "content": content,
            "risk": risk,
            "payment": payment,
            "print": print_required
        })
    except:
        st.warning("Data save failed")

    # ---------------------------
    # REMOVE USED CN
    # ---------------------------
    remove_cn(customer)

    # ---------------------------
    # PRINT CALL (PC ON irundha)
    # ---------------------------
    if print_required:
        try:
            requests.post(PRINT_API_URL, json={"cn": cn}, timeout=2)
        except:
            pass

    st.success(f"Booking Done ✅ CN: {cn}")