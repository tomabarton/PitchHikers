import streamlit as st

from data.access.data_access import DataAccess
from utils.log import log


st.set_page_config(page_title="Clubs")

st.sidebar.header("Clubs")
st.write("""This page is for accessing club information""")


@st.cache_data
def get_clubs() -> list[str]:
    dao = DataAccess("pitch_hickers", "clubs")
    return [club.name for club in dao.get_clubs()]

def get_club_details(club_name: str) -> dict[str,int]:
    dao = DataAccess("pitch_hickers", "users")
    num_supporters = dao.read_user_records({"supporting_club": club_name})
    return {"Club name": club_name, "Number of supporters": len(num_supporters)}


with st.form("club_details"):
    club_name = st.selectbox("Club", get_clubs())

    submitted = st.form_submit_button("Submit")
    
    if submitted:
        if not club_name:
            st.error("Please select a club name.")
        else:
            data = get_club_details(club_name)
            st.bar_chart(data)
    

