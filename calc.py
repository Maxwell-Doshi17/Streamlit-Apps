import streamlit as st
import numpy as np
import sympy as sp
import plotly.graph_objects as go
from scipy.integrate import quad

x = sp.symbols('x')

st.title("Calculus \"Disk Method\" Visualizer")
st.latex(r"V = \int_a^b dV = \int_a^b \pi [f(x)]^2 \, dx")
st.markdown("""The disk method calculates the volume of a solid of revolution 
            by integrating the area of circular cross-sections perpendicular 
            to the axis of rotation.""")
# Function selection
func_option = st.selectbox("Choose a function", ["x", "x^2", "x^3", "cos(x)", "sin(x)", "tan(x)", 
                                                 "csc(x)", "cot(x)", "sec(x)", "sqrt(x)",
                                                 "1/x", "1/(x^2)", "e^x", "e^-x"])

func_map = {
    "x" : x,
    "x^2": x**2,
    "x^3" : x**3,
    "cos(x)" : sp.cos(x),
    "csc(x)" : sp.csc(x),
    "1/x" : 1/x,
    "1/(x^2)" : 1/(x**2),
    "e^x" : sp.exp(x),
    "e^-x": sp.exp(-x),
    "sec(x)" : sp.sec(x),
    "cot(x)" : sp.cot(x),
    "sin(x)": sp.sin(x),
    "tan(x)" : sp.tan(x),
    "sqrt(x)": sp.sqrt(x)
}

f = func_map[func_option]

# Inputs
a, b = st.slider("Interval [a, b]", 0.0, 5.0, (0.0, 2.0))
resolution = st.slider("Resolution", 20, 100, 50)

# Convert to numeric
f_lamb = sp.lambdify(x, f, "numpy")

# Volume calculation
volume, _ = quad(lambda t: np.pi * (f_lamb(t)**2), a, b)

st.subheader(f"Volume ≈ {volume:.4f}")

x_vals = np.linspace(a, b, 200)
y_vals = f_lamb(x_vals)

fig2d = go.Figure()
fig2d.add_trace(go.Scatter(x=x_vals, y=y_vals, name="f(x)"))

st.plotly_chart(fig2d)

theta = np.linspace(0, 2*np.pi, resolution)
x_vals = np.linspace(a, b, resolution)

X, Theta = np.meshgrid(x_vals, theta)
Y = f_lamb(X) * np.cos(Theta)
Z = f_lamb(X) * np.sin(Theta)

fig3d = go.Figure(data=[
    go.Surface(x=X, y=Y, z=Z)
])

fig3d.update_layout(title="3D Solid of Revolution")

st.plotly_chart(fig3d)