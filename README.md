# Cyber Sierra AI Assistant

## About The Project

An AI powered App that lets users upload 1 or more CSV/Excel files, preview their data, ask questions about it, and even rate the responses.

Built for the FullStack Challenge for Candidates.

---

## Built With
**Streamlit** <br />
**LangChain** <br />
**OpenRouter** <br />
**Python**    

## How to Run Locally

1. Clone this repo
2. Get a free API Key at https://openrouter.ai/settings/keys
3. Create a `.env` file in the root folder:
   ```env
   OPENAI_API_KEY="OPENAI_API_KEY"
   OPENAI_API_BASE=https://openrouter.ai/api/v1
4. Run `streamlit run app.py`


## Thought Process 

### Issue with API Key
- I had issues with the given API Key so I had to use an API Key from OpenRouter
- Used `ChatOpenAI` instead of `OpenAI`

### Upload 1 or more csv/xls files
- Used `st.file_uploader(..., accept_multiple_files=True)` to allow multiple uploads.

### Display top N rows (N is a user defined parameter)
- `number_input` lets the user choose how many rows to view.
- For Excel files, the user can also choose the sheet to load.

### Ask questions to get answers from uploaded files
- Integrated `LangChain` with `create_pandas_dataframe_agent` to interpret prompts.
- The agent uses `ChatOpenAI` to communicate with GPT-3.5-turbo via OpenRouter.

### Prompt history and reuse
- Used `st.session_state.prompt_history` to track past prompts.
- A dropdown allows users to re-run previous questions easily.

### Get user feedback on answers
- Users can mark responses as 👍 Helpful or 👎 Not Helpful.
- Feedback is then stored in session.

---

## Security Considerations

### API Key Protection
- API keys are stored in an `.env` file and not included in the main file.
- `.env` is added to `.gitignore` to prevent commits.

### Input Safety
- User prompts are passed through an LLM agent with `handle_parsing_errors=True` to reduce errors.
- `allow_dangerous_code=True` is enabled to allow users to manipulate their own  data as they wish. Since users will upload their own files, there would be no risk to allow them to perform any operations on their own datasets.





