import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="KADIRS Tax Compliance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

local_css("assets/style.css")
# ============================================
# LOAD DATA
# ============================================
@st.cache_data
def load_data():
    return pd.read_csv("../data/validated_KADIRS_Tax_Compliance.csv")

with st.spinner("Loading dashboard..."):
    df = load_data()

# ============================================
# HEADER
# ============================================

st.title("📊 KADIRS Tax Compliance Monitoring Dashboard")

st.caption(
    "Interactive dashboard for monitoring tax compliance, "
    "revenue collection and taxpayer performance."
)

st.divider()

# ============================================
# SIDEBAR
# ============================================

st.sidebar.image(
    "https://img.icons8.com/color/96/tax.png",
    width=70
)

st.sidebar.title("Dashboard")

st.sidebar.markdown("---")

# ============================================
# SEARCH SECTION
# ============================================

st.sidebar.subheader("🔍 Search")

search_id = st.sidebar.text_input(
    "Taxpayer ID",
    placeholder="Enter Taxpayer ID..."
)

search_name = st.sidebar.text_input(
    "Business Name",
    placeholder="Enter Business Name..."
)

st.sidebar.markdown("---")

# ============================================
# FILTER SECTION
# ============================================

st.sidebar.subheader("📌 Filters")

lga = st.sidebar.multiselect(
    "LGA",
    sorted(df["lga"].unique())
)

taxpayer = st.sidebar.multiselect(
    "Taxpayer Type",
    sorted(df["taxpayer_type"].unique())
)

tax_type = st.sidebar.multiselect(
    "Tax Type",
    sorted(df["tax_type"].unique())
)

risk = st.sidebar.multiselect(
    "Risk Level",
    sorted(df["risk_level"].unique())
)

payment = st.sidebar.multiselect(
    "Payment Status",
    sorted(df["payment_status"].unique())
)

st.sidebar.markdown("---")

# ============================================
# RESET BUTTON
# ============================================

if st.sidebar.button("🔄 Reset Dashboard"):
    st.rerun()

# ============================================
# FILTER DATA
# ============================================

filtered_df = df.copy()

if search_id:
    filtered_df = filtered_df[
        filtered_df["taxpayer_id"]
        .astype(str)
        .str.contains(search_id, case=False)
    ]

if search_name:
    filtered_df = filtered_df[
        filtered_df["business_name"]
        .astype(str)
        .str.contains(search_name, case=False)
    ]

if lga:
    filtered_df = filtered_df[
        filtered_df["lga"].isin(lga)
    ]

if taxpayer:
    filtered_df = filtered_df[
        filtered_df["taxpayer_type"].isin(taxpayer)
    ]

if tax_type:
    filtered_df = filtered_df[
        filtered_df["tax_type"].isin(tax_type)
    ]

if risk:
    filtered_df = filtered_df[
        filtered_df["risk_level"].isin(risk)
    ]

if payment:
    filtered_df = filtered_df[
        filtered_df["payment_status"].isin(payment)
    ]

# ============================================
# DASHBOARD SUMMARY
# ============================================

st.subheader("Dashboard Summary")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "👥 Taxpayers",
    f"{filtered_df['taxpayer_id'].nunique():,}"
)

col2.metric(
    "💰 Revenue",
    f"₦{filtered_df['amount_paid'].sum():,.0f}"
)

col3.metric(
    "🧾 Tax Assessed",
    f"₦{filtered_df['amount_assessed'].sum():,.0f}"
)

col4.metric(
    "⚠ Outstanding",
    f"₦{filtered_df['outstanding_balance'].sum():,.0f}"
)

col5.metric(
    "📈 Compliance",
    f"{filtered_df['compliance_score'].mean():.1f}%"
)
st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Dashboard",
    "💰 Revenue Analysis",
    "📋 Compliance",
    "🔍 Audit",
    "⚠ Defaulters"
])
# ============================================
# SEARCH RESULT
# ============================================

if search_id or search_name:

    if len(filtered_df) > 0:

        st.success(f"{len(filtered_df)} matching record(s) found.")

    else:

        st.error("No matching taxpayer found.")

# ============================================
# DATA TABLE
# ============================================

with tab1:

    st.subheader("Executive Dashboard")

    col1, col2 = st.columns(2)

    with col1:

        monthly = (
            filtered_df.groupby("tax_month")["amount_paid"]
            .sum()
            .reset_index()
        )

        fig = px.line(
            monthly,
            x="tax_month",
            y="amount_paid",
            markers=True,
            title="Monthly Revenue Trend"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        payment = (
            filtered_df["payment_status"]
            .value_counts()
            .reset_index()
        )

        payment.columns = ["Payment Status", "Count"]

        fig = px.pie(
            payment,
            names="Payment Status",
            values="Count",
            hole=.5
        )

        st.plotly_chart(fig, use_container_width=True)
with tab2:

    st.subheader("Revenue Analysis")

    col1, col2 = st.columns(2)

    with col1:

        revenue_lga = (
            filtered_df.groupby("lga")["amount_paid"]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            revenue_lga,
            x="lga",
            y="amount_paid",
            color="amount_paid",
            title="Revenue by LGA"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        revenue_sector = (
            filtered_df.groupby("business_sector")["amount_paid"]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            revenue_sector,
            x="business_sector",
            y="amount_paid",
            color="amount_paid",
            title="Revenue by Business Sector"
        )

        st.plotly_chart(fig, use_container_width=True)
with tab3:

    st.subheader("Compliance Analysis")

    col1, col2 = st.columns(2)

    with col1:

        fig = px.histogram(
            filtered_df,
            x="compliance_score",
            nbins=20,
            title="Compliance Score Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        risk = (
            filtered_df["risk_level"]
            .value_counts()
            .reset_index()
        )

        risk.columns = ["Risk Level", "Count"]

        fig = px.bar(
            risk,
            x="Risk Level",
            y="Count",
            color="Risk Level"
        )

        st.plotly_chart(fig, use_container_width=True)

with tab4:

    st.subheader("Audit Analysis")

    audit = (
        filtered_df["audit_status"]
        .value_counts()
        .reset_index()
    )

    audit.columns = ["Audit Status", "Count"]

    fig = px.pie(
        audit,
        names="Audit Status",
        values="Count"
    )

    st.plotly_chart(fig, use_container_width=True)
with tab5:

    st.subheader("Top Tax Defaulters")

    top = (
        filtered_df.sort_values(
            "outstanding_balance",
            ascending=False
        )
        .head(20)
    )

    st.dataframe(
        top[
            [
                "taxpayer_id",
                "business_name",
                "lga",
                "amount_assessed",
                "amount_paid",
                "outstanding_balance"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )