import streamlit as st
import datetime
import requests
import time
import numpy as np
from textblob import TextBlob
import matplotlib.pyplot as plt
import pandas as pd
from supabase import create_client

# ---------------- Inject CSS for fade-in animation ----------------
st.markdown(
    """
    <style>
    .fade-in {
        animation: fadeInAnimation ease 2s;
        animation-iteration-count: 1;
        animation-fill-mode: forwards;
    }
    @keyframes fadeInAnimation {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- Supabase Connection ----------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- Google API Call Helper ----------------
def google_api_call(model, endpoint, prompt, system_instruction=None):
    api_key = st.secrets.get("GOOGLE_API_KEY", "")
    if not api_key:
        st.error("Missing Google API key!")
        st.stop()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:{endpoint}?key={api_key}"
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    if system_instruction:
        data["systemInstruction"] = {"parts": [{"text": system_instruction}]}
    with st.spinner("Connecting to AI coach... 🚀"):
        resp = requests.post(url, json=data)
        if resp.status_code == 429:
            time.sleep(2)
            resp = requests.post(url, json=data)
    if not resp.ok:
        st.error(f"Google API error {resp.status_code}: {resp.text}")
        st.stop()
    return resp.json()

# ---------------- BMI Calculator ----------------
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

# ---------------- Home Page ----------------
def home():
    st.markdown('<h1 class="fade-in">Welcome to Parmatma 🧘</h1>', unsafe_allow_html=True)
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
            st.balloons()
            st.success(f"Profile saved! BMI: {bmi:.2f} ({category}). {advice}")

# ---------------- BMI Calculator Page ----------------
def bmi_calculator():
    st.markdown('<h2 class="fade-in">BMI Calculator</h2>', unsafe_allow_html=True)
    profile = st.session_state.get("profile")
    if not profile:
        st.info("Please fill your profile first.")
        return
    bmi, category, advice = calculate_bmi(profile["weight"], profile["height"])
    # Dynamic color for category
    color = "green" if category == "Normal" else "orange" if category == "Overweight" else "red" if category == "Obese" else "blue"
    st.metric("BMI", f"{bmi:.2f}")
    st.markdown(f"<h3 style='color: {color};'>Category: {category}</h3>", unsafe_allow_html=True)
    st.write(advice)

# ---------------- Nutrition Coach ----------------
def nutrition_coach():
    st.markdown('<h2 class="fade-in">Nutrition Coach</h2>', unsafe_allow_html=True)
    profile = st.session_state.get("profile")
    if not profile:
        st.info("Please fill your profile first.")
        return

    category = st.session_state.get("bmi_category", "Unknown")
    st.write(f"Detected BMI Category: {category}")

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

# ---------------- Exercise Routines ----------------
def exercise_routines():
    st.markdown('<h2 class="fade-in">Exercise Routines</h2>', unsafe_allow_html=True)
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

# ---------------- Symptom Checker ----------------
def symptom_checker():
    st.markdown('<h2 class="fade-in">Symptom Checker</h2>', unsafe_allow_html=True)
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

# ---------------- Mental Health Chat ----------------
def mental_health_chat():
    st.markdown('<h2 class="fade-in">Mental Health Support Chat</h2>', unsafe_allow_html=True)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Talk to your wellness coach")
        send_clicked = st.form_submit_button("Send")

    if send_clicked and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        convo = "".join(
            f"{msg['role'].capitalize()}: {msg['content']}"
            for msg in st.session_state.chat_history[-10:]
)

        with st.spinner("Thinking... 🤔"):
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

        st.session_state.chat_history.append({"role": "assistant", "content": text})

        sentiment = TextBlob(user_input).sentiment.polarity
        emotion = "Positive" if sentiment > 0.2 else "Neutral" if sentiment > -0.2 else "Negative"
        st.markdown(f"Sentiment score: {sentiment:.2f} ({emotion})")
        if emotion == "Negative":
            st.info("Feeling down? Take a short break, breathe deeply, or reach out to someone you trust.")
        elif emotion == "Positive":
            st.info("Glad to hear you're feeling good! Keep up the positive mindset.")
        else:
            st.info("Thanks for sharing. Remember, support is available whenever you need it.")

    for msg in st.session_state.chat_history:
        who = "You" if msg["role"] == "user" else "Coach"
        st.markdown(f"{who}:** {msg['content']}")

# ---------------- Digital Soul Twin Feature ----------------
def digital_soul_twin():
    # Initialize session state for soul twin data
    if "soul_twin_profile" not in st.session_state:
        st.session_state.soul_twin_profile = {
            "daily_habits": [],
            "mood_history": [],
            "dates": []
        }

    st.markdown('<h1 class="fade-in">🌌 Digital Soul Twin - AI Health & Wellness Avatar</h1>', unsafe_allow_html=True)
    st.write("Track your daily health, mood, and habits. Your 'Soul Twin' learns and predicts your future wellbeing.")

    with st.form("daily_input_form"):
        sleep_hours = st.slider("Hours of sleep last night", 0, 12, 7)
        exercise_minutes = st.slider("Minutes of exercise today", 0, 120, 30)
        meal_quality = st.selectbox("Meal quality today", ["Healthy", "Average", "Unhealthy"])
        mood_text = st.text_area("Describe your mood and emotions", max_chars=200)
        submitted = st.form_submit_button("Update Soul Twin")

    if submitted:
        meal_score_map = {"Healthy": 1.0, "Average": 0.5, "Unhealthy": 0.0}
        meal_score = meal_score_map[meal_quality]
        sentiment = TextBlob(mood_text).sentiment.polarity  # -1 to 1
        today = datetime.date.today()
        day_data = {
            "date": today,
            "sleep": sleep_hours,
            "exercise": exercise_minutes,
            "meal_score": meal_score,
            "mood_text": mood_text,
            "sentiment": sentiment
        }

        st.session_state.soul_twin_profile["daily_habits"].append(day_data)
        st.session_state.soul_twin_profile["mood_history"].append(sentiment)
        st.session_state.soul_twin_profile["dates"].append(today)
        st.success(f"Data recorded for {today}!")

    def time_weighted_average(data, dates, decay=0.8):
        if not data:
            return None
        weights = []
        today = datetime.date.today()
        for d in dates:
            days_ago = (today - d).days
            weights.append(decay ** days_ago)
        weights = np.array(weights)
        data = np.array(data)
        weighted_avg = np.sum(data * weights) / np.sum(weights)
        return weighted_avg

    profile = st.session_state.soul_twin_profile

    if profile["daily_habits"]:
        sleep_avg = time_weighted_average([d["sleep"] for d in profile["daily_habits"]], profile["dates"])
        exercise_avg = time_weighted_average([d["exercise"] for d in profile["daily_habits"]], profile["dates"])
        meal_avg = time_weighted_average([d["meal_score"] for d in profile["daily_habits"]], profile["dates"])
        sentiment_avg = time_weighted_average(profile["mood_history"], profile["dates"])

        wellness_score = (sleep_avg/12 + exercise_avg/120 + meal_avg + (sentiment_avg + 1)/2) / 4

        feedback = []
        if sleep_avg < 6:
            feedback.append("Try to get at least 7 hours of quality sleep for better rest.")
        elif sleep_avg > 9:
            feedback.append("Excellent sleep habits! Keep it up.")
        else:
            feedback.append("Your sleep is moderate; fine tuning can boost your energy.")

        if exercise_avg < 20:
            feedback.append("Increase your daily exercise to 30+ minutes to improve health.")
        elif exercise_avg > 60:
            feedback.append("Great exercise routine! Stay consistent.")
        else:
            feedback.append("You are moderately active; more activity can help.")

        if meal_avg < 0.4:
            feedback.append("Consider healthier meals to support your wellbeing.")
        else:
            feedback.append("Your meal quality is good; balance is key.")

        if sentiment_avg < 0:
            feedback.append("Focus on mental wellness: mindfulness or talking to someone may help.")
        else:
            feedback.append("Your mood looks positive; keep nurturing mental health.")

        if wellness_score < 0.4:
            prediction = "Your current habits suggest potential decline in both mental and physical health if unchanged. Prioritize self-care."
        elif wellness_score > 0.7:
            prediction = "You are on a healthy path! Continuing your habits should sustain good mind & body balance."
        else:
            prediction = "Your habits are mixed; small positive changes can lead to meaningful improvements."

        st.header("🧘‍♂ Soul Twin Summary & Future Prediction")
        st.metric("Wellness Score", f"{wellness_score:.2f} / 1.0")
        st.write(prediction)

        st.subheader("Personalized Suggestions")
        for f in feedback:
            st.write("- " + f)

        st.subheader("Mood Sentiment Trend Over Time")
        plt.figure(figsize=(8, 3))
        plt.plot(profile["dates"], profile["mood_history"], marker='o', color='purple', linestyle='-')
        plt.fill_between(profile["dates"], profile["mood_history"], color='lavender', alpha=0.5)
        plt.axhline(y=0, color='gray', linestyle='--', linewidth=0.7)
        plt.title("Mood Sentiment Polarity Over Time")
        plt.ylabel("Sentiment (-1 to 1)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(plt)

        st.subheader("Recent Habit Records")
        df = pd.DataFrame(profile["daily_habits"])
        df["date"] = df["date"].astype(str)
        st.dataframe(df.sort_values(by="date", ascending=False).reset_index(drop=True))
    else:
        st.info("Please enter your daily data to see predictions and insights.")

# ---------------- Sidebar Navigation ----------------
st.sidebar.title("Parmatma Features")
page = st.sidebar.radio("Choose a feature", [
    "Home",
    "BMI Calculator",
    "Nutrition Coach",
    "Exercise Routines",
    "Symptom Checker",
    "Mental Health Support",
    "Digital Soul Twin"
])

# ---------------- Page Switcher ----------------
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
elif page == "Digital Soul Twin":
    digital_soul_twin()