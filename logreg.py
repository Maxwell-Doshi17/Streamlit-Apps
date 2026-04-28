import pandas as pd
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import roc_curve
from sklearn.metrics import roc_auc_score
import streamlit as st
st.set_page_config(page_title="Logistic Regression")

st.title("Simple Logistic Regression Walkthrough")

st.markdown("""
This walkthrough introduces the basic ideas behind **logistic regression**.

Unlike regular linear regression, logistic regression is used when the response variable is **binary**,
meaning it only has two possible outcomes such as:

- 0 = No
- 1 = Yes

For example, in the default NBA rookie dataset:

- **0** means the player did **not** stay in the NBA for 5 or more years
- **1** means the player **did** stay in the NBA for 5 or more years

You will choose:

- one **quantitative predictor** variable \(X\)
- one **binary response** variable \(Y\)
""")

st.markdown("### Logistic regression model")
st.markdown("The model predicts the probability that \(Y = 1\).")

st.latex(r"\log\left(\frac{p}{1-p}\right) = \beta_0 + \beta_1 x")

st.markdown("""
Where:

- $p$ = probability that the outcome is 1
- $\\frac{p}{1-p}$ = the **odds**
- $\\log\\left(\\frac{p}{1-p}\\right)$ = the **log-odds** or **logit**  
- $\\beta_0$ = intercept
- $\\beta_1$ = slope for the predictor \(x\)
""")

st.markdown("From that, we can solve for the predicted probability:")

st.latex(r"p = \frac{e^{\beta_0 + \beta_1 x}}{1 + e^{\beta_0 + \beta_1 x}}")

st.markdown("""
This is why logistic regression produces an **S-shaped curve** for probability instead of a straight line.
""")

uploaded_file = st.file_uploader("Upload your dataset (CSV)", type=["csv"])

def get_default_data():
    return pd.read_csv("data/nba_rookie.csv")

st.markdown("## Step 1: Load the data")
st.markdown("""
You can either:

- upload your own CSV file, or
- use the included NBA rookie dataset
""")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("Using uploaded dataset")
else:
    df = get_default_data()
    st.info("Using default sample dataset")

st.markdown("### Preview of the dataset")
st.dataframe(df)

st.markdown("### Available columns")
st.write(df.columns.tolist())

st.markdown("## Step 2: Choose the predictor and response variables")
st.markdown("""
Choose:

- **X** = your explanatory / predictor variable  
- **Y** = your binary target variable

For logistic regression, **Y must have exactly 2 unique values**.
""")

x_col = st.selectbox("Select X (feature - must be quantitative)", df.columns)
y_col = st.selectbox("Select Y (target - must be binary)", df.columns)

x = df[[x_col]]
y = df[y_col]

df["x"] = df[x_col]
df["y"] = df[y_col]

st.markdown("### Selected variables")
st.write(f"**X variable:** {x_col}")
st.write(f"**Y variable:** {y_col}")

st.markdown("## Step 3: Check that Y is binary")
if y.nunique() != 2:
    st.error("Y must be binary (only 2 unique values for logistic regression)")
    st.stop()

st.success("Y is binary, so logistic regression can be fit.")

