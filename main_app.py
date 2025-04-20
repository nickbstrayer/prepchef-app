import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="PrepChef Meal Planner", layout="wide")

# Spoonacular API key
API_KEY = "ZXLohb41LpxjixMvNwgd6xP0hDIYPiLR"

# Theme toggle
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "light"
theme = st.sidebar.selectbox("🌗 Theme Mode", ["light", "dark"])
st.session_state["theme_mode"] = theme

# Header
st.markdown("""
    <div style='text-align: center; padding: 1rem;'>
        <h1 style='margin-bottom: 0;'>👨‍🍳 PrepChef</h1>
        <p style='font-size: 1.1rem; color: gray;'>Your life. Your plate. Planned.</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar nav
menu = st.sidebar.radio("Navigate", ["Login", "Meal Plan", "Shopping List", "Order & Delivery"])

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_type = ""

# Login section
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

# Spoonacular fetch function with fallback
@st.cache_data(ttl=3600)
def fetch_recipe(cuisine, diet, intolerances):
    base_url = "https://api.spoonacular.com/recipes/complexSearch"
    def query(c, d, i):
        params = {
            "apiKey": API_KEY,
            "number": 1,
            "addRecipeInformation": True,
            "cuisine": c,
            "diet": d,
            "intolerances": i
        }
        res = requests.get(base_url, params=params)
        if res.status_code == 200:
            data = res.json()
            return data.get("results", [])[0] if data.get("results") else None
        return None

    # Try full query
    recipe = query(cuisine, diet, intolerances)
    if recipe: return recipe

    # Try removing cuisine
    recipe = query("", diet, intolerances)
    if recipe: return recipe

    # Try removing intolerances
    recipe = query("", diet, "")
    if recipe: return recipe

    # Return static fallback
    return {
        "title": "Simple Pasta",
        "image": "https://www.themealdb.com/images/media/meals/ustsqw1468250014.jpg",
        "instructions": "Boil pasta, add sauce, serve.",
        "extendedIngredients": [
            {"name": "pasta"}, {"name": "tomato sauce"}, {"name": "olive oil"}
        ]
    }

# Logged-in sections
if st.session_state.logged_in:
    st.sidebar.success(f"Logged in as {st.session_state.user_type}")

    if menu == "Meal Plan":
        st.subheader("🗓️ Create Your Meal Plan")
        day = st.date_input("Select date", value=datetime.today())
        meals_per_day = st.radio("Meals per day", ["One meal", "Three meals"])
        diet = st.selectbox("Diet", ["", "vegan", "vegetarian", "gluten free", "pescetarian"])
        allergies = st.multiselect("Allergies", ["dairy", "gluten", "peanut", "soy"])
        cuisines = st.multiselect("Preferred Cuisines", ["Mexican", "Italian", "Thai", "French", "Chinese"])

        if st.button("Generate Plan"):
            num = 3 if meals_per_day == "Three meals" else 1
            for i in range(num):
                selected_cuisine = cuisines[i % len(cuisines)] if cuisines else "American"
                recipe = fetch_recipe(selected_cuisine, diet, ",".join(allergies))

                st.markdown(f"#### 🍽️ {recipe['title']}")
                st.image(recipe.get("image"), width=350)
                st.write("**Ingredients Preview:**")
                st.write([i['name'] for i in recipe.get("extendedIngredients", [])])
                st.write("**Instructions:**")
                st.markdown(recipe.get("instructions") or "No instructions provided.")

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
