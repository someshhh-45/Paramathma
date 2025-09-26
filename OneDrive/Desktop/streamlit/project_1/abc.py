import streamlit as st
import datetime
import requests
import time

import supabase
from textblob import TextBlob
import folium
from streamlit_folium import st_folium
from supabase import create_client, Client




import streamlit as st
from supabase import create_client

# Connect to Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)



st.set_page_config(page_title="Parmatma - Health & Wellness", page_icon="🧘", layout="centered")

# ----- Helper functions -----


def google_api_call(model, endpoint, prompt, system_instruction=None):
    api_key = st.secrets.get("GOOGLE_API_KEY", "")
    if not api_key:
        st.error("Missing Google API key!")
        st.stop()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:{endpoint}?key={api_key}"
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    if system_instruction:
        data["systemInstruction"] = {"parts": [{"text": system_instruction}]}
    resp = requests.post(url, json=data)
    if resp.status_code == 429:
        time.sleep(2)
        resp = requests.post(url, json=data)
    if not resp.ok:
        st.error(f"Google API error {resp.status_code}: {resp.text}")
        st.stop()
    return resp.json()


def calculate_bmi(weight_kg, height_cm):
    if weight_kg <= 0 or height_cm <= 0:
        return 0, "Invalid", "Height and weight must be positive."
    bmi = weight_kg / ((height_cm / 100) ** 2)
    if bmi < 18.5:
        return bmi, "Underweight", "Focus on nutrient-dense foods and gain weight healthily."
    elif bmi < 25:
        return bmi, "Normal", "Maintain your current healthy lifestyle."
    elif bmi < 30:
        return bmi, "Overweight", "Consider a balanced diet and exercise."
    else:
        return bmi, "Obese", "Consult a healthcare provider."

def home():
    st.title("Welcome to Parmatma 🧘")
    with st.form("profile_form"):
        name = st.text_input("Name")
        age = st.number_input("Age", 5, 120)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        height = st.number_input("Height (cm)", 100, 250)
        weight = st.number_input("Weight (kg)", 20, 200)
        submitted = st.form_submit_button("Save Profile")
    if submitted:
        if not name.strip():
            st.error("Please enter your name.")
        else:
            st.session_state.profile = dict(name=name, age=age, gender=gender, height=height, weight=weight)
            bmi, category, advice = calculate_bmi(weight, height)
            st.session_state.bmi_category = category
            st.success(f"Profile saved! BMI: {bmi:.2f} ({category}). {advice}")


def bmi_calculator():
    st.header("BMI Calculator")
    profile = st.session_state.get("profile")
    if not profile:
        st.info("Please fill your profile first.")
        return
    bmi, category, advice = calculate_bmi(profile["weight"], profile["height"])
    st.metric("BMI", f"{bmi:.2f}")
    st.write(f"Category: {category}")
    st.write(advice)


def nutrition_coach():
    st.header("Nutrition Coach")
    profile = st.session_state.get("profile")
    if not profile:
        st.info("Please fill your profile first.")
        return

    category = st.session_state.get("bmi_category", "Unknown")
    st.write(f"Detected BMI Category: {category}")

    # Dietary preferences selection
    diet_prefs = st.multiselect(
        "Select dietary preferences (optional)",
        options=["Vegetarian", "Vegan", "Gluten-Free", "Low Carb", "High Protein", "Keto"],
        help="Choose any dietary preferences to tailor your nutrition plan."
    )

    allergies = st.text_area(
        "List any allergies or foods to avoid (optional)",
        placeholder="e.g. peanuts, dairy, shellfish"
    )

    goal = st.text_area(
        "Your specific nutrition goal",
        value="Balanced, healthy diet plan.",
        help="Describe your nutrition goals or any special requirements."
    )

    detail_level = st.radio(
        "Select plan detail level",
        options=["Brief", "Detailed"],
        index=0
    )

    if st.button("Generate Plan"):
        if not goal.strip():
            st.info("Please enter your nutrition goal.")
            return

        # Compose prompt with all inputs
        prompt = (
            f"Create a {detail_level.lower()} weekly nutrition plan for a person who is {category}. "
            f"Dietary preferences: {', '.join(diet_prefs) if diet_prefs else 'None'}. "
            f"Allergies or avoidance: {allergies if allergies.strip() else 'None'}. "
            f"Nutrition goal: {goal} "
            "Include meal ideas, portion guidance, and balanced nutrients."
        )

        response = google_api_call("gemini-2.0-flash-001", "generateContent", prompt)
        candidates = response.get("candidates", [])
        if candidates:
            text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            st.markdown(text)
        else:
            st.error("No response from nutrition coach API.")

