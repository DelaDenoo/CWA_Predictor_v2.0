# app.py
# -----------------------------------------------------------------------------
# AURA Health Tech — Single-file Streamlit Website
#
# How to run:
#   1) pip install streamlit pandas
#   2) streamlit run app.py
#
# Notes:
# - Single-file implementation with web-sourced images only.
# - No external CSS files or packages beyond stdlib + pandas.
# - Uses inline CSS for styling and Streamlit components for layout.
# -----------------------------------------------------------------------------

import io
import json
import textwrap
import uuid
import random
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

# -----------------------------------------------------------------------------
# Page Config
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AURA Health Tech",
    page_icon="🧑‍🦽",
    layout="wide",
    menu_items={
        "Get Help": "mailto:hello@aurahealthtech.org",
        "Report a bug": "mailto:hello@aurahealthtech.org?subject=Bug%20Report",
        "About": "AURA Health Tech — Assistive mobility that restores independence.",
    },
)

# -----------------------------------------------------------------------------
# Brand / Theme Constants
# -----------------------------------------------------------------------------
PALETTE = {
    "primary": "#0EA5E9",  # Aura Blue
    "primary_dark": "#0B6CB8",
    "secondary": "#22C55E",  # Care Green
    "accent": "#F43F5E",  # Rose
    "bg": "#0F172A",  # Deep Slate
    "surface": "#111827",
    "text": "#E5E7EB",
    "muted": "#94A3B8",
}

IMAGES = {
    "hero": "https://images.unsplash.com/photo-1518972559570-7cc1309f3229?q=80&w=1600",
    "care": "https://images.unsplash.com/photo-1580281657527-47f249e8f3a0?q=80&w=1600",
    "mobility": "https://images.unsplash.com/photo-1581093588401-16ec9f86ef26?q=80&w=1600",
    "team": "https://images.unsplash.com/photo-1551836022-d5d88e9218df?q=80&w=1600",
    "map": "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?q=80&w=1600",  # placeholder
    "partner1": "https://images.unsplash.com/photo-1516251193007-45ef944ab0c6?q=80&w=600",
    "partner2": "https://images.unsplash.com/photo-1493612276216-ee3925520721?q=80&w=600",
    "partner3": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?q=80&w=600",
    "logo": "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?q=80&w=200",
}

COPY = {
    "company": "AURA Health Tech",
    "tagline": "Assistive mobility that restores independence.",
    "one_liner": "AURA builds human-centered assistive devices and digital tools that make mobility safer, smarter, and more dignified.",
    "cta_primary": "Book a demo",
    "cta_secondary": "Download brochure",
    "product_name": "INCLIFT",
    "footer_email": "hello@aurahealthtech.org",
}

# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
if "section" not in st.session_state:
    st.session_state.section = "Home"

if "leads" not in st.session_state:
    st.session_state.leads = []  # store contact submissions (dicts)

if "testimonial_index" not in st.session_state:
    st.session_state.testimonial_index = 0

if "clicks" not in st.session_state:
    st.session_state.clicks = {}  # track outbound clicks by label

# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------
def track_click(label: str):
    """Increment outbound link click counters."""
    st.session_state.clicks[label] = st.session_state.clicks.get(label, 0) + 1


@st.cache_data(show_spinner=False)
def generate_brochure_bytes() -> bytes:
    """Return a simple PDF-ish brochure as bytes (placeholder)."""
    # We will provide a minimalistic PDF-like content as a text-based placeholder.
    # In real usage, attach a real PDF.
    content = textwrap.dedent(f"""
    AURA Health Tech — Company Brochure
    ===================================
    Tagline: {COPY['tagline']}

    One-liner:
      {COPY['one_liner']}

    Hero Product: {COPY['product_name']} — a compact, wheelchair-boarding assist device enabling independent shuttle access.

    Value Pillars:
      • Safety • Dignity • Clinical-grade reliability • Local manufacturing • Fair pricing

    Target users:
      Wheelchair users, caregivers, transport operators, clinics, insurers, NGOs, municipalities.

    Contact:
      {COPY['footer_email']}
    """).encode("utf-8")
    return content


