"""Suraj's Garage — authentication wrapper around streamlit-authenticator."""
from __future__ import annotations

import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.hasher import Hasher


def _build() -> stauth.Authenticate:
    """Build the authenticator from secrets.toml."""
    cfg = st.secrets["auth"]

    # Support both nested and flat credential layouts
    try:
        usernames_cfg = cfg["credentials"]["usernames"]
    except (KeyError, TypeError):
        usernames_cfg = cfg.get("credentials", {}).get("usernames", {})

    credentials = {"usernames": {}}
    for username, data in usernames_cfg.items():
        credentials["usernames"][username] = {
            "email": data.get("email", ""),
            "name": data.get("name", username),
            "password": data.get("password", ""),
        }

    return stauth.Authenticate(
        credentials=credentials,
        cookie_name=cfg.get("cookie_name", "surajs_garage_auth"),
        cookie_key=cfg.get("cookie_key", "CHANGE-ME"),
        cookie_expiry_days=int(cfg.get("cookie_expiry_days", 60)),
        auto_hash=False,
    )


def require_login() -> tuple[str, str, stauth.Authenticate]:
    """
    Render the login gate.
    Returns (display_name, username, authenticator).
    Stops the script if not authenticated.
    """
    authenticator = _build()

    # Render login form
    authenticator.login(location="main", key="login_widget")

    status = st.session_state.get("authentication_status")

    if status is False:
        st.error("Email or password is incorrect.")
        st.stop()

    if status is None:
        st.info(
            "Sign in to keep vehicle history, diagnostic tests, "
            "measurements, and professional reports on your account."
        )
        st.stop()

    name = st.session_state.get("name") or "Owner"
    username = st.session_state.get("username") or ""
    return name, username, authenticator


def generate_password_hash(password: str) -> str:
    """Utility for generating bcrypt hashes (used during setup)."""
    return Hasher.hash(password)