def exercise_routines():
    st.header("Exercise Routines")
    profile = st.session_state.get("profile")
    if not profile:
        st.info("Please provide your profile details on the Home page first.")
        return

    required_fields = ["gender", "height", "weight"]
    if any(field not in profile or not profile[field] for field in required_fields):
        st.warning("Please ensure your profile includes gender, height, and weight for personalized plans.")
        return

    part = st.selectbox(
        "Select body part to focus on",
        ["Arms", "Legs", "Core", "Back", "Chest", "Full Body"],
        help="Choose the primary body area for your workout routine."
    )
    goal = st.text_input(
        "Fitness goal",
        "Improve strength and endurance",
        help="Briefly describe your overall fitness goal."
    )
    fitness_level = st.selectbox(
        "Fitness level",
        ["Beginner", "Intermediate", "Advanced"],
        help="Choose your current fitness experience level."
    )
    duration = st.slider(
        "Workout duration (minutes)",
        min_value=10,
        max_value=120,
        value=30,
        step=5,
        help="Set how much time you want to dedicate for each workout."
    )

    if st.button("Generate Routine"):
        if not goal.strip():
            st.error("Please enter your fitness goal to generate a routine.")
            return

        prompt = (
            f"Create a well-rounded {duration}-minute exercise routine for a {fitness_level.lower()} "
            f"focused on {part}, targeting the goal: '{goal}'. Include warm-up and cool-down suggestions. "
            f"Tailor the routine for a {profile['gender']} considering general fitness principles."
        )
        response = google_api_call("gemini-2.0-flash-001", "generateContent", prompt)
        candidates = response.get("candidates", [])
        if candidates:
            text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            st.markdown(text)
        else:
            st.error("No response received from the exercise routine API.")

def symptom_checker():
    st.header("Symptom Checker")
    symptoms = st.text_area("Describe your symptoms")
    if st.button("Analyze"):
        if not symptoms.strip():
            st.error("Please enter symptoms.")
            return
        prompt = (
            f"User symptoms: {symptoms}. "
            "Predict possible diseases or conditions matching these symptoms. "
            "For each, provide a confidence score as a percentage and list which symptoms matched. "
            "Give only the top 3 predictions in a clear, brief format."
        )
        response = google_api_call("gemini-2.0-flash-001", "generateContent", prompt)
        candidates = response.get("candidates", [])
        if candidates:
            text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            st.markdown(text)
        else:
            st.error("No response from symptom checker API.")


def mental_health_chat():
    st.header("Mental Health Support Chat")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Talk to your wellness coach")
        send_clicked = st.form_submit_button("Send")

    if send_clicked and user_input.strip():
        # Append user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Build conversation string from last 10 messages for context (can adjust length)
        convo = "\n".join(
            f"{msg['role'].capitalize()}: {msg['content']}"
            for msg in st.session_state.chat_history[-10:]
        )

        with st.spinner("Thinking..."):
            reply = google_api_call(
                "gemini-2.0-flash-001",
                "generateContent",
                convo,
                "Short, kind, supportive replies under 100 words."
            )
            candidates = reply.get("candidates", [])
            if candidates:
                text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "I'm here to help.")
            else:
                text = "I'm here to help."

        # Append assistant reply
        st.session_state.chat_history.append({"role": "assistant", "content": text})

        # Sentiment analysis and friendly messages
        sentiment = TextBlob(user_input).sentiment.polarity
        emotion = "Positive" if sentiment > 0.2 else "Neutral" if sentiment > -0.2 else "Negative"
        st.markdown(f"Sentiment score: {sentiment:.2f} ({emotion})")
        if emotion == "Negative":
            st.info("Feeling down? Take a short break, breathe deeply, or reach out to someone you trust.")
        elif emotion == "Positive":
            st.info("Glad to hear you're feeling good! Keep up the positive mindset.")
        else:
            st.info("Thanks for sharing. Remember, support is available whenever you need it.")

    # Display chat messages
    for msg in st.session_state.chat_history:
        who = "You" if msg["role"] == "user" else "Coach"
        st.markdown(f"{who}:** {msg['content']}")





# ------ Sidebar Navigation -----


st.sidebar.title("Parmatma Features")
page = st.sidebar.radio("Choose a feature", [
    "Home",
    "BMI Calculator",
    "Nutrition Coach",
    "Exercise Routines",
    "Symptom Checker",
    "Mental Health Support",
    
])


# ------ Page switcher ------
if page == "Home":
    home()
elif page == "BMI Calculator":
    bmi_calculator()
elif page == "Nutrition Coach":
    nutrition_coach()
elif page == "Exercise Routines":
    exercise_routines()
elif page == "Symptom Checker":
    symptom_checker()
elif page == "Mental Health Support":
    mental_health_chat()
