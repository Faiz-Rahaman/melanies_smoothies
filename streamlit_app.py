# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Get name on order
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Get Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit names + SEARCH_ON values
fruit_df = (
    session
        .table("smoothies.public.fruit_options")
        .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

fruit_rows = fruit_df.collect()

fruit_list = [row["FRUIT_NAME"] for row in fruit_rows]
search_lookup = {row["FRUIT_NAME"]: row["SEARCH_ON"] for row in fruit_rows}

# Multiselect
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# Submit button
time_to_insert = st.button("Submit Order")

# Process order
if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        st.subheader(f"{fruit_chosen} Nutrition Information")

        search_term = search_lookup[fruit_chosen]

        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_term}"
        )

        if smoothiefroot_response.status_code == 200:
            st.dataframe(
                data=smoothiefroot_response.json(),
                use_container_width=True
            )
        else:
            st.error(f"Nutrition data not found for {fruit_chosen}")

    if time_to_insert:
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
else:
    st.info("Please choose at least one fruit 🍓")
