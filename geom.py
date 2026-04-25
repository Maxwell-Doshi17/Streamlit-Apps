import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
def midpoint(P, Q):
    return (P + Q) / 2
def line_intersection(P1, d1, P2, d2):
    # Solve P1 + t*d1 = P2 + s*d2
    A_mat = np.array([d1, -d2]).T
    b = P2 - P1
    t, s = np.linalg.solve(A_mat, b)
    return P1 + t * d1
def foot_of_perpendicular(P, Q, R):
    # foot from P to line QR
    QR = R - Q
    t = np.dot(P - Q, QR) / np.dot(QR, QR)
    return Q + t * QR
def circle_from_3_points(P1, P2, P3):
    temp = P2 - P1
    temp2 = P3 - P1
    A_mat = np.array([
        [temp[0], temp[1]],
        [temp2[0], temp2[1]]
    ])
    b = np.array([
        np.dot(temp, temp) / 2,
        np.dot(temp2, temp2) / 2
    ])
    center = np.linalg.solve(A_mat, b) + P1
    radius = np.linalg.norm(center - P1)
    return center, radius

st.title("Nine-Point Circle Visualization")

st.subheader("Nine-Point Circle: Key Geometry")

st.markdown("""
### Midpoint Formula
""")
st.latex(r"M = \left(\frac{x_1 + x_2}{2}, \frac{y_1 + y_2}{2}\right)")
st.markdown("The midpoint is the average of the x- and y-coordinates of two points.")


st.markdown("""
### Foot of a Perpendicular (Projection)
""")
st.latex(r"F = Q + \frac{(P - Q)\cdot (R - Q)}{(R - Q)\cdot (R - Q)} (R - Q)")
st.markdown("""
This finds the foot of the perpendicular from point $P$ onto the line through $Q$ and $R$.  
It works by projecting one vector onto another.
""")

st.markdown("""
### Perpendicular Direction
""")
st.latex(r"\text{If } (x, y) \rightarrow (-y, x)")
st.markdown("Swapping components and negating one gives a perpendicular direction vector.")


st.markdown("""
### Line Intersection (Altitudes → Orthocenter)
""")
st.latex(r"P_1 + t\vec{d}_1 = P_2 + s\vec{d}_2")
st.markdown("""
This represents two lines. Solving for $t$ and $s$ gives their intersection point, 
which is used to find the orthocenter.
""")

st.markdown("""
### Midpoints to Orthocenter
""")
st.latex(r"N_A = \frac{A + H}{2}")
st.markdown("These are midpoints between each vertex and the orthocenter.")

st.markdown("""
### Nine-Point Circle Center
""")
st.latex(r"N = \frac{O + H}{2}")
st.markdown("""
The nine-point center lies halfway between the circumcenter ($O$) and orthocenter ($H$).
""")
st.markdown("""
### Radius Relationship
""")
st.latex(r"r_9 = \frac{R}{2}")
st.markdown("The nine-point circle has half the radius of the circumcircle.")






vertex1_x = st.number_input("Vertex 1 X-Value", value = 0)
vertex1_y = st.number_input("Vertex 1 Y-Value", value = 0)
vertex2_x = st.number_input("Vertex 2 X-Value", value = 6)
vertex2_y = st.number_input("Vertex 2 Y-Value", value = 1)
vertex3_x = st.number_input("Vertex 3 X-Value", value = 2)
vertex3_y = st.number_input("Vertex 3 Y-Value", value = 5)

if st.button("Generate"):
    A = np.array([vertex1_x, vertex1_y])
    B = np.array([vertex2_x, vertex2_y])
    C = np.array([vertex3_x, vertex3_y])
    M_AB = midpoint(A, B)
    M_BC = midpoint(B, C)
    M_CA = midpoint(C, A)
    d_BC = C - B
    alt_A_dir = np.array([-d_BC[1], d_BC[0]])
    d_AC = C - A
    alt_B_dir = np.array([-d_AC[1], d_AC[0]])
    H = line_intersection(A, alt_A_dir, B, alt_B_dir)
    F_A = foot_of_perpendicular(A, B, C)
    F_B = foot_of_perpendicular(B, A, C)
    F_C = foot_of_perpendicular(C, A, B)
    N_A = midpoint(A, H)
    N_B = midpoint(B, H)
    N_C = midpoint(C, H)
    points = [M_AB, M_BC, M_CA, F_A, F_B, F_C, N_A, N_B, N_C]
    points_midpoint1 = [M_AB, M_BC, M_CA]
    points_feet = [F_A, F_B, F_C]
    points_midpoint2 = [N_A, N_B, N_C] 
    center, radius = circle_from_3_points(M_AB, M_BC, M_CA)
    theta = np.linspace(0, 2*np.pi, 200)
    circle_x = center[0] + radius * np.cos(theta)
    circle_y = center[1] + radius * np.sin(theta)
    fig, ax = plt.subplots(figsize=(6,6))
    ax.plot([A[0], B[0], C[0], A[0]],
         [A[1], B[1], C[1], A[1]], 'k-')
    ax.plot(circle_x, circle_y, 'b--', label="Nine-Point Circle")
    for i, p_m in enumerate(points_midpoint1):
        ax.scatter(p_m[0], p_m[1], color='red',
                label="Midpoints of Sides" if i == 0 else "")

    for i, p_o in enumerate(points_midpoint2):
        ax.scatter(p_o[0], p_o[1], color="green",
                label="Midpoints (Vertex–Orthocenter)" if i == 0 else "")

    for i, p_f in enumerate(points_feet):
        ax.scatter(p_f[0], p_f[1], color="black",
                label="Feet of Altitudes" if i == 0 else "")
    ax.scatter(H[0], H[1], color='blue', label="Orthocenter")
    ax.set_aspect('equal')    
    ax.legend(fontsize="8")
    ax.set_title("Nine-Point Circle Demonstration")
    st.pyplot(fig)