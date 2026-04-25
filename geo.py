import streamlit as st
import pandas as pd

df = pd.read_csv("data/geo-capitals_EN.csv")

def generate_question():
    options = df.sample(4, replace=False)
    answer = options.sample(1)
    return options, answer

if "options" not in st.session_state:
    st.session_state.options, st.session_state.answer = generate_question()
    st.session_state.submitted = False

options = st.session_state.options
answer = st.session_state.answer

country = answer["Country"].values[0]
correct_capital = answer["Capital"].values[0]

choices = options["Capital"].tolist()

choice = st.radio(
    f"What is the capital of {country}?",
    choices,
    index=None 
)

if st.button("Submit"):
    st.session_state.submitted = True
if st.session_state.submitted:
    if choice == correct_capital:
        st.success("Correct!")
    else:
        st.error(f"Wrong! The correct answer is {correct_capital}")

    if st.button("Next Question"):
        st.session_state.options, st.session_state.answer = generate_question()
        st.session_state.submitted = False
        st.rerun()