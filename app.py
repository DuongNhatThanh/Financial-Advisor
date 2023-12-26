import streamlit as st
from streamlit_option_menu import option_menu
from screens.index import get_routes
import streamlit_authenticator as stauth

st.set_page_config(
    layout="wide",
)

import yaml
from yaml.loader import SafeLoader

with open('config2.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)


authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)



authenticator.login('Login', 'main')
    
if st.session_state["authentication_status"] is not True:
    tab2, tab3, tab4 = st.tabs(["Register", "Forgot password", "Forgot username"])

    with tab2:
        try:
            if authenticator.register_user('Register user', preauthorization=False):
                st.success('User registered successfully')
                with open('config2.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
        except Exception as e:
            st.error(e)
    with tab3:
        try:
            username_of_forgotten_password, email_of_forgotten_password, new_random_password = authenticator.forgot_password('Forgot password')
            if username_of_forgotten_password:
                st.info(f'Your new password: {new_random_password}')
                # Random password should be transferred to user securely
                with open('config2.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
            else:
                st.error('Username not found')
        except Exception as e:
            st.error(e)
    with tab4:
        try:
            username_of_forgotten_username, email_of_forgotten_username = authenticator.forgot_username('Forgot username')
            if username_of_forgotten_username:
                st.info(f'Your new username: {username_of_forgotten_username}')
                # Username should be transferred to user securely
                with open('config2.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
            else:
                st.error('Email not found')
        except Exception as e:
            st.error(e)



if st.session_state["authentication_status"]:
    st.header('Analytics Reports')
    authenticator.logout('Logout', 'sidebar', key='unique_key')
    st.sidebar.write(f'Welcome *{st.session_state["name"]}*')
    if st.sidebar.button("Change password"):
        try:
            if authenticator.reset_password(st.session_state["username"], 'Reset password'):
                st.success('Password modified successfully')
                with open('config2.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
        except Exception as e:
            st.error(e)

    if st.sidebar.button("Update user details"):
        if st.session_state["authentication_status"]:
            try:
                if authenticator.update_user_details(st.session_state["username"], 'Update user details'):
                    st.success('Entries updated successfully')
            except Exception as e:
                st.error(e)


    routes = get_routes()

    with st.sidebar:
        global selected_screen
        
        selected_screen = option_menu("Taskbar", routes['name'], 
            icons=routes['icon'], menu_icon="book")
        
        # selected_screen = on_hover_tabs(tabName=routes['name'], 
        #                      iconName=routes['icon'], default_choice=0)
    
    routes['component'][selected_screen]()


elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')


hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

