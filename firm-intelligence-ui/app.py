
import streamlit as st
import httpx

# FastAPI base URL
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Firm Intelligence",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 Firm Intelligence")
st.caption("Ask questions, search knowledge and generate firm summaries.")

# --------------------------------------------------
# FEATURE 1: ASK AI
# --------------------------------------------------

st.header("1. Ask AI")

question = st.text_input(
    "Enter your question",
    key="agent_question",
    placeholder="e.g. How is profit per equity partner calculated?"
)

if st.button("Ask AI", key="ask_button"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            with st.spinner("Getting your answer..."):
                response = httpx.post(
                    f"{API_URL}/agent/ask",
                    json={"question": question},
                    timeout=90.0
                )
                response.raise_for_status()
                data = response.json()

            if not data:
                st.warning(
                    "The agent did not return a response. "
                    "It may have reached its iteration limit."
                )
            elif data.get("answer"):
                st.subheader("Answer")
                st.markdown(data["answer"])

                if data.get("stop_reason") == "max_iterations":
                    st.warning(
                        "The agent reached its iteration limit."
                    )
            else:
                st.warning(
                    "The agent did not complete the answer. "
                    "It may have reached its iteration limit."
                )

            if data:
                st.subheader("Usage")
                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Tool calls",
                    data.get("tool_calls_made", 0)
                )
                col2.metric(
                    "Input tokens",
                    data.get("input_tokens", 0)
                )
                col3.metric(
                    "Output tokens",
                    data.get("output_tokens", 0)
                )

        except httpx.HTTPStatusError as e:
            st.error(
                f"API error ({e.response.status_code}): "
                f"{e.response.text}"
            )
        except httpx.RequestError as e:
            st.error(f"Could not connect to the API: {e}")
        except ValueError:
            st.error("The API returned an invalid response.")

st.divider()

# --------------------------------------------------
# FEATURE 2: SEARCH ONLY
# --------------------------------------------------

st.header("2. Search Knowledge Base")

search_question = st.text_input(
    "What would you like to search for?",
    key="search_question",
    placeholder="e.g. UK legal market revenue"
)

if st.button("Search", key="search_button"):
    if not search_question.strip():
        st.warning("Please enter a search query.")
    else:
        try:
            with st.spinner("Searching documents..."):
                response = httpx.post(
                    f"{API_URL}/knowledge/search",
                    json={
                        "question": search_question,
                        "top_k": 8
                    },
                    timeout=60.0
                )

            if response.status_code == 409:
                st.warning(
                    "The knowledge index has not been built yet. "
                    "Ask the backend operator to build the index."
                )
            else:
                response.raise_for_status()
                data = response.json()
                results = data.get("results", [])

                if not results:
                    st.info("No search results were returned.")
                else:
                    st.success(f"Found {len(results)} results")

                    for index, result in enumerate(results, start=1):
                        with st.expander(
                            f"{index}. {result.get('title', 'Untitled')}"
                            f" — Score: {result.get('score', 0):.3f}"
                        ):
                            st.write("Document ID:", result.get("id", "N/A"))
                            st.write("Score:", result.get("score", "N/A"))
                            st.write(result.get("text", ""))

        except httpx.HTTPStatusError as e:
            st.error(
                f"Search failed ({e.response.status_code}): "
                f"{e.response.text}"
            )
        except httpx.RequestError as e:
            st.error(f"Could not connect to the API: {e}")
        except ValueError:
            st.error("The API returned an invalid response.")

st.divider()

# --------------------------------------------------
# FEATURE 3: STREAMING FIRM SUMMARY
# --------------------------------------------------

st.header("3. Streaming Firm Summary")

# Get firm IDs and names directly from the API
try:
    firms_response = httpx.get(
        f"{API_URL}/firms",
        timeout=15.0
    )
    firms_response.raise_for_status()
    firms = firms_response.json()

    if not firms:
        st.warning("No firms are currently available.")
    else:
        selected_firm = st.selectbox(
            "Select a firm",
            options=firms,
            format_func=lambda firm: (
                f"{firm['id']} - {firm['name']}"
            ),
            key="selected_firm"
        )

        if st.button("Generate streaming summary"):
            try:
                with httpx.stream(
                    "GET",
                    f"{API_URL}/firms/"
                    f"{selected_firm['id']}/summary/stream",
                    timeout=90.0
                ) as response:
                    response.raise_for_status()

                    st.subheader(
                        f"Summary: {selected_firm['name']}"
                    )
                    summary_placeholder = st.empty()
                    summary = ""

                    for chunk in response.iter_text():
                        if chunk:
                            summary += chunk
                            summary_placeholder.markdown(summary + "▌")

                    summary_placeholder.markdown(summary)

                    if not summary:
                        st.info("The API returned an empty summary.")

            except httpx.HTTPStatusError as e:
                st.error(
                    f"Summary failed ({e.response.status_code}): "
                    f"{e.response.text}"
                )
            except httpx.RequestError as e:
                st.error(f"Streaming connection failed: {e}")

except httpx.HTTPStatusError as e:
    st.error(
        f"Could not load firms ({e.response.status_code}): "
        f"{e.response.text}"
    )
except httpx.RequestError as e:
    st.error(f"Could not connect to the API: {e}")
except ValueError:
    st.error("The API returned an invalid firms response.")