"""AI Interview Coach - a Streamlit mock-interview studio powered by Groq."""

from __future__ import annotations

import html
import json
import re
from datetime import datetime

import streamlit as st
from groq import Groq

# ============================================================
# CONFIGURATION
# ============================================================
MAX_QUESTIONS = 5
DEFAULT_MODEL = "openai/gpt-oss-120b"

LEVELS = ["Junior", "Mid-level", "Senior"]
POSITIONS = ["Data Scientist", "Data Engineer", "ML Engineer", "BI Analyst", "Financial Analyst"]
COMPANIES = ["Amazon", "Meta", "Udemy", "365 Company", "Nestle", "LinkedIn", "Spotify"]
DIFFICULTIES = ["Easy", "Balanced", "Challenging", "Brutal"]
FOCUS_AREAS = ["General", "Technical", "Behavioral", "System Design", "Leadership"]

INTERVIEWER_AVATAR = "🎙️"

st.set_page_config(
    page_title="AI Interview Coach",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="auto",
)

# ============================================================
# STYLES
# ============================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root{
    --bg:#070B14;
    --surface:rgba(255,255,255,.045);
    --border:rgba(255,255,255,.09);
    --border-strong:rgba(255,255,255,.16);
    --text:#E9EEF9;
    --muted:#93A1B8;
    --violet:#8B7CFF;
    --cyan:#38D9F0;
    --pink:#FF7AB6;
    --green:#4ADE9B;
    --amber:#FFC46B;
    --grad:linear-gradient(120deg,#8B7CFF 0%,#38D9F0 100%);
}

html, body, .stApp, .stApp p, .stApp li, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4,
.stApp input, .stApp textarea, .stApp button, .stApp [data-testid="stMarkdownContainer"]{
    font-family:'Plus Jakarta Sans','Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
}
.stApp [data-testid="stIconMaterial"], .stApp .material-symbols-rounded{
    font-family:'Material Symbols Rounded' !important;
}

.stApp, [data-testid="stAppViewContainer"]{
    background:
        radial-gradient(1100px 620px at 10% -12%, rgba(139,124,255,.20), transparent 62%),
        radial-gradient(900px 520px at 94% -4%, rgba(56,217,240,.14), transparent 58%),
        radial-gradient(760px 720px at 50% 112%, rgba(255,122,182,.09), transparent 62%),
        #070B14;
    background-attachment:fixed;
    color:var(--text);
}

