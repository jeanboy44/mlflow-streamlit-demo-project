import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="EDA", page_icon="✅", layout="wide")
st.title("데이터 탐색")
df = pd.read_csv("data/test.csv", sep=",")
df = df.sort_values("uid")
df["target"] = df["target"].astype(str)
st.dataframe(df)

st.divider()

st.subheader("BY TARGET")
col1, col2, col3 = st.columns(3)
with col1:
    title = "Target Count"
    df_counts = df["target"].value_counts().reset_index()
    df_counts.columns = ["target", "count"]
    fig = px.bar(df_counts, x="target", y="count", color="target", title=title)
    st.plotly_chart(fig, key="target_count")

    title = "Air Temperature by Target"
    fig = px.box(df, x="target", y="air_temperature", color="target", title=title)
    st.plotly_chart(fig, key="air_temperature")

    title = "Process Temperature by Target"
    fig = px.box(df, x="target", y="process_temperature", color="target", title=title)
    st.plotly_chart(fig, key="process_temperature")


with col2:
    title = "Type vs Target"
    df_counts = df[["type", "target"]].value_counts().reset_index()
    df_counts.columns = ["type", "target", "count"]
    fig = px.bar(
        df_counts, x="type", y="count", color="target", barmode="relative", title=title
    )
    st.plotly_chart(fig, key="type_target_count")

    title = "Tool Wear by Target"
    fig = px.box(df, x="target", y="tool_wear", color="target", title=title)
    st.plotly_chart(fig, key="tool_wear")


with col3:
    title = "Rotational Speed by Target"
    fig = px.box(df, x="target", y="rotational_speed", color="target", title=title)
    st.plotly_chart(fig, key="rotational_speed")

    title = "Torque by Target"
    fig = px.box(df, x="target", y="torque", color="target", title=title)
    st.plotly_chart(fig, key="torque")

st.divider()

st.subheader("BY TYPE")
col1, col2, col3 = st.columns(3)
with col1:
    title = "Air Temperature by Type"
    fig = px.box(df, x="type", y="air_temperature", color="target", title=title)
    st.plotly_chart(fig, key="air_temperature_by_type")

    title = "Process Temperature by Type"
    fig = px.box(df, x="type", y="process_temperature", color="target", title=title)
    st.plotly_chart(fig, key="process_temperature_by_type")


with col2:
    title = "Tool Wear by Type"
    fig = px.box(df, x="type", y="tool_wear", color="target", title=title)
    st.plotly_chart(fig, key="tool_wear_by_type")

    title = "Torque by Type"
    fig = px.box(df, x="type", y="torque", color="target", title=title)
    st.plotly_chart(fig, key="torque_by_type")


with col3:
    title = "Rotational Speed by Type"
    fig = px.box(df, x="type", y="rotational_speed", color="target", title=title)
    st.plotly_chart(fig, key="rotational_speed_by_type")

st.divider()
st.subheader("BY UID")

title = "UID vs Air Temperature"
fig = px.line(df, x="uid", y="air_temperature", color="target", title=title)
st.plotly_chart(fig, key="uid_air_temperature")

title = "UID vs Rotational Speed"
fig = px.line(df, x="uid", y="rotational_speed", color="target", title=title)
st.plotly_chart(fig, key="uid_rotational_speed")

title = "UID vs Tool Wear"
fig = px.line(df, x="uid", y="tool_wear", color="target", title=title)
st.plotly_chart(fig, key="uid_tool_wear")

title = "UID vs Process Temperature"
fig = px.line(df, x="uid", y="process_temperature", color="target", title=title)
st.plotly_chart(fig, key="uid_process_temperature")

title = "UID vs Torque"
fig = px.line(df, x="uid", y="torque", color="target", title=title)
fig = fig.update_layout(xaxis_rangeslider_visible=True)
st.plotly_chart(fig, key="uid_torque")