def logistic_reg(x, y):
    st.markdown("## Step 4: Fit the logistic regression model")
    st.markdown("""
We now fit the model:

""")
    st.latex(r"\log\left(\frac{p}{1-p}\right) = \beta_0 + \beta_1 x")

    model = smf.logit("y ~ x", data=df).fit()

    st.markdown("### Model summary")
    st.text(model.summary())

    st.markdown("## Step 5: Get fitted values and coefficients")
    st.markdown("""
After fitting the model, we extract:

- the fitted log-odds
- the estimated intercept $\\beta_0$
- the estimated slope $\\beta_1$

These let us build the log-odds, odds, and probability curves.
""")

    fitted_log = model.fittedvalues

    b0 = model.params["Intercept"]
    b1 = model.params["x"]

    st.write(f"Estimated intercept ($\\beta_0$): {b0:.4f}")
    st.write(f"Estimated slope ($\\beta_1$): {b1:.4f}")

    st.latex(
        rf"\log\left(\frac{{p}}{{1-p}}\right) = {b0:.4f} + ({b1:.4f})x"
    )

    st.markdown("## Step 6: Create a smooth range of x-values for plotting")
    x_vals = np.linspace(df["x"].min(), df["x"].max(), 100)

    st.markdown("""
Using those x-values, we calculate:
1. **log-odds**
2. **odds**
3. **predicted probabilities**
""")

    log_odds = b0 + b1 * x_vals
    odds = np.exp(log_odds)
    probabilities = odds / (1 + odds)

    st.markdown("### Log-odds equation")
    st.latex(r"\text{log-odds} = \beta_0 + \beta_1 x")

    st.markdown("### Odds equation")
    st.latex(r"\text{odds} = e^{\beta_0 + \beta_1 x}")

    st.markdown("### Probability equation")
    st.latex(r"p = \frac{e^{\beta_0 + \beta_1 x}}{1 + e^{\beta_0 + \beta_1 x}}")

    st.markdown("## Step 7: Plot predicted log-odds")
    st.markdown("""
This graph shows the model on the **log-odds scale**.
Because the model is linear in the log-odds, this plot should be a straight line.
""")

    fig1, ax1 = plt.subplots()
    ax1.plot(x_vals, log_odds)
    ax1.set_xlabel("X")
    ax1.grid()
    ax1.set_ylabel("Log-Odds")
    ax1.set_title("Predicted Log-Odds")
    st.pyplot(fig1)

    st.markdown("## Step 8: Plot predicted odds")
    st.markdown("""
This graph shows the predicted **odds**.

Interpretation of odds:
- odds = 1 means equally likely
- odds > 1 means outcome 1 is more likely
- odds < 1 means outcome 1 is less likely
""")

    fig2, ax2 = plt.subplots()
    ax2.plot(x_vals, odds)
    ax2.set_xlabel("X")
    ax2.grid()
    ax2.set_ylabel("Odds")
    ax2.set_title("Predicted Odds")
    st.pyplot(fig2)

    st.markdown("## Step 9: Plot predicted probabilities")
    st.markdown("""
This is usually the most intuitive graph.

It shows the predicted probability that \(Y = 1\) as \(X\) changes.
Because logistic regression maps values into the interval from 0 to 1,
the curve has an **S-shape**.
""")

    fig3, ax3 = plt.subplots()
    ax3.plot(x_vals, probabilities)
    ax3.set_xlabel("X")
    ax3.grid()
    ax3.set_ylabel("Probability")
    ax3.set_title("Predicted Probability")
    ax3.scatter(df["x"], df["y"])
    st.pyplot(fig3)

    st.markdown("## Step 10: Look at deviance residuals")
    st.markdown("""
Residuals help us see how well the model fits.

For logistic regression, we often use **deviance residuals** instead of the regular residuals
used in linear regression.
""")

    resid = model.resid_dev

    fig4, ax4 = plt.subplots()
    sns.regplot(x=fitted_log, y=resid, lowess=True, ax=ax4)
    ax4.set_xlabel("Predicted Log-Odds")
    ax4.grid()
    ax4.set_ylabel("Deviance Residuals")
    ax4.set_title("Deviance Residuals vs. Predicted Log-Odds Values")
    st.pyplot(fig4)

    st.markdown("""
In a good model, residuals should look fairly patternless.
Strong structure or curvature can suggest a poor fit. The lowess line should be somewhat flat on y = 0.
""")

    
    st.markdown("""
## Step 11: From Probabilities to Classification

Logistic regression does **not directly predict 0 or 1**.

Instead, it predicts a **probability** that the outcome is 1:

- A value close to 1 → very likely the event happens  
- A value close to 0 → very unlikely the event happens  

To actually make a **classification decision**, we choose a **threshold**.

### Threshold rule
- If predicted probability is at least the threshold → predict **1**
- If predicted probability is below the threshold → predict **0**

The most common threshold is:

""")

    st.latex(r"\text{threshold} = 0.5")

    st.markdown("""
So:
- \( $p$ $\\geq$ 0.5 \) → classify as **1**
- \( $p$ $\\lt$ 0.5 \) → classify as **0**

### Why this matters

Changing the threshold changes how strict your model is:

- **Lower threshold (e.g., 0.3)** → more predictions of 1 (more sensitive)
- **Higher threshold (e.g., 0.7)** → fewer predictions of 1 (more strict)

This tradeoff is exactly what the **ROC curve** helps visualize.
""")

    st.markdown("## Step 12: Build the ROC curve")
    st.markdown("""
The **ROC curve** shows how well the model separates the two classes.

It compares:

- **True Positive Rate**
- **False Positive Rate**

The **AUC** (Area Under the Curve) summarizes model performance:

- **0.5** = no better than random guessing
- **1.0** = perfect classification
""")
    df["p"] = model.predict(df)
    fprs, tprs, thresholds = roc_curve(y_true=df["y"], y_score=df["p"])
    auc = roc_auc_score(y_true=df["y"], y_score=df["p"])

    st.write(f"ROC AUC: {auc:.3f}")

    fig5, ax5 = plt.subplots()
    ax5.plot(fprs, tprs, color='darkorange', lw=2,
             label='ROC curve (area = ' + str(round(auc, 3)) + ')')
    ax5.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    ax5.set_xlabel('False Positive Rate')
    ax5.set_ylabel('True Positive Rate')
    ax5.grid()
    ax5.set_title('ROC Curve')
    ax5.legend(loc="lower right")
    st.pyplot(fig5)

    st.markdown("## Step 13: Final interpretation")
    st.markdown("""
At this point, you have:

- fit a logistic regression model
- estimated the coefficients
- visualized log-odds, odds, and probabilities
- checked deviance residuals
- evaluated classification performance with the ROC curve and AUC

That is the core workflow of a simple logistic regression analysis.
""")

    return model.summary()

logistic_reg(df["x"], df["y"])