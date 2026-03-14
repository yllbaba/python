from __future__ import annotations

import json
from datetime import date
from typing import Any, Dict, Optional, Tuple
import urllib.error
import urllib.parse
import urllib.request

import streamlit as st

from visualizations.charts import (
    assists_per_game_chart,
    performance_trend_chart,
    points_per_game_chart,
    rebounds_per_game_chart,
)


def api_request(
    method: str,
    url: str,
    token: Optional[str] = None,
    body: Optional[Dict[str, Any]] = None,
) -> Tuple[int, Any]:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request) as response:
            content = response.read().decode("utf-8")
            if not content:
                return response.status, None
            try:
                return response.status, json.loads(content)
            except json.JSONDecodeError:
                return response.status, content
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8")
        try:
            return exc.code, json.loads(error_body)
        except json.JSONDecodeError:
            return exc.code, {"detail": error_body}


st.set_page_config(page_title="Basketball Game Tracker", layout="wide")

if "token" not in st.session_state:
    st.session_state["token"] = None
if "api_base" not in st.session_state:
    st.session_state["api_base"] = "http://localhost:8000"

st.title("Basketball Game Tracker Dashboard")

with st.sidebar:
    st.header("Connection")
    st.session_state["api_base"] = st.text_input("API Base URL", st.session_state["api_base"])
    if st.session_state["token"]:
        if st.button("Log out"):
            st.session_state["token"] = None
            st.experimental_rerun()

if not st.session_state["token"]:
    st.subheader("Sign In")
    login_col, register_col = st.columns(2)

    with login_col:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                status, data = api_request(
                    "POST",
                    f"{st.session_state['api_base']}/auth/login",
                    body={"username": username, "password": password},
                )
                if status == 200:
                    st.session_state["token"] = data["token"]
                    st.success("Logged in")
                    st.experimental_rerun()
                else:
                    st.error(data.get("detail", "Login failed"))

    with register_col:
        with st.form("register_form"):
            new_username = st.text_input("New username")
            new_password = st.text_input("New password", type="password")
            registered = st.form_submit_button("Register")
            if registered:
                status, data = api_request(
                    "POST",
                    f"{st.session_state['api_base']}/auth/register",
                    body={"username": new_username, "password": new_password},
                )
                if status == 201:
                    st.success("Registration successful. Log in on the left.")
                else:
                    st.error(data.get("detail", "Registration failed"))
    st.stop()

st.subheader("Game Management")
create_col, list_col = st.columns([1, 2])

with create_col:
    with st.form("create_game_form"):
        game_date = st.date_input("Game Date", value=date.today())
        opponent = st.text_input("Opponent")
        submitted = st.form_submit_button("Create Game")
        if submitted:
            status, data = api_request(
                "POST",
                f"{st.session_state['api_base']}/stats/games",
                token=st.session_state["token"],
                body={"game_date": game_date.isoformat(), "opponent": opponent},
            )
            if status == 201:
                st.success(f"Game created with id {data['id']}")
            else:
                st.error(data.get("detail", "Failed to create game"))

with list_col:
    st.markdown("**Games**")
    status, games = api_request(
        "GET",
        f"{st.session_state['api_base']}/stats/games",
        token=st.session_state["token"],
    )
    if status == 200 and games:
        st.dataframe(games, use_container_width=True)
        game_choices = {f"{g['id']} - {g['game_date']} vs {g['opponent']}": g["id"] for g in games}
        selected_label = st.selectbox("Select game", list(game_choices.keys()))
        selected_game_id = game_choices[selected_label]
    else:
        st.info("No games yet.")
        selected_game_id = None

st.subheader("Add Game Stats")
if selected_game_id:
    with st.form("add_stats_form"):
        player_name = st.text_input("Player Name")
        points = st.number_input("Points", min_value=0, step=1)
        assists = st.number_input("Assists", min_value=0, step=1)
        rebounds = st.number_input("Rebounds", min_value=0, step=1)
        steals = st.number_input("Steals", min_value=0, step=1)
        blocks = st.number_input("Blocks", min_value=0, step=1)
        turnovers = st.number_input("Turnovers", min_value=0, step=1)
        minutes_played = st.number_input("Minutes Played", min_value=0.0, step=1.0)
        submitted = st.form_submit_button("Add Stats")
        if submitted:
            status, data = api_request(
                "POST",
                f"{st.session_state['api_base']}/stats/games/{selected_game_id}/stats",
                token=st.session_state["token"],
                body={
                    "player_name": player_name,
                    "points": int(points),
                    "assists": int(assists),
                    "rebounds": int(rebounds),
                    "steals": int(steals),
                    "blocks": int(blocks),
                    "turnovers": int(turnovers),
                    "minutes_played": float(minutes_played),
                },
            )
            if status == 201:
                st.success("Stats added")
            else:
                st.error(data.get("detail", "Failed to add stats"))

    st.markdown("**Current Game Stats**")
    detail_status, detail = api_request(
        "GET",
        f"{st.session_state['api_base']}/stats/games/{selected_game_id}",
        token=st.session_state["token"],
    )
    if detail_status == 200:
        st.dataframe(detail["stats"], use_container_width=True)

