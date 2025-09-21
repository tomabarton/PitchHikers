from datetime import date
import streamlit as st
from streamlit_searchbox import st_searchbox
from data.access.data_access import DataAccess
from data.entity.journey import build_journey, CarJourney, CoachJourney, TrainJourney
from data.entity.transport import CarEmissionType, Car, Coach, Train
from data.entity.club import Club, Fixture
from data.google.places import GooglePlacesClient, Place

st.set_page_config(page_title="Journey")
st.write("# Journey Planner")
st.sidebar.header("Journey Planner")

st.logo("pages/images/PitchHikersLogo.jpg", size="large")  # TODO: sort path

# Check login
if not (st.user.get("is_logged_in", False) and DataAccess().is_existing_user(st.user.get("email", ""))):
    st.error("You need to create a PitchHikers account to plan journeys.")
    st.stop()

user_id = st.user.sub
dao = DataAccess()
clubs: list[Club] = dao.get_clubs()
current_supporting_club: Club | None = dao.get_supporting_club_for_user(user_id)
users_journeys: list[CarJourney | CoachJourney | TrainJourney] | None = dao.get_journeys_for_users(user_id)


# Utility functions
def get_supporting_club() -> Club | None:
    default_index: int | None = next((i for i, club in enumerate(clubs) if club == current_supporting_club), 0) if current_supporting_club else None
    return st.selectbox("Supporting club:", clubs, index=default_index, format_func=lambda club: club.name, key="supporting_club_select")


def select_journey(key: str) -> CarJourney | CoachJourney | TrainJourney | None:
    if not users_journeys:
        st.info("You have not submitted any journeys yet.")
        return None
    journey = st.selectbox(
        "Select the journey:",
        users_journeys,
        index=None,
        format_func=lambda journey: f"{dao.fixture_mapping[journey.fixture_id].home_club.name} vs {dao.fixture_mapping[journey.fixture_id].away_club.name}, "
                                    f"{dao.fixture_mapping[journey.fixture_id].start_time.strftime('%Y-%m-%d %H:%M')} ({journey.transport._type})",
        key=key
    )
    return journey


def get_autocomplete_predictions(search_query: str) -> list[Place]:
    if len(search_query) < 3:
        return []
    return GooglePlacesClient().get_place_predictions(search_query)


# Tabs
add_journey_tab, edit_journey_tab, delete_journey_tab = st.tabs(
    ["Submit a new journey", "Edit an existing journey", "Delete an existing journey"]
)

# Add Journey Tab
with add_journey_tab:
    st.markdown("Please submit your journey details below.")

    supporting_club = get_supporting_club()
    if supporting_club:
        fixtures = dao.get_recent_and_upcoming_fixtures(supporting_club)
        attending_fixture = st.selectbox(
            "Attending fixture:",
            fixtures,
            index=None,
            format_func=lambda fixture: f'{fixture.home_club.name} vs {fixture.away_club.name}, {fixture.start_time.strftime("%Y-%m-%d %H:%M")}',
            key="fixture_select"
        )

        if attending_fixture:
            origin = st_searchbox(get_autocomplete_predictions, "Origin of journey", "Search for address...", key="add_origin_address", debounce=200)
            destination = st_searchbox(get_autocomplete_predictions, "Destination of journey", "Search for address...", key="add_destination_address", debounce=200)
            transport_options = [Car(), Coach(), Train()]
            transport = st.selectbox("Method of transport:", transport_options, index=None, format_func=lambda option: option._type, key="add_transport_select")

            if origin and destination and transport:
                params = "mode=transit" if isinstance(transport, Train) else ""
                st.markdown(
                    f"""<iframe src="https://www.google.com/maps/embed/v1/directions?origin=place_id:{origin.id}&destination=place_id:{destination.id}&key=AIzaSyCF-RWdp-WtJki31YRQRTXctuNo1bICe4U&{params}" width="640" height="480"></iframe>""",
                    unsafe_allow_html=True
                )
                st.write(f"Powered by Google, ©{date.today().year} Google")

                distance = st.number_input("Estimate journey distance in miles:", min_value=5, max_value=500, step=5, key="add_distance")

                if distance:
                    num_passengers = 0
                    if isinstance(transport, Car):
                        num_passengers = st.number_input("Total number of passengers:", min_value=1, max_value=7, step=1, key="add_num_passengers")
                        emission_options = [CarEmissionType.ELECTRIC, CarEmissionType.HYBRID, CarEmissionType.PETROL, CarEmissionType.DIESEL]
                        transport.emission_type = st.selectbox("Car emission type:", emission_options, index=None, format_func=lambda option: str(option).split('.')[-1].title(), key="add_emission_type_select")
                        if transport.emission_type and transport.emission_type.has_engine_size():
                            transport.engine_size = st.number_input("Engine size of car:", min_value=1.0, max_value=10.0, step=0.2, format="%0.1f", key="add_engine_size")

                    if st.button("Submit journey", key="submit_journey"):
                        journey = build_journey(attending_fixture.id, origin, destination, distance, transport, num_passengers)
                        if dao.create_journey(journey, user_id, supporting_club):
                            st.success("Journey has been successfully added")
                        else:
                            st.error("There was an error adding your journey.")
            else:
                st.info("Please complete all journey details to continue.")
        else:
            st.info("Select a fixture to begin planning your journey.")
    else:
        st.info("Select a supporting club to continue.")


