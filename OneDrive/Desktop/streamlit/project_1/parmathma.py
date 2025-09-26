import streamlit as st
import datetime
import requests
import time
from textblob import TextBlob


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


# Define an example prompt to avoid NameError on initial call, or remove if unused
prompt = "Hello, how can I help you today?"
response = google_api_call("gemini-2.5-flash", "generateContent", prompt)


# For mental health chat, update this call inside mental_health_chat():
# Correct argument order: model, endpoint, prompt, system_instruction
def mental_health_chat():
    st.header("Mental Health Support Chat")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    user_input = st.text_input("Talk to your wellness coach")
    if st.button("Send") and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        convo = "\n".join(f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.chat_history[-5:])
        reply = google_api_call("gemini-2.5-flash", "generateContent", convo, "Short, kind, supportive replies.")
        text = reply.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "I'm here to help.")
        st.session_state.chat_history.append({"role": "assistant", "content": text})
        sentiment = TextBlob(user_input).sentiment.polarity
        st.markdown(f"Sentiment score: *{sentiment:.2f}*")
    for msg in st.session_state.chat_history:
        who = "You" if msg["role"] == "user" else "Coach"
        st.markdown(f"{who}:** {msg['content']}")


# (Other functions remain unchanged...)

# You can include the rest of your code here for other pages and helpers as needed



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

def get_hospitals_nearby(location):
    api_key = st.secrets.get("GOOGLE_PLACES_KEY", "")
    if not api_key:
        st.error("Missing Google Places API key!")
        st.stop()
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": f"hospital near {location}", "key": api_key}
    resp = requests.get(url, params=params)
    if not resp.ok:
        st.error(f"Google Places API error: {resp.status_code} {resp.text}")
        st.stop()
    return resp.json().get("results", [])

def get_platforms_by_location(city):
    city = city.strip().lower()
    metro_platforms = {
        "mumbai": [
            ("Practo", "https://www.practo.com", "Mobile-friendly, video & clinic consults"),
            ("Apollo 24|7", "https://www.apollo247.com", "Telehealth + medicine delivery"),
            ("MFine", "https://www.mfine.co", "AI-driven video consults"),
        ],
        "bangalore": [
            ("Practo", "https://www.practo.com/bangalore", "Top Bangalore doctors"),
            ("MFine", "https://www.mfine.co", "Teleconsult & fast support"),
            ("DocPrime", "https://www.docprime.com", "24/7 video consults"),
        ],
        "delhi": [
            ("Practo", "https://www.practo.com/delhi", "Delhi doctors with instant booking"),
            ("Apollo 24|7", "https://www.apollo247.com", "Full hospital network support"),
            ("1mg", "https://www.1mg.com", "Teleconsult & delivery"),
        ]
    }
    return metro_platforms.get(city, [
        ("Practo", "https://www.practo.com", "Instant booking"),
        ("Apollo 24|7", "https://www.apollo247.com", "Online consults"),
        ("MFine", "https://www.mfine.co", "Quick video calls"),
        ("1mg", "https://www.1mg.com", "Consult & medicine delivery"),
        ("DocPrime", "https://www.docprime.com", "Video consultations"),
    ])

# ------------- Pages -------------

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
    st.write(f"Category: *{category}*")
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

    user_input = st.text_input("Talk to your wellness coach")
    send_clicked = st.button("Send")

    if send_clicked and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        convo = "\n".join(
            f"{msg['role'].capitalize()}: {msg['content']}"
            for msg in st.session_state.chat_history[-5:]
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

        st.session_state.chat_history.append({"role": "assistant", "content": text})

        sentiment = TextBlob(user_input).sentiment.polarity
        emotion = "Positive" if sentiment > 0.2 else "Neutral" if sentiment > -0.2 else "Negative"
        st.markdown(f"Sentiment score: *{sentiment:.2f}* ({emotion})")

        if emotion == "Negative":
            st.info("Feeling down? Take a short break, breathe deeply, or reach out to someone you trust.")
        elif emotion == "Positive":
            st.info("Glad to hear you're feeling good! Keep up the positive mindset.")
        else:
            st.info("Thanks for sharing. Remember, support is available whenever you need it.")

    for msg in st.session_state.chat_history:
        who = "You" if msg["role"] == "user" else "Coach"
        st.markdown(f"{who}:** {msg['content']}")


import streamlit as st
import sqlite3
import datetime
import pandas as pd
import requests
import time
from textblob import TextBlob

st.set_page_config(page_title="Parmatma - Health & Wellness Tracker", page_icon="🧘‍♂", layout="centered")

DB_PATH = "parmatma.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, age INTEGER, gender TEXT, height REAL, weight REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS symptom_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, symptoms TEXT, response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mental_health_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, mood_note TEXT, sentiment REAL, response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, specialty TEXT, location TEXT, date TEXT, time TEXT, status TEXT DEFAULT 'Booked',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

def save_personal_details_to_db(details):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, age, gender, height, weight) VALUES (?, ?, ?, ?, ?)",
        (details['name'], details['age'], details['gender'], details['height'], details['weight'])
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id