st.subheader("Update Or Delete Stat")
update_col, delete_col = st.columns(2)

with update_col:
    with st.form("update_stat_form"):
        stat_id = st.number_input("Stat ID", min_value=1, step=1)
        new_points = st.number_input("New Points", min_value=0, step=1)
        new_assists = st.number_input("New Assists", min_value=0, step=1)
        new_rebounds = st.number_input("New Rebounds", min_value=0, step=1)
        new_steals = st.number_input("New Steals", min_value=0, step=1)
        new_blocks = st.number_input("New Blocks", min_value=0, step=1)
        new_turnovers = st.number_input("New Turnovers", min_value=0, step=1)
        new_minutes = st.number_input("New Minutes Played", min_value=0.0, step=1.0)
        submitted = st.form_submit_button("Update Stat")
        if submitted:
            status, data = api_request(
                "PUT",
                f"{st.session_state['api_base']}/stats/entries/{int(stat_id)}",
                token=st.session_state["token"],
                body={
                    "points": int(new_points),
                    "assists": int(new_assists),
                    "rebounds": int(new_rebounds),
                    "steals": int(new_steals),
                    "blocks": int(new_blocks),
                    "turnovers": int(new_turnovers),
                    "minutes_played": float(new_minutes),
                },
            )
            if status == 200:
                st.success("Stat updated")
            else:
                st.error(data.get("detail", "Failed to update stat"))

with delete_col:
    with st.form("delete_stat_form"):
        delete_stat_id = st.number_input("Stat ID to delete", min_value=1, step=1)
        submitted = st.form_submit_button("Delete Stat")
        if submitted:
            status, data = api_request(
                "DELETE",
                f"{st.session_state['api_base']}/stats/entries/{int(delete_stat_id)}",
                token=st.session_state["token"],
            )
            if status == 200:
                st.success("Stat deleted")
            else:
                st.error(data.get("detail", "Failed to delete stat"))

st.subheader("Filters")
filter_col1, filter_col2, filter_col3 = st.columns(3)
with filter_col1:
    use_from = st.checkbox("Filter from date")
    filter_date_from = st.date_input("From", value=date.today()) if use_from else None
with filter_col2:
    use_to = st.checkbox("Filter to date")
    filter_date_to = st.date_input("To", value=date.today()) if use_to else None
with filter_col3:
    filter_opponent = st.text_input("Opponent contains")

query_params: Dict[str, str] = {}
if filter_date_from:
    query_params["date_from"] = filter_date_from.isoformat()
if filter_date_to:
    query_params["date_to"] = filter_date_to.isoformat()
if filter_opponent:
    query_params["opponent"] = filter_opponent
query_suffix = f"?{urllib.parse.urlencode(query_params)}" if query_params else ""

st.subheader("Summary")
summary_status, summary = api_request(
    "GET",
    f"{st.session_state['api_base']}/stats/summary{query_suffix}",
    token=st.session_state["token"],
)
if summary_status == 200:
    metrics = st.columns(4)
    metrics[0].metric("Games", summary["games_played"])
    metrics[1].metric("Total Points", summary["total_points"])
    metrics[2].metric("Avg Points", f"{summary['average_points_per_game']:.1f}")
    metrics[3].metric("Total Assists", summary["total_assists"])
    st.write(summary)

st.subheader("Leaderboard")
leader_status, leaderboard = api_request(
    "GET",
    f"{st.session_state['api_base']}/stats/leaderboard{query_suffix}",
    token=st.session_state["token"],
)
if leader_status == 200 and leaderboard:
    st.dataframe(leaderboard, use_container_width=True)

st.subheader("Player Profiles")
profile_status, profiles = api_request(
    "GET",
    f"{st.session_state['api_base']}/stats/players{query_suffix}",
    token=st.session_state["token"],
)
if profile_status == 200 and profiles:
    st.dataframe(profiles, use_container_width=True)

st.subheader("Performance Trends")
trend_status, trends = api_request(
    "GET",
    f"{st.session_state['api_base']}/stats/trends{query_suffix}",
    token=st.session_state["token"],
)
if trend_status == 200 and trends:
    points_fig = points_per_game_chart(trends)
    assists_fig = assists_per_game_chart(trends)
    rebounds_fig = rebounds_per_game_chart(trends)
    trend_fig = performance_trend_chart(trends)

    if points_fig:
        st.pyplot(points_fig)
    if assists_fig:
        st.pyplot(assists_fig)
    if rebounds_fig:
        st.pyplot(rebounds_fig)
    if trend_fig:
        st.pyplot(trend_fig)

st.subheader("Export CSV")
export_status, export_data = api_request(
    "GET",
    f"{st.session_state['api_base']}/stats/export{query_suffix}",
    token=st.session_state["token"],
)
if export_status == 200 and export_data is not None:
    st.download_button(
        "Download CSV",
        data=export_data,
        file_name="basketball_stats.csv",
        mime="text/csv",
    )
