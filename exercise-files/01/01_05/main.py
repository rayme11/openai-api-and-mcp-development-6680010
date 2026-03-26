from colorama import Fore
import streamlit as st
from pathlib import Path
import tempfile
from openai import OpenAI
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = OpenAI()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tech Learning Assistant", page_icon="🎓", layout="centered"
)

st.markdown(
    """
    <style>
    .stButton>button { border: 1px solid #3498db; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("🎓 Tech Learning Assistant")
st.caption(
    "Choose a subject, pick your level, explore topics, and dive deep into any concept."
)

# ── Constants ─────────────────────────────────────────────────────────────────
MODELS = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]

SUBJECTS = {
    "🐍 Python": "Python programming",
    "🔧 SRE (Site Reliability Engineering)": "Site Reliability Engineering (SRE)",
    "👔 Leadership & Career (Senior / Director / VP)": "Leadership & Career",
}

SUBJECT_ICONS = {
    "🐍 Python": "🐍",
    "🔧 SRE (Site Reliability Engineering)": "🔧",
    "👔 Leadership & Career (Senior / Director / VP)": "👔",
}

CAREER_LABEL = "👔 Leadership & Career (Senior / Director / VP)"

# ── Session state defaults ────────────────────────────────────────────────────
for key, default in {
    "topics": [],
    "selected_topic": None,
    "explanation": None,
    "level": None,
    "model": MODELS[0],
    "subject": None,
    "subject_label": None,
    "is_career": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ── Helper functions ──────────────────────────────────────────────────────────
def fetch_topics(subject: str, level: str, model: str) -> list[dict]:
    """Fetch 10 topics for the given subject and level, sorted by complexity."""
    print(f"\n{'─'*60}")
    print(f"[fetch_topics] Called with:")
    print(f"  Subject : {subject}")
    print(f"  Level   : {level}")
    print(f"  Model   : {model}")
    prompt = (
        f"You are a {subject} tutor. Return exactly 10 learning topics suitable for a "
        f"'{level}' student, sorted from simplest to most complex. "
        f"Respond ONLY with a valid JSON array, no markdown, no explanation. "
        f"Each element must be an object with two keys: "
        f'"title" (string) and "complexity" (integer 1-10). Example: '
        f'[{{"title": "Variables", "complexity": 1}}]'
    )
    print(f"\n>>> PROMPT SENT TO {model}:")
    print(f"{'·'*60}")
    print(prompt)
    print(f"{'·'*60}")
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    raw = response.choices[0].message.content.strip()
    print(f"\n<<< RAW RESPONSE FROM {model}:")
    print(f"{'·'*60}")
    print(raw)
    print(f"{'·'*60}")
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    topics = json.loads(raw)
    print(f"[fetch_topics] Retrieved {len(topics)} topics:")
    for t in topics:
        print(f"  [{t['complexity']:2}] {t['title']}")
    print(f"{'─'*60}")
    return topics


def fetch_explanation(topic: str, subject: str, level: str, model: str) -> str:
    """Explain the topic and include free online practice resources."""
    print(f"\n{'─'*60}")
    print(f"[fetch_explanation] Called with:")
    print(f"  Topic   : {topic}")
    print(f"  Subject : {subject}")
    print(f"  Level   : {level}")
    print(f"  Model   : {model}")

    is_sre = "reliability" in subject.lower() or "sre" in subject.lower()

    if is_sre:
        resources_instruction = (
            f"4. **Free Hands-On Labs & Resources** — list 5 to 7 specific free hands-on labs "
            f"or interactive resources where the student can practice '{topic}' right now. "
            f"Search across these major free lab providers first:\n"
            f"- **Google Cloud**: Google Cloud Skills Boost free labs (cloudskillsboost.google), "
            f"  Google SRE workbook labs (sre.google/workbook)\n"
            f"- **AWS**: AWS Skill Builder free tier (skillbuilder.aws), AWS Workshops (workshops.aws), "
            f"  AWS Well-Architected Labs (wellarchitectedlabs.com)\n"
            f"- **Azure**: Microsoft Learn free modules (learn.microsoft.com), "
            f"  Azure free sandbox labs\n"
            f"- **Linux Foundation**: Training free courses (trainingportal.linuxfoundation.org)\n"
            f"- **Kubernetes/Docker**: Play with Kubernetes (labs.play-with-k8s.com), "
            f"  Play with Docker (labs.play-with-docker.com), Killercoda (killercoda.com)\n"
            f"- **GitHub**: Repos with runbooks, chaos engineering exercises, or SRE labs\n"
            f"- **Other**: Instruqt free tracks, Katacoda archived scenarios, Google Colab notebooks\n\n"
            f"For each resource include: the provider name, resource name, direct URL, and one sentence "
            f"on exactly what the student can practice there related to '{topic}'. "
            f"STRICT RULE: Every resource must be 100% free — no credit card, no paid subscription, "
            f"no free-trial-only content. Skip any resource that requires payment to access.\n\n"
            f"5. **Senior / Director / VP Reading List** — list 4 to 6 free articles, "
            f"engineering blogs, or publications relevant to '{topic}' at a leadership level "
            f"(Senior Engineer, Staff, Director, or VP). Focus on: strategic thinking, "
            f"industry trends, architectural decisions, interview preparation, and technology "
            f"leadership. Pull from sources like:\n"
            f"- Google SRE Book / Workbook (sre.google — free online)\n"
            f"- Netflix Tech Blog (netflixtechblog.com)\n"
            f"- Increment magazine (increment.com — free)\n"
            f"- ACM Queue (queue.acm.org — free)\n"
            f"- The Morning Paper (blog.acolyer.org)\n"
            f"- LinkedIn Engineering Blog, Uber Engineering, Airbnb Engineering\n"
            f"- IEEE Spectrum free articles (spectrum.ieee.org)\n"
            f"- USENIX ;login: free articles (usenix.org/publications/login)\n"
            f"- Martin Fowler's blog (martinfowler.com — free)\n"
            f"- High Scalability (highscalability.com — free)\n\n"
            f"For each item include: the title, author/publication, direct URL, and one sentence "
            f"on why it is valuable for leadership-level career growth or interview prep. "
            f"STRICT RULE: No paywalled articles — every link must be freely readable without "
            f"a subscription or login."
        )
    else:
        resources_instruction = (
            f"4. **Free Practice Resources** — list 3 to 5 specific, real, currently active "
            f"free resources (websites, playgrounds, notebooks, or courses) where a student "
            f"can practice this exact topic hands-on. For each resource include: the name, "
            f"the URL, and one sentence on what they can do there. "
            f"Only include resources that are completely free with no paid membership required.\n\n"
            f"5. **Senior / Director / VP Reading List** — list 3 to 5 free articles or blog posts "
            f"about '{topic}' written for experienced engineers or tech leaders. "
            f"Focus on architectural patterns, industry trends, or interview-level depth. "
            f"Pull from: martinfowler.com, netflixtechblog.com, increment.com, queue.acm.org, "
            f"highscalability.com, or major engineering blogs. "
            f"For each include: the title, author/publication, direct URL, and one sentence "
            f"on why it is valuable. STRICT RULE: No paywalled articles, completely free to read."
        )

    prompt = (
        f"You are a friendly {subject} tutor. Explain the topic '{topic}' "
        f"for a '{level}' student.\n\n"
        f"Structure your response in markdown with these sections:\n"
        f"1. **What it is** — a clear, concise definition\n"
        f"2. **Why it matters** — practical importance\n"
        f"3. **Example** — a concrete code or real-world example\n"
        f"{resources_instruction}"
    )
    print(f"\n>>> PROMPT SENT TO {model}:")
    print(f"{'·'*60}")
    print(prompt)
    print(f"{'·'*60}")
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )
    explanation = response.choices[0].message.content
    print(f"\n<<< RESPONSE FROM {model}:")
    print(f"{'·'*60}")
    print(explanation)
    print(f"{'·'*60}")
    print(f"[fetch_explanation] Done — {len(explanation)} chars received")
    print(f"{'─'*60}")
    return explanation


def fetch_career_topics(model: str) -> list[dict]:
    """Fetch 10 leadership/career topics, sorted by complexity."""
    print(f"\n{'─'*60}")
    print(f"[fetch_career_topics] Called with model: {model}")
    prompt = (
        "You are a tech career coach for senior engineers and tech leaders. "
        "Return exactly 10 topics that a Senior Engineer, Staff Engineer, Director, or VP "
        "of Engineering should master for career growth, job interviews, and leadership. "
        "Topics should cover: system design, interview prep, technology trends, engineering "
        "strategy, team leadership, architectural thinking, and industry best practices. "
        "Sort from most foundational to most advanced. "
        "Respond ONLY with a valid JSON array, no markdown, no explanation. "
        "Each element must be an object with two keys: "
        '"title" (string) and "complexity" (integer 1-10). Example: '
        '[{"title": "System Design Interviews", "complexity": 3}]'
    )
    print(f"\n>>> PROMPT SENT TO {model}:")
    print(f"{'·'*60}")
    print(prompt)
    print(f"{'·'*60}")
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    raw = response.choices[0].message.content.strip()
    print(f"\n<<< RAW RESPONSE FROM {model}:")
    print(f"{'·'*60}")
    print(raw)
    print(f"{'·'*60}")
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    topics = json.loads(raw)
    print(f"[fetch_career_topics] Retrieved {len(topics)} topics:")
    for t in topics:
        print(f"  [{t['complexity']:2}] {t['title']}")
    print(f"{'─'*60}")
    return topics


def fetch_career_explanation(topic: str, model: str) -> str:
    """Return a leadership-level deep-dive with free reading resources."""
    print(f"\n{'─'*60}")
    print(f"[fetch_career_explanation] Topic: {topic} | Model: {model}")
    prompt = (
        f"You are a tech career coach for Senior Engineers, Staff Engineers, Directors, "
        f"and VPs of Engineering. Provide a deep-dive on the topic: '{topic}'.\n\n"
        f"Structure your response in markdown with these sections:\n"
        f"1. **Overview** — what this topic is and why it matters at a leadership level\n"
        f"2. **Key Concepts** — the 4-6 most important ideas a senior/director/VP must understand\n"
        f"3. **Interview Insights** — common interview questions or discussion points for senior+ roles, "
        f"with example strong answers or talking points\n"
        f"4. **Free Reading List** — list 5 to 7 free articles, blog posts, or book chapters "
        f"from sources like: sre.google, martinfowler.com, netflixtechblog.com, increment.com, "
        f"queue.acm.org, highscalability.com, usenix.org, blog.acolyer.org, lethain.com (Will Larson), "
        f"staffeng.com, leaddev.com (free articles), or major engineering blogs (Uber, Airbnb, LinkedIn, Stripe). "
        f"For each include: title, author/publication, direct URL, and one sentence on why it is "
        f"valuable for career growth or interview prep. "
        f"STRICT RULE: Every link must be freely readable — no paywall, no subscription, no login required.\n"
        f"5. **Recommended Next Steps** — 3 concrete actions this person can take this week to "
        f"level up on this topic"
    )
    print(f"\n>>> PROMPT SENT TO {model}:")
    print(f"{'·'*60}")
    print(prompt)
    print(f"{'·'*60}")
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )
    explanation = response.choices[0].message.content
    print(f"\n<<< RESPONSE FROM {model}:")
    print(f"{'·'*60}")
    print(explanation)
    print(f"{'·'*60}")
    print(f"[fetch_career_explanation] Done — {len(explanation)} chars received")
    print(f"{'─'*60}")
    return explanation


# ── Step 1 – Choose subject, level, model ────────────────────────────────────
st.subheader("Step 1 — What do you want to learn?")

# Subject picker outside form so UI can react to it immediately
subject_label = st.selectbox(
    "Subject",
    list(SUBJECTS.keys()),
    key="subject_picker",
    help="Choose Python, SRE, or the Leadership & Career track (no level needed).",
)
is_career = subject_label == CAREER_LABEL

with st.form("level_form"):
    if is_career:
        st.info(
            "👔 Leadership & Career track — no expertise level needed. Just pick your model and go."
        )
        (col_model,) = (st.columns(1),)
        model = st.selectbox(
            "AI model", MODELS, help="More capable models give richer insights."
        )
    else:
        col_level, col_model = st.columns(2)
        with col_level:
            level = st.selectbox(
                "Expertise level",
                ["Beginner", "Intermediate", "Advanced"],
                help="Beginner: just starting | Intermediate: comfortable with basics | Advanced: ready for complex concepts",
            )
        with col_model:
            model = st.selectbox(
                "AI model",
                MODELS,
                help="More capable models give richer explanations.",
            )
    submitted = st.form_submit_button("🔍 Get Topics")

if submitted:
    subject = SUBJECTS[subject_label]
    if is_career:
        with st.spinner("Fetching leadership & career topics..."):
            st.session_state.topics = fetch_career_topics(model)
        st.session_state.level = "Senior+"
    else:
        with st.spinner(f"Fetching top 10 {level} {subject} topics..."):
            st.session_state.topics = fetch_topics(subject, level, model)
        st.session_state.level = level
    st.session_state.subject = subject
    st.session_state.subject_label = subject_label
    st.session_state.is_career = is_career
    st.session_state.model = model
    st.session_state.selected_topic = None
    st.session_state.explanation = None

# ── Step 2 – Pick a topic ─────────────────────────────────────────────────────
if st.session_state.topics:
    st.divider()
    icon = SUBJECT_ICONS.get(st.session_state.get("subject_label", ""), "📘")
    st.subheader(
        f"Step 2 — Pick a topic  "
        f"*({icon} {st.session_state.subject} · {st.session_state.level})*"
    )
    st.caption("Topics are sorted from simplest → most complex.")

    topic_titles = [f"{t['complexity']}. {t['title']}" for t in st.session_state.topics]
    chosen = st.radio("Select a topic to learn about:", topic_titles, key="topic_radio")

    if st.button("📖 Explain this topic"):
        clean_title = chosen.split(". ", 1)[1]
        st.session_state.selected_topic = clean_title
        with st.spinner(
            f"Generating content for '{clean_title}' with {st.session_state.model}..."
        ):
            if st.session_state.get("is_career"):
                st.session_state.explanation = fetch_career_explanation(
                    clean_title, st.session_state.model
                )
            else:
                st.session_state.explanation = fetch_explanation(
                    clean_title,
                    st.session_state.subject,
                    st.session_state.level,
                    st.session_state.model,
                )

# ── Step 3 – Show explanation + resources ────────────────────────────────────
if st.session_state.explanation:
    st.divider()
    st.subheader(f"📚 {st.session_state.selected_topic}")
    st.caption(
        f"Subject: **{st.session_state.subject}** · "
        f"Level: **{st.session_state.level}** · "
        f"Model: `{st.session_state.model}`"
    )
    st.markdown(st.session_state.explanation)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ Choose a different topic"):
            st.session_state.selected_topic = None
            st.session_state.explanation = None
            st.rerun()
    with col2:
        if st.button("🔄 Start over"):
            st.session_state.topics = []
            st.session_state.selected_topic = None
            st.session_state.explanation = None
            st.session_state.level = None
            st.session_state.subject = None
            st.rerun()
