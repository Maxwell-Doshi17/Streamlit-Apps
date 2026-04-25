import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import random

df = pd.read_csv("data/geo-capitals_EN.csv")
if "dict1" not in st.session_state:
    st.session_state.dict1 = {"Right": [], "Wrong": []}
    st.session_state.cont = {"Right": [], "Wrong": []}
def generate_question():
    answer = df.sample(1)
    wrong = df[df["Country"] != answer["Country"].values[0]].sample(3)
    options = pd.concat([answer, wrong]).sample(frac=1)
    return options, answer
if "game_over" not in st.session_state:
    st.session_state.game_over = False
# Initialize state
if "options" not in st.session_state:
    st.session_state.options, st.session_state.answer = generate_question()
    st.session_state.submitted = False
    st.session_state.score = 0
    st.session_state.total = 0
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
if st.button("Submit") and not st.session_state.submitted:
    if choice is None:
        st.warning("Pick an answer first.")
    else:
        st.session_state.submitted = True
        st.session_state.total += 1
        if choice == correct_capital:
            st.session_state.score += 1
            st.session_state.dict1["Right"].append(country)
            st.session_state.cont["Right"].append(answer["Continent"].values[0])
            st.success("Correct!")
        else:
            st.session_state.dict1["Wrong"].append(country)
            st.session_state.cont["Wrong"].append(answer["Continent"].values[0])
            st.error(f"Wrong! The correct answer is {correct_capital}")

st.write(f"Score: {st.session_state.score} / {st.session_state.total}")

if st.session_state.submitted:
    if st.button("Next Question"):
        st.session_state.options, st.session_state.answer = generate_question()
        st.session_state.submitted = False
        st.rerun()
if st.button("End Game"):
    st.session_state.game_over = True
    st.rerun()

if st.session_state.game_over:
    st.title("Game Over 🎉")

    score = st.session_state.score
    total = st.session_state.total

    st.write(f"Final Score: {score} / {total}")

    df_graph = pd.DataFrame(
    [(result, cont) for result, lst in st.session_state.cont.items() for cont in lst],
    columns=["Result", "Continent"]
)    
    


    counts = pd.crosstab(df_graph["Continent"], df_graph["Result"])

    fig, ax = plt.subplots()
    counts.plot(kind="bar", stacked=True, ax=ax)

    ax.set_xlabel("Continent")
    ax.set_ylabel("Number of Countries")
    ax.set_title("Performance by Continent")

    plt.xticks(rotation=25)
    st.pyplot(fig)

