```python
import streamlit as st
import snowflake.connector
import requests

st.title("Customize Your Smoothie! 🥤")

# 👉 CONNECT (using secrets)
conn = snowflake.connector.connect(**st.secrets["snowflake"])
session = conn.cursor()

# 👉 GET FRUIT MAP (IMPORTANT CHANGE)
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

# 👉 SHOW DATA PER FRUIT (FIXED + PROPER INDENTATION)
if ingredients:

    for fruit_chosen in ingredients:

        search_value = fruit_map.get(fruit_chosen)

        if search_value:
            try:
                response = requests.get(
                    f"https://my.smoothiefroot.com/api/fruit/{search_value}"
                )

                st.subheader(f"{fruit_chosen} Nutrition Information")

                st.dataframe(
                    response.json(),
                    use_container_width=True
                )

            except:
                st.warning(f"Error fetching data for {fruit_chosen}")
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

        ingredients_string = ' '.join(ingredients)

        my_insert_stmt = f"""
        insert into smoothies.public.orders(name_on_order, ingredients)
        values ('{name_on_order}', '{ingredients_string}')
        """

        session.execute(my_insert_stmt)

        st.success(f"Your Smoothie is ordered, {name_on_order}! 🎉")
```
