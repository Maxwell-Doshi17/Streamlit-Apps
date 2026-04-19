import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import streamlit as st

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Supply & Demand", layout="wide")

# ── Global style ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap');

html, body, [class*="css"] { font-family: 'DM Mono', monospace; }

h1, h2, h3 { font-family: 'Syne', sans-serif !important; letter-spacing: -1px; }

/* dark background */
.stApp { background: #0f0f0f; color: #e8e8e0; }

/* tab bar */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 2px solid #2a2a2a;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.6rem 1.2rem;
    color: #666;
    border: none;
    background: transparent;
}
.stTabs [aria-selected="true"] {
    color: #c8f564 !important;
    border-bottom: 2px solid #c8f564 !important;
    background: transparent !important;
}

/* sidebar */
section[data-testid="stSidebar"] {
    background: #141414;
    border-right: 1px solid #222;
}
section[data-testid="stSidebar"] * { color: #e8e8e0 !important; }

/* number inputs */
input[type="number"] {
    background: #1a1a1a !important;
    border: 1px solid #333 !important;
    border-radius: 4px !important;
    color: #c8f564 !important;
    font-family: 'DM Mono', monospace !important;
}

/* slider */
.stSlider [data-baseweb="slider"] { margin-top: 0.3rem; }

/* metric cards */
.metric-card {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 6px;
    padding: 0.8rem 1rem;
    margin: 0.3rem 0;
}
.metric-label {
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #666;
    margin-bottom: 0.2rem;
}
.metric-value {
    font-size: 1.15rem;
    font-weight: 500;
    color: #c8f564;
}

/* generate button */
.stButton > button {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    background: #c8f564 !important;
    color: #0f0f0f !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 0.55rem 1.4rem !important;
    font-weight: 500 !important;
    transition: opacity 0.15s !important;
    width: 100%;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* error */
.stAlert { background: #1a1a1a !important; border-color: #ff4455 !important; }

/* equation display */
.eq-box {
    background: #1a1a1a;
    border-left: 3px solid #c8f564;
    padding: 0.5rem 1rem;
    margin: 0.4rem 0;
    font-size: 0.85rem;
    border-radius: 0 4px 4px 0;
    color: #aaa;
}
.eq-box span { color: #c8f564; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# ── Matplotlib dark theme ─────────────────────────────────────────────────────
mpl.rcParams.update({
    "figure.facecolor": "#0f0f0f",
    "axes.facecolor":   "#141414",
    "axes.edgecolor":   "#333",
    "axes.labelcolor":  "#aaa",
    "xtick.color":      "#555",
    "ytick.color":      "#555",
    "text.color":       "#e8e8e0",
    "legend.facecolor": "#1a1a1a",
    "legend.edgecolor": "#333",
    "legend.fontsize":  8,
    "grid.color":       "#222",
    "grid.linestyle":   "--",
    "grid.alpha":       0.5,
})

COLORS = {
    "demand":   "#ff4455",
    "supply":   "#4488ff",
    "cs":       "#4488ff",
    "ps":       "#44cc88",
    "dwl":      "#ff4455",
    "gov":      "#f5d040",
    "line":     "#c8f564",
    "world":    "#aa88ff",
    "tariff":   "#ff8844",
}

# ── Shared sidebar controls ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='margin-bottom:0.2rem'> Parameters</h2>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("**Demand curve**")
    c1, c2 = st.columns(2)
    with c1: d_slope = st.number_input("Slope", value=-1.0, key="ds", step=0.5)
    with c2: d_int   = st.number_input("Intercept", value=10.0, key="di", step=1.0)

    st.markdown("**Supply curve**")
    c1, c2 = st.columns(2)
    with c1: s_slope = st.number_input("Slope", value=1.0, key="ss", step=0.5)
    with c2: s_int   = st.number_input("Intercept", value=0.0, key="si", step=1.0)

    xrange = st.slider("X axis range", 1, 30, 12)

    # live equation preview
    st.markdown("---")
    st.markdown(f"""
    <div class='eq-box'>P<sub>D</sub> = <span>{d_slope:+g}</span> · Q {'+' if d_int >= 0 else ''} <span>{d_int:g}</span></div>
    <div class='eq-box'>P<sub>S</sub> = <span>{s_slope:+g}</span> · Q {'+' if s_int >= 0 else ''} <span>{s_int:g}</span></div>
    """, unsafe_allow_html=True)

    # equilibrium preview
    denom = d_slope - s_slope
    if denom != 0:
        eq_q = (s_int - d_int) / denom
        eq_p = s_slope * eq_q + s_int
        if eq_q > 0 and eq_p > 0:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Equilibrium</div>
                <div class='metric-value'>Q = {eq_q:.2f} &nbsp;|&nbsp; P = {eq_p:.2f}</div>
            </div>""", unsafe_allow_html=True)

# ── Plotting helper ───────────────────────────────────────────────────────────
def base_plot(xrange, s_slope, d_slope, s_int, d_int):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    quantity = np.linspace(0, xrange, 600)
    price_S  = s_slope * quantity + s_int
    price_D  = d_slope * quantity + d_int
    ax.plot(quantity, price_D, color=COLORS["demand"], lw=2, label="Demand")
    ax.plot(quantity, price_S, color=COLORS["supply"], lw=2, label="Supply")
    ax.set_xlabel("Quantity", fontsize=9)
    ax.set_ylabel("Price",    fontsize=9)
    ax.set_xlim(0, xrange)
    ax.set_ylim(0, None)
    ax.grid(True)
    eq_q = (s_int - d_int) / (d_slope - s_slope)
    eq_p = s_slope * eq_q + s_int
    return fig, ax, quantity, price_S, price_D, eq_q, eq_p

def show_metrics(**kwargs):
    cols = st.columns(len(kwargs))
    for col, (label, val) in zip(cols, kwargs.items()):
        with col:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>{label}</div>
                <div class='metric-value'>{val:.2f}</div>
            </div>""", unsafe_allow_html=True)

def validate_base(s_slope, d_slope, s_int, d_int):
    denom = d_slope - s_slope
    if denom == 0:
        return None, None, "Supply and demand slopes cannot be equal."
    eq_q = (s_int - d_int) / denom
    eq_p = s_slope * eq_q + s_int
    if eq_q <= 0 or eq_p <= 0:
        return None, None, "Equilibrium must be in positive quantity and price space."
    return eq_q, eq_p, None

# ── Title ─────────────────────────────────────────────────────────────────────
st.markdown("<h1 style='margin-bottom:0'>Supply & Demand</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#555;font-size:0.8rem;margin-top:0'>Interactive economics visualizer</p>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tabs = st.tabs(["Autarky", "Price Ceiling", "Price Floor", "Imports", "Exports", "Tariff"])

# ─────────────────────────── TAB 0 — AUTARKY ─────────────────────────────────
with tabs[0]:
    if st.button("Generate", key="btn0"):
        eq_q, eq_p, err = validate_base(s_slope, d_slope, s_int, d_int)
        if err:
            st.error(err)
        else:
            fig, ax, qty, pS, pD, eq_q, eq_p = base_plot(xrange, s_slope, d_slope, s_int, d_int)
            ax.set_title("Autarky", fontsize=11, pad=10)
            ax.plot([eq_q, eq_q], [0, eq_p], color="#555", linestyle="--", lw=1)
            ax.plot([0,    eq_q], [eq_p, eq_p], color="#555", linestyle="--", lw=1)
            ax.fill_between(qty, pD, eq_p, where=(pD >= eq_p), color=COLORS["cs"], alpha=0.35, label="Consumer Surplus")
            ax.fill_between(qty, pS, eq_p, where=(pS <= eq_p), color=COLORS["ps"], alpha=0.35, label="Producer Surplus")
            ax.legend()
            st.pyplot(fig)
            plt.close(fig)
            cs = (d_int - eq_p) * eq_q * 0.5
            ps = (eq_p - s_int) * eq_q * 0.5
            show_metrics(**{"Consumer Surplus": cs, "Producer Surplus": ps, "Total Gains": cs + ps})

# ─────────────────────────── TAB 1 — PRICE CEILING ───────────────────────────
with tabs[1]:
    ceil_val = st.number_input("Price Ceiling (must be below equilibrium)", value=4.0, step=0.5, key="ceil")
    if st.button("Generate", key="btn1"):
        eq_q, eq_p, err = validate_base(s_slope, d_slope, s_int, d_int)
        if err:
            st.error(err)
        elif ceil_val >= eq_p:
            st.error(f"Ceiling ({ceil_val}) must be below equilibrium price ({eq_p:.2f}).")
        else:
            fig, ax, qty, pS, pD, eq_q, eq_p = base_plot(xrange, s_slope, d_slope, s_int, d_int)
            ax.set_title("Price Ceiling", fontsize=11, pad=10)
            ceil_supply = (ceil_val - s_int) / s_slope
            ceil_demand = (ceil_val - d_int) / d_slope
            shortage_Q  = d_slope * ceil_supply + d_int

            ax.axhline(y=ceil_val, color=COLORS["line"], lw=1.5, linestyle="-", label="Price Ceiling")
            ax.axvline(x=ceil_supply, color="#555", linestyle="--", lw=1)
            ax.axvline(x=ceil_demand, color="#555", linestyle="--", lw=1)

            ax.fill_between(qty[qty <= ceil_supply], pS[qty <= ceil_supply], ceil_val, color=COLORS["ps"], alpha=0.4, label="Producer Surplus")
            ax.fill_between(qty[qty <= ceil_supply], pD[qty <= ceil_supply], ceil_val, color=COLORS["cs"], alpha=0.4, label="Consumer Surplus")
            ax.fill_between(qty, pS, pD, where=(pD >= pS) & (qty >= ceil_supply), color=COLORS["dwl"], alpha=0.25, label="DWL")
            ax.legend()
            st.pyplot(fig)
            plt.close(fig)

            ps  = (ceil_val - s_int) * ceil_supply * 0.5
            cs  = ((shortage_Q - ceil_val) * ceil_supply) + ((d_int - shortage_Q) * ceil_supply * 0.5)
            dwl = (shortage_Q - ceil_val) * (eq_q - ceil_supply) * 0.5
            show_metrics(**{"Consumer Surplus": cs, "Producer Surplus": ps,
                            "Total Gains": cs + ps, "Shortage": ceil_demand - ceil_supply, "DWL": dwl})

# ─────────────────────────── TAB 2 — PRICE FLOOR ─────────────────────────────
with tabs[2]:
    floor_val = st.number_input("Price Floor (must be above equilibrium)", value=6.0, step=0.5, key="floor")
    if st.button("Generate", key="btn2"):
        eq_q, eq_p, err = validate_base(s_slope, d_slope, s_int, d_int)
        if err:
            st.error(err)
        elif floor_val <= eq_p:
            st.error(f"Floor ({floor_val}) must be above equilibrium price ({eq_p:.2f}).")
        else:
            fig, ax, qty, pS, pD, eq_q, eq_p = base_plot(xrange, s_slope, d_slope, s_int, d_int)
            ax.set_title("Price Floor", fontsize=11, pad=10)
            floor_supply = (floor_val - s_int) / s_slope
            floor_demand = (floor_val - d_int) / d_slope
            surplus_Q    = s_slope * floor_demand + s_int

            ax.axhline(y=floor_val, color=COLORS["line"], lw=1.5, linestyle="-", label="Price Floor")
            ax.axvline(x=floor_supply, color="#555", linestyle="--", lw=1)
            ax.axvline(x=floor_demand, color="#555", linestyle="--", lw=1)

            ax.fill_between(qty[qty <= floor_demand], pD[qty <= floor_demand], floor_val, color=COLORS["cs"], alpha=0.4, label="Consumer Surplus")
            ax.fill_between(qty[qty <= floor_demand], pS[qty <= floor_demand], floor_val, color=COLORS["ps"], alpha=0.4, label="Producer Surplus")
            ax.fill_between(qty, pS, pD, where=(pD >= pS) & (qty >= floor_demand), color=COLORS["dwl"], alpha=0.25, label="DWL")
            ax.legend()
            st.pyplot(fig)
            plt.close(fig)

            cs  = (d_int - floor_val) * floor_demand * 0.5
            ps  = ((floor_val - surplus_Q) * floor_demand) + ((surplus_Q - s_int) * floor_demand * 0.5)
            dwl = (floor_val - surplus_Q) * (eq_q - floor_demand) * 0.5
            show_metrics(**{"Consumer Surplus": cs, "Producer Surplus": ps,
                            "Total Gains": cs + ps, "Surplus": floor_supply - floor_demand, "DWL": dwl})

# ─────────────────────────── TAB 3 — IMPORTS ─────────────────────────────────
with tabs[3]:
    world_val = st.number_input("World Price (must be below equilibrium)", value=3.0, step=0.5, key="world_imp")
    if st.button("Generate", key="btn3"):
        eq_q, eq_p, err = validate_base(s_slope, d_slope, s_int, d_int)
        if err:
            st.error(err)
        elif world_val >= eq_p:
            st.error(f"World price ({world_val}) must be below equilibrium ({eq_p:.2f}) to generate imports.")
        else:
            fig, ax, qty, pS, pD, eq_q, eq_p = base_plot(xrange, s_slope, d_slope, s_int, d_int)
            ax.set_title("Trade with Imports", fontsize=11, pad=10)
            imp_demand = (world_val - d_int) / d_slope
            imp_supply = (world_val - s_int) / s_slope

            ax.axhline(y=world_val, color=COLORS["world"], lw=1.5, linestyle="-", label="World Price")
            ax.fill_between(qty, pD, world_val, where=(pD >= world_val), color=COLORS["cs"], alpha=0.4, label="Consumer Surplus")
            ax.fill_between(qty, pS, world_val, where=(pS <= world_val), color=COLORS["ps"], alpha=0.4, label="Producer Surplus")
            ax.legend()
            st.pyplot(fig)
            plt.close(fig)

            cs = (d_int - world_val) * imp_demand * 0.5
            ps = (world_val - s_int) * imp_supply * 0.5
            show_metrics(**{"Consumer Surplus": cs, "Producer Surplus": ps,
                            "Total Gains": cs + ps, "Amount Imported": imp_demand - imp_supply})

# ─────────────────────────── TAB 4 — EXPORTS ─────────────────────────────────
with tabs[4]:
    world_exp = st.number_input("World Price (must be above equilibrium)", value=7.0, step=0.5, key="world_exp")
    if st.button("Generate", key="btn4"):
        eq_q, eq_p, err = validate_base(s_slope, d_slope, s_int, d_int)
        if err:
            st.error(err)
        elif world_exp <= eq_p:
            st.error(f"World price ({world_exp}) must be above equilibrium ({eq_p:.2f}) to generate exports.")
        else:
            fig, ax, qty, pS, pD, eq_q, eq_p = base_plot(xrange, s_slope, d_slope, s_int, d_int)
            ax.set_title("Trade with Exports", fontsize=11, pad=10)
            exp_demand = (world_exp - d_int) / d_slope
            exp_supply = (world_exp - s_int) / s_slope

            ax.axhline(y=world_exp, color=COLORS["world"], lw=1.5, linestyle="-", label="World Price")
            ax.fill_between(qty, pD, world_exp, where=(pD >= world_exp), color=COLORS["cs"], alpha=0.4, label="Consumer Surplus")
            ax.fill_between(qty, pS, world_exp, where=(pS <= world_exp), color=COLORS["ps"], alpha=0.4, label="Producer Surplus")
            ax.legend()
            st.pyplot(fig)
            plt.close(fig)

            cs = (d_int - world_exp) * exp_demand * 0.5
            ps = (world_exp - s_int) * exp_supply * 0.5
            show_metrics(**{"Consumer Surplus": cs, "Producer Surplus": ps,
                            "Total Gains": cs + ps, "Amount Exported": exp_supply - exp_demand})

# ─────────────────────────── TAB 5 — TARIFF ──────────────────────────────────
with tabs[5]:
    c1, c2 = st.columns(2)
    with c1: world_tar  = st.number_input("World Price", value=3.0, step=0.5, key="world_tar")
    with c2: tariff_val = st.number_input("Tariff Price (world < tariff < eq)", value=4.5, step=0.5, key="tariff")
    if st.button("Generate", key="btn5"):
        eq_q, eq_p, err = validate_base(s_slope, d_slope, s_int, d_int)
        if err:
            st.error(err)
        elif world_tar >= eq_p:
            st.error(f"World price ({world_tar}) must be below equilibrium ({eq_p:.2f}).")
        elif tariff_val <= world_tar:
            st.error(f"Tariff ({tariff_val}) must be above world price ({world_tar}).")
        elif tariff_val >= eq_p:
            st.error(f"Tariff ({tariff_val}) must be below equilibrium ({eq_p:.2f}).")
        else:
            fig, ax, qty, pS, pD, eq_q, eq_p = base_plot(xrange, s_slope, d_slope, s_int, d_int)
            ax.set_title("Trade with Tariff", fontsize=11, pad=10)

            tar_demand  = (tariff_val - d_int) / d_slope
            tar_supply  = (tariff_val - s_int) / s_slope
            imp_supply  = (world_tar  - s_int) / s_slope
            imp_demand  = (world_tar  - d_int) / d_slope

            ax.axhline(y=world_tar,  color=COLORS["world"],  lw=1.5, linestyle="-",  label="World Price")
            ax.axhline(y=tariff_val, color=COLORS["tariff"], lw=1.5, linestyle="--", label="Tariff")
            for x in [tar_demand, tar_supply, imp_demand, imp_supply]:
                ax.axvline(x=x, color="#333", linestyle="--", lw=0.8)

            ax.fill_between(qty, pD, tariff_val, where=(pD >= tariff_val), color=COLORS["cs"], alpha=0.4, label="Consumer Surplus")
            ax.fill_between(qty, pS, tariff_val, where=(pS <= tariff_val), color=COLORS["ps"], alpha=0.4, label="Producer Surplus")

            mask_gov = (qty >= tar_supply) & (qty <= tar_demand)
            ax.fill_between(qty[mask_gov], world_tar, tariff_val, color=COLORS["gov"], alpha=0.5, label="Gov. Revenue")

            mask_dwl_l = (qty >= imp_supply) & (qty <= tar_supply)
            ax.fill_between(qty[mask_dwl_l], pS[mask_dwl_l], world_tar, color=COLORS["dwl"], alpha=0.3, label="DWL")
            mask_dwl_r = (qty >= tar_demand) & (qty <= imp_demand)
            ax.fill_between(qty[mask_dwl_r], world_tar, pD[mask_dwl_r], color=COLORS["dwl"], alpha=0.3)

            ax.legend()
            st.pyplot(fig)
            plt.close(fig)

            cs      = (d_int - tariff_val) * tar_demand * 0.5
            ps      = (tariff_val - s_int) * tar_supply * 0.5
            ge      = (tariff_val - world_tar) * (tar_demand - tar_supply)
            dwl     = ((tariff_val - world_tar) * (tar_supply - imp_supply) * 0.5 +
                       (tariff_val - world_tar) * (imp_demand - tar_demand) * 0.5)
            show_metrics(**{"Consumer Surplus": cs, "Producer Surplus": ps, "Gov. Revenue": ge,
                            "Total Gains": cs + ps + ge, "DWL": dwl,
                            "Imports": imp_demand - imp_supply})