def save_symptom_entry(user_id, symptoms, response):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO symptom_entries (user_id, symptoms, response) VALUES (?, ?, ?)",
        (user_id, symptoms, response)
    )
    conn.commit()
    conn.close()

def save_mental_health_entry(user_id, mood_note, sentiment, response):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO mental_health_entries (user_id, mood_note, sentiment, response) VALUES (?, ?, ?, ?)",
        (user_id, mood_note, sentiment, response)
    )
    conn.commit()
    conn.close()

def save_appointment(user_id, specialty, location, date, time):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO appointments (user_id, specialty, location, date, time) VALUES (?, ?, ?, ?, ?)",
        (user_id, specialty, location, date, time)
    )
    conn.commit()
    conn.close()

def load_user_history(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM symptom_entries WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
    symptoms = cursor.fetchall()
    cursor.execute("SELECT * FROM mental_health_entries WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
    mental = cursor.fetchall()
    cursor.execute("SELECT * FROM appointments WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
    appointments = cursor.fetchall()
    conn.close()
    return symptoms, mental, appointments

def google_api_call(model, endpoint, payload):
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("Google API key missing. Please add it to secrets.toml.")
        st.stop()
    api_key = st.secrets["GOOGLE_API_KEY"]
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:{endpoint}?key={api_key}"
    retries, max_retries, delay = 0, 3, 1
    while retries < max_retries:
        try:
            response = requests.post(api_url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            if response.status_code == 429:
                retries += 1
                time.sleep(delay)
                delay *= 2
            else:
                raise err
        except Exception as e:
            raise e
    raise Exception("Max retries exceeded for API call.")

def calculate_bmi_and_category(weight_kg, height_cm):
    if height_cm <= 0 or weight_kg <= 0:
        return 0, "Invalid", "Height and weight must be positive numbers."
    bmi = weight_kg / ((height_cm / 100) ** 2)
    if bmi < 18.5:
        category, advice = "Underweight", "Focus on nutrient-dense foods and consult a professional for healthy weight gain."
    elif 18.5 <= bmi < 25:
        category, advice = "Normal", "Maintain balanced diet and regular exercise."
    elif 25 <= bmi < 30:
        category, advice = "Overweight", "Consider a balanced diet and increase activity."
    else:
        category, advice = "Obese", "Consult a professional for personalized weight management."
    return bmi, category, advice

def infermedica_symptom_checker(symptom_text):
    return ("Possible causes: Common cold, flu. Advice: Rest, hydrate, see doctor if symptoms worsen.",
            [{"title": "Common Cold", "uri": "https://www.cdc.gov/common-cold/"},
             {"title": "Flu", "uri": "https://www.cdc.gov/flu/"}])

def generate_user_full_report(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user: return "No personal details found."
    lines = []
    lines.append(f"Personal Details:\nName: {user['name']} Age: {user['age']} Gender: {user['gender']} Height: {user['height']} Weight: {user['weight']} Registered On: {user['timestamp']}\n")
    cursor.execute("SELECT * FROM symptom_entries WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
    symptoms = cursor.fetchall()
    lines.append("\nSymptoms:")
    lines += [f"Date: {s['timestamp']} Symptoms: {s['symptoms']} Analysis: {s['response']}" for s in symptoms]
    cursor.execute("SELECT * FROM appointments WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
    appts = cursor.fetchall()
    lines.append("\nDoctor Appointments:")
    lines += [f"Date: {a['date']} Time: {a['time']} Specialty: {a['specialty']} Location: {a['location']} Status: {a['status']}" for a in appts]
    cursor.execute("SELECT * FROM mental_health_entries WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
    mental = cursor.fetchall()
    lines.append("\nMental Health:")
    lines += [f"Date: {m['timestamp']} Note: {m['mood_note']} Sentiment: {m['sentiment']:.2f} Advice: {m['response']}" for m in mental]
    conn.close()
    return "\n".join(lines)

def generate_medical_summary(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user: return "No user found."
    bmi, category, advice = calculate_bmi_and_category(user['weight'], user['height'])
    cursor.execute("SELECT * FROM appointments WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1", (user_id,))
    last_appt = cursor.fetchone()
    cursor.execute("SELECT * FROM symptom_entries WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1", (user_id,))
    last_symptom = cursor.fetchone()
    report = [f"Medical Report for {user['name']} (as of {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n"]
    report.append(f"Age: {user['age']} Gender: {user['gender']} Height: {user['height']} Weight: {user['weight']} BMI: {bmi:.2f} ({category})")
    report.append(f"\nBMI Advice: {advice}")
    if last_appt:
        report.append(f"\nRecent Appointment: {last_appt['date']} {last_appt['time']} [{last_appt['specialty']}] in {last_appt['location']}, Status: {last_appt['status']}")
    if last_symptom:
        report.append(f"\nLatest Symptom: {last_symptom['symptoms']} ({last_symptom['response']})")
    report.append("\nPlease consult a healthcare professional for diagnosis and treatment.")
    conn.close()
    return "\n".join(report)

def eq_summary(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    cursor.execute("SELECT * FROM appointments WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1", (user_id,))
    last_appt = cursor.fetchone()
    bmi, category, advice = calculate_bmi_and_category(user['weight'], user['height'])
    msg = f"""EQ-Summary for {user['name']}
- Gender: {user['gender']} Age: {user['age']}
- BMI: {bmi:.2f} ({category})
- Last Doctor Visit: {last_appt['date']} {last_appt['time']} [{last_appt['specialty']}] in {last_appt['location']}, Status: {last_appt['status']}" if last_appt else "No appointments"
- Advice: {advice}
"""
    return msg

def home_page():
    st.title("Welcome to Parmatma 🧘‍♂")
    st.markdown("Your all-in-one health and wellness companion.")
    with st.form("personal_details_form"):
        name = st.text_input("Name")
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", min_value=5, max_value=120, step=1)
        with col2:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, format="%.2f")
        weight = st.number_input("Weight (kg)", min_value=20.0, max_value=200.0, format="%.2f")
        submitted = st.form_submit_button("Submit Details")
        if submitted:
            if not name:
                st.error("Please enter your name.")
            elif height <= 0 or weight <= 0:
                st.error("Height and weight must be positive.")
            else:
                details = {'name': name, 'age': age, 'gender': gender,
                           'height': height, 'weight': weight}
                user_id = save_personal_details_to_db(details)
                st.session_state['user_id'] = user_id
                st.session_state['personal'] = details
                bmi, category, advice = calculate_bmi_and_category(weight, height)
                st.session_state['bmi_category'] = category
                st.success(f"Hello {name}! Details saved.")
                st.info(eq_summary(user_id))

def doctor_appointments_page():
    st.header("Doctor Appointments & Telemedicine 🏥")
    user_id = st.session_state.get('user_id')
    with st.form("appointment_form"):
        location = st.text_input("City/Locality for appointment")
        specialty = st.selectbox("Specialty", ["General", "Cardiologist", "Dermatologist", "Dentist", "Other"])
        appt_date = st.date_input("Appointment Date", value=datetime.date.today())
        appt_time = st.time_input("Appointment Time")
        submitted = st.form_submit_button("Book Appointment")
        if submitted:
            if not (location and specialty and appt_date and appt_time):
                st.error("Fill all fields for appointment booking.")
            elif not user_id:
                st.error("Please enter your personal details first.")
            else:
                save_appointment(user_id, specialty, location, str(appt_date), str(appt_time))
                st.success(f"Appointment booked!")
    st.markdown("---")
    st.subheader("Your Appointment History")
    if user_id:
        _, _, appointments = load_user_history(user_id)
        if appointments:
            for a in appointments:
                st.markdown(f"- {a['date']} {a['time']}, {a['specialty']} at {a['location']} | {a['status']}")
        else:
            st.info("No appointments booked yet.")

def show_history_sidebar():
    user_id = st.session_state.get('user_id')
    if not user_id: return
    symptoms, mental, appointments = load_user_history(user_id)
    st.sidebar.header("Your History")
    st.sidebar.markdown("Latest Symptoms")
    for entry in symptoms[:2]:
        st.sidebar.markdown(f"{entry['timestamp']}: {entry['symptoms']}")
    st.sidebar.markdown("Appointments")
    for a in appointments[:2]:
        st.sidebar.markdown(f"{a['date']} {a['time']} [{a['specialty']}] at {a['location']}")
    st.sidebar.markdown("Mental Wellness")
    for m in mental[:2]:
        st.sidebar.markdown(f"{m['timestamp']}: Sentiment: {m['sentiment']:.2f}")
    full_report = generate_user_full_report(user_id)
    med_report = generate_medical_summary(user_id)
    st.sidebar.download_button(
        label="Download History",
        data=full_report,
        file_name="user_history.txt",
        mime="text/plain"
    )
    st.sidebar.download_button(
        label="Download Medical Report",
        data=med_report,
        file_name="medical_report.txt",
        mime="text/plain"
    )

## Add your other pages (BMI calculator, nutrition, exercises, symptoms, mental health, emergency...)

st.sidebar.title("Parmatma Menu 🥕")
pages = {
    "-- Personal Details --": home_page,
    "Doctor Appointments": doctor_appointments_page,
    # Add other pages as needed: e.g. "BMI Calculator": bmi_calculator_page, etc.
}
selection = st.sidebar.radio("Choose a feature:", list(pages.keys()))
pages[selection]()
show_history_sidebar()

import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

# --- Helper Function to Geocode Location with Nominatim ---
def geocode_location(location):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": location,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "ParmatmaHealthApp/1.0 (+https://yourdomain.com/contact)"
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200 and response.json():
        result = response.json()[0]
        return float(result["lat"]), float(result["lon"])
    else:
        return None, None

# --- Helper Function to Query Hospitals Nearby via Overpass API ---
def get_nearby_hospitals(lat, lon, radius=5000):
    overpass_query = f"""
    [out:json];
    node["amenity"="hospital"](around:{radius},{lat},{lon});
    out body;
    """
    overpass_url = "https://overpass-api.de/api/interpreter"
    response = requests.post(overpass_url, data={"data": overpass_query})
    if response.status_code == 200:
        data = response.json()
        hospitals = []
        for element in data.get("elements", []):
            name = element.get("tags", {}).get("name", "Unnamed Hospital")
            hospital_lat = element.get("lat")
            hospital_lon = element.get("lon")
            hospitals.append({
                "name": name,
                "lat": hospital_lat,
                "lon": hospital_lon
            })
        return hospitals
    else:
        return []

# --- Optional: Display Hospitals on Interactive Map ---
def display_hospitals_map(hospitals, center_lat, center_lon):
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13)
    for hos in hospitals:
        folium.Marker(
            [hos['lat'], hos['lon']], 
            popup=hos['name']
        ).add_to(m)
    st_folium(m, width=700, height=450)

# --- Streamlit UI ---
st.title("Parmatma Emergency Support")
st.write("Find hospitals near your location based on OpenStreetMap data.")

location = st.text_input("Enter your city or address")

if st.button("Find Hospitals"):
    if not location.strip():
        st.error("Please enter a valid location.")
    else:
        # Step 1: Geocode Location
        lat, lon = geocode_location(location)
        if lat is None or lon is None:
            st.error("Failed to find coordinates for the location. Please try another location.")
        else:
            st.success(f"Location found: Latitude {lat:.5f}, Longitude {lon:.5f}")
            
            # Step 2: Query Hospitals Nearby
            hospitals = get_nearby_hospitals(lat, lon)
            
            if hospitals:
                st.success(f"Found {len(hospitals)} hospitals within 5 km of {location}:")
                
                # Step 3: Display List of Hospitals
                for hos in hospitals[:10]:  # limit to first 10 for display
                    st.write(f"- **{hos['name']}** (Lat: {hos['lat']:.5f}, Lon: {hos['lon']:.5f})")
                
                # Step 4 (Optional): Show Hospitals on Map
                display_hospitals_map(hospitals, lat, lon)
            else:
                st.warning(f"No hospitals found within 5 km of {location}.")



# ------ Sidebar Navigation -----

st.sidebar.title("Parmatma Features")
page = st.sidebar.radio("Choose a feature", [
    "Home",
    "BMI Calculator",
    "Nutrition Coach",
    "Exercise Routines",
    "Symptom Checker",
    "Mental Health Support",
    "Doctor Appointment Booking",
    "Emergency Support"
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
elif page == "Doctor Appointment Booking":
    doctor_appointments()
elif page == "Emergency Support":
    emergency_support()

# ---- Platforms by location utility
def get_platforms_by_location(city):
    city = city.strip().lower()
    metro_data = {
        "mumbai": [
            ("Practo", "https://www.practo.com", "Video & in-clinic consults"),
            ("Apollo 24|7", "https://www.apollo247.com", "Hospital network telemedicine"),
            ("MFine", "https://www.mfine.co", "AI-driven video consults"),
        ],
        "bangalore": [
            ("Practo", "https://www.practo.com/bangalore", "Bangalore specialists"),
            ("MFine", "https://www.mfine.co", "Video consultations"),
            ("DocPrime", "https://www.docprime.com", "24/7 video consults"),
        ],
        "delhi": [
            ("Practo", "https://www.practo.com/delhi", "Delhi doctors"),
            ("Apollo 24|7", "https://www.apollo247.com", "Hospital network telemedicine"),
            ("1mg", "https://www.1mg.com", "Teleconsults and medicine"),
        ]
    }
    return metro_data.get(city, [
        ("Practo", "https://www.practo.com", "Quick and easy appointments"),
        ("Apollo 24|7", "https://www.apollo247.com", "Trusted provider"),
        ("MFine", "https://www.mfine.co", "Video and audio consults"),
        ("1mg", "https://www.1mg.com", "Consult and medicine delivery"),
        ("DocPrime", "https://www.docprime.com", "Video appointments")
    ])