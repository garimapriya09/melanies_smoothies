# Import python packages
import streamlit as st

# from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

import snowflake.connector

st.title("Snowflake MFA Connection")

mfa_code = st.text_input(
    "Enter your current 6-digit MFA code",
    type="password",
    max_chars=6,
)

if st.button("Connect to Snowflake"):
    if not mfa_code.isdigit() or len(mfa_code) != 6:
        st.error("Enter a valid 6-digit MFA code.")
    else:
        try:
            cfg = st.secrets["connections"]["snowflake"]

            from snowflake.snowpark import Session

            session = Session.builder.configs({
                "account": cfg["account"],
                "user": cfg["user"],
                "password": cfg["password"],
                "passcode": mfa_code,
                "authenticator": "username_password_mfa",
                "warehouse": cfg["warehouse"],
                "database": cfg["database"],
                "schema": cfg["schema"],
                "role": cfg["role"],
            }).create()

            st.session_state["snowpark_session"] = session
            st.success("Connected to Snowflake!")

        except Exception as e:
            st.error(f"Connection failed: {e}")


# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom Smoothie!"""
)

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be: ", name_on_order)

# cnx = st.connection("snowflake")
# session = cnx.session()
# session = get_active_session()

session = st.session_state.get("snowpark_session")

if session is None:
    st.info("Please connect to Snowflake first.")
    st.stop()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
# st.dataframe(data=my_dataframe, use_container_width=True)


ingredients_list = st.multiselect(
    "Choose upto 5 ingredients:",
    my_dataframe,
    max_selections = 5
)

if ingredients_list:
    # st.write(ingredients_list)
    # st.text(ingredients_list)
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    # st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                    values ('""" + ingredients_string + """', '""" + name_on_order + """')"""
    # st.write(my_insert_stmt)
    
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")

# New section to display Smoothiefroot nutrition information
import requests  
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")  
# st.text(smoothiefroot_response).json()
sf_df = st.dataframe(data=smoothiefroot_response).json(), use_container_width=True)

