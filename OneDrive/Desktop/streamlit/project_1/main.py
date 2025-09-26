import streamlit as st
import requests
import time
from textblob import TextBlob
import folium
from streamlit_folium import st_folium
import sqlite3
import pandas as pd
from io import StringIO

st.set_page_config(page_title="Parmatma - Health & Wellness", page_icon="🧘", layout="centered")

# --- Set up SQLite DB for user profiles and appointments ---
conn = sqlite3.connect('parmatma.db', check_same_thread=False)
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    gender TEXT,
    height REAL,
    weight REAL,
    vegan TEXT
)""")
c.execute("""CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    doctor TEXT,
    specialty TEXT,
    datetime TEXT
)""")
conn.commit()

# ------ Helper functions ------

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


def save_profile(name, age, gender, height, weight, vegan=None):
    # Save profile to DB
    c.execute("INSERT INTO profiles (name, age, gender, height, weight, vegan) VALUES (?, ?, ?, ?, ?, ?)",
              (name, age, gender, height, weight, vegan))
    conn.commit()

def get_latest_profile():
    c.execute("SELECT * FROM profiles ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    if row:
        return {
            "id": row[0], "name": row[1], "age": row[2], "gender": row[3],
            "height": row[4], "weight": row[5], "vegan": row[6]
        }
    return None

# Real-time ambulance driver info fetching simulation
def fetch_real_time_ambulance_info(location):
    # Simulated dynamic data; Replace with real API call as available
    import random
    driver_names = ["Rajesh Kumar", "Sunita Singh", "Amar Patel", "Neha Sharma"]
    selected_driver = random.choice(driver_names)
    phone_number = f"88{random.randint(100000,999999)}"
    eta = random.randint(5, 15)
    ambulance_id = f"AMB-{1000 + random.randint(1, 999)}"
    vehicle_type = random.choice(["Basic Life Support", "Advanced Life Support", "Patient Transport"])
    return {
        "driver_name": selected_driver,
        "driver_phone": phone_number,
        "ambulance_id": ambulance_id,
        "eta_minutes": eta,
        "vehicle_type": vehicle_type
    }


# -------------- Pages ----------------

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
            bmi, category, advice = calculate_bmi(weight, height)
            if category == "Underweight":
                is_vegan = st.radio("Are you vegan?", ("Yes", "No"))
                save_profile(name, age, gender, height, weight, is_vegan)
                st.success(f"Profile saved! BMI: {bmi:.2f} ({category}). {advice}")
                st.write(f"Nutrition advice based on vegan: {is_vegan}")
                if is_vegan == "Yes":
                    st.write("""
                    Vegan diet for weight gain: include nuts, seeds, tofu, legumes, plant-based smoothies with protein powders, fortified foods.
                    """)
                else:
                    st.write("""
                    Non-vegan weight gain diet: include eggs, dairy, lean meats, fish, nuts, healthy oils and small frequent meals.
                    """)
            else:
                save_profile(name, age, gender, height, weight)
                st.success(f"Profile saved! BMI: {bmi:.2f} ({category}). {advice}")

    # Show saved profile info
    profile = get_latest_profile()
    if profile:
        st.write(f"Latest profile: {profile['name']}, Age: {profile['age']}, Gender: {profile['gender']}, Vegan: {profile.get('vegan', 'Unknown')}")

import streamlit as st

def get_latest_profile():
    return st.session_state.get("profile")

def nutrition_coach():
    profile = get_latest_profile()
    
    if profile is None:
        st.info("Please fill your profile first in Home tab.")
        return

       

    st.header("Nutrition Coach")
    category = profile.get("bmi_category", "Unknown")
    st.write(f"BMI Category: {category}")

    diet_type = profile.get("diet_type", "Non-Vegetarian")  # "Vegan", "Vegetarian", or "Non-Vegetarian"
    gluten_free = profile.get("gluten_free", False)        # Boolean
    allergies = profile.get("allergies", "")

    st.write(f"Diet Type: {diet_type}")
    st.write(f"Gluten-Free: {'Yes' if gluten_free else 'No'}")
    if allergies:
        st.write(f"Allergies: {allergies}")

    if category == "Underweight":
        st.write("Suggestions for weight gain:")
        if diet_type == "Vegan":
            st.write("""
            - Nutrient dense plant-based protein such as tofu, tempeh, legumes  
            - Nut butters, seeds, avocados  
            - Plant-based protein powders  
            - Frequent small meals and smoothies  
            - Include quinoa and amaranth for gluten-free grains if applicable  
            """)
        elif diet_type == "Vegetarian":
            st.write("""
            - Protein sources like eggs, dairy, legumes, and paneer  
            - Healthy fats such as nuts and olive oil  
            - Frequent small meals, smoothies  
            - Gluten-free grains like brown rice, millet, and buckwheat if gluten-free  
            """)
        else:  # Non-Vegetarian
            st.write("""
            - Protein from eggs, chicken, fish, and lean meats  
            - Healthy fats like nuts, seeds, olive oil  
            - Frequent small meals, balanced macronutrients  
            - Use gluten-free grains if gluten-free  
            """)
    else:
        # For other BMI categories, provide general advice or personalized tips
        st.write("General nutrition advice:")
        st.write("Maintain balanced nutrients and adjust diet according to your health goals.")
        if gluten_free:
            st.write("Ensure your gluten-free diet includes adequate fiber and vitamins from alternative grains.")

    st.markdown("---")
    st.write("For personalized meal plans, consider using AI-powered nutrition coaching or consulting a dietitian.")

def exercise_routines():
    profile = get_latest_profile()
    if not profile:
        st.info("Please fill your profile first in Home tab.")
        return
    st.header("Exercise Routines")
    gender = profile.get("gender", "Other").lower()
    body_part = st.selectbox("Choose body part to exercise", [
        "Full Body", "Upper Body", "Lower Body", "Core", "Cardio",
        "Arms (Biceps & Triceps)", "Legs (Quads, Hamstrings, Calves)"
    ])
    routines = {
        "male": {...},  # Use previous detailed dict (same as prior for brevity here)
        "female": {...},
        "other": {...}
    }
    # For brevity, re-define routines as before or import from prior code, or expand here

    gender_key = gender if gender in routines else "other"
    selected_routine = routines.get(gender_key, {}).get(body_part.lower(), [])
    if selected_routine:
        st.write(f"Recommended exercises for {body_part}:")
        for exercise in selected_routine:
            st.write(f"- {exercise}")
    else:
        st.write("No routines available for this option.")

# Mental Health Support Chatbot with loop input

def mental_health_chat():
    st.header("Mental Health Support Chat")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if prompt := st.text_input("Talk to your wellness coach"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        # For demo, simple echo or call API with conversation context
        response = f"Coach Reply: I hear you said, '{prompt}'. I'm here to help."
        st.session_state.chat_history.append({"role": "assistant", "content": response})

    for msg in st.session_state.chat_history:
        who = "You" if msg["role"] == "user" else "Coach"
        st.markdown(f"{who}:** {msg['content']}")

# Doctor Appointment Booking with real-time slot info as details

def doctor_appointments():
    st.header("Doctor Appointment Booking")
    city = st.text_input("Enter your city or area")
    specialty = st.selectbox("Select Specialization", ["General Physician", "Cardiologist", "Dermatologist", "Pediatrician", "Gynecologist", "Other"])

    # Replace with real API calls
    def get_available_doctors(city, specialty):
        return {
            "Dr. A Sharma": ["2025-09-21 10:00", "2025-09-21 14:00"],
            "Dr. B Verma": ["2025-09-22 09:00", "2025-09-23 11:30"],
        }

    if st.button("Show Available Doctors"):
        if not city.strip():
            st.error("Enter valid city")
            return
        doctors = get_available_doctors(city, specialty)
        for doc, slots in doctors.items():
            st.write(f"{doc}")
            if st.checkbox(f"Show available slots for {doc}", key=doc):
                for slot in slots:
                    st.write(f"- {slot}")

# Emergency Support with real-time ambulance info retrieval simulation

def emergency_support():
    st.title("Parmatma Emergency Support")
    location = st.text_input("Enter your city or area for ambulance support")
    if st.button("Request Ambulance Driver Contact"):
        if not location.strip():
            st.error("Please enter a valid location.")
            return
        st.info("Searching ambulance driver for location, please wait...")
        time.sleep(1)
        info = fetch_real_time_ambulance_info(location)
        st.success(f"Ambulance driver: {info['driver_name']}")
        st.write(f"Phone: {info['driver_phone']}")
        st.write(f"Ambulance ID: {info['ambulance_id']}")
        st.write(f"ETA: {info['eta_minutes']} minutes")
        st.write(f"Vehicle type: {info['vehicle_type']}")
        st.info("Please call the driver directly for coordination.")
    st.info("Emergency Numbers in India:\n- Call 112 (Police, Fire, Ambulance)\n- Call 108 (Ambulance)")
    if st.button("Call Ambulance (108)"):
        st.write("Please call 108 immediately for ambulance services.")

# Summary download as CSV/text of profile for user to download

def download_profile_summary():
    profile = get_latest_profile()
    if not profile:
        st.info("No profile to download. Please add your profile first.")
        return
    data = {
        "Name": profile['name'],
        "Age": profile['age'],
        "Gender": profile['gender'],
        "Height (cm)": profile['height'],
        "Weight (kg)": profile['weight'],
        "Vegan": profile.get('vegan', 'Unknown'),
    }
    df = pd.DataFrame([data])
    csv = df.to_csv(index=False)
    st.download_button("Download Profile Summary CSV", data=csv, file_name="parmatma_profile.csv", mime="text/csv")

# Sidebar and routing

st.sidebar.title("Parmatma Features")
page = st.sidebar.radio("Choose a feature", [
    "Home",
    "BMI Calculator",
    "Nutrition Coach",
    "Exercise Routines",
    "Symptom Checker",
    "Mental Health Support",
    "Doctor Appointment Booking",
    "Emergency Support",
    "Download Profile Summary"
])

if page == "Home":
    home()
elif page == "BMI Calculator":
    profile = get_latest_profile()
    if profile:
        bmi, category, advice = calculate_bmi(profile['weight'], profile['height'])
        st.metric("BMI", f"{bmi:.2f}")
        st.write(f"Category: {category}")
        st.write(advice)
    else:
        st.info("Please fill your profile first.")
elif page == "Nutrition Coach":
    nutrition_coach()
elif page == "Exercise Routines":
    exercise_routines()
elif page == "Symptom Checker":
    # existing symptom_checker function here
    st.info("Symptom checker not implemented here.")
elif page == "Mental Health Support":
    mental_health_chat()
elif page == "Doctor Appointment Booking":
    doctor_appointments()
elif page == "Emergency Support":
    emergency_support()
elif page == "Download Profile Summary":
    download_profile_summary()