[data-testid="stHeader"]{background:transparent;}
[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"]{display:none;}
#MainMenu, footer{visibility:hidden;}

[data-testid="stMainBlockContainer"], .block-container{
    padding-top:2.2rem;
    padding-bottom:3.4rem;
    max-width:1120px;
}

/* ---------- cards ---------- */
[class*="st-key-card-"]{
    background:linear-gradient(180deg, rgba(255,255,255,.062), rgba(255,255,255,.022));
    border:1px solid var(--border);
    border-radius:22px;
    padding:1.4rem 1.5rem;
    box-shadow:0 24px 60px -34px rgba(0,0,0,.95), inset 0 1px 0 rgba(255,255,255,.05);
    backdrop-filter:blur(14px);
    -webkit-backdrop-filter:blur(14px);
}
[class*="st-key-card-strengths"]{border-left:3px solid rgba(74,222,155,.65);}
[class*="st-key-card-improve"]{border-left:3px solid rgba(255,196,107,.65);}

/* ---------- hero ---------- */
.hero{text-align:center; padding:.4rem 0 1.7rem;}
.hero-badge{
    display:inline-flex; align-items:center; gap:.45rem;
    font-size:.72rem; letter-spacing:.16em; text-transform:uppercase;
    color:#C7D2E5; background:rgba(255,255,255,.055);
    border:1px solid var(--border); padding:.4rem .9rem; border-radius:999px;
}
.hero h1{
    font-size:2.65rem; line-height:1.1; font-weight:800; letter-spacing:-.035em;
    color:#F5F8FF; margin:1.05rem 0 .65rem;
}
.hero h1 span{
    background:var(--grad); -webkit-background-clip:text; background-clip:text;
    -webkit-text-fill-color:transparent;
}
.hero p{color:var(--muted); max-width:660px; margin:0 auto; font-size:1rem; line-height:1.65;}
.hero-chips{display:flex; flex-wrap:wrap; gap:.5rem; justify-content:center; margin-top:1.2rem;}
.chip{
    font-size:.77rem; color:#C7D2E5; background:rgba(255,255,255,.045);
    border:1px solid var(--border); padding:.36rem .78rem; border-radius:999px;
}

/* ---------- card headings ---------- */
.card-title{display:flex; align-items:center; gap:.65rem; font-size:1.02rem; font-weight:700; color:#F1F5FF;}
.card-title .icon{
    display:grid; place-items:center; width:34px; height:34px; border-radius:11px;
    background:rgba(139,124,255,.16); border:1px solid rgba(139,124,255,.28); font-size:1rem;
}
.card-sub{color:var(--muted); font-size:.85rem; margin:.25rem 0 .9rem;}
.side-label{
    font-size:.68rem; letter-spacing:.16em; text-transform:uppercase;
    color:#7C8AA0; margin:.9rem 0 .45rem; font-weight:600;
}

/* ---------- steps ---------- */
.steps{display:flex; flex-direction:column; gap:.85rem; margin-top:.55rem;}
.step-item{display:flex; gap:.75rem; align-items:flex-start;}
.step-num{
    flex:0 0 auto; width:26px; height:26px; border-radius:9px; display:grid; place-items:center;
    font-size:.78rem; font-weight:700; color:#08101E; background:var(--grad);
}
.step-item b{display:block; font-size:.88rem; color:#EDF2FF; font-weight:600;}
.step-item div span{font-size:.8rem; color:var(--muted); line-height:1.5;}
.step-item .step-num{font-size:.78rem; font-weight:800; color:#08101E; line-height:1;}

/* ---------- sidebar ---------- */
[data-testid="stSidebar"]{
    background:linear-gradient(180deg, rgba(11,17,31,.98), rgba(7,11,20,.98));
    border-right:1px solid rgba(255,255,255,.06);
}
[data-testid="stSidebarContent"]{padding-top:1.4rem;}
.brand{display:flex; align-items:center; gap:.75rem; padding:.1rem 0 .4rem;}
.brand-mark{
    display:grid; place-items:center; width:42px; height:42px; border-radius:14px;
    background:var(--grad); font-size:1.15rem; box-shadow:0 12px 26px -14px rgba(139,124,255,.9);
}
.brand b{display:block; font-size:.98rem; color:#F3F7FF; letter-spacing:-.01em;}
.brand small{color:var(--muted); font-size:.68rem; letter-spacing:.14em; text-transform:uppercase;}

.stepper{display:flex; flex-direction:column; gap:.7rem; margin:.55rem 0 .2rem;}
.step{display:flex; align-items:center; gap:.65rem; color:var(--muted);}
.step .dot{flex:0 0 auto; width:9px; height:9px; border-radius:50%; background:rgba(255,255,255,.18);}
.step > div{display:flex; flex-direction:column;}
.step b{font-size:.84rem; font-weight:600; color:inherit;}
.step .sub{font-size:.72rem; color:#76839A;}
.step.active{color:#F1F5FF;}
.step.active b{font-weight:700;}
.step.active .dot{background:var(--cyan); box-shadow:0 0 0 4px rgba(56,217,240,.16);}
.step.done .dot{background:var(--green);}
.step.done{color:#A9B7CD;}

.kv{
    display:flex; justify-content:space-between; gap:1rem; padding:.42rem 0;
    border-bottom:1px dashed rgba(255,255,255,.07); font-size:.83rem;
}
.kv:last-child{border-bottom:none;}
.kv span{color:var(--muted);}
.kv b{color:#E9EEF9; font-weight:600; text-align:right;}

.bar{height:8px; border-radius:99px; background:rgba(255,255,255,.08); overflow:hidden;}
.bar i{display:block; height:100%; border-radius:99px; background:var(--grad); transition:width .5s ease;}
.side-note{font-size:.74rem; color:#76839A; margin-top:.45rem;}
.side-footer{
    font-size:.7rem; color:#5F6C81; letter-spacing:.04em; padding-top:1rem;
    border-top:1px solid rgba(255,255,255,.06); margin-top:1rem;
}
.timer{display:flex; align-items:center; gap:.5rem; font-size:.82rem; color:var(--muted);}
.timer b{font-size:1.05rem; color:#F3F7FF; font-variant-numeric:tabular-nums;}

/* ---------- interview ---------- */
.quiz-head{display:flex; align-items:center; justify-content:space-between; gap:1rem; margin-bottom:.85rem;}
.quiz-meta{display:flex; align-items:center; gap:.45rem; flex-wrap:wrap;}
.pill{
    font-size:.74rem; padding:.3rem .7rem; border-radius:999px;
    border:1px solid var(--border); background:rgba(255,255,255,.05); color:#C7D2E5;
}
.pill.strong{
    color:#DCD6FF; border-color:rgba(139,124,255,.35); background:rgba(139,124,255,.14);
}
.quiz-foot{
    display:flex; align-items:center; justify-content:space-between; gap:1rem;
    font-size:.78rem; color:var(--muted); margin:.1rem 0 1.25rem;
}

/* ---------- chat ---------- */
[data-testid="stChatMessage"]{
    background:rgba(255,255,255,.038);
    border:1px solid var(--border);
    border-radius:18px;
    padding:1rem 1.15rem;
    margin-bottom:.85rem;
    backdrop-filter:blur(10px);
}
[data-testid="stChatMessage"]:has(.role-ai){
    background:linear-gradient(135deg, rgba(139,124,255,.13), rgba(56,217,240,.055));
    border-color:rgba(139,124,255,.24);
}
[data-testid="stChatMessage"]:has(.role-me){
    background:linear-gradient(135deg, rgba(56,217,240,.09), rgba(255,255,255,.028));
    border-color:rgba(56,217,240,.2);
}
.role-ai, .role-me{display:none;}
[data-testid="stChatMessage"] [data-testid="stChatMessageContent"] p{
    line-height:1.62; color:#E6EDF9; margin-bottom:.3rem;
}
[data-testid="stChatMessageAvatarCustom"], [data-testid="stChatMessageAvatarAssistant"]{
    background:rgba(139,124,255,.18) !important; border:1px solid rgba(139,124,255,.3) !important;
}
[data-testid="stChatMessageAvatarUser"]{
    background:rgba(56,217,240,.16) !important; border:1px solid rgba(56,217,240,.3) !important;
}

.thinking{display:flex; align-items:center; gap:.5rem; color:var(--muted); font-size:.86rem;}
.thinking span{
    width:6px; height:6px; border-radius:50%; background:var(--violet);
    animation:bounce 1.2s infinite ease-in-out;
}
.thinking span:nth-child(2){animation-delay:.15s; background:var(--cyan);}
.thinking span:nth-child(3){animation-delay:.3s; background:var(--pink);}
@keyframes bounce{0%,80%,100%{transform:translateY(0); opacity:.45;} 40%{transform:translateY(-4px); opacity:1;}}

[data-testid="stChatInput"]{
    border-radius:16px; background:rgba(255,255,255,.05); border:1px solid var(--border);
    transition:border-color .2s ease, box-shadow .2s ease;
}
[data-testid="stChatInput"]:focus-within{
    border-color:rgba(139,124,255,.55); box-shadow:0 0 0 4px rgba(139,124,255,.13);
}
[data-testid="stChatInput"] textarea{color:#F1F5FF;}
[data-testid="stBottom"] > div{background:transparent;}
[data-testid="stBottomBlockContainer"]{padding-bottom:1rem;}

/* ---------- controls ---------- */
.stButton button, .stDownloadButton button, [data-testid="stFormSubmitButton"] button{
    border-radius:12px; font-weight:600; font-size:.88rem;
    border:1px solid var(--border-strong); background:rgba(255,255,255,.06); color:#EAF0FB;
    transition:all .18s ease;
}
.stButton button:hover, .stDownloadButton button:hover, [data-testid="stFormSubmitButton"] button:hover{
    border-color:rgba(139,124,255,.6); background:rgba(139,124,255,.14);
    color:#fff; transform:translateY(-1px);
}
button[kind*="primary"]{
    background:var(--grad) !important; border:none !important; color:#08101E !important;
    box-shadow:0 16px 32px -18px rgba(139,124,255,.95);
}
button[kind*="primary"]:hover{filter:brightness(1.07); transform:translateY(-1px);}

[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea{
    background:rgba(255,255,255,.045) !important; border:1px solid var(--border) !important;
    border-radius:12px !important; color:#F1F5FF !important;
}
[data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus{
    border-color:rgba(139,124,255,.6) !important;
    box-shadow:0 0 0 3px rgba(139,124,255,.15) !important;
}
[data-baseweb="select"] > div{
    background:rgba(255,255,255,.045) !important;
    border-color:var(--border) !important;
    border-radius:12px !important;
}
[data-testid="stWidgetLabel"] p{
    font-size:.8rem !important; font-weight:600; color:#B9C6DA !important;
}
[data-testid="stForm"]{border:none !important; padding:0 !important; background:transparent !important;}
[data-testid="stExpander"] details{
    border-radius:14px !important; background:rgba(255,255,255,.035) !important;
    border:1px solid var(--border) !important;
}
[data-testid="stAlert"]{border-radius:14px;}

/* ---------- feedback ---------- */
.report-head{display:flex; align-items:flex-end; justify-content:space-between; gap:1rem; flex-wrap:wrap; margin-bottom:1.1rem;}
.report-head h2{margin:0 0 .25rem; font-size:1.75rem; letter-spacing:-.025em; color:#F5F8FF;}
.report-head .meta{color:var(--muted); font-size:.85rem;}

.score-ring{
    --pct:0; --band:var(--violet);
    width:158px; height:158px; border-radius:50%; margin:.4rem auto 0;
    background:conic-gradient(var(--band) calc(var(--pct) * 1%), rgba(255,255,255,.08) 0);
    display:grid; place-items:center; position:relative;
}
.score-ring::after{
    content:""; position:absolute; inset:-4px; border-radius:50%;
    box-shadow:0 0 46px -12px var(--band); opacity:.4; pointer-events:none;
}
.score-ring .inner{
    width:126px; height:126px; border-radius:50%; background:#0B1220;
    display:grid; place-items:center; text-align:center; border:1px solid rgba(255,255,255,.06);
}
.score-ring .num{font-size:2.35rem; font-weight:800; color:#F6F9FF; line-height:1;}
.score-ring .num small{font-size:.85rem; color:var(--muted); font-weight:600; margin-left:.1rem;}
.score-ring .verdict{
    margin-top:.35rem; font-size:.64rem; text-transform:uppercase;
    letter-spacing:.13em; color:var(--muted);
}
.score-caption{text-align:center; color:var(--muted); font-size:.78rem; margin-top:.85rem;}

.crit{margin-bottom:.85rem;}
.crit:last-child{margin-bottom:0;}
.crit-top{display:flex; justify-content:space-between; font-size:.82rem; margin-bottom:.32rem;}
.crit-top span{color:#C7D3E6;}
.crit-top b{color:#F1F5FF; font-variant-numeric:tabular-nums;}
.crit-bar{height:7px; border-radius:99px; background:rgba(255,255,255,.08); overflow:hidden;}
.crit-bar i{display:block; height:100%; border-radius:99px; background:var(--grad);}

ul.clean{margin:.5rem 0 0; padding-left:0; list-style:none;}
ul.clean li{
    position:relative; padding-left:1.45rem; margin-bottom:.6rem;
    color:#DCE5F3; font-size:.89rem; line-height:1.55;
}
ul.clean li:last-child{margin-bottom:0;}
ul.clean li::before{content:"✓"; position:absolute; left:0; color:var(--green); font-weight:700;}
ul.clean.warn li::before{content:"→"; color:var(--amber);}

.roadmap{display:flex; flex-direction:column; gap:.7rem; margin-top:.4rem;}
.roadmap .r{display:flex; gap:.75rem; align-items:flex-start; font-size:.89rem; color:#DCE5F3; line-height:1.55;}
.roadmap .r b{
    display:grid; place-items:center; flex:0 0 auto; width:24px; height:24px; border-radius:8px;
    background:rgba(56,217,240,.16); color:#9BE9F6; font-size:.74rem;
}
.empty-note{color:var(--muted); font-size:.85rem; font-style:italic;}

.tiles{display:grid; grid-template-columns:repeat(4,1fr); gap:.75rem; margin:.2rem 0 1rem;}
.tile{
    background:rgba(255,255,255,.045); border:1px solid var(--border);
    border-radius:15px; padding:.85rem .95rem;
}
.tile .v{font-size:1.2rem; font-weight:700; color:#F3F7FF; letter-spacing:-.01em;}
.tile .l{
    font-size:.66rem; text-transform:uppercase; letter-spacing:.12em;
    color:var(--muted); margin-top:.2rem;
}

.center-note{text-align:center; color:#76839A; font-size:.76rem; margin-top:.4rem;}

@media (max-width:820px){
    .hero h1{font-size:1.9rem;}
    .hero p{font-size:.94rem;}
    .tiles{grid-template-columns:repeat(2,1fr);}
    [data-testid="stMainBlockContainer"], .block-container{padding-left:1rem; padding-right:1rem;}
}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# SESSION STATE
# ============================================================
DEFAULTS = {
    "phase": "setup",
    "messages": [],
    "answers": 0,
    "name": "",
    "years": "",
    "skills": "",
    "experience": "",
    "level": "Mid-level",
    "position": "Data Scientist",
    "company": "Amazon",
    "difficulty": "Balanced",
    "focus_area": "General",
    "started_at": None,
    "ended_at": None,
    "feedback": None,
}
for _key, _value in DEFAULTS.items():
    if _key not in st.session_state:
        st.session_state[_key] = _value

# ============================================================
# HELPERS
# ============================================================
def secret(key: str, default: str = "") -> str:
    try:
        value = st.secrets.get(key, default)
    except Exception:
        return default
    return str(value) if value else default


def model_name() -> str:
    return secret("GROQ_MODEL", DEFAULT_MODEL)


def api_ready() -> bool:
    return bool(secret("GROQ_API_KEY"))


@st.cache_resource(show_spinner=False)
def _groq_client(api_key: str) -> Groq:
    return Groq(api_key=api_key)


def client() -> Groq:
    return _groq_client(secret("GROQ_API_KEY"))


def friendly_error(exc: Exception) -> str:
    text = str(exc)
    low = text.lower()
    if "401" in text or "invalid api key" in low or "api key" in low:
        return "The Groq API key was rejected. Check `GROQ_API_KEY` in `streamlit/.streamlit/secrets.toml`."
    if "429" in text or "rate limit" in low:
        return "Groq is rate-limiting requests right now. Wait a few seconds and try again."
    if "model" in low and ("not found" in low or "decommission" in low):
        return f"The model `{model_name()}` is not available. Set `GROQ_MODEL` in your secrets to a supported model."
    if "connection" in low or "timeout" in low:
        return "Could not reach Groq. Check your internet connection and try again."
    return f"Groq returned an error: {text[:220]}"


def parse_stream(stream):
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content


def elapsed_seconds() -> int:
    start = st.session_state.started_at
    if not start:
        return 0
    end = st.session_state.ended_at or datetime.now()
    return max(0, int((end - start).total_seconds()))


def fmt_duration(seconds: int) -> str:
    minutes, secs = divmod(seconds, 60)
    return f"{minutes}m {secs:02d}s"


def restart() -> None:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


def card_title(icon: str, title: str, subtitle: str = "") -> None:
    sub = f'<div class="card-sub">{html.escape(subtitle)}</div>' if subtitle else ""
    st.markdown(
        f'<div class="card-title"><span class="icon">{icon}</span>'
        f"<span>{html.escape(title)}</span></div>{sub}",
        unsafe_allow_html=True,
    )


def tiles_html(items) -> str:
    cells = "".join(
        f'<div class="tile"><div class="v">{html.escape(str(value))}</div>'
        f'<div class="l">{html.escape(str(label))}</div></div>'
        for label, value in items
    )
    return f'<div class="tiles">{cells}</div>'


def steps_html(items) -> str:
    rows = "".join(
        f'<div class="step-item"><span class="step-num">{index}</span>'
        f"<div><b>{html.escape(title)}</b><span>{html.escape(detail)}</span></div></div>"
        for index, (title, detail) in enumerate(items, 1)
    )
    return f'<div class="steps">{rows}</div>'


def bullets_html(items, kind: str = "good") -> str:
    if not items:
        return '<div class="empty-note">Nothing flagged here.</div>'
    css = "clean" if kind == "good" else "clean warn"
    rows = "".join(f"<li>{html.escape(str(item))}</li>" for item in items)
    return f'<ul class="{css}">{rows}</ul>'


def roadmap_html(items) -> str:
    rows = "".join(
        f'<div class="r"><b>{index}</b><span>{html.escape(str(item))}</span></div>'
        for index, item in enumerate(items, 1)
    )
    return f'<div class="roadmap">{rows}</div>'


def option_index(options, value) -> int:
    return options.index(value) if value in options else 0


# ============================================================
# PROMPTS & MODEL CALLS
# ============================================================
def interviewer_prompt() -> str:
    state = st.session_state
    asked = state.answers + 1
    difficulty_note = {
        "Easy": "warm, foundational questions with plenty of encouragement",
        "Balanced": "realistic questions of mixed difficulty",
        "Challenging": "probing questions that expect concrete examples and trade-offs",
        "Brutal": "tough, high-pressure questions with follow-ups on weak spots",
    }.get(state.difficulty, "realistic questions")
    closing = " This is the final question, so make it a strong closer." if asked >= MAX_QUESTIONS else ""
    parts = str(state.name).split()
    first_name = parts[0] if parts else "there"

    return f"""You are Alex Morgan, a senior hiring manager at {state.company} interviewing {state.name} for a {state.level} {state.position} role.

Candidate background: {state.experience or "not provided"}.
Skills: {state.skills or "not provided"}.
Interview difficulty: {state.difficulty} - {difficulty_note}. Focus area: {state.focus_area}.

Rules:
- Ask exactly ONE question per reply, then stop.
- On your very first reply, greet {first_name} in one short sentence and ask your first question. Do not mention being an AI.
- After each answer, acknowledge it in one short sentence, then ask the next question.
- Keep the whole reply under 60 words. No headings, no bullet points, no numbered questions.
- Make questions realistic and specific to the role and focus area, and do not repeat earlier questions.
- This is question {asked} of {MAX_QUESTIONS}.{closing}
- Never score or evaluate the candidate during the interview."""


def interview_messages() -> list:
    history = [m for m in st.session_state.messages if m["role"] != "system"]
    return [{"role": "system", "content": interviewer_prompt()}] + history


def generate_question() -> None:
    """Stream the next interviewer turn into the current chat bubble."""
    slot = st.empty()
    slot.markdown(
        '<div class="thinking"><span></span><span></span><span></span>'
        "Interviewer is thinking…</div>",
        unsafe_allow_html=True,
    )
    try:
        stream = client().chat.completions.create(
            model=model_name(),
            messages=interview_messages(),
            stream=True,
            temperature=0.7,
        )
        slot.empty()
        reply = st.write_stream(parse_stream(stream))
    except Exception as exc:  # surfaced to the user
        slot.empty()
        st.error(friendly_error(exc))
        if st.button("Try again", key="retry_question"):
            st.rerun()
        return

    reply = reply.strip() if isinstance(reply, str) else ""
    if reply:
        st.session_state.messages.append({"role": "assistant", "content": reply})
    else:
        st.warning("The interviewer returned an empty reply.")
        if st.button("Ask again", key="retry_question"):
            st.rerun()


def submit_answer(text: str) -> None:
    state = st.session_state
    state.messages.append({"role": "user", "content": text})
    state.answers += 1
    if state.answers >= MAX_QUESTIONS:
        state.phase = "review"
        state.ended_at = datetime.now()
    st.rerun()


def clamp_int(value):
    try:
        number = int(round(float(value)))
    except (TypeError, ValueError):
        return None
    return max(0, min(10, number))


def clean_items(value, limit: int = 4) -> list:
    if isinstance(value, str):
        parts = re.split(r"[\n;]", value)
    elif isinstance(value, (list, tuple)):
        parts = [str(part) for part in value]
    else:
        return []
    cleaned = [part.strip(" -•\t") for part in parts]
    return [part for part in cleaned if part][:limit]


def loads_json(raw: str):
    text = (raw or "").strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except Exception:
            return None
    return None


def build_feedback() -> dict:
    state = st.session_state
    transcript = "\n".join(
        f"{'Candidate' if m['role'] == 'user' else 'Interviewer'}: {m['content']}"
        for m in state.messages
        if m["role"] != "system"
    )

    prompt = f"""You are an expert interview coach. Assess this mock interview for a {state.level} {state.position} role at {state.company} (difficulty: {state.difficulty}, focus area: {state.focus_area}).

Return ONLY a valid JSON object - no markdown fences, no commentary - in exactly this shape:
{{
  "score": <integer 0-10>,
  "verdict": "<2-3 words, e.g. Strong hire / Promising / Needs work>",
  "summary": "<3-4 sentences of direct, second-person feedback>",
  "criteria": {{"Communication": <0-10>, "Structure": <0-10>, "Relevance": <0-10>, "Depth": <0-10>, "Confidence": <0-10>}},
  "strengths": ["<specific strength>", "<specific strength>", "<specific strength>"],
  "improvements": ["<specific improvement>", "<specific improvement>", "<specific improvement>"],
  "next_steps": ["<actionable practice step>", "<actionable practice step>", "<actionable practice step>"]
}}

Reference what the candidate actually said. Keep each list item under 22 words. Be honest but constructive."""

    completion = client().chat.completions.create(
        model=model_name(),
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Transcript:\n\n{transcript}"},
        ],
        temperature=0.3,
        max_completion_tokens=2000,
    )
    return normalize_feedback(completion.choices[0].message.content or "")


def normalize_feedback(raw: str) -> dict:
    data = loads_json(raw)
    if not isinstance(data, dict):
        data = {}

    score = clamp_int(data.get("score"))
    summary = str(data.get("summary") or "").strip()
    verdict = str(data.get("verdict") or "").strip()

    criteria = {}
    criteria_raw = data.get("criteria")
    if isinstance(criteria_raw, dict):
        for key, value in criteria_raw.items():
            label = str(key).replace("_", " ").strip().title()
            number = clamp_int(value)
            if label and number is not None:
                criteria[label] = number

    strengths = clean_items(data.get("strengths"))
    improvements = clean_items(data.get("improvements"))
    next_steps = clean_items(data.get("next_steps"))

    if not summary:
        summary = raw.strip()
    if not verdict:
        verdict = "Interview report"

    return {
        "ok": bool(score is not None or strengths or improvements or criteria),
        "score": score,
        "verdict": verdict,
        "summary": summary,
        "criteria": criteria,
        "strengths": strengths,
        "improvements": improvements,
        "next_steps": next_steps,
        "raw": raw,
    }


def score_band(score):
    if score is None:
        return "#8B7CFF", "Not scored"
    if score >= 8:
        return "#4ADE9B", "Strong"
    if score >= 6:
        return "#38D9F0", "Promising"
    if score >= 4:
        return "#FFC46B", "Needs work"
    return "#FF7AB6", "Early stage"


def build_report(feedback: dict) -> str:
    state = st.session_state
    score = feedback["score"]
    lines = [
        "# Mock Interview Report",
        "",
        f"**Candidate:** {state.name}",
        f"**Role:** {state.level} {state.position} at {state.company}",
        f"**Difficulty:** {state.difficulty}  ·  **Focus:** {state.focus_area}",
        f"**Date:** {datetime.now().strftime('%d %b %Y, %H:%M')}",
        f"**Duration:** {fmt_duration(elapsed_seconds())}  ·  **Questions answered:** {state.answers}/{MAX_QUESTIONS}",
        "",
        "## Score",
        "",
        f"**{score if score is not None else '-'} / 10** - {feedback['verdict']}",
        "",
    ]
    if feedback["criteria"]:
        lines += ["| Criteria | Score |", "| --- | --- |"]
        lines += [f"| {label} | {value}/10 |" for label, value in feedback["criteria"].items()]
        lines.append("")
    if feedback["summary"]:
        lines += ["## Overall feedback", "", feedback["summary"], ""]
    sections = (
        ("Strengths", "strengths"),
        ("Areas to improve", "improvements"),
        ("Next steps", "next_steps"),
    )
    for heading, key in sections:
        items = feedback[key]
        if items:
            lines += [f"## {heading}", ""] + [f"- {item}" for item in items] + [""]
    lines += ["## Transcript", ""]
    for message in state.messages:
        if message["role"] == "system":
            continue
        who = "Candidate" if message["role"] == "user" else "Interviewer"
        lines += [f"**{who}:** {message['content']}", ""]
    return "\n".join(lines)


# ============================================================
# SIDEBAR & DIALOGS
# ============================================================
@st.fragment(run_every=1)
def live_timer() -> None:
    if st.session_state.get("started_at") and st.session_state.phase in ("interview", "review"):
        st.markdown(
            f'<div class="timer">⏱ <b>{fmt_duration(elapsed_seconds())}</b><span>elapsed</span></div>',
            unsafe_allow_html=True,
        )


@st.dialog("Start a new session?")
def new_session_dialog() -> None:
    st.write("This clears your current interview, answers and feedback.")
    first, second = st.columns(2)
    if first.button("Start over", type="primary", use_container_width=True):
        restart()
    if second.button("Keep this session", use_container_width=True):
        st.rerun()


@st.dialog("End the interview now?")
def end_interview_dialog() -> None:
    st.write("You can still get a scored report from the answers you have given so far.")
    if st.button("End and see results", type="primary", use_container_width=True):
        st.session_state.ended_at = datetime.now()
        st.session_state.phase = "review"
        st.rerun()
    if st.button("Continue interview", use_container_width=True):
        st.rerun()


def render_sidebar() -> None:
    state = st.session_state
    phase = state.phase
    current = {"setup": 0, "interview": 1, "review": 2, "feedback": 2}.get(phase, 0)

    with st.sidebar:
        st.markdown(
            '<div class="brand"><span class="brand-mark">🎯</span>'
            "<div><b>Interview Coach</b><small>AI practice studio</small></div></div>",
            unsafe_allow_html=True,
        )

        steps = [
            ("Set up", "Profile & target role"),
            ("Interview", "Five adaptive questions"),
            ("Report", "Scores & next steps"),
        ]
        rows = []
        for index, (title, subtitle) in enumerate(steps):
            css = "step done" if index < current else ("step active" if index == current else "step")
            rows.append(
                f'<div class="{css}"><span class="dot"></span>'
                f'<div><b>{title}</b><span class="sub">{subtitle}</span></div></div>'
            )
        st.markdown(f'<div class="stepper">{"".join(rows)}</div>', unsafe_allow_html=True)

        if phase == "setup":
            st.markdown('<div class="side-label">What you get</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="side-note">A tailored mock interview, a score across five criteria, '
                "and a downloadable report you can keep.</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<div class="side-label">Session</div>', unsafe_allow_html=True)
            details = [
                ("Candidate", state.name or "—"),
                ("Role", f"{state.level} {state.position}"),
                ("Company", state.company),
                ("Difficulty", state.difficulty),
                ("Focus", state.focus_area),
            ]
            st.markdown(
                "".join(
                    f'<div class="kv"><span>{html.escape(label)}</span>'
                    f"<b>{html.escape(str(value))}</b></div>"
                    for label, value in details
                ),
                unsafe_allow_html=True,
            )

            st.markdown('<div class="side-label">Progress</div>', unsafe_allow_html=True)
            pct = int(state.answers / MAX_QUESTIONS * 100)
            st.markdown(
                f'<div class="bar"><i style="width:{pct}%"></i></div>'
                f'<div class="side-note">{state.answers} of {MAX_QUESTIONS} questions answered</div>',
                unsafe_allow_html=True,
            )
            live_timer()

        st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
        if phase == "interview":
            if st.button("End interview early", use_container_width=True):
                end_interview_dialog()
        if phase in ("interview", "review", "feedback"):
            if st.button("New session", use_container_width=True):
                new_session_dialog()

        st.markdown(
            '<div class="side-footer">Powered by Groq · Built with Streamlit</div>',
            unsafe_allow_html=True,
        )


# ============================================================
# SCREENS
# ============================================================
HERO = """
<div class="hero">
    <span class="hero-badge">🎯 AI Interview Coach</span>
    <h1>Walk into your next interview<br/><span>prepared, not nervous.</span></h1>
    <p>A realistic mock interview with an AI hiring manager, tailored to your target role, company and difficulty.
    Finish with a scored report and a clear plan to improve.</p>
    <div class="hero-chips">
        <span class="chip">⏱ 8-minute session</span>
        <span class="chip">🧠 Adaptive questions</span>
        <span class="chip">📊 Scored feedback</span>
        <span class="chip">📥 Downloadable report</span>
    </div>
</div>
"""


def render_setup() -> None:
    st.markdown(HERO, unsafe_allow_html=True)

    if not api_ready():
        st.warning(
            "No Groq API key found. Add `GROQ_API_KEY` to `streamlit/.streamlit/secrets.toml` "
            "and reload the page to start an interview."
        )

    with st.form("setup_form", border=False):
        left, right = st.columns([1.6, 1], gap="large")

        with left:
            with st.container(border=False, key="card-profile"):
                card_title("🧑", "Candidate profile", "Tell the interviewer who you are.")
                name_col, years_col = st.columns([1.5, 1])
                with name_col:
                    name = st.text_input(
                        "Full name",
                        value=st.session_state.name,
                        placeholder="e.g. Aisha Khan",
                        max_chars=40,
                    )
                with years_col:
                    years = st.text_input(
                        "Years of experience",
                        value=st.session_state.years,
                        placeholder="e.g. 3",
                        max_chars=12,
                    )
                skills = st.text_input(
                    "Core skills",
                    value=st.session_state.skills,
                    placeholder="Python, SQL, machine learning, stakeholder communication",
                    max_chars=160,
                )
                experience = st.text_area(
                    "Experience summary",
                    value=st.session_state.experience,
                    placeholder="Two lines about your most recent role and the work you are proud of…",
                    max_chars=400,
                    height=104,
                )

            with st.container(border=False, key="card-role"):
                card_title("🎯", "Target role", "The interview adapts to these choices.")
                level_col, company_col = st.columns(2)
                with level_col:
                    level = st.segmented_control(
                        "Level",
                        LEVELS,
                        default=st.session_state.level,
                        required=True,
                    )
                with company_col:
                    company = st.selectbox(
                        "Company",
                        COMPANIES,
                        index=option_index(COMPANIES, st.session_state.company),
                    )
                position_col, difficulty_col = st.columns(2)
                with position_col:
                    position = st.selectbox(
                        "Position",
                        POSITIONS,
                        index=option_index(POSITIONS, st.session_state.position),
                    )
                with difficulty_col:
                    difficulty = st.select_slider(
                        "Difficulty",
                        DIFFICULTIES,
                        value=st.session_state.difficulty,
                    )
                focus = st.pills(
                    "Focus area",
                    FOCUS_AREAS,
                    default=st.session_state.focus_area,
                    required=True,
                )

        with right:
            with st.container(border=False, key="card-how"):
                card_title("🧭", "How it works", "About 8 minutes, start to report.")
                st.markdown(
                    steps_html(
                        [
                            ("Set the scene", "Pick your role, company and how tough it should be."),
                            ("Answer five questions", "One at a time, just like a real screen."),
                            ("Get your report", "A score, strengths, gaps and next steps."),
                        ]
                    ),
                    unsafe_allow_html=True,
                )

            with st.container(border=False, key="card-tips"):
                card_title("💡", "Answer like a pro", "Small habits that score well.")
                st.markdown(
                    '<ul class="clean">'
                    "<li>Use STAR: situation, task, action, result.</li>"
                    "<li>Lead with the outcome, then explain how.</li>"
                    "<li>Name real numbers and tools you used.</li>"
                    "<li>Keep answers to 3-5 sentences.</li>"
                    "</ul>",
                    unsafe_allow_html=True,
                )

        st.markdown("<div style='height:.45rem'></div>", unsafe_allow_html=True)
        _, center, _ = st.columns([1, 1.25, 1])
        with center:
            submitted = st.form_submit_button(
                "Start interview  →", type="primary", use_container_width=True
            )
        st.markdown(
            '<div class="center-note">Free-text answers · Instant scored report · Download as Markdown</div>',
            unsafe_allow_html=True,
        )

    if not submitted:
        return

    if not name.strip():
        st.error("Add your name so the interviewer can greet you.")
        return
    if not api_ready():
        st.error("Add `GROQ_API_KEY` to `streamlit/.streamlit/secrets.toml` before starting.")
        return

    st.session_state.update(
        {
            "name": name.strip(),
            "years": years.strip(),
            "skills": skills.strip(),
            "experience": experience.strip(),
            "level": level or st.session_state.level,
            "position": position,
            "company": company,
            "difficulty": difficulty,
            "focus_area": focus or st.session_state.focus_area,
            "phase": "interview",
            "messages": [],
            "answers": 0,
            "started_at": datetime.now(),
            "ended_at": None,
            "feedback": None,
        }
    )
    st.rerun()


def render_interview() -> None:
    state = st.session_state
    pct = int(state.answers / MAX_QUESTIONS * 100)
    question_no = min(state.answers + 1, MAX_QUESTIONS)

    st.markdown(
        f"""
        <div class="quiz-head">
            <div class="quiz-meta">
                <span class="pill strong">{html.escape(state.level)} {html.escape(state.position)}</span>
                <span class="pill">{html.escape(state.company)}</span>
                <span class="pill">{html.escape(state.difficulty)}</span>
                <span class="pill">{html.escape(state.focus_area)}</span>
            </div>
        </div>
        <div class="bar"><i style="width:{pct}%"></i></div>
        <div class="quiz-foot">
            <span>Question {question_no} of {MAX_QUESTIONS}</span>
            <span>Started {state.started_at.strftime('%H:%M') if state.started_at else ''}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for message in state.messages:
        if message["role"] == "system":
            continue
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown('<span class="role-me"></span>', unsafe_allow_html=True)
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant", avatar=INTERVIEWER_AVATAR):
                st.markdown('<span class="role-ai"></span>', unsafe_allow_html=True)
                st.markdown(message["content"])

    needs_question = state.answers < MAX_QUESTIONS and (
        not state.messages or state.messages[-1]["role"] != "assistant"
    )
    if needs_question:
        with st.chat_message("assistant", avatar=INTERVIEWER_AVATAR):
            st.markdown('<span class="role-ai"></span>', unsafe_allow_html=True)
            generate_question()

    if state.answers < MAX_QUESTIONS:
        answer = st.chat_input(
            "Type your answer — 3 to 5 sentences · Enter to send, Shift + Enter for a new line",
            max_chars=1200,
        )
        if answer:
            submit_answer(answer)


def render_review() -> None:
    state = st.session_state
    st.markdown(
        f"""
        <div class="report-head">
            <div>
                <h2>Interview complete 🎉</h2>
                <div class="meta">{html.escape(state.level)} {html.escape(state.position)} ·
                {html.escape(state.company)} · {html.escape(state.difficulty)} ·
                {state.answers} of {MAX_QUESTIONS} answered</div>
            </div>
            <div class="pill strong">⏱ {fmt_duration(elapsed_seconds())}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=False, key="card-review"):
        card_title("📊", "Ready for your report?", "We score five criteria and give you a plan.")
        st.markdown(
            tiles_html(
                [
                    ("Duration", fmt_duration(elapsed_seconds())),
                    ("Questions", f"{state.answers}/{MAX_QUESTIONS}"),
                    ("Difficulty", state.difficulty),
                    ("Focus", state.focus_area),
                ]
            ),
            unsafe_allow_html=True,
        )
        if st.button("Get my feedback  →", type="primary", use_container_width=True):
            state.phase = "feedback"
            st.rerun()

    with st.expander("Review your transcript"):
        for message in state.messages:
            if message["role"] == "system":
                continue
            who = "You" if message["role"] == "user" else "Interviewer"
            st.markdown(f"**{who}:** {message['content']}")


def render_feedback() -> None:
    state = st.session_state

    if state.feedback is None:
        st.markdown(
            '<div class="report-head"><div><h2>Scoring your interview</h2>'
            '<div class="meta">Reading your answers and building a plan…</div></div></div>',
            unsafe_allow_html=True,
        )
        with st.spinner("Analysing your answers…"):
            try:
                state.feedback = build_feedback()
            except Exception as exc:  # surfaced to the user
                st.error(friendly_error(exc))
                if st.button("Try again", type="primary"):
                    st.rerun()
                return
        st.rerun()

    feedback = state.feedback
    color, band = score_band(feedback["score"])
    pct = (feedback["score"] or 0) * 10

    st.markdown(
        f"""
        <div class="report-head">
            <div>
                <h2>Your interview report</h2>
                <div class="meta">{html.escape(state.level)} {html.escape(state.position)} ·
                {html.escape(state.company)} · {html.escape(state.difficulty)} ·
                {state.answers} of {MAX_QUESTIONS} answered · {fmt_duration(elapsed_seconds())}</div>
            </div>
            <div class="pill strong">Generated {datetime.now().strftime('%d %b, %H:%M')}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not feedback["ok"]:
        st.warning(
            "The coach replied in an unexpected format, so here is its response verbatim. "
            "Try regenerating the feedback for a scored breakdown."
        )
        with st.container(border=False, key="card-summary"):
            card_title("💬", "Coach notes")
            st.markdown(feedback["summary"] or feedback["raw"] or "No feedback returned.")
        if st.button("Regenerate feedback", type="primary", use_container_width=True):
            state.feedback = None
            st.rerun()
        return

    score_inner = (
        f'<div class="num">{feedback["score"]}<small>/10</small></div>'
        if feedback["score"] is not None
        else '<div class="num">—</div>'
    )

    left, right = st.columns([1, 1.35], gap="large")
    with left:
        with st.container(border=False, key="card-score"):
            st.markdown(
                f'<div class="score-ring" style="--pct:{pct};--band:{color}">'
                f'<div class="inner">{score_inner}'
                f'<div class="verdict">{html.escape(feedback["verdict"])}</div></div></div>'
                f'<div class="score-caption">Overall score · {html.escape(band)} signal</div>',
                unsafe_allow_html=True,
            )
    with right:
        with st.container(border=False, key="card-criteria"):
            card_title("📈", "Score breakdown", "How you came across in each area.")
            if feedback["criteria"]:
                rows = "".join(
                    f'<div class="crit"><div class="crit-top"><span>{html.escape(label)}</span>'
                    f'<b>{value}/10</b></div><div class="crit-bar">'
                    f'<i style="width:{value * 10}%"></i></div></div>'
                    for label, value in feedback["criteria"].items()
                )
                st.markdown(rows, unsafe_allow_html=True)
            else:
                st.markdown(
                    '<div class="empty-note">No per-criteria scores were returned.</div>',
                    unsafe_allow_html=True,
                )

    strength_col, improve_col = st.columns(2, gap="large")
    with strength_col:
        with st.container(border=False, key="card-strengths"):
            card_title("✅", "What worked", "Keep doing these.")
            st.markdown(bullets_html(feedback["strengths"]), unsafe_allow_html=True)
    with improve_col:
        with st.container(border=False, key="card-improve"):
            card_title("🎯", "Where to improve", "Your biggest upside.")
            st.markdown(
                bullets_html(feedback["improvements"], kind="warn"), unsafe_allow_html=True
            )

    if feedback["summary"]:
        with st.container(border=False, key="card-summary"):
            card_title("💬", "Overall feedback")
            st.markdown(feedback["summary"])

    if feedback["next_steps"]:
        with st.container(border=False, key="card-next"):
            card_title("🚀", "Your next practice steps", "Do these before the real thing.")
            st.markdown(roadmap_html(feedback["next_steps"]), unsafe_allow_html=True)

    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
    action_one, action_two, action_three = st.columns([1, 1, 1])
    with action_one:
        st.download_button(
            "📥 Download report",
            data=build_report(feedback),
            file_name=f"interview_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with action_two:
        if st.button("↻ Regenerate feedback", use_container_width=True):
            state.feedback = None
            st.rerun()
    with action_three:
        if st.button("New interview", type="primary", use_container_width=True):
            restart()


# ============================================================
# ROUTER
# ============================================================
render_sidebar()

if st.session_state.phase == "setup":
    render_setup()
elif st.session_state.phase == "interview":
    render_interview()
elif st.session_state.phase == "review":
    render_review()
else:
    render_feedback()

