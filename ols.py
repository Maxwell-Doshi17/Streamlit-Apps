import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd

st.title("Ordinary Least Squares with Linear Algebra")

st.markdown("""
This tool demonstrates how **linear algebra** can be used to model data using **least squares regression**.

We represent the system as $Ax = b$, where $A$ is the design matrix, $x$ is the vector of unknown coefficients, and $b$ contains the observed values. 

When no exact solution exists, we solve the normal equations $A^T A \\hat{x} = A^T b$ to find the best-fit model that minimizes error.

Use this tool to input data, choose model terms, and visualize the resulting fit.
""")





feature_map = {
    "1": lambda x: np.ones(len(x)),
    "x": lambda x: np.array(x),
    "x^2": lambda x: np.array(x)**2,
    "x^3": lambda x: np.array(x)**3,
    "x^0.5": lambda x: np.sqrt(x),
    "sin(x)": lambda x: np.sin(x),
    "cos(x)": lambda x: np.cos(x),
    "log(x)": lambda x: np.log(x),
}



st.subheader("Enter Data Points")
st.markdown("""
Choose the number of data points and enter your $(x, y)$ values below.
""")


n = st.number_input("How many data points?", min_value=1, step=1)

if "data" not in st.session_state or len(st.session_state["data"]) != n:
    st.session_state["data"] = pd.DataFrame({
        "x": [0.0]*n,
        "y": [0.0]*n
    })

st.subheader("Enter values:")

edited_df = st.data_editor(
    st.session_state["data"],
    num_rows="fixed",
    key="editor"
)

if st.button("Save Data"):
    st.session_state["data"] = edited_df
    st.write("Data Saved")
# Extract values
x = edited_df["x"].to_numpy()
y = edited_df["y"].to_numpy()
st.write("Input Desired Range for Graphing")
x_min = st.number_input("X Minimum Value", value=0.0)
x_max = st.number_input("X Maximum Value", value=10.0)
y_min = st.number_input("Y Minimum Value", value=0.0)
y_max = st.number_input("Y Maximum Value", value=10.0)
if st.button("Plot Data Points"):

    fig, ax = plt.subplots()
    ax.scatter(x, y, label="Data")
    ax.axhline(0, color="black", linewidth=1)
    ax.axvline(0, color="black", linewidth=1)
    ax.grid(True, linestyle="--", alpha=0.5)
    plt.title("Inputted Data Points")
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.legend()
    st.pyplot(fig)

st.subheader("Choose Model Terms")

st.markdown("""
Select which functions to include in your model.

Each selected term becomes a column in the design matrix $A$.
""")

terms = st.multiselect(
    "Select model terms:",
    ["1", "x", "x^2", "x^3", "x^0.5", "sin(x)", "cos(x)", "log(x)"],
    default=["1", "x"]  # optional default (linear model)
)

A = np.column_stack([feature_map[t](x) for t in terms])
B = (np.array(y)).reshape(-1,1)
def to_latex_matrix(M):
    rows = []
    for row in M:
        rows.append(" & ".join(f"{val:.3f}" for val in row))
    return r"\begin{bmatrix}" + " \\\\ ".join(rows) + r"\end{bmatrix}"
def symbolic_beta(terms):
    rows = []
    for i, term in enumerate(terms):
        rows.append(f"\\beta_{{{i}}}")
    return r"\begin{bmatrix}" + r" \\ ".join(rows) + r"\end{bmatrix}"
if st.button("Show Matricies"):
    st.subheader("Matrix Formulation")

    st.markdown("""
    We construct the system:

    $A x = b$

    - $A$ = design matrix (built from your selected terms)
    - $x$ = coefficients we are solving for
    - $b$ = observed output values
    """)
    Ahat = A.T @ A
    Bhat = A.T @ B
    Xhat = np.linalg.solve(Ahat, Bhat)
    st.latex(f"A = {to_latex_matrix(A)}")
    st.latex(f"b = {to_latex_matrix(B)}")
    st.latex(f"x = {symbolic_beta(terms)}")
    st.markdown("""
    ### No exact solution?

    When $Ax = b$ has no solution (which happens when the system is **overdetermined**),
    we find the vector $\\hat{x}$ that best fits the data.

    This is done by solving the **normal equations**:
    """)

    st.latex(r"A^T A \hat{x} = A^T b")

    st.markdown("""
    This minimizes the squared error between the predicted values and the actual data. Solving this system gets:
    """)
    st.latex(rf"\hat{{x}} = {to_latex_matrix(Xhat)}")
    st.markdown("""
    Now we can plot the fitted curve from the least squares solution $\\hat{x}$ 
    along with the original data points:
    """)    
    xaxis = np.linspace(x_min, x_max, 500)
    equation = np.zeros(len(xaxis))
    for i, term in enumerate(terms):
        equation += Xhat[i] * feature_map[term](xaxis)
    fig, ax = plt.subplots()
    ax.scatter(x, y, label="Data")
    ax.plot(xaxis, equation, label="Fit")
    ax.axhline(0, color="black", linewidth=1)
    ax.axvline(0, color="black", linewidth=1)
    ax.grid(True, linestyle="--", alpha=0.5)
    plt.title("Fitted Curve with Data Points")
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.legend()
    st.pyplot(fig)