import streamlit as st
import numpy as np
import sympy as sp
import plotly.graph_objects as go



x = sp.symbols('x')

def taylor_series(func, a, n):
    series = 0
    for i in range(n+1):
        term = (func.diff(x, i).subs(x, a) / sp.factorial(i)) * (x - a)**i
        series += term
    return sp.simplify(series)

st.title("🧠 Taylor Series Visualizer")

# Function selection
func_option = st.selectbox("Choose a function", ["sin(x)", "cos(x)", "exp(x)", "log(1+x)"])

func_map = {
    "sin(x)": sp.sin(x),
    "cos(x)": sp.cos(x),
    "exp(x)": sp.exp(x),
    "log(1+x)": sp.log(1+x)
}

f = func_map[func_option]

# Inputs
a = st.slider("Expansion point (a)", -2.0, 2.0, 0.0)
n = st.slider("Degree (n)", 1, 10, 3)
x_min, x_max = st.slider("x range", -5.0, 5.0, (-2.0, 2.0))

# Compute Taylor
Tn = taylor_series(f, a, n)

# Convert to numeric functions
f_lamb = sp.lambdify(x, f, "numpy")
Tn_lamb = sp.lambdify(x, Tn, "numpy")

x_vals = np.linspace(x_min, x_max, 400)

y_true = f_lamb(x_vals)
y_approx = Tn_lamb(x_vals)

# Plot
fig = go.Figure()

fig.add_trace(go.Scatter(x=x_vals, y=y_true, name="f(x)"))
fig.add_trace(go.Scatter(x=x_vals, y=y_approx, name=f"Taylor (n={n})"))

st.plotly_chart(fig)

# Error
error = y_true - y_approx

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=x_vals, y=error, name="Error"))

st.subheader("Error Graph")
st.plotly_chart(fig2)

# Show equation
st.subheader("Taylor Polynomial")
st.latex(sp.latex(Tn))