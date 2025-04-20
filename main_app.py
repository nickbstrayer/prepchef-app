import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

# Theme toggle
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "light"
theme = st.sidebar.selectbox("🌗 Theme Mode", ["light", "dark"])
st.session_state["theme_mode"] = theme

# Title and branding
st.set_page_config(page_title="PrepChef Meal Planner", layout="wide")
st.markdown("""
    <div style='text-align: center; padding: 1rem;'>
        <h1 style='margin-bottom: 0;'>👨‍🍳 PrepChef</h1>
        <p style='font-size: 1.1rem; color: gray;'>Your life. Your plate. Planned.</p>
    </div>
""", unsafe_allow_html=True)

# Navigation
menu = st.sidebar.radio("Navigate", ["Login", "Meal Plan", "Shopping List", "Order & Delivery"])

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_type = ""

# Login
if menu == "Login" and not st.session_state.logged_in:
    st.subheader("Login")
    user_type = st.radio("Select User Type", ["user", "admin"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.session_state.user_type = user_type
        elif username == "user" and password == "user123":
            st.session_state.logged_in = True
            st.session_state.user_type = user_type
        else:
            st.error("Invalid credentials")

# Simulated AI fetch (replace with real API integration)
def fetch_recipe_stub():
    return {
        "title": "Chicken Tinga Tacos",
        "image": "https://www.themealdb.com/images/media/meals/wvpsxx1468256321.jpg",
        "instructions": "Cook chicken, mix with tinga sauce, serve in tortillas.",
        "ingredients": ["chicken", "onion", "garlic", "tomato", "chipotle"]
    }

if st.session_state.logged_in:
    st.sidebar.success(f"Logged in as {st.session_state.user_type}")

    if menu == "Meal Plan":
        st.subheader("🗓️ Create Your Meal Plan")
        date = st.date_input("Select date", value=datetime.today())
        meals_per_day = st.radio("Meals per day", ["One meal", "Three meals"])
        restrictions = st.multiselect("Dietary restrictions", ["Dairy-Free", "Gluten-Free"])
        cuisines = st.multiselect("Cuisine preferences", ["Mexican", "Italian", "Thai"])
        taste = st.radio("Taste profile", ["Spicy", "Mild", "Neutral"])

        if st.button("Generate Meal Plan"):
            meal = fetch_recipe_stub()
            st.image(meal["image"], width=400)
            st.markdown(f"### {meal['title']}")
            st.write("**Ingredients:**")
            st.write(meal["ingredients"])
            st.write("**Instructions:**")
            st.write(meal["instructions"])

    elif menu == "Shopping List":
        st.subheader("🛒 Shopping List")
        ingredients = ["chicken", "onion", "garlic", "tomato"]
        df = pd.DataFrame(ingredients, columns=["Items"])
        st.dataframe(df)
        st.download_button("Download CSV", df.to_csv(index=False), "shopping_list.csv")

    elif menu == "Order & Delivery":
        st.subheader("📦 Delivery Options")
        zip_code = st.text_input("ZIP Code")
        address = st.text_input("Address")
        store = st.selectbox("Preferred Store", ["Walmart", "Instacart"])
        if st.button("Find Store"):
            st.success(f"Found {store} near {zip_code} (simulated)")
            st.markdown(f"[Open {store}](https://{store.lower()}.com)")

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center;font-size:12px;color:gray;'>This app is for informational and planning purposes only. Creator: <b>Nick Budhai</b> | &copy; 2025 | <a href='#'>Terms of Use</a> | <a href='#'>Privacy Policy</a></p>", unsafe_allow_html=True)
