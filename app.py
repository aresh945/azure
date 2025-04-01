import streamlit as st
import pandas as pd
import os
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.chat_models import ChatOpenAI
import matplotlib.pyplot as plt
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Load secrets from Azure Key Vault
KVUri = "https://keyvault-data-explorer.vault.azure.net"
credential = DefaultAzureCredential()
client = SecretClient(vault_url=KVUri, credential=credential)

openai_key = client.get_secret("OPENAI-API-KEY").value
openai_base = client.get_secret("OPENAI-API-BASE").value

# Set env vars for LangChain compatibility
os.environ["OPENAI_API_KEY"] = openai_key
os.environ["OPENAI_API_BASE"] = openai_base

# Debug line to verify secrets loaded correctly (remove after testing)
st.write("🔑 Key loaded:", openai_key[:5] + "..." + openai_key[-4:])

# Define LLM agent
def create_agent(df):
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        openai_api_key=openai_key,
        openai_api_base=openai_base
    )
    return create_pandas_dataframe_agent(llm, df, verbose=True, handle_parsing_errors=True, allow_dangerous_code=True)

# Session state init
for key, default in {
    "prompt_history": [],
    "reuse_prompt": "",
    "feedback": {},
    "answers": {}
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Streamlit layout
st.title("Cyber Sierra AI Assistant")

uploaded_files = st.file_uploader("Upload CSV or Excel files", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    filenames = [f.name for f in uploaded_files]
    selected_filename = st.selectbox("Select file(s):", filenames)
    selected_file = next(f for f in uploaded_files if f.name == selected_filename)

    if selected_filename.endswith(".csv"):
        df = pd.read_csv(selected_file)
    else:
        xls = pd.ExcelFile(selected_file, engine="openpyxl")
        sheet_names = xls.sheet_names
        selected_sheet = st.selectbox("Select a sheet:", sheet_names)
        df = pd.read_excel(xls, sheet_name=selected_sheet, engine="openpyxl")

    st.write("### Preview your data:")
    n_rows = st.number_input("How many rows do you want to see?", min_value=1, max_value=len(df), value=5)
    st.dataframe(df.head(n_rows))

    st.write("### Ask questions:")
    col1, col2 = st.columns(2)

    with col1:
        question = st.text_input("Enter your question:", value=st.session_state.reuse_prompt)

    with col2:
        if st.session_state.prompt_history:
            reuse = st.selectbox("Past prompts:", [""] + list(st.session_state.prompt_history))
            if reuse:
                st.session_state.reuse_prompt = reuse

    if st.session_state.reuse_prompt and question == st.session_state.reuse_prompt:
        st.session_state.reuse_prompt = ""

    if question.strip():
        if question not in st.session_state.prompt_history:
            st.session_state.prompt_history.append(question)

        if question not in st.session_state.answers:
            agent = create_agent(df)
            with st.spinner("Loading..."):
                answer = agent.run(question)
                st.session_state.answers[question] = answer
        else:
            answer = st.session_state.answers[question]

        st.write("### Answer:")
        st.write(answer)

        fig = plt.gcf()
        if fig.get_axes():
            st.pyplot(fig)
            plt.clf()

        if question not in st.session_state.feedback:
            col3, col4 = st.columns(2)
            with col3:
                if st.button("👍 Helpful", key=f"helpful_{question}"):
                    st.session_state.feedback[question] = "Helpful"
                    st.rerun()
            with col4:
                if st.button("👎 Not Helpful", key=f"not_helpful_{question}"):
                    st.session_state.feedback[question] = "Not Helpful"
                    st.rerun()
        else:
            fb = st.session_state.feedback[question]
            if fb == "Helpful":
                st.success("Thank you for your feedback!")
            else:
                st.info("Thank you for your feedback!")
