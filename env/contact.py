import streamlit as st

# Inject dashboard.css for consistent styling
with open("static/dashboard.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("Contact Us")

with st.form("contact_form"):
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    question = st.text_area("Your Question")
    submitted = st.form_submit_button("Send")

if submitted:
    st.success("Thank you for reaching out! We will get in touch with you as soon as we can.")
else:
    st.write("Please fill out the form and click Send.")