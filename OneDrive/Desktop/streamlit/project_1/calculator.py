import streamlit as st
import datetime

st.title("🎂 Age Calculator")

# Get today's date
today = datetime.date.today()

# Ask user for date of birth
dob = st.date_input("Enter your Date of Birth:", today)

# Calculate age
if dob > today:
    st.error("Date of birth cannot be in the future!")
else:
    age_years = today.year - dob.year- ((today.month, today.day) < (dob.month, dob.day))
    st.success(f"Your age is: {age_years} years")