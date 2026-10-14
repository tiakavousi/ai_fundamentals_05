import os
import requests
import streamlit as st

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Retail Banking UI", layout="wide")
st.title("Retail Banking")
st.caption(f"Backend: {BACKEND_URL}")


def call(method, path, *, params=None, json=None, timeout=15):
    url = f"{BACKEND_URL}{path}"
    try:
        r = requests.request(method, url, params=params, json=json, timeout=timeout)
    except requests.Timeout:
        st.error(f"Request timed out after {timeout}s: {url}")
        return None
    except requests.ConnectionError as e:
        st.error(f"Connection error: {e}")
        return None
    except requests.RequestException as e:
        st.error(f"Request error: {e}")
        return None
    if r.status_code != 200:
        try:
            body = r.json()
        except Exception:
            body = r.text
        st.error(f"HTTP {r.status_code} from {url}")
        st.json(body) if isinstance(body, (dict, list)) else st.code(body)
        return None
    try:
        return r.json()
    except Exception:
        st.error("Response was not valid JSON")
        st.code(r.text)
        return None


def render_tokens(data: dict):
    it = data.get("input_tokens")
    ot = data.get("output_tokens")
    if it is not None or ot is not None:
        c1, c2 = st.columns(2)
        c1.metric("input_tokens", it if it is not None else "—")
        c2.metric("output_tokens", ot if ot is not None else "—")


tab1, tab2, tab3 = st.tabs([
    "Search Knowledge Base",
    "LLM Generating Complaint Summary",
    "Ask Agent",
])

with tab1:
    st.subheader("Search Knowledge Base")
    query = st.text_input("Query", key="kb_query")
    top_k = st.number_input("top_k", min_value=1, max_value=50, value=3, step=1, key="kb_topk")
    if st.button("Search", key="kb_btn"):
        if not query.strip():
            st.warning("Please enter a query.")
        else:
            data = call("GET", "/knowledge/search",
                        params={"query": query, "top_k": int(top_k)}, timeout=15)
            if data is not None:
                hits = data.get("hits", data if isinstance(data, list) else [])
                if not hits:
                    st.info("No hits.")
                else:
                    rows = []
                    for h in hits:
                        snip = h.get("snippet") or h.get("text") or h.get("content") or ""
                        if len(snip) > 200:
                            snip = snip[:200] + "…"
                        rows.append({
                            "id": h.get("id"),
                            "title": h.get("title"),
                            "score": h.get("score"),
                            "snippet": snip,
                        })
                    st.dataframe(rows, use_container_width=True)
                with st.expander("Raw response"):
                    st.json(data)

with tab2:
    st.subheader("LLM Generating Complaint Summary")
    cid = st.number_input("complaint_id", min_value=1, value=1, step=1, key="sum_cid")
    if st.button("Generate summary", key="sum_btn"):
        data = call("POST", f"/complaints/{int(cid)}/summary", timeout=60)
        if data is not None:
            summary = data.get("summary") or data.get("text")
            if summary:
                st.markdown(summary)
            render_tokens(data if isinstance(data, dict) else {})
            with st.expander("Raw response"):
                st.json(data)

with tab3:
    st.subheader("Ask Agent")
    question = st.text_area("Question", key="ag_q", height=100)
    if st.button("Ask", key="ag_btn"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            data = call("POST", "/agent/ask",
                        json={"question": question}, timeout=60)
            if data is not None:
                answer = data.get("answer", "")
                st.markdown("**Answer**")
                st.markdown(answer if answer else "_(empty)_")
                c1, c2, c3 = st.columns(3)
                c1.metric("tool_calls_made", data.get("tool_calls_made", "—"))
                c2.metric("complete", str(data.get("complete", "—")))
                c3.metric("stop_reason", str(data.get("stop_reason", "—")))
                render_tokens(data)
                with st.expander("Raw response"):
                    st.json(data)
