import streamlit as st

from data.access.data_access import DataAccess
from data.entity.user import User
from data.google.people import GooglePeopleClient


st.set_page_config(page_title="Pitcher Hikers")
st.write("# Welcome to Pitch Hikers")

st.sidebar.header("Login to Pitch Hikers")


st.logo("pages/images/PitchHikersLogo.jpg", size="large")  # TODO: sort path

def is_existing_user() -> User | None:  # Singleton to stop re-creating
    return DataAccess().is_existing_user(email)


def create_user():
    date_of_birth, id = GooglePeopleClient().get_user_details(), st.user.sub
    user = User(id, fname, lname, date_of_birth, email)
    DataAccess().create_user(user)

    return id, date_of_birth

if not st.user.get("is_logged_in", False):
    st.sidebar.button("Login with Google", on_click=st.login)
    st.stop()

else:
    st.sidebar.button("Logout", on_click=st.logout)

fname = st.user.given_name  # Google user info
lname = st.user.family_name
email = st.user.email

def delete_user_and_logout():
    if DataAccess().delete_user(st.user.sub):
        st.success("Your PitchHikers account has been deleted.")
        st.logout()
    else:
        st.error("There was an error deleting your PitchHikers account. Please try again later.")

user = is_existing_user()
if not user:
    st.markdown("A PitchHikers account associated with your Google login could not be detected - please create an account to continue.")
    st.button("Create PitchHikers account", on_click=create_user)
    st.stop()
else:
    st.sidebar.button("Delete account", on_click=delete_user_and_logout)



if user:
    st.session_state['user'] = user
    st.markdown(f"Welcome to PitchHikers {fname}!")






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
