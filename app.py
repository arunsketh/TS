import streamlit as st
import pandas as pd
import numpy as np

# Page setup
st.set_page_config(page_title="Friction Calibration", layout="wide")
st.title("FEA vs. Test Data: Contact Parameter Calibration")
st.markdown("Adjust the Abaqus contact parameters to match the surrogate FEA model against the TES dataset.")

# --- Sidebar Inputs ---
st.sidebar.header("Abaqus Contact Parameters")
mu_static = st.sidebar.slider("Static Friction (mu at slip=1)", 0.1, 1.0, 0.8, 0.05)
mu_kin1 = st.sidebar.slider("Kinetic Friction 1 (mu at slip=2)", 0.1, 1.0, 0.6, 0.05)
mu_kin2 = st.sidebar.slider("Kinetic Friction 2 (mu at slip=3)", 0.1, 1.0, 0.3, 0.05)
slip_tol = st.sidebar.slider("Slip Tolerance", 0.001, 0.100, 0.020, 0.001)

# --- Test Data (TES) ---
degrees = np.arange(19)
tes_moment = [
    0, 1844, 3688, 5211, 6734, 7792, 8851, 9747, 10643, 
    11270, 11897, 12240, 12583, 12863, 12988, 13151, 13210, 13195, 13158
]

# --- Surrogate FEA Model ---
def calculate_surrogate_fea(theta_array, mu_s, mu_k1, mu_k2, tol):
    """
    Approximates Abaqus implicit solver torsional moment response 
    based on friction decay and slip tolerance penalties.
    """
    fea_moment = np.zeros_like(theta_array, dtype=float)
    
    # Base penalty stiffness is inversely proportional to slip tolerance
    penalty_stiffness = 3000 * (1 - (tol * 5)) 
    
    for i, t in enumerate(theta_array):
        # Model friction decay as rotation (slip proxy) increases
        if t <= 5:
            current_mu = mu_s
        elif t <= 12:
            # Linear decay from static to first kinetic stage
            current_mu = mu_s - (mu_s - mu_k1) * ((t - 5) / 7)
        else:
            # Linear decay from first to second kinetic stage
            current_mu = mu_k1 - (mu_k1 - mu_k2) * ((t - 12) / 6)
            
        # Theoretical elastic moment (stick phase)
        m_elastic = penalty_stiffness * t
        
        # Maximum allowable sliding moment capacity (slip phase)
        # Scaled to match the general magnitude of the test rig
        m_capacity = 16000 * current_mu 
        
        # Smooth transition between stick and slip using a logistic function 
        # Tighter slip tolerance creates a sharper, more abrupt transition
        transition_sharpness = 0.05 / max(tol, 0.001)
        slip_transition = 1 / (1 + np.exp(-((m_elastic - m_capacity) / m_capacity) * transition_sharpness))
        
        # Blended final moment
        fea_moment[i] = (m_elastic * (1 - slip_transition)) + (m_capacity * slip_transition)
        
    return fea_moment

# Generate FEA curve based on slider inputs
fea_moment_calculated = calculate_surrogate_fea(degrees, mu_static, mu_kin1, mu_kin2, slip_tol)

# --- Data Compilation and Plotting ---
df_plot = pd.DataFrame({
    "Degree (°)": degrees,
    "TES Moment (lbs-ft)": tes_moment,
    "Surrogate FEA (lbs-ft)": fea_moment_calculated
}).set_index("Degree (°)")

# Display Interactive Chart
st.line_chart(
    df_plot, 
    color=["#ff0000", "#0000ff"],
    height=500
)

# Display tabular comparison for specific inspection
col1, col2 = st.columns(2)
with col1:
    st.subheader("Peak Comparison")
    peak_tes = max(tes_moment)
    peak_fea = max(fea_moment_calculated)
    
    st.metric(label="TES Peak Moment", value=f"{peak_tes:,.0f} lbs-ft")
    st.metric(label="FEA Peak Moment", value=f"{peak_fea:,.0f} lbs-ft", delta=f"{peak_fea - peak_tes:,.0f} lbs-ft")

with col2:
    st.subheader("Early Stiffness (3°)")
    stiffness_tes = df_plot.loc[3, "TES Moment (lbs-ft)"]
    stiffness_fea = df_plot.loc[3, "Surrogate FEA (lbs-ft)"]
    
    st.metric(label="TES at 3°", value=f"{stiffness_tes:,.0f} lbs-ft")
    st.metric(label="FEA at 3°", value=f"{stiffness_fea:,.0f} lbs-ft", delta=f"{stiffness_fea - stiffness_tes:,.0f} lbs-ft")
