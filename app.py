import pathlib

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="HR Attrition Dashboard", page_icon="📊", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    data_path = pathlib.Path("Dataset") / "Raw" / "HR Employee Attrition.csv"
    df = pd.read_csv(data_path)
    return df


def add_attrition_label(df: pd.DataFrame) -> pd.DataFrame:
    labeled_df = df.copy()
    if "Attrition" in labeled_df.columns:
        labeled_df["Attrition Label"] = labeled_df["Attrition"].map({"Yes": 1, "No": 0})
    return labeled_df


def main() -> None:
    st.title("Employee Attrition Analysis")
    st.caption("Interactive overview of attrition patterns from the HR dataset")

    try:
        df = load_data()
    except FileNotFoundError:
        st.error("Dataset file not found at Dataset/Raw/HR Employee Attrition.csv")
        st.stop()

    df = add_attrition_label(df)

    if "Department" in df.columns:
        department_filter = st.sidebar.multiselect(
            "Department", sorted(df["Department"].dropna().unique().tolist())
        )
        if department_filter:
            df = df[df["Department"].isin(department_filter)]

    if "JobRole" in df.columns:
        role_filter = st.sidebar.multiselect(
            "Job Role", sorted(df["JobRole"].dropna().unique().tolist())
        )
        if role_filter:
            df = df[df["JobRole"].isin(role_filter)]

    total_employees = len(df)
    attrition_rate = (
        (df["Attrition"] == "Yes").mean() * 100 if "Attrition" in df.columns and total_employees else 0
    )
    avg_income = df["MonthlyIncome"].mean() if "MonthlyIncome" in df.columns and total_employees else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Employees", f"{total_employees:,}")
    c2.metric("Attrition Rate", f"{attrition_rate:.1f}%")
    c3.metric("Avg. Monthly Income", f"${avg_income:,.0f}")

    left, right = st.columns(2)

    if "Department" in df.columns and "Attrition" in df.columns and not df.empty:
        dept_attrition = (
            df.groupby("Department", as_index=False)["Attrition Label"].mean().sort_values("Attrition Label")
        )
        fig = px.bar(
            dept_attrition,
            x="Department",
            y="Attrition Label",
            title="Attrition Rate by Department",
            labels={"Attrition Label": "Attrition Rate"},
        )
        fig.update_yaxes(tickformat=".0%")
        left.plotly_chart(fig, use_container_width=True)

    if "JobSatisfaction" in df.columns and "Attrition" in df.columns and not df.empty:
        sat_attrition = (
            df.groupby("JobSatisfaction", as_index=False)["Attrition Label"].mean().sort_values("JobSatisfaction")
        )
        fig = px.line(
            sat_attrition,
            x="JobSatisfaction",
            y="Attrition Label",
            markers=True,
            title="Attrition Rate by Job Satisfaction",
            labels={"Attrition Label": "Attrition Rate"},
        )
        fig.update_yaxes(tickformat=".0%")
        right.plotly_chart(fig, use_container_width=True)

    if "MonthlyIncome" in df.columns and "Attrition" in df.columns and not df.empty:
        fig = px.box(
            df,
            x="Attrition",
            y="MonthlyIncome",
            color="Attrition",
            title="Monthly Income Distribution by Attrition",
        )
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("Preview Data"):
        st.dataframe(df.head(30), use_container_width=True)


if __name__ == "__main__":
    main()
