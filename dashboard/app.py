"""Streamlit dashboard entry point."""

import streamlit as st

st.set_page_config(page_title="bess-desk", page_icon="🔋", layout="wide")
st.title("🔋 bess-desk")
st.caption("Agent-orchestrated BESS trading desk")

st.info("Dashboard under construction. See ROADMAP.md for planned pages.")

st.markdown("""
### Planned pages

- **Trading floor** — live agent activity and recent memos
- **Approvals** — pending proposals awaiting human decision
- **P&L** — revenue by product with attribution
- **Audit log** — every memo, bid, and decision, replayable
""")
