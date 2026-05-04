import streamlit as st
import snowflake.connector
from snowflake.snowpark.functions import col
import requests

st.title("Customize Your Smoothie! 🥤")

# 👉 CONNECT TO SNOWFLAKE
conn = snowflake.connector.connect(**st.secrets["snowflake"])
session = conn.cursor()

# 👉 NAME INPUT
name_on_order = st.text_input("Name for your smoothie order")

# 👉 LOAD FRUIT OPTIONS
session.execute("SELECT FRUIT_NAME FROM smoothies.public.fruit_options")
fruit_list = [row[0] for row in session.fetchall()]

# 👉 MULTISELECT
ingredients = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# 👉 SHOW SELECTED INGREDIENTS
if ingredients:
    st.write("Your selected ingredients:")
    st.write(ingredients)

    # 👉 API CALL (dynamic based on first selected fruit)
    fruit = ingredients[0].lower()

    try:
        response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit}")
        data = response.json()

        st.subheader(f"Nutrition Info for {ingredients[0]}")
        st.dataframe(data, use_container_width=True)

    except Exception as e:
        st.warning("Could not fetch nutrition data")

# 👉 SUBMIT BUTTON
submit = st.button("Submit Order")

if submit:
    if not name_on_order:
        st.warning("Please enter a name")
    elif not ingredients:
        st.warning("Please select at least one ingredient")
    else:
        # 👉 BUILD STRING
        ingredients_string = ''

        for fruit_chosen in ingredients:
            ingredients_string = ingredients_string + fruit_chosen + ' '

        # 👉 SQL INSERT
        my_insert_stmt = """ 
        insert into smoothies.public.orders(name_on_order, ingredients)
        values ('""" + name_on_order + """', '""" + ingredients_string + """')
        """

        # 👉 DEBUG (optional)
        st.write(my_insert_stmt)

        # 👉 EXECUTE
        session.execute(my_insert_stmt)

        st.success(f"Your Smoothie is ordered, {name_on_order}! 🎉")
