import streamlit as st
from datetime import date

from data.access.data_access import DataAccess
from data.entity.user import User
from data.entity.club import Club
from utils.log import log
from pages.st_utils.st_utils import get_clubs


st.set_page_config(page_title="User Registration")

st.sidebar.header("User Registration")
st.write("""This page is for registering user details""")



def submit_user(
        fname: str, 
        lname: str, 
        date_of_birth: date, 
        email: str, 
        supporting_club: Club|None,
    ) -> bool:
    user = User(fname, lname, date_of_birth, email)
    dao = DataAccess()  # TODO: Add relevant details
    return dao.create_user(user, supporting_club)

#if not st.user.get("is_logged_in", False):
#    st.warning("You must be logged in to register as a user.")
#    st.stop()

with st.form("user_registration_form"):
    fname = str(st.text_input("First Name")).strip()
    lname = str(st.text_input("Last Name")).strip()
    date_of_birth = st.date_input("Date of birth", format="YYYY/MM/DD")
    email = str(st.text_input("Email", value=st.user.get("email", ""))).strip()
    supporting_club = st.selectbox("Supporting Club", get_clubs())
    
    submitted = st.form_submit_button("Submit")
    
    if submitted:
        log.info(f"User registration submitted: {fname} {lname}, Date of birth: {date_of_birth}, Email: {email}, Club: {supporting_club}")
        if not (fname and lname and date_of_birth and email):
            st.error("Please fill in all fields.")
        else:
            if submit_user(fname, lname, date_of_birth, email, supporting_club):
                st.success(f"Thank you {fname} {lname} for registering!")
            else:
                st.error("There was an error registering your details")
