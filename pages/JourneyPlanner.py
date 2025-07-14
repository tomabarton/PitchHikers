from datetime import date
import streamlit as st

from data.access.data_access import DataAccess
from data.entity.journey import EmissionType

from utils.log import log

st.set_page_config(page_title="Journey Planner")

st.sidebar.header("Journey Planner")
st.write("""This page is for planning journeys""")

def get_place_id(
        location: str  # TODO: Some validation
    ) -> bool:
    return True

with st.form("journey_planner"):
    origin = st.text_input("Origin")
    destination = st.text_input("Destination")
    travel_mode = st.selectbox("Travel mode", ["DRIVE"])
    if travel_mode == "DRIVE":
        emission_type = st.selectbox("Emission type", 
                                     [EmissionType.DIESEL, 
                                      EmissionType.GASOLINE, 
                                      EmissionType.ELECTRIC, 
                                      EmissionType.HYBRID])
        num_passengers = st.number_input("Number of passengers", min_value=1, max_value=6, step=1)
    submitted = st.form_submit_button("Submit")
    if submitted:
        if not (origin and destination and travel_mode):
            st.error("Please fill in the journey planner fields.")
        else:
            page = True  # get_place_id(origin, destination, travel_mode)
            if page:
                st.markdown("""<iframe src="https://www.google.com/maps/embed/v1/directions?origin=place_id:ChIJ4VrZFmIhe0gRWXOEyaeteDc&destination=place_id:ChIJPW-XS4YPdkgR-GWlHng4qkg&key=AIzaSyCF-RWdp-WtJki31YRQRTXctuNo1bICe4U" width="640" height="480"></iframe>""",
                            unsafe_allow_html=True)  
                st.write(f"Powered by Google, ©{date.today().year} Google")          
            else:
                st.error("There was an error generating journey plan")

