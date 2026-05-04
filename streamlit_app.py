import streamlit as st
import snowflake.connector
import requests
import pandas as pd

st.title("Customize Your Smoothie! 🥤")

# 👉 CONNECT
conn = snowflake.connector.connect(**st.secrets["snowflake"])
session = conn.cursor()

# 👉 LOAD DATA (Snowflake → Pandas)
query = "SELECT FRUIT_NAME, SEARCH_ON FROM smoothies.public.fruit_options"
pd_df = pd.read_sql(query, conn)

fruit_list = pd_df["FRUIT_NAME"].tolist()

# 👉 INPUT
name_on_order = st.text_input("Name for your smoothie order")

ingredients = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# 👉 SHOW DATA PER FRUIT (USING .loc)
if ingredients:
    for fruit_chosen in ingredients:
        try:
            # 🔥 GET SEARCH VALUE
            search_value = pd_df.loc[
                pd_df["FRUIT_NAME"] == fruit_chosen,
                "SEARCH_ON"
            ].iloc[0]

            # (optional debug - you can remove later)
            st.write(f"Search value for {fruit_chosen}: {search_value}")

            # 👉 API CALL
            response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{search_value}",
                timeout=5
            )

            # 👉 HANDLE RESPONSE
            if response.status_code == 200 and response.json():
                st.subheader(f"{fruit_chosen} Nutrition Information")
                st.dataframe(response.json(), use_container_width=True)
            else:
                st.info(f"{fruit_chosen} data not available in SmoothieFroot API")

        except IndexError:
            st.warning(f"No SEARCH_ON mapping for {fruit_chosen}")

        except requests.exceptions.RequestException:
            st.error(f"API error for {fruit_chosen}")

# 👉 SUBMIT
submit = st.button("Submit Order")

if submit:
    if not name_on_order:
        st.warning("Please enter a name")
    elif not ingredients:
        st.warning("Please select at least one ingredient")
    else:
        try:
            ingredients_string = ' '.join(ingredients)

            insert_query = """
                INSERT INTO smoothies.public.orders(name_on_order, ingredients)
                VALUES (%s, %s)
            """

            session.execute(insert_query, (name_on_order, ingredients_string))

            st.success(f"Your Smoothie is ordered, {name_on_order}! 🎉")

        except Exception:
            st.error("Failed to place order.")
