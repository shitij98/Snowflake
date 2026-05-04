import streamlit as st
import snowflake.connector
from snowflake.snowpark.functions import col

st.title("Customize Your Smoothie! 🥤")

conn = snowflake.connector.connect(
    user="shitij.gupta@wolterskluwer.com",
    password="Lalaji@11235813",
    account="SYS_ADMIN",
    warehouse="COMPUTE_WH",
    database="SMOOTHIES",
    schema="PUBLIC"
)

session = conn.cursor()

# 👉 NAME INPUT
name_on_order = st.text_input("Name for your smoothie order")

# 👉 DATA
session.execute("SELECT FRUIT_NAME FROM smoothies.public.fruit_options")
fruit_list = [row[0] for row in session.fetchall()]

ingredients = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)
# 👉 BUTTON
submit = st.button("Submit Order")
if submit and ingredients and name_on_order:

    ingredients_string = ''

    for fruit_chosen in ingredients:
        ingredients_string = ingredients_string + fruit_chosen + ' '

    my_insert_stmt = """ 
    insert into smoothies.public.orders(name_on_order, ingredients)
    values ('""" + name_on_order + """', '""" + ingredients_string + """')
    """

    st.write(my_insert_stmt)  # debug

    session.execute(my_insert_stmt)

    st.success("Your Smoothie is ordered, " + name_on_order + "! 🎉")