# Edit Journey Tab
with edit_journey_tab:
    st.markdown("Please select a journey to edit.")
    selected_journey = select_journey(key="edit_journey_select")

    if selected_journey:
        origin = st_searchbox(get_autocomplete_predictions, "Origin of journey", "Search for address...", key="edit_origin_address", debounce=200, default=selected_journey.origin, default_searchterm=selected_journey.origin.address)
        destination = st_searchbox(get_autocomplete_predictions, "Destination of journey", "Search for address...", key="edit_destination_address", debounce=200, default=selected_journey.destination, default_searchterm=selected_journey.destination.address)

        transport_options = [Car(), Coach(), Train()]
        transport_type = selected_journey.transport._type
        transport_index = next((i for i, t in enumerate(transport_options) if t._type == transport_type), None)
        transport = st.selectbox("Method of transport:", transport_options, key="edit_transport_select", index=transport_index, format_func=lambda option: option._type)

        if origin and destination and transport:
            params = "mode=transit" if isinstance(transport, Train) else ""
            st.markdown(
                f"""<iframe src="https://www.google.com/maps/embed/v1/directions?origin=place_id:{origin.id}&destination=place_id:{destination.id}&key=AIzaSyCF-RWdp-WtJki31YRQRTXctuNo1bICe4U&{params}" width="640" height="480"></iframe>""",
                unsafe_allow_html=True
            )
            st.write(f"Powered by Google, ©{date.today().year} Google")

            distance = st.number_input("Estimate journey distance in miles:", min_value=5, max_value=500, step=5, value=selected_journey.distance, key="edit_distance")

            num_passengers = selected_journey.num_passengers
            if isinstance(transport, Car):
                num_passengers = st.number_input("Total number of passengers:", key="edit_num_passengers", min_value=1, max_value=7, step=1, value=selected_journey.num_passengers)
                emission_options = [CarEmissionType.ELECTRIC, CarEmissionType.HYBRID, CarEmissionType.PETROL, CarEmissionType.DIESEL]
                emission_type = selected_journey.transport.emission_type  # TODO: Need to fix this
                emission_index = next((i for i, t in enumerate(emission_options) if t.name == emission_type), None)
                transport.emission_type = st.selectbox("Car emission type:", emission_options, key="edit_emission_type_select", index=emission_index, format_func=lambda option: str(option).split('.')[-1].title())
                
                if transport.emission_type:
                    if transport.emission_type.has_engine_size():
                        engine_size_value = float(selected_journey.transport.engine_size) if selected_journey.transport.engine_size is not None else 1.0
                        transport.engine_size = st.number_input("Engine size of car:", key="edit_engine_size", min_value=1.0, max_value=10.0, step=0.2, format="%0.1f", value=engine_size_value)

            if st.button("Update journey", key="update_journey"):
                journey = build_journey(selected_journey.fixture_id, origin, destination, distance, transport, num_passengers)
                journey.id = selected_journey.id
                if dao.update_journey(journey):
                    st.success("Journey has been successfully updated.")
                else:
                    st.error("There was an error updating your journey.")
        else:
            st.info("Please complete all journey details to continue.")


# Delete Journey Tab
with delete_journey_tab:
    st.markdown("Please select a journey to delete.")
    selected_journey = select_journey(key="delete_journey_select")

    if selected_journey:
        confirmed = st.checkbox("I confirm I want to delete this journey", key="delete_confirm")
        if st.button("Delete journey", key="delete_journey"):
            if confirmed:
                if dao.delete_journey_for_user(selected_journey, user_id):
                    st.success("Journey has been successfully deleted.")
                else:
                    st.error("There was an error deleting your journey.")
            else:
                st.warning("Please confirm before deleting.")
    else:
        st.info("Select a journey to delete.")
