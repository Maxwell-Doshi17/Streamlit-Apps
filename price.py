import matplotlib.pyplot as plt
import numpy as np
import math
from scipy.stats import norm
import streamlit as st

st.title("Simple Securities Valuation Interface")
tabs = st.tabs(["Stock", "Bond", "Future", "European Option"])

def bond_price(face_value, coupon_rate, ttm, market_rate, n_periods=1):
    periods = int(round(ttm * n_periods))
    coupon = face_value * (coupon_rate / n_periods)
    r = market_rate / n_periods
    total_coupons = 0
    for i in range(1, periods + 1):
        current = coupon / ((1 + r)**i)
        total_coupons += current
    pvfv = face_value / ((1 + r)**periods)
    price = total_coupons + pvfv
    if price > face_value:
        type = "Premium"
    elif price < face_value:
        type = "Discount"
    else:
        type = "Par"
    return price, type

# get yield-to-maturity from price
def solve_ytm(price, face, coupon_rate, ttm, n_periods=1):
    low = 0.0001
    high = 1.0
    for x in range(100):
        mid = (low + high) / 2
        val, _ = bond_price(face, coupon_rate, ttm, mid, n_periods)
        if val > price:
            low = mid
        else:
            high = mid
    return mid

def bond_to_ytm_plot(face, coupon, ttm, n_periods=1):
    price_vals = np.linspace(200,1600,100)
    ytms = []
    for price in price_vals:
        ytm = solve_ytm(price, face, coupon, ttm, n_periods)
        ytms.append(ytm)
    fig10, ax10 = plt.subplots()
    ax10.plot(ytms, price_vals)
    ax10.set_xlabel("Yield-to-Maturity")
    ax10.set_ylim(0, max(price_vals))
    ax10.grid()
    ax10.set_xlim(0, max(ytms))
    ax10.set_title("Bond vs Yield-to-Maturity")
    ax10.set_ylabel("Price")
    st.pyplot(fig10)


# Stock valuation model using ggm/ddm
# g = 0 for no growth
def ggm(dividend, discount_rate, growth_rate):
    total = dividend*(1+growth_rate) / (discount_rate - growth_rate)
    return total


# futures financial asset valuation
def futures(spot, rfr, annual_dividend, Tf):
    q = annual_dividend / spot
    value = spot * (np.exp((rfr-q)*Tf))
    return value

# european options
def black_scholes_merton(S, K, T, r, sigma, option_type="call"):
    if S <= 0 or K <= 0 or T <= 0 or sigma <= 0:
        raise ValueError("S, K, T, and sigma must be positive numbers.")
    if option_type not in ("call", "put"):
        raise ValueError("option_type must be 'call' or 'put'.")
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if option_type == "call":
        price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    else:  # put
        price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return price

def greeks(S, K, T, r, sigma, option_type="call"):
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    pdf = norm.pdf(d1)
    if option_type == "call":
        delta = norm.cdf(d1)
        theta = -(S * pdf * sigma) / (2 * math.sqrt(T)) - r * K * math.exp(-r*T) * norm.cdf(d2)
        rho = K * T * math.exp(-r*T) * norm.cdf(d2)
    elif option_type == "put":
        delta = norm.cdf(d1) - 1
        rho = -K * T * math.exp(-r*T) * norm.cdf(-d2)
        theta = -(S * pdf * sigma) / (2 * math.sqrt(T)) + r * K * math.exp(-r*T) * norm.cdf(-d2)
    gamma = pdf / (S * sigma * math.sqrt(T))
    vega = S * pdf * math.sqrt(T)
    return delta, gamma, vega, theta, rho

