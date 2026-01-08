import streamlit as st
from snowflake.snowpark.functions import col
import requests

# --------------------------------------------------
# App Title
# --------------------------------------------------
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# --------------------------------------------------
# Name on Order
# --------------------------------------------------
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# --------------------------------------------------
# Snowflake Session
# --------------------------------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# --------------------------------------------------
# Get FRUIT_NAME + SEARCH_ON from Snowflake
# --------------------------------------------------
fruit_df = (
    session
        .table("smoothies.public.fruit_options")
        .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

fruit_rows = fruit_df.collect()

# UI list (what user sees)
fruit_list = [row["FRUIT_NAME"] for row in fruit_rows]

# Lookup dictionary (what API uses)
search_lookup = {
    row["FRUIT_NAME"]: row["SEARCH_ON"]
    for row in fruit_rows
}

# --------------------------------------------------
# Multiselect
# --------------------------------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# --------------------------------------------------
# Submit Button
# --------------------------------------------------
submit_order = st.button("Submit Order")

# --------------------------------------------------
# Process Order
# --------------------------------------------------
if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        st.subheader(fruit_chosen + " Nutrition Information")

        # Use SEARCH_ON value for API call
        search_term = search_lookup[fruit_chosen]

        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_term.lower()}"
        )

        st.dataframe(
            smoothiefroot_response.json(),
            use_container_width=True
        )

    # --------------------------------------------------
    # Insert only when Submit button is clicked
    # --------------------------------------------------
    if submit_order:
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """
        session.sql(my_insert_stmt).collect()

        st.success(
            f"Your Smoothie is ordered, {name_on_order}!",
            icon="✅"
        )
