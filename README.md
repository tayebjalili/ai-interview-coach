# AI Interview Coach

A mock interview practice studio built with **Streamlit** and **Groq**. It runs a short,
adaptive interview for a role you choose, then scores your answers and writes a report you
can download as Markdown.

## Features

- Setup for candidate name, position, company, seniority, difficulty and focus area
- Five-question adaptive interview streamed token by token
- Live timer, progress bar and a transcript you can review before finishing
- Structured feedback: overall score, per-criterion scores, strengths, improvements and next steps
- Downloadable Markdown report

## Run locally

```bash
python -m pip install -r requirements.txt
```

Create `.streamlit/secrets.toml` with your Groq API key (get one at
<https://console.groq.com/keys>):

```toml
GROQ_API_KEY = "gsk_your_key_here"
```

Then start the app from the repository root:

```bash
python -m streamlit run app.py
```

It opens on <http://localhost:8501>.

`.streamlit/secrets.toml` is listed in `.gitignore` and is never committed.

## Deploy to Streamlit Community Cloud

1. Push this repository to GitHub (already done for `tayebjalili/ai-interview-coach`).
2. Go to <https://share.streamlit.io> and sign in with GitHub.
3. Click **Create app** → **Deploy a public app from GitHub**.
4. Fill in:
   - **Repository:** `tayebjalili/ai-interview-coach`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Open **Advanced settings → Secrets** and paste:

   ```toml
   GROQ_API_KEY = "gsk_your_key_here"
   ```

6. Click **Deploy**. Streamlit installs `requirements.txt`, injects the secret into
   `st.secrets`, and your app is live at `https://<your-app>.streamlit.app`.

The optional secret `GROQ_MODEL` overrides the default model
(`openai/gpt-oss-120b`).

## Project layout

```
app.py                  # the whole app: UI, prompts, interview flow, feedback, report
requirements.txt        # runtime dependencies
.streamlit/config.toml  # dark theme and server settings
.streamlit/secrets.toml # local API key (git-ignored)
```