with tabs[0]:
    st.markdown("""Stock valuation using the Gordon Growth Model: """)
    st.latex(r"P_0 = \frac{D_1}{r - g} = \frac{D_0(1+g)}{r - g}")
    st.markdown("""This model assumes a constant growth rate and discount rate.
                The discount rate must be larger than the growth rate. 
                A growth rate of 0 follows the general Dividend Discount Model: """)
    st.latex(r"P_0 = \sum_{t=1}^{\infty} \frac{D_t}{(1+r)^t}")
    dividend = st.number_input("Dividend", value=1.00, step=0.50)
    discount_rate = st.number_input("Discount Rate", value=0.07, step=0.01)
    growth_rate = st.number_input("Growth Rate", value=0.03, step=0.01)
    if not discount_rate > growth_rate:
        st.error("Discount Rate must be larger than Growth Rate")
    dividends_list = np.linspace(0, 50, 100)
    discounts_list = np.linspace(growth_rate + 0.001, 0.15, 100)
    growths_list = np.linspace(0, (discount_rate - 0.001), 100)
    if st.button("Calculate", key="stockbutton"):
        stockprice = ggm(dividend, discount_rate, growth_rate)
        st.metric("Stock Valuation", f"${stockprice:,.2f}")
        stockprices1 = ggm(dividend, discounts_list, growth_rate)
        stockprices2 = ggm(dividend, discount_rate, growths_list)
        stockprices3 = ggm(dividends_list, discount_rate, growth_rate)
        fig1, ax1 = plt.subplots()
        ax1.plot(discounts_list, stockprices1)
        ax1.set_title("Stock Valuation vs Discount Rate (Holding Growth/Dividend Constant)")
        ax1.set_xlabel("Discount Rate")
        ax1.set_ylabel("Stock Valuation")
        ax1.set_ylim(0, None)
        ax1.grid()
        st.pyplot(fig1)
        fig2, ax2 = plt.subplots()
        ax2.plot(growths_list, stockprices2)
        ax2.set_title("Stock Valuation vs Growth Rate (Holding Dividend/Discount Rate Constant)")
        ax2.set_xlabel("Growth Rate")
        ax2.set_ylabel("Stock Valuation")
        ax2.set_xlim(0, None)
        ax2.set_ylim(0, None)
        ax2.grid()
        st.pyplot(fig2)
        fig3, ax3 = plt.subplots()
        ax3.plot(dividends_list, stockprices3)
        ax3.set_title("Stock Valuation vs Dividend (Holding Discount/Growth Rates Constant)")
        ax3.set_xlabel("Dividend")
        ax3.set_ylabel("Stock Valuation")
        ax3.grid()
        ax3.set_xlim(0, None)
        ax3.set_ylim(0, None)
        st.pyplot(fig3)
with tabs[1]: 
    st.markdown("""Bond valuation using Discounted Cash Flow: """)
    st.latex(r"P = \sum_{t=1}^{N} \frac{F \cdot \frac{c}{n}}{\left(1+\frac{y}{n}\right)^t} + \frac{F}{\left(1+\frac{y}{n}\right)^N}")
    st.markdown("""
This model applies discounted cash flow (DCF) valuation, where a bond’s price equals the present value of its coupon payments and face value, discounted at the yield to maturity.
""")
    face_value = st.number_input("Face Value", value = 1000, step= 50)
    coupon_rate = st.number_input("Coupon Rate", value = 0.05, step = 0.005)
    ttm = st.number_input("Time to Maturity (years)", value = 5.0, step = 1.0, key="ttmbond")
    market_rate = st.number_input("Market Rate", value = 0.06, step = 0.005)
    n_periods = st.selectbox("Payment Frequency", [1, 2, 4], index=1)
    if st.button("Calculate", key="bondbutton"):
        bondprice, bond_type = bond_price(face_value, coupon_rate, ttm, market_rate, n_periods)
        st.metric("Bond Valuation", f"${bondprice:,.2f}")
        st.metric("Bond Type", bond_type)
        bond_to_ytm_plot(face_value, coupon_rate, ttm, n_periods=1)


with tabs[2]:
    st.markdown("""Futures Valuation using Cost-of-Carry Model: """)
    st.latex(r"F_0 = S_0 e^{(r - q)T}")
    st.markdown("""
This model applies the no-arbitrage principle to price futures on financial assets, assuming dividends are paid continuously as a yield.
""")
    spot = st.number_input("Spot Price", value = 100.0, step = 5.0, key="spotfuture")
    rfr = st.number_input("Risk-Free Rate", value = 0.05, step = 0.005, key="rfrfuture")
    annual_dividend = st.number_input("Annual Dividend", value = 2.0, step = 0.5)
    Tf = st.number_input("Time to Maturity (Years)", value = 1.0, step = 0.25, key="ttmfuture")
    T_vals = np.linspace(0.1, 10, 100)
    if st.button("Calculate", key="futuresbutton"):
        valuation_future = futures(spot, rfr, annual_dividend, Tf)
        st.metric("Futures Valuation", f"${valuation_future:,.2f}")
        futures_vals = futures(spot, rfr, annual_dividend, T_vals)
        fig20, ax20 = plt.subplots()
        ax20.set_xlabel("Time to Maturity (Years)")
        ax20.set_ylabel("Futures Price")
        ax20.set_title("Futures Price vs Time to Maturity")
        ax20.grid()
        ax20.plot(T_vals, futures_vals) 
        st.pyplot(fig20)





