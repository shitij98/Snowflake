import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

st.title("Customize Your Smoothie! 🥤")

session = get_active_session()

# 👉 NAME INPUT
name_on_order = st.text_input("Name for your smoothie order")

# 👉 DATA
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
fruit_list = [row["FRUIT_NAME"] for row in my_dataframe.collect()]

ingredients = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5   # 🔥 THIS LINE
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

    session.sql(my_insert_stmt).collect()

    st.success("Your Smoothie is ordered, " + name_on_order + "! 🎉")
