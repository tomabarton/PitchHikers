import streamlit as st

from data.access.data_access import DataAccess
from utils.log import log


st.set_page_config(page_title="Registration Plate")

st.sidebar.header("Registration Plate")
st.write("""This page is for querying registration plates""")

def submit_reg(
        reg_plate: str
    ) -> dict[str,str]:
    pass

with st.form("registration_plate_form"):
    reg_plate = st.text_input("Registration plate")
    submitted = st.form_submit_button("Submit")
    
    if submitted:
        if not reg_plate:
            st.error("Please fill in registration plate field.")
        else:
            # TODO: Some regex assertion
            if submit_reg(reg_plate):
                pass
            else:
                st.error("There was an error submitting the registration plate")

