import streamlit as st
from data.access.data_access import DataAccess
from data.entity.club import Club
from data.entity.user import User


@st.cache_data
def get_clubs() -> list[Club]:
    dao = DataAccess()
    return dao.get_clubs()

@st.cache_data
def get_users() -> list[User]:
    dao = DataAccess()
    return dao.get_users()