with tabs[3]:
    st.markdown("""European Option Valuation using the Black-Scholes-Merton Model: """)
    st.latex(r"C = S_0 N(d_1) - K e^{-rT} N(d_2)")
    st.latex(r"P = K e^{-rT} N(-d_2) - S_0 N(-d_1)")
    st.latex(r"d_1 = \frac{\ln(S_0/K) + (r + \frac{1}{2}\sigma^2)T}{\sigma\sqrt{T}}")
    st.latex(r"d_2 = d_1 - \sigma\sqrt{T}")
    st.markdown("""The Black-Scholes-Merton model prices European options by discounting the expected payoff under a risk-neutral probability framework.
                The model follows these asusmptions:
                \n- No arbitrage
                \n- Constant volatility
                \n- Constant interest rate
                \n- Lognormal stock prices
                \n- No dividends
                \n- European exercise only""")
    S = st.number_input("Spot Price", value=100.0, step=5.0, key="spotoption")
    K = st.number_input("Strike Price", value=100.0, step=5.0)
    T = st.number_input("Time to Maturity (Years)", value=1.0, step=0.25, key="ttmoption")
    r = st.number_input("Risk-Free Rate", value= 0.05, step=0.005, key="rfroption")
    sigma = st.number_input("Volatility", value= 0.20, step=0.01)
    option_type = st.selectbox("Option Type",["call", "put"])
    S_vals = np.linspace(0.5*K, 1.5*K, 200)
    T_vals = np.linspace(0.01, 2, 200)
    sigmas = np.linspace(0.01, 1.0, 200)
    if st.button("Calculate", key="Optionbutton"):
        bsmvalue = black_scholes_merton(S, K, T, r, sigma, option_type)
        delta, gamma, vega, theta, rho = greeks(S, K, T, r, sigma, option_type)
        st.metric("Option Valuation", f"${bsmvalue:,.2f}")
        st.latex(r"\Delta_{call} = N(d_1), \quad \Delta_{put} = N(d_1) - 1")
        st.metric("Delta", f"{delta:,.4f}")
        st.latex(r"\Gamma = \frac{N'(d_1)}{S_0 \sigma \sqrt{T}}")
        st.metric("Gamma", f"{gamma:,.6f}")
        st.latex(r"\text{Vega} = S_0 \sqrt{T} \cdot N'(d_1)")
        st.metric("Vega", f"{vega:,.4f}")
        st.latex(r"\Theta_{call} = -\frac{S_0 N'(d_1)\sigma}{2\sqrt{T}} - rK e^{-rT} N(d_2)")
        st.latex(r"\Theta_{put} = -\frac{S_0 N'(d_1)\sigma}{2\sqrt{T}} + rK e^{-rT} N(-d_2)")
        st.metric("Theta", f"{theta:,.4f}")
        st.latex(r"\rho_{call} = K T e^{-rT} N(d_2)")
        st.latex(r"\rho_{put} = -K T e^{-rT} N(-d_2)")
        st.metric("Rho", f"{rho:,.4f}")
        g1options_prices = [black_scholes_merton(s, K, T, r, sigma, option_type) for s in S_vals]
        fig15, ax15 = plt.subplots()
        ax15.plot(S_vals, g1options_prices)
        ax15.set_title("Option Price vs Stock Price")
        ax15.set_xlabel("Stock Price")
        ax15.set_ylabel("Option Price")
        ax15.grid()
        st.pyplot(fig15)
        g2options_prices = [black_scholes_merton(S, K, t, r, sigma, option_type) for t in T_vals]
        fig16, ax16 = plt.subplots()
        ax16.plot(T_vals, g2options_prices)
        ax16.set_title("Option Price vs Time to Maturity")
        ax16.set_xlabel("Time to Maturity (Years)")
        ax16.set_ylabel("Option Price")
        ax16.grid()
        st.pyplot(fig16)
        g3options_prices = [black_scholes_merton(S, K, T, r, s, option_type) for s in sigmas]
        fig17, ax17 = plt.subplots()
        ax17.plot(sigmas, g3options_prices)
        ax17.set_title("Option Price vs Volatility")
        ax17.set_xlabel("Volatility")
        ax17.set_ylabel("Option Price")
        ax17.grid()
        st.pyplot(fig17)