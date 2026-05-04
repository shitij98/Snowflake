import streamlit as st
import snowflake.connector
import pandas as pd

st.title("Pending Smoothie Orders 🧾")

# 👉 CONNECT
conn = snowflake.connector.connect(**st.secrets["snowflake"])

# 👉 LOAD ONLY UNFILLED ORDERS
query = """
SELECT ORDER_ID, INGREDIENTS, NAME_ON_ORDER, ORDER_FILLED
FROM smoothies.public.orders
WHERE ORDER_FILLED = FALSE
"""
df = pd.read_sql(query, conn)

if df.empty:
    st.success("All orders are filled 🎉")
else:
    st.write("Mark orders as filled:")

    # 👉 Editable table
    edited_df = st.data_editor(df, use_container_width=True)

    # 👉 Submit button
    if st.button("Update Orders"):
        try:
            cursor = conn.cursor()

            for _, row in edited_df.iterrows():
                cursor.execute(
                    """
                    UPDATE smoothies.public.orders
                    SET ORDER_FILLED = %s
                    WHERE ORDER_ID = %s
                    """,
                    (row["ORDER_FILLED"], row["ORDER_ID"])
                )

            st.success("Orders updated successfully ✅")

        except Exception as e:
            st.error("Update failed ❌")
