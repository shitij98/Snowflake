```python
import streamlit as st
import snowflake.connector
import requests

st.title("Customize Your Smoothie! 🥤")

# 👉 CONNECT (using secrets)
conn = snowflake.connector.connect(**st.secrets["snowflake"])
session = conn.cursor()

# 👉 GET FRUIT MAP
session.execute("SELECT FRUIT_NAME, SEARCH_ON FROM smoothies.public.fruit_options")
rows = session.fetchall()

fruit_map = {row[0]: row[1] for row in rows}
fruit_list = list(fruit_map.keys())

# 👉 INPUT
name_on_order = st.text_input("Name for your smoothie order")

ingredients = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# 👉 SHOW DATA PER FRUIT
if ingredients:
    for fruit_chosen in ingredients:

        search_value = fruit_map.get(fruit_chosen)

        if search_value:
            try:
                response = requests.get(
                    f"https://my.smoothiefroot.com/api/fruit/{search_value}",
                    timeout=5
                )

                if response.status_code == 200:
                    st.subheader(f"{fruit_chosen} Nutrition Information")
                    st.dataframe(response.json(), use_container_width=True)
                else:
                    st.warning(f"No data found for {fruit_chosen}")

            except requests.exceptions.RequestException:
                st.error(f"API error for {fruit_chosen}")
        else:
            st.warning(f"No API mapping found for {fruit_chosen}")

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

            # ✅ SAFE SQL (no injection)
            insert_query = """
                INSERT INTO smoothies.public.orders(name_on_order, ingredients)
                VALUES (%s, %s)
            """

            session.execute(insert_query, (name_on_order, ingredients_string))

            st.success(f"Your Smoothie is ordered, {name_on_order}! 🎉")

        except Exception as e:
            st.error("Failed to place order. Check logs.")
```
