import streamlit as st
from data.access.data_access import DataAccess
from data.entity.club import Club
from data.entity.transport import CarEmissionType, Car, Coach, Train

st.set_page_config(page_title="Transports")
st.write("# Pit stop")
st.sidebar.header("Pit stop")

st.logo("pages/images/PitchHikersLogo.jpg", size="large")  # TODO: sort path

if not (st.user.get("is_logged_in", False) and DataAccess().is_existing_user(st.user.get("email", ""))):
    st.error("You need to create a PitchHikers account to access the Pit stop.")
    st.stop()

dao = DataAccess()
transports: list[Car | Coach | Train ] = dao.get_clubs()
current_supporting_club: Club | None = dao.get_supporting_club_for_user(st.user.sub)

if current_supporting_club:
    st.markdown(f"Your current supporting club is: {current_supporting_club.name}, selecting a new club will update this.")
else:
    st.markdown("You currently do not have a supporting club, please select one below.")

supporting_club: Club | None = st.selectbox("Please select your club:", clubs, index=None, format_func=lambda club: club.name)

submitted = st.button("Submit club")
if submitted:
    if dao.add_supporting_club_for_user(st.user.sub, supporting_club):
        st.success(f"Your supporting club has been updated to {supporting_club.name}.")
    else:
        st.error("There was an error updating your supporting club. Please try again later.")