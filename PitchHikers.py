from datetime import date
import streamlit as st
import pandas as pd
import numpy as np
from data.access.data_access import DataAccess
from data.entity.club import Club
from data.entity.user import User



st.set_page_config(page_title="Pitcher Hikers")
st.write("# Welcome to Pitch Hickers")

st.logo("pages/images/PitchHikersLogo.jpg", size="large")  # TODO: sort path

st.sidebar.success("Login page")

global dao 
dao = DataAccess()

def is_existing_user():  # Singleton to stop re-creating
    return dao.is_existing_user(st.user.email)

def submit_user(
        fname: str, 
        lname: str, 
        date_of_birth: date, 
        email: str, 
        supporting_club: Club|None,
    ) -> bool:
    user = User(None, fname, lname, date_of_birth, email)
    dao = DataAccess()  # TODO: Add relevant details
    return dao.create_user(user, supporting_club)

def get_extra_user_info() -> tuple[date,Club|None]:
    date_of_birth: date = st.date_input("Date of birth", format="YYYY/MM/DD", max_value="today", min_value="1900-01-01")
    supporting_club: Club | None = st.selectbox("Supporting Club", dao.clubs_cache)
    if not date_of_birth:
        st.error("Please fill in all fields.")
    else: 
        return date_of_birth, supporting_club

if not st.user.get("is_logged_in", False):
    st.button("Login with Google", on_click=st.login)
    st.stop()

if not is_existing_user():
    st.write("Thank you for logging in! Please fill in your details below to register as a new user.")
    with st.form("user_registration_form"):
        date_of_birth, supporting_club = get_extra_user_info()
    
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            if not (date_of_birth):
                st.error("Please fill in all fields.")
            else:
                fname = st.user["given_name"]  # Google user info
                lname = st.user["family_name"]
                email = st.user["email"]
                if submit_user(fname, lname, date_of_birth, email, supporting_club):
                    st.success(f"Thank you {fname} {lname} for registering!")
                else:
                    st.error("There was an error registering your details")

st.markdown(f"Welcome! {st.user.name}")

st.button("Log Out", on_click=st.logout)






# @st.cache_data
# def load_data():
#     dao = DataAccess()
#     return dao.get_club_supporter_num()

# def get_num_supporters():
#     data = load_data()
#     num_supporters = Counter()
#     for datum in data:
#         num_supporters[datum['supporting_club']] += 1
#     return num_supporters

# data_load_state = st.text('Loading data...')
# #data = get_num_supporters()
# st.bar_chart(load_data())
# data_load_state.text("Done! (using st.cache_data)")

# if st.checkbox('Show raw data'):
#     st.subheader('Raw data')
#     #st.write(data)
