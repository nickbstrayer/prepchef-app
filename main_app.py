import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import requests
import random

st.set_page_config(page_title="PrepChef Meal Planner", layout="wide")

API_KEY = "ZXLohb41LpxjixMvNwgd6xP0hDIYPiLR"

if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "light"
theme = st.sidebar.selectbox("🌗 Theme Mode", ["light", "dark"])
st.session_state["theme_mode"] = theme

st.markdown("""
    <div style='text-align: center; padding: 1rem;'>
        <h1 style='margin-bottom: 0;'>👨‍🍳 PrepChef</h1>
        <p style='font-size: 1.1rem; color: gray;'>Your life. Your plate. Planned.</p>
    </div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("Navigate", ["Login", "Meal Plan", "Shopping List", "Order & Delivery"])

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_type = ""
    st.session_state.feedback = {}
    st.session_state.user_preferences = {
        "diet": "",
        "allergies": [],
        "cuisines": []
    }

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

@st.cache_data(ttl=86400)
def get_all_mealdb_recipes():
    categories = ["Beef", "Chicken", "Lamb", "Pasta", "Pork", "Seafood", "Vegan", "Vegetarian"]
    all_meals = []
    for category in categories:
        res = requests.get(f"https://www.themealdb.com/api/json/v1/1/filter.php?c={category}")
        if res.status_code == 200:
            meals = res.json().get("meals", [])
            for m in meals:
                meal_id = m.get("idMeal")
                detail_res = requests.get(f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}")
                if detail_res.status_code == 200:
                    detail = detail_res.json().get("meals", [])[0]
                    if detail and detail.get("strInstructions") and detail.get("strMeal") and detail.get("strMealThumb"):
                        all_meals.append({
                            "title": detail["strMeal"],
                            "image": detail["strMealThumb"],
                            "instructions": detail["strInstructions"],
                            "extendedIngredients": [
                                {"name": detail[k]} for k in detail if k.startswith("strIngredient") and detail[k] and detail[k] != ""
                            ]
                        })
    return all_meals

if st.session_state.logged_in:
    st.sidebar.success(f"Logged in as {st.session_state.user_type}")

    if menu == "Meal Plan":
        st.subheader("🗓️ Create Your Meal Plan")
        day = st.date_input("Start Date", value=datetime.today())
        plan_days = st.selectbox("How many days to plan?", [1, 5, 7])

        # User Preferences
        st.markdown("### 🍽️ Set Your Preferences")
        diet = st.selectbox("Diet", ["", "vegan", "vegetarian", "keto", "gluten free", "pescetarian"], index=0)
        allergies = st.multiselect("Allergies", ["dairy", "gluten", "peanut", "soy", "shellfish", "eggs"])
        cuisines = st.multiselect("Preferred Cuisines", ["Mexican", "American Traditional", "Thai", "Italian", "Caribbean", "French", "African", "Chinese"])

        if st.button("Save Preferences"):
            st.session_state.user_preferences = {
                "diet": diet,
                "allergies": allergies,
                "cuisines": cuisines
            }
            st.success("Preferences saved.")

        if st.button("Generate Plan"):
            fallback_pool = get_all_mealdb_recipes()
            random.shuffle(fallback_pool)
            used_titles = set()
            weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

            all_titles = set([m["title"] for m in fallback_pool])
            liked_titles = {k.split("_")[-1] for k, v in st.session_state.feedback.items() if v == "like"}

            if liked_titles == all_titles:
                st.warning("You’ve liked all available meals! Please add new cuisines or refresh options.")

            for d in range(plan_days):
                label = weekdays[d % 7]
                st.markdown(f"### 📅 {label} – {day + timedelta(days=d):%B %d}")

                for meal_time in ["Breakfast", "Lunch", "Dinner"]:
                    recipe = None
                    for fallback in fallback_pool:
                        if fallback['title'] not in used_titles:
                            recipe = fallback
                            used_titles.add(recipe['title'])
                            break

                    if recipe:
                        key = f"{label}_{meal_time}_{recipe['title']}"
                        st.markdown(f"#### 🍽️ {meal_time}: {recipe['title']}")
                        st.image(recipe.get("image"), width=350)
                        st.write("**Ingredients Preview:**")
                        st.write([i['name'] for i in recipe.get("extendedIngredients", [])])
                        st.write("**Instructions:**")
                        st.markdown(recipe.get("instructions") or "No instructions provided.")

                        cols = st.columns([1, 1])
                        with cols[0]:
                            if st.button("👍", key=f"like_{key}"):
                                st.session_state.feedback[key] = "like"
                        with cols[1]:
                            if st.button("👎", key=f"dislike_{key}"):
                                st.session_state.feedback[key] = "dislike"

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

st.markdown("---")
st.markdown("<p style='text-align:center;font-size:12px;color:gray;'>This app is for informational and planning purposes only. Creator: <b>Nick Budhai</b> | &copy; 2025 | <a href='#'>Terms of Use</a> | <a href='#'>Privacy Policy</a></p>", unsafe_allow_html=True)
