import streamlit as st
import json
import time
import requests
from factsearch import Factool

# page configuration
st.set_page_config(
    page_title="FactSearch Demo - LLM Output Factuality Checking",
    layout="wide",
    initial_sidebar_state="expanded"
)

# test connection to SearXNG
def check_searxng_connection(base_url="http://localhost:8888"):
    """Check if the local SearXNG instance is reachable."""
    try:
        response = requests.get(base_url, timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False

searxng_available = check_searxng_connection()
if not searxng_available:
    st.warning("Cannot connect to local SearXNG instance. Fact-checking is disabled until connection is restored.")

# initialise session state
if 'factool_instance' not in st.session_state:
    st.session_state.factool_instance = None
if 'results_history' not in st.session_state:
    st.session_state.results_history = []

def initialize_factool(model_name):
    """Initialise FactSearch instance with selected model"""
    try:
        with st.spinner(f"Initialising FactSearch with {model_name}..."):
            factool_instance = Factool(model_name)
        st.success(f"FactSearch initialised with {model_name}")
        return factool_instance
    except Exception as e:
        st.error(f"Error initialising FactSearch: {str(e)}")
        return None

# format results and gui display
def format_results(results):
    if not results or 'detailed_information' not in results:
        return None
    detailed_info = results['detailed_information'][0]

    # pair up claim_level_factuality with queries and evidences
    claims_raw = detailed_info.get('claim_level_factuality', [])
    queries_raw = detailed_info.get('queries', [])
    evidences_raw = detailed_info.get('evidences', [])  # list of {evidence: [...], source: [...]}

    enriched_claims = []
    for i, claim in enumerate(claims_raw):
        if claim is None:
            enriched_claims.append(None)
            continue
        enriched = dict(claim)
        # attach query used for this claim
        if i < len(queries_raw):
            q = queries_raw[i]
            enriched['query'] = q[0] if isinstance(q, list) and q else str(q)
        # attach evidence snippets and sources
        if i < len(evidences_raw):
            ev = evidences_raw[i]
            if isinstance(ev, dict):
                snippets = ev.get('evidence', [])
                sources = ev.get('source', [])
                enriched['evidence_snippets'] = snippets if isinstance(snippets, list) else [snippets]
                enriched['evidence_sources'] = sources if isinstance(sources, list) else [sources]
            else:
                enriched['evidence_snippets'] = []
                enriched['evidence_sources'] = []
        enriched_claims.append(enriched)

    return {
        'prompt': detailed_info.get('prompt', ''),
        'response': detailed_info.get('response', ''),
        'response_level_factuality': detailed_info.get('response_level_factuality', False),
        'claim_level_factuality': enriched_claims,
        'reasoning': detailed_info.get('reasoning', ''),
        'avg_claim_factuality': results.get('average_claim_level_factuality', 0),
        'avg_response_factuality': results.get('average_response_level_factuality', 0)
    }


def display_claim_evidence(claim, index):
    """Render a single claim expander with verdict, query, and evidence."""
    if claim is None:
        return

    is_factual = claim.get('factuality', False)
    claim_text = claim.get('claim', f'Claim {index + 1}')
    verdict_label = "Factual" if is_factual else "Not Factual"
    bg_color = "#f0fdf4" if is_factual else "#fef2f2"
    border_color = "#bbf7d0" if is_factual else "#fecaca"

    with st.expander(f"Claim {index + 1}: {claim_text[:80]}{'...' if len(claim_text) > 80 else ''}"):

        # verdict badge
        st.markdown(
            f"""<div style="display:inline-block; padding:4px 12px; border-radius:20px;
                background:{bg_color}; border:1px solid {border_color};
                ; font-weight:600; font-size:0.85rem; margin-bottom:10px;">
                {verdict_label}
            </div>""",
            unsafe_allow_html=True
        )

        # claim text
        st.markdown(f"**Claim:** {claim_text}")

        # reasoning
        if claim.get('reasoning'):
            st.markdown(f"**Reasoning:** {claim['reasoning']}")

        # search query used
        if claim.get('query'):
            st.markdown(
                f"""<div style="background:#f8fafc; border-left:3px solid #94a3b8;
                    padding:8px 12px; border-radius:4px; margin:10px 0;
                    font-size:0.85rem; color:#475569;">
                    🔎 <strong>Search query:</strong> {claim['query']}
                </div>""",
                unsafe_allow_html=True
            )

        # evidence sources
        snippets = claim.get('evidence_snippets', [])
        sources = claim.get('evidence_sources', [])

        if snippets or sources:
            st.markdown("**Evidence retrieved:**")
            max_items = max(len(snippets), len(sources))
            for j in range(max_items):
                snippet = snippets[j] if j < len(snippets) else None
                source = sources[j] if j < len(sources) else None

                source_html = ""
                if source:
                    source_html = f'<a href="{source}" target="_blank" style="color:#2563eb; font-size:0.8rem; word-break:break-all;">{source}</a>'

                snippet_html = ""
                if snippet:
                    snippet_html = f'<p style="margin:4px 0 0 0; font-size:0.85rem; color:#374151;">{snippet}</p>'

                st.markdown(
                    f"""<div style="background:#f8fafc; border:1px solid #e2e8f0;
                        border-radius:6px; padding:10px 12px; margin:6px 0;">
                        <div style="font-weight:600; font-size:0.8rem; color:#64748b; margin-bottom:2px;">
                            Source {j + 1}
                        </div>
                        {source_html}
                        {snippet_html}
                    </div>""",
                    unsafe_allow_html=True
                )
        else:
            st.caption("No evidence retrieved for this claim.")

        if claim.get('error'):
            st.error(f"Error: {claim['error']}")


def display_results(results):
    if not results:
        return

    st.subheader("Overall Results")
    col1, col2 = st.columns(2)
    with col1:
        factuality_color = "green" if results['response_level_factuality'] else "red"
        st.markdown(
            f"**Response Factuality**: <span style='color:{factuality_color}'>"
            f"{'Factual' if results['response_level_factuality'] else 'Not Factual'}</span>",
            unsafe_allow_html=True
        )
    with col2:
        st.metric("Average Claim Factuality", f"{results['avg_claim_factuality']:.2%}")

    st.subheader("Query & Response")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Original Question:**")
        st.info(results['prompt'])
    with col2:
        st.markdown("**Response Being Checked:**")
        st.info(results['response'])

    st.subheader("Detailed Analysis")
    if results['reasoning']:
        st.markdown("**Reasoning:**")
        st.write(results['reasoning'])

    if results['claim_level_factuality']:
        claims = [c for c in results['claim_level_factuality'] if c is not None]
        n_factual = sum(1 for c in claims if c.get('factuality', False))
        n_total = len(claims)

        st.markdown(
            f"**Claim-by-Claim Analysis** — "
            f"{n_factual}/{n_total} claims factual"
        )

        for i, claim in enumerate(results['claim_level_factuality']):
            display_claim_evidence(claim, i)


# gui

st.title("FactSearch")
st.markdown("*Fact-checking system powered by SearXNG*")

# configure sidebar
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input(
    "OpenAI API Key:",
    type="password",
    help="Enter your OpenAI API key. You can find it at https://platform.openai.com/account/api-keys",
    placeholder="sk-..."
)
if api_key:
    import os
    os.environ['OPENAI_API_KEY'] = api_key

model_options = ["gpt-4o", "gpt-5", "gpt-5-mini", "gpt-5.2", "qwen3:1.7b", "qwen3:8b"]
selected_model = st.sidebar.selectbox("Select Foundation Model:", model_options, index=0)

is_local_model = selected_model.startswith("qwen")
can_initialize = bool(api_key) or is_local_model

if st.sidebar.button("Initialize FactSearch", type="primary", disabled=not can_initialize):
    if api_key:
        os.environ['OPENAI_API_KEY'] = api_key
    st.session_state.factool_instance = initialize_factool(selected_model)

if st.session_state.factool_instance:
    st.sidebar.success("FactSearch Ready")
elif api_key or is_local_model:
    st.sidebar.info("Click 'Initialise FactSearch' to get started")
else:
    st.sidebar.warning('Please enter an OpenAI key or select a local model')

# main window
if st.session_state.factool_instance:
    st.header("Input Section")
    tab1, tab2 = st.tabs(["Manual Input", "Example Templates"])
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            prompt = st.text_area("Question/Prompt:", placeholder="Enter the question or prompt here...", height=100)
        with col2:
            response = st.text_area("Response to Check:", placeholder="Enter the response that needs fact-checking...", height=100)
    with tab2:
        st.markdown("**Quick Examples:**")
        examples = [
            {"name": "Music Facts", "prompt": "Who wrote Purple Haze?", "response": "The song \"Purple Haze\" was written by Jimi Hendrix. It was released in 1967 and is one of his most famous tracks."},
            {"name": "Historical Facts", "prompt": "When did World War II end?", "response": "World War II ended on September 2, 1945, when Japan formally surrendered aboard the USS Missouri in Tokyo Bay."},
            {"name": "Science Facts", "prompt": "What is the speed of light?", "response": "The speed of light in a vacuum is approximately 300,000 kilometers per second, which is exactly 299,792,458 meters per second."}
        ]
        for example in examples:
            if st.button(f"Load: {example['name']}"):
                prompt = example['prompt']
                response = example['response']
                st.rerun()

    # run fact checking
    run_disabled = not (prompt and response and searxng_available)
    if st.button("Run Fact Check", type="primary", disabled=run_disabled):
        with st.spinner("Fact-checking in progress..."):
            try:
                inputs = [{"prompt": prompt, "response": response, "category": "kbqa"}]
                start_time = time.time()
                results = st.session_state.factool_instance.run(inputs)
                end_time = time.time()
                formatted_results = format_results(results)
                if formatted_results:
                    formatted_results['processing_time'] = end_time - start_time
                    st.session_state.results_history.insert(0, formatted_results)
                    if len(st.session_state.results_history) > 10:
                        st.session_state.results_history = st.session_state.results_history[:10]
                st.success(f"Fact-checking completed in {end_time - start_time:.2f} seconds")
            except Exception as e:
                st.error(f"Error during fact-checking: {str(e)}")
    elif not searxng_available:
        st.warning("Fact-checking disabled because SearXNG is not reachable.")

    # results display
    if st.session_state.results_history:
        st.header("Results")
        st.subheader("Latest Result")
        display_results(st.session_state.results_history[0])
        if len(st.session_state.results_history) > 1:
            st.subheader("Previous Results")
            for i, result in enumerate(st.session_state.results_history[1:], 1):
                with st.expander(f"Result {i}: {result['prompt'][:50]}..."):
                    display_results(result)
        st.subheader("Export Results")
        if st.button("Download Results as TXT"):
            txt_data = "\n\n".join([str(item) for item in st.session_state.results_history])
            st.download_button(
                label="Download TXT File",
                data=txt_data,
                file_name=f"factsearch_results_{time.strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
else:
    st.markdown("""
    This demo showcases a fact-checking system that uses:
    - **KBQA Pipeline**: Knowledge Base Question Answering for fact verification
    - **SearXNG Backend**: Self-hosted search engine for information retrieval
    - **LLM Integration**: Various GPT foundation models for NLP tasks
    """)
    st.info("Please initialize FactSearch using the sidebar to get started.")