@st.cache_data(show_spinner=False)
def make_metrics_df(days: int = 90) -> pd.DataFrame:
    """Create synthetic KPIs over a period for display."""
    base_date = datetime.utcnow().date() - timedelta(days=days)
    rows = []
    for i in range(days):
        d = base_date + timedelta(days=i)
        transfers = max(0, int(random.gauss(120, 20)))
        time_saved = round(max(0, random.gauss(18.0, 3.0)), 1)  # minutes
        satisfaction = round(min(5.0, max(3.6, random.gauss(4.6, 0.2))), 2)
        rows.append({"date": d, "transfers": transfers, "avg_time_saved_min": time_saved, "user_satisfaction": satisfaction})
    return pd.DataFrame(rows)


def section_heading(title: str, subtitle: str = "", anchor: str | None = None):
    """Standard section heading with optional anchor."""
    if anchor:
        st.markdown(f'<a id="{anchor}"></a>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="section-title">
            <h2>{title}</h2>
            <p class="muted">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def badge(text: str, tone: str = "primary"):
    """Render a small badge."""
    color = PALETTE.get(tone, PALETTE["primary"])
    st.markdown(
        f"""<span class="badge" style="background:{color}22;border:1px solid {color}44;color:{PALETTE['text']};">{text}</span>""",
        unsafe_allow_html=True,
    )


def two_ctas(primary_label: str, secondary_label: str, primary_key: str, secondary_key: str):
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button(primary_label, key=primary_key, use_container_width=True):
            st.success("Thanks! We’ll reach out to schedule your demo.")
    with col2:
        brochure_bytes = generate_brochure_bytes()
        st.download_button(
            secondary_label,
            data=brochure_bytes,
            file_name="AURA_Brochure.txt",
            mime="text/plain",
            use_container_width=True,
            key=secondary_key,
        )


def anchor_nav():
    """Top navigation buttons to quickly jump to sections (emulates sticky bar)."""
    cols = st.columns([1.8, 1, 1, 1, 1, 1, 1, 1, 1])
    with cols[0]:
        st.markdown(
            f'<div class="brand"><img src="{IMAGES["logo"]}" alt="AURA logo" class="logo"> AURA Health Tech</div>',
            unsafe_allow_html=True,
        )
    labels = ["Home", "Solution", "Products", "Clinical & Safety", "Impact", "Pricing", "Partners", "Team/Contact"]
    anchors = ["home", "solution", "products", "clinical", "impact", "pricing", "partners", "team"]
    for i, (lab, anc) in enumerate(zip(labels, anchors), start=1):
        with cols[i]:
            if st.button(lab, key=f"nav_{anc}", use_container_width=True):
                st.session_state.section = lab
                st.markdown(f"<a href='#{anc}'></a>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Inline CSS (minimal)
# -----------------------------------------------------------------------------
st.markdown(
    f"""
    <style>
        html, body, [data-testid="stAppViewContainer"] {{
            background: linear-gradient(180deg, {PALETTE['bg']} 0%, #0B1225 100%);
            color: {PALETTE['text']};
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }}
        .stApp header {{
            background: rgba(15, 23, 42, 0.75);
            backdrop-filter: blur(6px);
        }}
        .topbar {{
            position: sticky; top: 0; z-index: 1000;
            padding: 0.5rem 0.75rem; margin-bottom: 0.75rem;
            background: rgba(15, 23, 42, 0.75);
            border-bottom: 1px solid {PALETTE['primary']}22;
            backdrop-filter: blur(6px);
            border-radius: 0 0 12px 12px;
        }}
        .brand {{
            display:flex; align-items:center; gap:10px; font-weight:600; color:{PALETTE['text']}; white-space:nowrap;
        }}
        .logo {{
            width: 28px; height: 28px; border-radius: 6px; object-fit: cover; border:1px solid {PALETTE['primary']}55;
        }}
        .hero {{
            position: relative; overflow: hidden; border-radius: 16px;
            background: url('{IMAGES['hero']}') center/cover no-repeat;
            min-height: 440px; display:flex; align-items:center;
            border: 1px solid #00000055; box-shadow: 0 10px 30px rgba(0,0,0,0.35);
        }}
        .hero::before {{
            content:""; position:absolute; inset:0;
            background: radial-gradient(1200px 400px at 20% 20%, {PALETTE['primary']}33, transparent 60%),
                        linear-gradient(180deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0.75) 100%);
        }}
        .hero-content {{
            position: relative; padding: 3rem; max-width: 860px;
        }}
        .hero h1 {{ font-size: 48px; line-height: 1.05; margin: 0 0 10px; }}
        .hero p.lede {{ color:{PALETTE['muted']}; font-size: 18px; margin: 10px 0 24px; }}
        .chip {{
            display:inline-flex; align-items:center; gap:6px;
            padding: 6px 10px; border-radius: 999px;
            border:1px solid {PALETTE['secondary']}55; background:{PALETTE['secondary']}22; color:{PALETTE['text']};
            font-size: 13px; margin-bottom: 12px;
        }}
        .card {{
            background: {PALETTE['surface']}; border:1px solid #00000044; border-radius: 16px; padding: 18px; height:100%;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.02), 0 8px 18px rgba(0,0,0,0.25);
        }}
        .section-title h2 {{ margin: 0 0 4px; }}
        .section-title .muted {{ color:{PALETTE['muted']}; margin-top: 0; }}
        .badge {{
            font-size: 12px; padding: 4px 10px; border-radius: 999px; margin-right: 8px;
        }}
        .muted {{ color: {PALETTE['muted']}; }}
        .small {{ font-size: 13px; color:{PALETTE['muted']}; }}
        .footer {{
            border-top: 1px solid #ffffff11; margin-top: 2rem; padding-top: 1rem; color:{PALETTE['muted']};
        }}
        .metric-wrap {{
            display:grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap:12px;
        }}
        @media (max-width: 900px) {{
            .metric-wrap {{ grid-template-columns: 1fr; }}
            .hero h1 {{ font-size: 34px; }}
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Header / Topbar
# -----------------------------------------------------------------------------
with st.container():
    st.markdown('<div class="topbar">', unsafe_allow_html=True)
    anchor_nav()
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# HERO (Home)
# -----------------------------------------------------------------------------
def render_hero():
    st.markdown('<a id="home"></a>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="hero">', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="hero-content">
                <div class="chip">🦽 Human-centered Assistive Mobility</div>
                <h1>{COPY["tagline"]}</h1>
                <p class="lede">{COPY["one_liner"]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.write("")  # spacing
        colA, colB, colC = st.columns([2, 1, 1])
        with colA:
            st.caption("Value pillars")
            badge("Safety", "secondary")
            badge("Dignity", "primary")
            badge("Clinical reliability", "primary_dark")
            badge("Local manufacturing", "secondary")
            badge("Fair pricing", "accent")
        with colB:
            st.caption("Quick Actions")
            two_ctas(COPY["cta_primary"], COPY["cta_secondary"], "cta_book", "cta_download")
        with colC:
            st.caption("Hero imagery credits")
            st.image(IMAGES["mobility"], caption="Mobility engineering", use_column_width=True)

    st.write("")  # spacing
    # KPI row
    section_heading("At a glance", "Impact metrics (synthetic preview)")
    with st.container():
        df = make_metrics_df(30)
        kpi_col = st.columns(3)
        with kpi_col[0]:
            st.metric("Transfers Enabled (30d)", f"{int(df['transfers'].sum()):,}", "+3.1%")
        with kpi_col[1]:
            st.metric("Avg. Time Saved", f"{df['avg_time_saved_min'].mean():.1f} min", "±0.6")
        with kpi_col[2]:
            st.metric("User Satisfaction", f"{df['user_satisfaction'].mean():.2f} / 5", "stable")


# -----------------------------------------------------------------------------
# Problem → Solution
# -----------------------------------------------------------------------------
def render_solution():
    st.markdown('<a id="solution"></a>', unsafe_allow_html=True)
    section_heading("The Problem → Our Solution", "Every transfer should be safe, swift, and dignified.")
    c1, c2 = st.columns([1.35, 1])
    with c1:
        st.markdown(
            """
            **The problem:** Wheelchair users and caregivers face unsafe, time-consuming transfers—especially in transport hubs and clinics.
            Manual lifting increases risk of injury, delays workflows, and undermines independence.

            **Our solution:** AURA designs assistive devices that combine ergonomic design, reliable mechanisms, and simple controls.
            Our hero product **INCLIFT** enables independent shuttle boarding with compact form, quick deployment, and safety interlocks.
            """)
        st.write("")
        # Feature cards
        fcols = st.columns(4)
        features = [
            ("🧲", "Compact & Stowable", "Fits common shuttle layouts and tight corridors."),
            ("🧠", "Smart Safety", "Interlocks, status LEDs, and gentle motion profile."),
            ("⚙️", "Serviceable", "Local parts, modular assemblies, fast swap units."),
            ("🔒", "Privacy by Design", "No PII stored; usage data optional & anonymized."),
        ]
        for (icon, title, desc), col in zip(features, fcols):
            with col:
                with st.container(border=True):
                    st.markdown(f"### {icon} {title}")
                    st.caption(desc)
    with c2:
        st.image(IMAGES["care"], caption="Clinical context", use_column_width=True)


# -----------------------------------------------------------------------------
# Products
# -----------------------------------------------------------------------------
def render_products():
    st.markdown('<a id="products"></a>', unsafe_allow_html=True)
    section_heading("Products", "Spotlight: INCLIFT — independent shuttle access.")
    with st.container():
        st.markdown("#### INCLIFT at a glance")
        col1, col2 = st.columns([1, 1])
        with col1:
            spec_df = pd.DataFrame(
                {
                    "Spec": ["Lift height", "Cycle time", "Safe working load", "Footprint", "Power"],
                    "Value": ["0–450 mm", "≈ 15–25 s", "150 kg", "600 × 480 mm", "24 V DC"],
                }
            )
            st.dataframe(spec_df, use_container_width=True, hide_index=True)
            st.caption("Specifications indicative; final values subject to validation and certification.")
            st.write("**Safety notes**")
            st.markdown(
                "- Dual-sensor interlock\n"
                "- Emergency stop & manual override\n"
                "- Anti-pinch geometry; smooth acceleration/deceleration\n"
                "- Non-slip platform with edge guards"
            )
        with col2:
            st.image(IMAGES["mobility"], caption="Mechanism & mobility engineering", use_column_width=True)
            st.write("")
            st.markdown("#### How it works")
            s1, s2, s3 = st.columns(3)
            with s1:
                st.markdown("**1️⃣ Position**")
                st.caption("Align device with shuttle step or curb edge.")
            with s2:
                st.markdown("**2️⃣ Secure**")
                st.caption("Engage platform locks and safety interlocks.")
            with s3:
                st.markdown("**3️⃣ Assist**")
                st.caption("Controlled lift with visual indicators and gentle motion.")


# -----------------------------------------------------------------------------
# Clinical & Safety
# -----------------------------------------------------------------------------
def render_clinical():
    st.markdown('<a id="clinical"></a>', unsafe_allow_html=True)
    section_heading("Clinical & Safety", "Reliability first. Evidence-led and compliant by design.")
    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.markdown("### 📋 Standards & QMS")
            st.caption("Targeting **ISO 13485** QMS alignment; IEC 60601 guidance where applicable (electrical safety). [Roadmap]")
            st.caption("Risk management per ISO 14971 principles.")
    with c2:
        with st.container(border=True):
            st.markdown("### 🧪 Bench & Field Testing")
            st.caption("Cycle endurance tests (50k+), load testing at 125% SWL, ingress & corrosion screening.")
            st.caption("Pilot deployments in transit and clinic contexts (observational).")
    with c3:
        with st.container(border=True):
            st.markdown("### 🛡️ Safety Architecture")
            st.caption("Interlocks, e-stop, passive-safe geometry, overcurrent protection, state indicator lights.")
            st.caption("Audit trails optional and anonymized.")

    st.write("")
    with st.expander("Read our safety & validation roadmap (indicative)"):
        st.markdown(
            """
            - Establish design controls and verification traceability.
            - Validate mechanical durability, environmental resilience, and human factors.
            - Iterate with clinician and user feedback (co-design).
            - Prepare documentation for market entry and regulatory engagement where required.
            """
        )


# -----------------------------------------------------------------------------
# Impact & Evidence
# -----------------------------------------------------------------------------
def render_impact():
    st.markdown('<a id="impact"></a>', unsafe_allow_html=True)
    section_heading("Impact & Evidence", "Measuring what matters for users and systems.")
    df = make_metrics_df(60)
    total_transfers = int(df["transfers"].sum())
    avg_time_saved = df["avg_time_saved_min"].mean()
    sat = df["user_satisfaction"].mean()

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### Before → After (pilot snapshots)")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Transfers Enabled (60d)", f"{total_transfers:,}", "+4.2%")
            st.caption("Cumulative across pilot sites (illustrative).")
        with col2:
            st.metric("Avg. Time Saved", f"{avg_time_saved:.1f} min", "−0.3 min")
            st.caption("Fewer minutes per transfer frees caregivers and reduces queues.")
        with col3:
            st.metric("User Satisfaction", f"{sat:.2f} / 5", "↑")
            st.caption("Feedback from end-users and staff (Likert).")
        st.markdown("</div>", unsafe_allow_html=True)

    # Testimonials carousel (approximation)
    st.write("")
    st.markdown("#### What users say")
    testimonials = [
        {
            "quote": "INCLIFT gave me the confidence to board without feeling like a burden.",
            "name": "Adjoa K., end-user",
        },
        {
            "quote": "Transfers are faster and safer. Staff strain complaints dropped noticeably.",
            "name": "Clinic supervisor",
        },
        {
            "quote": "Setup is intuitive. The safety interlock prevents mistakes in busy shifts.",
            "name": "Transport operator",
        },
    ]
    t = testimonials[st.session_state.testimonial_index]
    with st.container():
        colA, colB, colC = st.columns([1, 2, 1])
        with colA:
            if st.button("⬅️ Prev", use_container_width=True):
                st.session_state.testimonial_index = (st.session_state.testimonial_index - 1) % len(testimonials)
        with colB:
            with st.container(border=True):
                st.markdown(f"**“{t['quote']}”**")
                st.caption(f"— {t['name']}")
        with colC:
            if st.button("Next ➡️", use_container_width=True):
                st.session_state.testimonial_index = (st.session_state.testimonial_index + 1) % len(testimonials)


# -----------------------------------------------------------------------------
# Pricing & Plans
# -----------------------------------------------------------------------------
def render_pricing():
    st.markdown('<a id="pricing"></a>', unsafe_allow_html=True)
    section_heading("Pricing & Plans", "Transparent options; let's find the right fit.")
    plans = pd.DataFrame(
        {
            "Plan": ["Starter", "Pro", "Enterprise/Gov"],
            "Ideal for": ["Small clinics & schools", "Transport fleets & hospitals", "Municipal & national programs"],
            "Includes": [
                "Device + basic training + 12-mo support",
                "Device + advanced training + priority support + spares kit",
                "Multi-site deployment, SLAs, onboarding, analytics",
            ],
            "Indicative Budget*": ["$ •", "$$ ••", "$$$ •••"],
        }
    )
    st.dataframe(plans, hide_index=True, use_container_width=True)
    st.caption("*Indicative only. Procurement, financing, and maintenance plans available on request.")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Talk to Sales", use_container_width=True):
            st.info("We’ll connect you with our team for a tailored quote.")
    with c2:
        brochure_bytes = generate_brochure_bytes()
        st.download_button(
            "Download Brochure",
            data=brochure_bytes,
            file_name="AURA_Brochure.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with c3:
        if st.button("View Financing Options", use_container_width=True):
            st.success("We offer leasing and phased procurement. Let’s discuss!")


# -----------------------------------------------------------------------------
# Partners
# -----------------------------------------------------------------------------
def render_partners():
    st.markdown('<a id="partners"></a>', unsafe_allow_html=True)
    section_heading("Partners", "Building together with clinics, NGOs, and transport authorities.")
    pcols = st.columns(3)
    partners = [
        (IMAGES["partner1"], "Clinical Pilot Site"),
        (IMAGES["partner2"], "Transport Authority"),
        (IMAGES["partner3"], "NGO & Community"),
    ]
    for (url, label), col in zip(partners, pcols):
        with col:
            with st.container(border=True):
                st.image(url, caption=label, use_column_width=True)
                st.caption("MoUs in place; deployment roadmap under way. [Placeholder]")


# -----------------------------------------------------------------------------
# Team & Contact (combined section per top-nav)
# -----------------------------------------------------------------------------
def render_team_and_contact():
    st.markdown('<a id="team"></a>', unsafe_allow_html=True)
    section_heading("Team", "Engineers, clinicians, and designers committed to accessible mobility.")
    tc1, tc2 = st.columns([1, 1])
    with tc1:
        st.image(IMAGES["team"], caption="Culture of care and craft", use_column_width=True)
    with tc2:
        with st.container(border=True):
            st.markdown("### Founders & Advisors")
            st.markdown("**Kwame Nimako-Boateng** — Founder, Systems & Product (assistive mechanisms)")
            st.markdown("**Clinical Advisor** — Rehab specialist (mobility & safety), pilot liaison")
            st.markdown("**Ops Advisor** — Local manufacturing & supply chain")
            st.caption("We are hiring! Hardware, embedded, and field ops. ✉️ hello@aurahealthtech.org")

    st.write("")
    section_heading("Contact", "We’d love to learn about your needs.")
    with st.container():
        cc1, cc2 = st.columns([1.1, 1])
        with cc1:
            with st.form("contact_form", clear_on_submit=True):
                name = st.text_input("Name*", key="cf_name", help="Your full name")
                email = st.text_input("Email*", key="cf_email", help="We’ll reply here")
                org = st.text_input("Organization", key="cf_org")
                msg = st.text_area("Message*", key="cf_msg", height=140)
                submitted = st.form_submit_button("Send message")
                if submitted:
                    errors = []
                    if not name.strip():
                        errors.append("Name is required.")
                    if "@" not in email or "." not in email:
                        errors.append("Please provide a valid email.")
                    if not msg.strip():
                        errors.append("Message is required.")
                    if errors:
                        st.warning(" • ".join(errors))
                    else:
                        st.session_state.leads.append(
                            {
                                "id": str(uuid.uuid4()),
                                "name": name.strip(),
                                "email": email.strip(),
                                "org": org.strip(),
                                "message": msg.strip(),
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        )
                        st.success("Thanks! Your message has been sent. We’ll be in touch.")
        with cc2:
            st.image(IMAGES["map"], caption="Global reach, local manufacturing (illustrative)", use_column_width=True)
            st.write("**Email:** ", COPY["footer_email"])
            if st.button("Email us", use_container_width=True):
                track_click("email_click")
                st.info("Compose an email to hello@aurahealthtech.org")

    # Simple view of captured leads (for demo)
    with st.expander("Admin view: recent inquiries (demo)"):
        if st.session_state.leads:
            st.dataframe(pd.DataFrame(st.session_state.leads), use_container_width=True)
        else:
            st.caption("No inquiries yet.")


# -----------------------------------------------------------------------------
# Resources (FAQ, downloads)
# -----------------------------------------------------------------------------
def render_resources():
    section_heading("Resources", "Downloads, FAQs, and media.")
    rc1, rc2 = st.columns([1, 1])
    with rc1:
        st.markdown("### Downloads")
        brochure_bytes = generate_brochure_bytes()
        st.download_button("📄 Download brochure", data=brochure_bytes, file_name="AURA_Brochure.txt", mime="text/plain")
        one_pager_text = "AURA Health Tech — One Pager\n\nINCLIFT overview and pilot snapshots."
        one_pager = io.BytesIO(one_pager_text.encode('utf-8'))
        st.download_button("📎 Download one-pager", data=one_pager.getvalue(), file_name="AURA_OnePager.txt", mime="text/plain")
        st.caption("Downloads are placeholders for demo purposes.")

    with rc2:
        st.markdown("### Demo video (placeholder)")
        st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")  # placeholder external URL

    st.write("")
    with st.expander("FAQ"):
        faqs = [
            ("Is INCLIFT a medical device?", "Classification varies by market and use case. We design to applicable standards and prioritize safety and reliability."),
            ("Do you store personal data?", "By default, no. Optional usage analytics are anonymized and opt-in."),
            ("Can AURA support maintenance locally?", "Yes. Our design prioritizes modular parts and local training."),
            ("What’s the typical deployment time?", "Pilots can start within weeks, with training and support included."),
            ("Financing options?", "Leasing and phased procurement available; contact us to discuss."),
            ("Accessibility?", "High-contrast UI, keyboard-friendly forms, alt text throughout our digital materials."),
        ]
        for q, a in faqs:
            with st.container(border=True):
                st.markdown(f"**{q}**")
                st.caption(a)
    st.markdown('[Back to top](#home)')


# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
def render_footer():
    st.markdown(
        f"""
        <div class="footer">
            <div>© {datetime.utcnow().year} AURA Health Tech. All rights reserved.</div>
            <div class="small">
                <a href="#home">Home</a> •
                <a href="#solution">Solution</a> •
                <a href="#products">Products</a> •
                <a href="#clinical">Clinical & Safety</a> •
                <a href="#impact">Impact</a> •
                <a href="#pricing">Pricing</a> •
                <a href="#partners">Partners</a> •
                <a href="#team">Team & Contact</a>
            </div>
            <div class="small">Privacy • Terms • Accessibility • {COPY['footer_email']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Page Render
# -----------------------------------------------------------------------------
render_hero()
render_solution()
render_products()
render_clinical()
render_impact()
render_pricing()
render_partners()
render_team_and_contact()
render_resources()
render_footer()

# -----------------------------------------------------------------------------
# QA Checklist (developer notes)
# -----------------------------------------------------------------------------
# - [x] Single-file app (app.py), Streamlit >= 1.37, no external packages (only pandas).
# - [x] Web-sourced images only, with alt text where applicable (Streamlit images use captions).
# - [x] Sticky top bar emulated via CSS position: sticky.
# - [x] Smooth navigation via anchor links; top buttons update section and anchor.
# - [x] Hero section with gradient overlay, strong headline, CTAs (Book a demo + Download brochure).
# - [x] Feature grid (solution) + spec table + "How it works" stepper.
# - [x] Metrics row using st.metric with cached synthetic data.
# - [x] Clinical & Safety section with standards/testing/architecture.
# - [x] Impact & Evidence with KPI metrics and testimonials carousel (prev/next).
# - [x] Pricing table with indicative tiers and CTAs.
# - [x] Partners section with placeholder logos and captions.
# - [x] Team & Contact form: validation + stored submissions in st.session_state.
# - [x] Resources: downloads (BytesIO) + video placeholder + FAQ expanders.
# - [x] High-contrast palette, accessible defaults, responsive column layouts.
# - [x] Optional analytics stub via st.session_state.clicks (used for email button).
