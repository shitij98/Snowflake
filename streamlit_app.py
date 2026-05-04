import streamlit as st
import snowflake.connector
from snowflake.snowpark.functions import col
import requests

st.title("Customize Your Smoothie! 🥤")

# 👉 CONNECT
conn = snowflake.connector.connect(**st.secrets["snowflake"])
session = conn.cursor()

# 👉 INPUT
name_on_order = st.text_input("Name for your smoothie order")

# 👉 GET FRUITS
session.execute("SELECT FRUIT_NAME FROM smoothies.public.fruit_options")
fruit_list = [row[0] for row in session.fetchall()]

ingredients = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# 👉 SHOW DATA PER FRUIT (THIS IS THE FIXED PART)
if ingredients:

    st.subheader("Nutrition Information")

    for fruit_chosen in ingredients:
        fruit = fruit_chosen.lower()

        try:
            smoothiefroot_response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{fruit}"
            )

            st.write(f"🍓 {fruit_chosen}")

            st.dataframe(
                data=smoothiefroot_response.json(),
                use_container_width=True
            )

        except:
            st.warning(f"Could not fetch data for {fruit_chosen}")

# 👉 SUBMIT
submit = st.button("Submit Order")

if submit:
    if not name_on_order:
        st.warning("Please enter a name")
    elif not ingredients:
        st.warning("Please select at least one ingredient")
    else:

        ingredients_string = ''

        for fruit_chosen in ingredients:
            ingredients_string = ingredients_string + fruit_chosen + ' '

        my_insert_stmt = """ 
        insert into smoothies.public.orders(name_on_order, ingredients)
        values ('""" + name_on_order + """', '""" + ingredients_string + """')
        """

        session.execute(my_insert_stmt)

        st.success(f"Your Smoothie is ordered, {name_on_order}! 🎉")
