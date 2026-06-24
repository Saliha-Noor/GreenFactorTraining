import streamlit as st
import os
import json
import shutil
import time
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# PAGE CONFIG (must be first Streamlit call)
# ============================================================================

st.set_page_config(
    page_title="Exam Forge",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# ELITE DESIGN SYSTEM — Full CSS overhaul
# ============================================================================

def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --color-primary:   #667eea;
        --color-secondary: #764ba2;
        --color-accent:    #f093fb;
        --color-gold:      #FFD700;
        --color-success:   #10b981;
        --color-warning:   #f59e0b;
        --color-danger:    #ef4444;
        --color-dark:      #1e293b;
        --color-light:     #f8fafc;

        --g-arc: linear-gradient(135deg,
            #667eea 0%, #764ba2 25%,
            #f093fb 50%, #f5576c 75%,
            #fda085 100%);
        --g-secondary: linear-gradient(120deg, #89f7fe 0%, #66a6ff 100%);
        --g-success:   linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --g-gold:      linear-gradient(135deg, #FFD700 0%, #FFA500 50%, #FF8C00 100%);
        --g-warm:      linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);

        --c-violet:  #667eea;
        --c-indigo:  #764ba2;
        --c-cyan:    #f093fb;
        --c-amber:   #f59e0b;
        --c-emerald: #10b981;
        --c-rose:    #ef4444;

        --ink:    #1e293b;
        --ink-80: rgba(30,41,59,0.8);
        --ink-50: rgba(30,41,59,0.5);
        --ink-20: rgba(30,41,59,0.2);

        --surface:      transparent;
        --surface-card: #ffffff;

        --glass-bg:     rgba(255,255,255,0.1);
        --glass-border: rgba(255,255,255,0.2);
        --glass-shadow: 0 8px 32px 0 rgba(31,38,135,0.37);
        --glass-blur:   blur(12px);

        --dark-glass:  rgba(0,0,0,0.15);
        --dark-border: rgba(255,255,255,0.15);
        --dark-shadow: 0 8px 40px rgba(0,0,0,0.4);

        --font-display: 'Space Grotesk', sans-serif;
        --font-body:    'Plus Jakarta Sans', sans-serif;
        --font-mono:    'JetBrains Mono', monospace;

        --t-xs:   clamp(0.7rem,  1.2vw, 0.78rem);
        --t-sm:   clamp(0.82rem, 1.5vw, 0.9rem);
        --t-base: clamp(0.93rem, 2vw,   1rem);
        --t-md:   clamp(1rem,    2.2vw, 1.1rem);
        --t-lg:   clamp(1.1rem,  2.5vw, 1.25rem);
        --t-xl:   clamp(1.25rem, 3vw,   1.5rem);
        --t-2xl:  clamp(1.5rem,  3.5vw, 2rem);
        --t-3xl:  clamp(2rem,    4.5vw, 2.75rem);
        --t-4xl:  clamp(2.5rem,  5.5vw, 3.5rem);

        --s1: 8px;  --s2: 16px; --s3: 24px; --s4: 32px;
        --s5: 40px; --s6: 48px; --s7: 56px; --s8: 64px;

        --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
        --ease-out:    cubic-bezier(0.16, 1, 0.3, 1);
        --dur-fast:    140ms;
        --dur-base:    260ms;
        --dur-slow:    440ms;

        --r-sm:  8px;
        --r-md:  14px;
        --r-lg:  20px;
        --r-xl:  28px;
        --r-2xl: 40px;

        --z-nav:     200;
        --z-overlay: 300;
        --z-tooltip: 400;
    }

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    #MainMenu, .stDeployButton, footer, header,
    [data-testid='stToolbar'],
    [data-testid='stSidebar'] { visibility: hidden !important; height: 0 !important; display: none !important; }
    .main > div { padding-top: 0 !important; }
    .block-container { padding-top: 0 !important; max-width: 100% !important; padding-left: 0 !important; padding-right: 0 !important; }

    html, body, .stApp {
        font-family: var(--font-body);
        background: var(--surface);
        color: var(--ink);
        line-height: 1.65;
        font-size: var(--t-base);
        -webkit-font-smoothing: antialiased;
    }

    .stApp::before {
        content: '';
        position: fixed; inset: 0; z-index: 0;
        background:
            radial-gradient(ellipse 80% 60% at 15% 30%, rgba(99,102,241,0.14) 0%, transparent 60%),
            radial-gradient(ellipse 70% 50% at 85% 15%, rgba(59,130,246,0.10) 0%, transparent 55%),
            radial-gradient(ellipse 60% 70% at 60% 85%, rgba(79,70,229,0.09) 0%, transparent 50%),
            linear-gradient(160deg, #eef2ff 0%, #dbeafe 40%, #e0f2fe 100%);
        animation: meshShift 18s ease-in-out infinite alternate;
        pointer-events: none;
    }
    @keyframes meshShift { 0% { opacity: 1; } 50% { opacity: 0.85; } 100% { opacity: 1; } }
    .stApp > * { position: relative; z-index: 1; }

    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--c-violet); border-radius: 99px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--c-indigo); }

    .ef-navbar {
        position: sticky; top: 0; z-index: var(--z-nav);
        background: rgba(244,243,255,0.82);
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        border-bottom: 1px solid var(--glass-border);
        padding: 0 var(--s4);
        height: 64px;
        display: flex; align-items: center; justify-content: space-between;
        box-shadow: 0 1px 0 rgba(124,58,237,0.08), 0 4px 24px rgba(79,70,229,0.06);
    }

    .ef-logo {
        font-family: var(--font-display);
        font-size: var(--t-xl);
        font-weight: 700;
        letter-spacing: -0.03em;
        background: var(--g-arc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        display: flex; align-items: center; gap: var(--s1);
    }

    .ef-progress-track { display: flex; gap: 5px; align-items: center; }
    .ef-seg {
        height: 5px; width: 36px; border-radius: 99px;
        background: rgba(79,70,229,0.12);
        position: relative; overflow: hidden;
        transition: background var(--dur-base) var(--ease-out);
    }
    .ef-seg.done { background: var(--g-arc); }
    .ef-seg.done::after {
        content: '';
        position: absolute; inset: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent);
        animation: shimmerSlide 2.2s ease-in-out infinite;
    }
    @keyframes shimmerSlide { 0% { transform: translateX(-100%); } 100% { transform: translateX(100%); } }

    div[data-testid='column'] .stButton > button {
        font-family: var(--font-body) !important;
        font-size: var(--t-sm) !important;
        font-weight: 600 !important;
        border-radius: var(--r-md) !important;
        transition: all var(--dur-base) var(--ease-out) !important;
        border: 1.5px solid transparent !important;
        padding: 9px 18px !important;
        white-space: nowrap;
    }
    div[data-testid='column'] .stButton > button[kind="primary"] {
        background: var(--g-arc) !important;
        color: #fff !important;
        border-color: transparent !important;
        box-shadow: 0 4px 16px rgba(124,58,237,0.28) !important;
    }
    div[data-testid='column'] .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(124,58,237,0.38) !important;
    }
    div[data-testid='column'] .stButton > button[kind="secondary"] {
        background: rgba(255,255,255,0.7) !important;
        color: var(--ink-80) !important;
        border-color: rgba(79,70,229,0.18) !important;
        backdrop-filter: blur(8px);
    }
    div[data-testid='column'] .stButton > button[kind="secondary"]:hover {
        background: rgba(255,255,255,0.95) !important;
        border-color: var(--c-violet) !important;
        color: var(--c-violet) !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button {
        font-family: var(--font-body) !important;
        font-weight: 600 !important;
        border-radius: var(--r-md) !important;
        transition: all var(--dur-base) var(--ease-out) !important;
    }
    .stButton > button[kind="primary"] {
        background: var(--g-arc) !important;
        color: #fff !important;
        border: none !important;
        box-shadow: 0 4px 20px rgba(124,58,237,0.3) !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(124,58,237,0.42) !important;
    }

    .ef-page {
        max-width: 1320px;
        margin: 0 auto;
        padding: var(--s4) var(--s4) var(--s8);
    }

    .ef-hero {
        position: relative;
        border-radius: var(--r-2xl);
        overflow: hidden;
        padding: var(--s8) var(--s6);
        margin-bottom: var(--s6);
        min-height: 320px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        background: var(--g-arc);
        box-shadow: 0 20px 60px rgba(124,58,237,0.3), 0 4px 12px rgba(0,0,0,0.08);
    }
    .ef-hero::before {
        content: '';
        position: absolute; inset: 0; z-index: 0;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.06'/%3E%3C/svg%3E");
        background-size: 200px;
        opacity: 0.4;
        animation: noiseScroll 8s steps(2) infinite;
    }
    @keyframes noiseScroll {
        0% { transform: translate(0,0); } 25% { transform: translate(-5%, 5%); }
        50% { transform: translate(5%, -5%); } 75% { transform: translate(-3%, -3%); }
        100% { transform: translate(0,0); }
    }
    .ef-hero::after {
        content: '';
        position: absolute; inset: 0; z-index: 0;
        background:
            radial-gradient(circle 180px at 10% 80%, rgba(255,255,255,0.12) 0%, transparent 70%),
            radial-gradient(circle 140px at 90% 20%, rgba(255,255,255,0.10) 0%, transparent 70%),
            radial-gradient(circle 100px at 55% 50%, rgba(255,255,255,0.07) 0%, transparent 70%);
        animation: orbDrift 12s ease-in-out infinite alternate;
    }
    @keyframes orbDrift { 0% { transform: scale(1) translate(0,0); } 100% { transform: scale(1.08) translate(2%, -2%); } }
    .ef-hero-content { position: relative; z-index: 1; }
    .ef-hero-tag {
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(255,255,255,0.18);
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 99px;
        padding: 5px 14px;
        font-size: var(--t-xs);
        font-weight: 600;
        color: #fff;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: var(--s3);
        backdrop-filter: blur(8px);
        animation: fadeSlideUp 0.6s var(--ease-out) both;
    }
    .ef-hero-title {
        font-family: var(--font-display);
        font-size: var(--t-4xl);
        font-weight: 700;
        color: #fff;
        letter-spacing: -0.04em;
        line-height: 1.1;
        margin-bottom: var(--s2);
        animation: fadeSlideUp 0.6s var(--ease-out) 0.1s both;
    }
    .ef-hero-sub {
        font-size: var(--t-lg);
        color: rgba(255,255,255,0.85);
        font-weight: 400;
        max-width: 520px;
        animation: fadeSlideUp 0.6s var(--ease-out) 0.2s both;
    }
    @keyframes fadeSlideUp { from { opacity: 0; transform: translateY(24px); } to { opacity: 1; transform: translateY(0); } }

    .ef-glass {
        background: var(--glass-bg);
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        border: 1px solid var(--glass-border);
        border-radius: var(--r-lg);
        padding: var(--s4);
        box-shadow: var(--glass-shadow);
        transition: transform var(--dur-base) var(--ease-out), box-shadow var(--dur-base) var(--ease-out);
        position: relative;
        overflow: hidden;
    }
    .ef-glass::before {
        content: '';
        position: absolute; top: 0; left: 0; right: 0; height: 2px;
        background: var(--g-arc);
        opacity: 0;
        transition: opacity var(--dur-base) ease;
    }
    .ef-glass:hover::before { opacity: 1; }
    .ef-glass:hover { transform: translateY(-3px); box-shadow: 0 16px 48px rgba(79,70,229,0.16), 0 2px 8px rgba(0,0,0,0.06); }
    .ef-glass h1, .ef-glass h2, .ef-glass h3,
    .ef-glass h4, .ef-glass p, .ef-glass span,
    .ef-glass li { color: var(--ink); }

    .ef-menu-card {
        background: var(--surface-card);
        border: 1px solid rgba(79,70,229,0.1);
        border-radius: var(--r-xl);
        padding: var(--s4) var(--s4) var(--s3);
        box-shadow: 0 2px 12px rgba(0,0,0,0.05), 0 1px 3px rgba(0,0,0,0.04);
        transition: all var(--dur-slow) var(--ease-out);
        position: relative; overflow: hidden;
        height: 100%;
    }
    .ef-menu-card::after {
        content: '';
        position: absolute; inset: 0;
        background: var(--g-arc);
        opacity: 0;
        transition: opacity var(--dur-base) ease;
        z-index: 0;
    }
    .ef-menu-card:hover {
        transform: translateY(-6px) scale(1.01);
        box-shadow: 0 20px 48px rgba(124,58,237,0.18), 0 4px 12px rgba(0,0,0,0.06);
        border-color: rgba(124,58,237,0.3);
    }
    .ef-menu-card:hover .mc-icon,
    .ef-menu-card:hover .mc-title,
    .ef-menu-card:hover .mc-desc { position: relative; z-index: 1; }
    .ef-menu-card .mc-icon-wrap {
        width: 52px; height: 52px;
        border-radius: var(--r-md);
        background: linear-gradient(135deg, rgba(124,58,237,0.1), rgba(6,182,212,0.1));
        display: flex; align-items: center; justify-content: center;
        font-size: 1.7rem;
        margin-bottom: var(--s2);
        position: relative; z-index: 1;
        transition: all var(--dur-base) var(--ease-spring);
    }
    .ef-menu-card:hover .mc-icon-wrap { background: rgba(255,255,255,0.25); transform: scale(1.1) rotate(-4deg); }
    .mc-title {
        font-family: var(--font-display);
        font-size: var(--t-md);
        font-weight: 700;
        color: var(--ink);
        margin-bottom: 6px;
        letter-spacing: -0.02em;
        position: relative; z-index: 1;
        transition: color var(--dur-base) ease;
    }
    .mc-desc {
        font-size: var(--t-sm);
        color: var(--ink-50);
        line-height: 1.55;
        position: relative; z-index: 1;
        transition: color var(--dur-base) ease;
    }
    .mc-status { margin-top: var(--s2); position: relative; z-index: 1; }
    .ef-menu-card:hover .mc-title { color: var(--ink); }
    .ef-menu-card:hover .mc-desc  { color: var(--ink-80); }

    .ef-metric {
        background: var(--surface-card);
        border: 1px solid rgba(79,70,229,0.08);
        border-radius: var(--r-lg);
        padding: var(--s3) var(--s3) var(--s2);
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: all var(--dur-base) var(--ease-out);
    }
    .ef-metric:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(79,70,229,0.12); }
    .ef-metric-val {
        font-family: var(--font-display);
        font-size: var(--t-2xl);
        font-weight: 700;
        letter-spacing: -0.03em;
        background: var(--g-arc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.1;
        margin-bottom: 6px;
    }
    .ef-metric-val.good { background: var(--g-success); -webkit-background-clip: text; background-clip: text; }
    .ef-metric-val.warn { background: var(--g-warm); -webkit-background-clip: text; background-clip: text; }
    .ef-metric-label { font-size: var(--t-xs); font-weight: 600; color: var(--ink-50); letter-spacing: 0.04em; text-transform: uppercase; }

    .ef-badge {
        display: inline-flex; align-items: center; gap: 4px;
        padding: 3px 10px;
        border-radius: 99px;
        font-size: var(--t-xs);
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        white-space: nowrap;
    }
    .ef-badge-violet  { background: rgba(124,58,237,0.1); color: var(--c-violet); border: 1px solid rgba(124,58,237,0.2); }
    .ef-badge-cyan    { background: rgba(6,182,212,0.1);  color: #0891b2;         border: 1px solid rgba(6,182,212,0.2); }
    .ef-badge-emerald { background: rgba(16,185,129,0.1); color: #059669;         border: 1px solid rgba(16,185,129,0.2); }
    .ef-badge-amber   { background: rgba(245,158,11,0.1); color: #d97706;         border: 1px solid rgba(245,158,11,0.2); }
    .ef-badge-rose    { background: rgba(244,63,94,0.1);  color: #e11d48;         border: 1px solid rgba(244,63,94,0.2); }
    .ef-badge-ink     { background: rgba(13,15,26,0.07);  color: var(--ink-80);   border: 1px solid rgba(13,15,26,0.12); }

    .ef-heading {
        font-family: var(--font-display);
        font-size: var(--t-3xl);
        font-weight: 700;
        color: var(--ink);
        letter-spacing: -0.04em;
        margin-bottom: var(--s2);
        line-height: 1.15;
    }
    .ef-sub { font-size: var(--t-base); color: var(--ink-50); margin-bottom: var(--s4); max-width: 600px; }
    .ef-eyebrow { font-size: var(--t-xs); font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: var(--c-violet); margin-bottom: var(--s1); }

    .ef-feature-card {
        background: var(--surface-card);
        border: 1px solid rgba(79,70,229,0.08);
        border-radius: var(--r-xl);
        padding: var(--s5) var(--s4);
        text-align: center;
        transition: all var(--dur-slow) var(--ease-out);
        position: relative; overflow: hidden;
    }
    .ef-feature-card::before {
        content: '';
        position: absolute; inset: 0;
        background: var(--g-arc);
        opacity: 0;
        transition: opacity var(--dur-slow) ease;
        z-index: 0;
    }
    .ef-feature-card:hover { transform: translateY(-10px); box-shadow: 0 24px 60px rgba(124,58,237,0.2); }
    .ef-feature-card:hover::before { opacity: 1; }
    .ef-feature-card:hover .ef-feature-title,
    .ef-feature-card:hover .ef-feature-desc { color: #fff; }
    .ef-feature-card > * { position: relative; z-index: 1; }
    .ef-feature-icon {
        width: 64px; height: 64px;
        border-radius: var(--r-lg);
        background: linear-gradient(135deg, rgba(124,58,237,0.12), rgba(6,182,212,0.12));
        display: flex; align-items: center; justify-content: center;
        font-size: 2rem;
        margin: 0 auto var(--s3);
        transition: all var(--dur-base) var(--ease-spring);
    }
    .ef-feature-card:hover .ef-feature-icon { background: rgba(255,255,255,0.2); transform: scale(1.15) rotate(-6deg); }
    .ef-feature-title {
        font-family: var(--font-display);
        font-size: var(--t-lg);
        font-weight: 700;
        color: var(--ink);
        letter-spacing: -0.02em;
        margin-bottom: var(--s1);
        transition: color var(--dur-base) ease;
    }
    .ef-feature-desc { font-size: var(--t-sm); color: var(--ink-50); line-height: 1.6; transition: color var(--dur-base) ease; }

    .ef-timeline { position: relative; padding: var(--s2) 0; }
    .ef-timeline::before {
        content: '';
        position: absolute;
        left: 24px; top: 0; bottom: 0; width: 2px;
        background: linear-gradient(to bottom, var(--c-violet), var(--c-cyan));
        opacity: 0.2;
    }
    .ef-timeline-item {
        display: flex; align-items: flex-start; gap: var(--s3);
        margin-bottom: var(--s4);
        animation: fadeSlideUp 0.5s var(--ease-out) both;
    }
    .ef-timeline-dot {
        width: 48px; height: 48px;
        border-radius: 50%;
        border: 2px solid rgba(124,58,237,0.2);
        background: var(--surface-card);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.2rem;
        flex-shrink: 0;
        position: relative; z-index: 1;
        box-shadow: 0 2px 12px rgba(124,58,237,0.1);
        transition: all var(--dur-base) var(--ease-spring);
    }
    .ef-timeline-dot.done {
        background: var(--g-arc);
        border-color: transparent;
        color: white;
        box-shadow: 0 4px 16px rgba(124,58,237,0.35);
        transform: scale(1.08);
    }
    .ef-timeline-body {
        background: var(--surface-card);
        border: 1px solid rgba(79,70,229,0.08);
        border-radius: var(--r-md);
        padding: var(--s2) var(--s3);
        flex: 1;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        transition: all var(--dur-base) ease;
    }
    .ef-timeline-body:hover { border-color: rgba(124,58,237,0.2); box-shadow: 0 4px 16px rgba(124,58,237,0.08); }
    .ef-timeline-body h4 { font-family: var(--font-display); font-size: var(--t-base); font-weight: 700; color: var(--ink); letter-spacing: -0.02em; margin-bottom: 3px; }
    .ef-timeline-body p { font-size: var(--t-sm); color: var(--ink-50); margin: 0; }

    .ef-question-card {
        background: var(--surface-card);
        border: 1px solid rgba(79,70,229,0.08);
        border-radius: var(--r-lg);
        padding: var(--s4);
        margin-bottom: var(--s3);
        transition: all var(--dur-base) ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .ef-question-card:hover { border-color: rgba(124,58,237,0.2); box-shadow: 0 6px 24px rgba(124,58,237,0.08); }
    .ef-question-meta { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--s3); flex-wrap: wrap; gap: 8px; }
    .ef-question-num { font-family: var(--font-mono); font-size: var(--t-xs); color: var(--ink-50); font-weight: 500; }
    .ef-question-text { font-size: var(--t-md); font-weight: 500; color: var(--ink); line-height: 1.6; margin-bottom: var(--s2); }

    .ef-empty {
        text-align: center;
        padding: var(--s8) var(--s4);
        background: var(--surface-card);
        border: 2px dashed rgba(124,58,237,0.18);
        border-radius: var(--r-xl);
    }
    .ef-empty-icon { font-size: 3.5rem; display: block; margin-bottom: var(--s3); opacity: 0.5; }
    .ef-empty h3 { font-family: var(--font-display); font-size: var(--t-xl); font-weight: 700; color: var(--ink); letter-spacing: -0.02em; margin-bottom: var(--s1); }
    .ef-empty p { font-size: var(--t-sm); color: var(--ink-50); max-width: 380px; margin: 0 auto var(--s4); }

    .ef-topic-row {
        background: var(--surface-card);
        border: 1px solid rgba(79,70,229,0.08);
        border-radius: var(--r-lg);
        padding: var(--s3) var(--s4);
        margin-bottom: var(--s2);
        display: flex; justify-content: space-between; align-items: center;
        flex-wrap: wrap; gap: var(--s2);
        transition: all var(--dur-base) ease;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }
    .ef-topic-row:hover { border-color: rgba(124,58,237,0.2); box-shadow: 0 4px 20px rgba(124,58,237,0.08); transform: translateX(4px); }
    .ef-topic-name { font-family: var(--font-display); font-size: var(--t-base); font-weight: 700; color: var(--ink); letter-spacing: -0.02em; }
    .ef-topic-concepts { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 6px; }
    .ef-concept-pill { font-size: var(--t-xs); padding: 2px 8px; border-radius: 99px; background: rgba(124,58,237,0.07); color: var(--c-violet); font-weight: 600; }

    .ef-score-ring {
        background: var(--glass-bg);
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        border: 1px solid var(--glass-border);
        border-radius: var(--r-2xl);
        padding: var(--s6) var(--s4);
        text-align: center;
        box-shadow: var(--glass-shadow);
        margin-bottom: var(--s4);
    }

    .ef-proc-card {
        background: var(--surface-card);
        border: 1px solid rgba(124,58,237,0.15);
        border-radius: var(--r-lg);
        padding: var(--s3) var(--s4);
        margin: var(--s2) 0;
        box-shadow: 0 2px 10px rgba(124,58,237,0.06);
    }
    .ef-proc-card h4 { font-family: var(--font-display); font-size: var(--t-base); font-weight: 700; color: var(--c-violet); margin: 0; }

    .ef-paper-sheet {
        background: #fff;
        border-radius: var(--r-xl);
        padding: var(--s6) var(--s8);
        box-shadow: 0 8px 40px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid rgba(79,70,229,0.06);
        margin-top: var(--s4);
    }
    .ef-paper-title { font-family: 'Georgia', serif; font-size: var(--t-2xl); font-weight: 700; color: var(--ink); text-align: center; letter-spacing: -0.02em; margin-bottom: var(--s1); }
    .ef-paper-meta { font-size: var(--t-sm); color: var(--ink-50); text-align: center; font-style: italic; margin-bottom: var(--s3); }
    .ef-paper-divider { border: none; border-top: 2px solid var(--ink); margin: var(--s3) 0; }
    .ef-paper-section { font-family: 'Georgia', serif; font-size: var(--t-lg); font-weight: 700; color: var(--ink); border-bottom: 1px solid rgba(0,0,0,0.12); padding-bottom: var(--s1); margin: var(--s4) 0 var(--s3); }
    .ef-paper-question { margin: var(--s3) 0 var(--s4) var(--s2); padding: var(--s2) var(--s3); border-radius: var(--r-md); background: rgba(79,70,229,0.02); border: 1px solid rgba(79,70,229,0.04); }
    .ef-paper-question p { color: var(--ink); font-size: var(--t-base); line-height: 1.7; margin: 0; }
    .ef-paper-lines { margin-top: var(--s2); border-bottom: 1px dotted #ccc; height: 70px; }
    .ef-topic-chip { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 700; color: white; margin-left: 8px; vertical-align: middle; }

    .ef-paper-instructions {
        margin: 0 0 8px 0;
        padding: 5px 0;
        font-size: var(--t-sm);
        color: var(--ink);
        line-height: 1.6;
        display: block;
    }

    .ef-notes-viewer {
        background: var(--surface-card);
        border: 1px solid rgba(79,70,229,0.08);
        border-radius: var(--r-lg);
        padding: var(--s5) var(--s6);
        max-height: 500px;
        overflow-y: auto;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
        font-size: var(--t-base);
        line-height: 1.8;
        color: var(--ink);
    }

    [data-testid='stRadio'] > div { display: flex; gap: 10px; flex-wrap: wrap; }
    [data-testid='stRadio'] label {
        border: 1.5px solid rgba(79,70,229,0.15) !important;
        border-radius: var(--r-md) !important;
        padding: 8px 14px !important;
        transition: all var(--dur-base) ease !important;
        background: var(--surface-card) !important;
        font-size: var(--t-sm) !important;
        cursor: pointer !important;
    }
    [data-testid='stRadio'] label:hover { border-color: var(--c-violet) !important; background: rgba(124,58,237,0.04) !important; }
    [data-testid='stSelectbox'] > div > div { border-radius: var(--r-md) !important; border: 1.5px solid rgba(79,70,229,0.15) !important; background: var(--surface-card) !important; font-family: var(--font-body) !important; }
    [data-testid='stFileUploader'] { border: 2px dashed rgba(124,58,237,0.25) !important; border-radius: var(--r-lg) !important; background: rgba(124,58,237,0.02) !important; transition: all var(--dur-base) ease !important; }
    [data-testid='stFileUploader']:hover { border-color: var(--c-violet) !important; background: rgba(124,58,237,0.04) !important; }
    [data-testid='stProgress'] > div > div { background: var(--g-arc) !important; border-radius: 99px !important; }
    [data-testid='stProgress'] > div { background: rgba(124,58,237,0.1) !important; border-radius: 99px !important; height: 8px !important; }
    [data-testid='stExpander'] { background: var(--surface-card) !important; border: 1px solid rgba(79,70,229,0.08) !important; border-radius: var(--r-md) !important; box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important; margin-bottom: var(--s2) !important; }
    [data-testid='stCheckbox'] { font-size: var(--t-sm) !important; }
    [data-testid='stAlert'] { border-radius: var(--r-md) !important; border-left-width: 4px !important; }
    [data-testid='stSpinner'] { color: var(--c-violet) !important; }

    @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
    @keyframes pulseRing { 0% { box-shadow: 0 0 0 0 rgba(124,58,237,0.35); } 70% { box-shadow: 0 0 0 12px rgba(124,58,237,0); } 100% { box-shadow: 0 0 0 0 rgba(124,58,237,0); } }
    .float { animation: float 3.5s ease-in-out infinite; }
    .pulse { animation: pulseRing 2s ease infinite; }

    @media (max-width: 768px) {
        .ef-hero { padding: var(--s6) var(--s3); min-height: 240px; }
        .ef-hero-title { font-size: var(--t-3xl); }
        .ef-navbar { padding: 0 var(--s2); }
        .ef-paper-sheet { padding: var(--s4) var(--s3); }
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# SESSION STATE MANAGEMENT
# ============================================================================

def init_session_state():
    defaults = {
        'current_page': 'Home',
        'home_sub': None,
        'materials_sub': None,
        'study_sub': None,
        'quiz_sub': None,
        'results_sub': None,
        'classroom_connected': False,
        'classroom_courses': [],
        'chosen_course_id': None,
        'chosen_course_name': "",
        'course_materials': [],
        'selected_lectures': [],
        'github_selected_repo': "",
        'github_folders': [],
        'github_root_files': [],
        'github_folder_name': "",
        'github_folder_files': [],
        'selected_github_files': [],
        'uploaded_names': [],
        'quiz_submitted': False,
        'user_answers': {},
        'session_chunk_files': [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ============================================================================
# HELPERS
# ============================================================================

def nav(page: str):
    st.session_state["current_page"] = page
    st.rerun()

def step_done(key: str) -> bool:
    paths = {
        "fetch":    "data/chunks",
        "notes":    "data/output/notes",
        "plan":     "data/output/plan.json",
        "analyze":  "data/output/paper_analysis.json",
        "quiz":     "data/output/quiz/full_quiz.json",
        "score":    "data/output/scores/score_report.json",
        "practice": "data/output/practice_paper/practice_paper.json",
    }
    p = paths.get(key, "")
    if not p: return False
    if os.path.isdir(p): return bool(os.listdir(p))
    return os.path.exists(p)

def get_repos():
    raw = os.getenv("GITHUB_REPOS", os.getenv("GITHUB_REPO", ""))
    return [r.strip() for r in raw.split(",") if r.strip()]

def clear_pipeline():
    for folder in ["data/chunks", "data/output"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    st.session_state["selected_lectures"] = []
    st.session_state["selected_github_files"] = []
    st.session_state["uploaded_names"] = []
    st.session_state["quiz_submitted"] = False
    st.session_state["user_answers"] = {}
    st.session_state["session_chunk_files"] = []

_PIPELINE_KEYS = ["fetch", "notes", "plan", "analyze", "practice", "quiz", "score"]
_PROGRESS_KEYS = ["fetch", "notes", "plan", "analyze", "practice", "quiz"]

def go_sub(state_key: str, value):
    st.session_state[state_key] = value
    st.rerun()

def back_to_menu(state_key: str, label: str = "← Back"):
    if st.button(label, key=f"back_{state_key}_{st.session_state.get(state_key)}"):
        st.session_state[state_key] = None
        st.rerun()

def badge(text, variant="violet"):
    return f'<span class="ef-badge ef-badge-{variant}">{text}</span>'

def menu_card(icon: str, title: str, desc: str, status_html: str = "") -> bool:
    st.markdown(f"""
    <div class="ef-menu-card">
        <div class="mc-icon-wrap">{icon}</div>
        <div class="mc-title">{title}</div>
        <div class="mc-desc">{desc}</div>
        <div class="mc-status">{status_html}</div>
    </div>
    """, unsafe_allow_html=True)
    return st.button("Open →", key=f"open_{title}", use_container_width=True)

def metric(val, label, variant=""):
    return f'<div class="ef-metric"><div class="ef-metric-val {variant}">{val}</div><div class="ef-metric-label">{label}</div></div>'


# ============================================================================
# NAVIGATION
# ============================================================================

def render_navbar():
    segs = ""
    for step in _PROGRESS_KEYS:
        cls = "ef-seg done" if step_done(step) else "ef-seg"
        segs += f'<div class="{cls}"></div>'

    done_count = sum(1 for k in _PROGRESS_KEYS if step_done(k))
    total_steps = len(_PROGRESS_KEYS)

    st.markdown(f"""
    <div class="ef-navbar">
        <div class="ef-logo">⚡ ExamForge</div>
        <div style="display:flex;align-items:center;gap:16px;">
            <span style="font-size:0.72rem;font-weight:600;color:var(--ink-50);letter-spacing:0.05em;text-transform:uppercase;">
                {done_count}/{total_steps} steps
            </span>
            <div class="ef-progress-track">{segs}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_tab_navigation():
    tabs = [
        ("Home", "🏠 Home"),
        ("Materials", "📤 Materials"),
        ("Study & Plan", "📚 Study"),
        ("Practice Paper", "📋 Practice"),
        ("Quiz", "🎯 Quiz"),
        ("Results", "📊 Results"),
    ]
    cols = st.columns(len(tabs))
    for col, (page_id, label) in zip(cols, tabs):
        with col:
            is_current = st.session_state["current_page"] == page_id
            if st.button(label, key=f"tab_{page_id}", use_container_width=True,
                         type=("primary" if is_current else "secondary")):
                st.session_state["current_page"] = page_id
                st.rerun()
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


# ============================================================================
# HOME PAGE  ── exact UI from app.py 
# ============================================================================

def render_home_page():
    sub = st.session_state["home_sub"]
    if sub is None:         _render_home_menu()
    elif sub == "pipeline": _render_home_pipeline()
    elif sub == "features": _render_home_features()
    elif sub == "quick":    _render_home_quick_actions()


def _render_home_menu():
    done_count = sum(1 for k in _PIPELINE_KEYS if step_done(k))

    if done_count == 0:
        status_badge = badge("Not started", "ink")
    elif done_count == len(_PIPELINE_KEYS):
        status_badge = badge("✓ Complete", "emerald")
    else:
        status_badge = badge(f"{done_count}/{len(_PIPELINE_KEYS)} done", "violet")

    st.markdown(f"""
    <div class="ef-hero">
        <div class="ef-hero-content">
            <div class="ef-hero-tag">✨ AI-Powered Exam Prep</div>
            <h1 class="ef-hero-title">Your Personal<br>Exam Engine</h1>
            <p class="ef-hero-sub">Import materials, generate notes, analyze past papers,<br>build a practice exam, and quiz yourself — all in one place.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="ef-glass" style="margin-bottom:var(--s4);display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
        <div>
            <div class="ef-eyebrow">Progress</div>
            <span style="font-family:var(--font-display);font-size:var(--t-xl);font-weight:700;color:var(--ink);letter-spacing:-0.02em;">
                Your learning journey {("is complete 🎉" if done_count == len(_PIPELINE_KEYS) else "awaits")}
            </span>
        </div>
        <div>{status_badge}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="ef-eyebrow" style="margin-bottom:var(--s2);">Explore</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if menu_card("📍", "Learning Pipeline",
                     "Every step from raw materials to final score — see what's done.",
                     badge(f"{done_count}/{len(_PIPELINE_KEYS)} complete", "violet")):
            go_sub("home_sub", "pipeline")
    with col2:
        if menu_card("✨", "Key Features",
                     "What ExamForge can do for you, at a glance."):
            go_sub("home_sub", "features")
    with col3:
        if menu_card("🚀", "Quick Actions",
                     "Jump straight to Materials, Practice Paper, or Results."):
            go_sub("home_sub", "quick")


def _render_home_pipeline():
    back_to_menu("home_sub")
    st.markdown("""
    <div style="margin-bottom:var(--s4);">
        <div class="ef-eyebrow">Overview</div>
        <h1 class="ef-heading">Learning Pipeline</h1>
        <p class="ef-sub">Each step builds on the last. Green = done, grey = up next.</p>
    </div>
    """, unsafe_allow_html=True)

    items = [
        ("fetch",    "📤", "Import Materials",    "Classroom, GitHub, or direct upload"),
        ("notes",    "📝", "Generate Notes",       "AI-written notes from your files"),
        ("plan",     "📅", "Study Plan",           "Prioritised topics and time estimates"),
        ("analyze",  "🔍", "Analyze Past Papers",  "Frequency and pattern extraction"),
        ("practice", "📋", "Practice Paper",       "Custom exam matching real format"),
        ("quiz",     "🎯", "Adaptive Quiz",        "MCQ weighted by plan and analysis"),
        ("score",    "📊", "Results",              "Detailed breakdown and insights"),
    ]

    st.markdown('<div class="ef-timeline">', unsafe_allow_html=True)
    for i, (key, icon, title, desc) in enumerate(items):
        done = step_done(key)
        dot_class = "ef-timeline-dot done" if done else "ef-timeline-dot"
        dot_content = "✓" if done else icon
        st.markdown(f"""
        <div class="ef-timeline-item" style="animation-delay:{i*0.07}s">
            <div class="{dot_class}">{dot_content}</div>
            <div class="ef-timeline-body">
                <h4>{title}</h4>
                <p>{desc}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def _render_home_features():
    back_to_menu("home_sub")
    st.markdown("""
    <div style="margin-bottom:var(--s4);">
        <div class="ef-eyebrow">What's inside</div>
        <h1 class="ef-heading">Key Features</h1>
        <p class="ef-sub">Everything you need to go from raw notes to exam-ready, powered by AI.</p>
    </div>
    """, unsafe_allow_html=True)

    features = [
        ("📤", "Smart Import",        "Pull lecture files from Google Classroom, browse GitHub repos, or drop in any PDF/PPTX/DOCX."),
        ("📝", "AI Notes",            "Chunked, structured notes generated fresh from your materials — not generic summaries."),
        ("📅", "Study Plan",          "Topics ranked by exam priority, with time estimates and key concepts to focus on."),
        ("🔍", "Paper Analysis",      "Frequency maps, question-type distributions, and recommended focus from past exams."),
        ("📋", "Practice Paper",      "A full exam paper in real format, weighted by your analysis and study plan."),
        ("🎯", "Adaptive Quiz",       "MCQ quiz weighted by topic importance. Submit once and get instant per-question feedback."),
    ]

    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="ef-feature-card" style="animation-delay:{i*0.09}s">
                <div class="ef-feature-icon">{icon}</div>
                <div class="ef-feature-title">{title}</div>
                <div class="ef-feature-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


def _render_home_quick_actions():
    back_to_menu("home_sub")
    st.markdown("""
    <div style="margin-bottom:var(--s4);">
        <div class="ef-eyebrow">Shortcuts</div>
        <h1 class="ef-heading">Quick Actions</h1>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📤 Add Materials", key="quick_start", use_container_width=True, type="primary"):
            nav("Materials")
    with col2:
        if st.button("📋 Practice Paper", key="quick_practice", use_container_width=True,
                     disabled=not step_done("analyze")):
            nav("Practice Paper")
    with col3:
        if st.button("📊 View Results", key="quick_progress", use_container_width=True,
                     disabled=not step_done("score")):
            nav("Results")


# ============================================================================
# MATERIALS PAGE
# ============================================================================

def render_materials_page():
    sub = st.session_state["materials_sub"]
    if sub is None:           _render_materials_menu()
    elif sub == "classroom":  _render_materials_classroom()
    elif sub == "github":     _render_materials_github()
    elif sub == "upload":     _render_materials_upload()
    elif sub == "process":    _render_materials_process()


def _render_materials_menu():
    st.markdown("""
    <div style="margin-bottom:var(--s4);">
        <div class="ef-eyebrow">Step 1</div>
        <h1 class="ef-heading">Study Materials</h1>
        <p class="ef-sub">Import from Classroom, GitHub, or upload directly. Mix sources freely.</p>
    </div>
    """, unsafe_allow_html=True)

    if step_done("fetch"):
        col_a, col_b = st.columns([5, 1])
        with col_a:
            st.markdown(f"""
            <div class="ef-glass" style="margin-bottom:var(--s3);">
                {badge("✓ Materials processed", "emerald")}
                <span style="margin-left:8px;font-size:var(--t-sm);color:var(--ink-50);">
                    Add more below or clear everything to restart.
                </span>
            </div>
            """, unsafe_allow_html=True)
        with col_b:
            if st.button("🗑 Clear all", key="clear_all_materials", use_container_width=True):
                clear_pipeline()
                st.rerun()

    lec_n = len(st.session_state["selected_lectures"])
    gh_n  = len(st.session_state["selected_github_files"])
    up_n  = len(st.session_state.get("uploaded_names", []))
    total = lec_n + gh_n + up_n

    # ── Three source cards ──
    col1, col2, col3 = st.columns(3)
    with col1:
        if menu_card("🎓", "Google Classroom",
                     "Connect OAuth and pull lecture PDFs, slides, and docs from your enrolled courses.",
                     badge(f"{lec_n} selected", "violet") if lec_n else ""):
            go_sub("materials_sub", "classroom")
    with col2:
        if menu_card("🐙", "GitHub Past Papers",
                     "Browse a configured repo and pick past exam paper files by folder.",
                     badge(f"{gh_n} selected", "violet") if gh_n else ""):
            go_sub("materials_sub", "github")
    with col3:
        if menu_card("📁", "Direct Upload",
                     "Drop in PDF, PPTX, DOCX, or TXT files from your device.",
                     badge(f"{up_n} ready", "cyan") if up_n else ""):
            go_sub("materials_sub", "upload")

    # ── Process summary strip below all three cards ──
    st.markdown("<div style='height:var(--s3)'></div>", unsafe_allow_html=True)
    s_html = badge(f"{total} ready to process", "emerald") if total else badge("Nothing selected yet", "amber")
    st.markdown(f"""
    <div class="ef-glass" style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px;">
        <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;">
            <div class="ef-eyebrow" style="margin:0;">Process</div>
            {metric(lec_n, "Classroom")}
            {metric(gh_n,  "GitHub")}
            {metric(up_n,  "Uploaded")}
            {metric(total, "Total", "good" if total else "warn")}
        </div>
        <div style="display:flex;align-items:center;gap:10px;">
            {s_html}
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:var(--s2)'></div>", unsafe_allow_html=True)

    col_proc, col_clr = st.columns([4, 1])
    with col_proc:
        if st.button(f"🚀 Process {total} file(s)" if total else "🚀 Process Files",
                     key="open_process_strip", use_container_width=True,
                     type="primary", disabled=(total == 0)):
            go_sub("materials_sub", "process")
    with col_clr:
        if st.button("↩ Clear selection", key="clear_sel_strip", use_container_width=True,
                     disabled=(total == 0)):
            st.session_state["selected_lectures"] = []
            st.session_state["selected_github_files"] = []
            st.session_state["uploaded_names"] = []
            st.session_state["github_folder_files"] = []
            st.session_state["github_folder_name"] = ""
            st.session_state["course_materials"] = []
            st.session_state["chosen_course_id"] = None
            st.rerun()


def _render_materials_classroom():
    back_to_menu("materials_sub")
    st.markdown("""
    <div style="margin-bottom:var(--s4);">
        <div class="ef-eyebrow">Materials → Classroom</div>
        <h1 class="ef-heading">Google Classroom</h1>
    </div>
    """, unsafe_allow_html=True)

    if not os.path.exists("credentials.json"):
        st.warning(
            "**One-time setup needed.**  \n"
            "1. Go to console.cloud.google.com  \n"
            "2. Create a project → enable **Google Classroom API** and **Google Drive API**  \n"
            "3. Create **OAuth 2.0 credentials** (Desktop app) → download the JSON  \n"
            "4. Rename it to `credentials.json` and place it in your project folder"
        )
        return

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Connect to Classroom", key="connect_classroom", type="primary", use_container_width=True):
            if os.path.exists("token.json"):
                os.remove("token.json")
            with st.spinner("Opening browser for Google sign-in…"):
                try:
                    from tools.classroom_tool import list_enrolled_courses
                    courses = list_enrolled_courses()
                    st.session_state["classroom_courses"] = courses
                    st.session_state["classroom_connected"] = True
                    st.session_state["chosen_course_id"] = None
                    st.session_state["course_materials"] = []
                    st.session_state["selected_lectures"] = []
                    st.rerun()
                except FileNotFoundError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Connection failed: {e}")
    with col2:
        if st.session_state["classroom_connected"]:
            n = len(st.session_state["classroom_courses"])
            st.success(f"Connected — {n} active course(s) found")

    if st.session_state["classroom_connected"] and st.session_state["classroom_courses"]:
        courses = st.session_state["classroom_courses"]
        st.markdown("**Step 1 — Choose a course:**")
        course_opts = ["— select a course —"] + [
            c["name"] + (f"  ({c['section']})" if c.get("section") else "")
            for c in courses
        ]
        chosen_label = st.selectbox("Your courses", course_opts, key="course_sel", label_visibility="collapsed")

        if chosen_label != "— select a course —":
            idx = course_opts.index(chosen_label) - 1
            chosen_course = courses[idx]

            if st.button("📋 Load lectures", key="load_lec_btn", type="primary"):
                with st.spinner("Fetching all materials from this course…"):
                    try:
                        from tools.classroom_tool import list_materials_in_course
                        mats = list_materials_in_course(chosen_course["id"])
                        st.session_state["course_materials"] = mats
                        st.session_state["chosen_course_id"] = chosen_course["id"]
                        st.session_state["chosen_course_name"] = chosen_course["name"]
                        st.session_state["selected_lectures"] = []
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not load materials: {e}")

            if (st.session_state["course_materials"]
                    and st.session_state["chosen_course_id"] == chosen_course["id"]):
                mats = st.session_state["course_materials"]
                st.markdown(f"**Step 2 — Select lectures from '{chosen_course['name']}':**")
                sel_all_lec = st.checkbox(f"Select all {len(mats)} file(s)", key="sel_all_lec")
                selected_lec = []
                for m in mats:
                    parent = m.get("parent_title", "")
                    lbl = m["title"] + (f"   —   {parent[:55]}" if parent else "")
                    if sel_all_lec or st.checkbox(lbl, key=f"lec_{m['id']}"):
                        selected_lec.append(m)
                st.session_state["selected_lectures"] = selected_lec
                if selected_lec:
                    st.success(f"{len(selected_lec)} lecture(s) selected")
            elif st.session_state["chosen_course_id"] and not st.session_state["course_materials"]:
                st.warning("No downloadable files found. Files must be PDF, PPTX, or DOCX.")


def _render_materials_github():
    back_to_menu("materials_sub")
    st.markdown("""
    <div style="margin-bottom:var(--s4);">
        <div class="ef-eyebrow">Materials → GitHub</div>
        <h1 class="ef-heading">GitHub Past Papers</h1>
    </div>
    """, unsafe_allow_html=True)

    repos = get_repos()
    if not repos:
        st.warning("No repos configured. Add `GITHUB_REPOS=username/repo1,username/repo2` to your `.env` file.")
        return

    col1, col2 = st.columns([2, 1])
    with col1:
        chosen_repo = st.selectbox("Repository", ["— select a repo —"] + repos, key="repo_sel", label_visibility="collapsed")
    with col2:
        if chosen_repo != "— select a repo —":
            if st.button("📂 Load folders", key="load_folders", type="primary", use_container_width=True):
                with st.spinner(f"Scanning {chosen_repo}…"):
                    try:
                        from tools.github_tool import list_folders_in_repo
                        folders, root_files = list_folders_in_repo(chosen_repo)
                        st.session_state["github_selected_repo"] = chosen_repo
                        st.session_state["github_folders"] = folders
                        st.session_state["github_root_files"] = root_files
                        st.session_state["github_folder_name"] = ""
                        st.session_state["github_folder_files"] = []
                        st.session_state["selected_github_files"] = []
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not load repo: {e}")

    if (st.session_state["github_selected_repo"] == chosen_repo
            and chosen_repo != "— select a repo —"
            and st.session_state["github_folders"]):
        folders = st.session_state["github_folders"]
        root_files = st.session_state["github_root_files"]

        st.markdown("**Step 1 — Choose a subject folder:**")
        folder_names = ["— select a folder —"] + [f["name"] for f in folders]
        chosen_folder_name = st.selectbox("Subject folder", folder_names, key="folder_sel", label_visibility="collapsed")

        if chosen_folder_name != "— select a folder —":
            folder_obj = next(f for f in folders if f["name"] == chosen_folder_name)

            if st.button("📋 Load files", key="load_ff", type="primary"):
                with st.spinner("Loading files in folder…"):
                    try:
                        from tools.github_tool import list_files_in_path
                        files = list_files_in_path(chosen_repo, folder_obj["path"])
                        st.session_state["github_folder_name"] = chosen_folder_name
                        st.session_state["github_folder_files"] = files
                        st.session_state["selected_github_files"] = []
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

            if (st.session_state["github_folder_name"] == chosen_folder_name
                    and st.session_state["github_folder_files"]):
                ffiles = st.session_state["github_folder_files"]
                st.markdown(f"**Step 2 — Select papers from '{chosen_folder_name}':**")
                sel_all_gh = st.checkbox(f"Select all {len(ffiles)} file(s)", key="sel_all_gh")
                sel_gh = []
                for fi in ffiles:
                    size = f"{fi.get('size_kb','?')} KB"
                    lbl = f"{fi['name']}   ({size})"
                    if sel_all_gh or st.checkbox(lbl, key=f"ghf_{fi['path']}"):
                        sel_gh.append(fi)
                st.session_state["selected_github_files"] = sel_gh
                if sel_gh:
                    st.success(f"{len(sel_gh)} file(s) selected")

        if root_files:
            st.markdown("**Root-level files (not in any folder):**")
            for fi in root_files:
                if st.checkbox(fi["name"], key=f"root_{fi['path']}"):
                    cur = st.session_state["selected_github_files"]
                    if fi not in cur:
                        st.session_state["selected_github_files"] = cur + [fi]


def _render_materials_upload():
    back_to_menu("materials_sub")
    st.markdown("""
    <div style="margin-bottom:var(--s4);">
        <div class="ef-eyebrow">Materials → Upload</div>
        <h1 class="ef-heading">Direct Upload</h1>
        <p class="ef-sub">No Classroom or GitHub? Drop in your files below.</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Upload files",
        type=['pdf', 'pptx', 'docx', 'txt'],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    if uploaded_files:
        os.makedirs("data/raw", exist_ok=True)
        saved = []
        for f in uploaded_files:
            path = os.path.join("data/raw", f.name)
            with open(path, "wb") as out:
                out.write(f.getbuffer())
            saved.append(f.name)
        st.session_state["uploaded_names"] = saved
        st.success(f"✓ {len(saved)} file(s) ready to process")


def _render_materials_process():
    back_to_menu("materials_sub")
    st.markdown("""
    <div style="margin-bottom:var(--s4);">
        <div class="ef-eyebrow">Materials → Process</div>
        <h1 class="ef-heading">Review & Process</h1>
    </div>
    """, unsafe_allow_html=True)

    lec_n = len(st.session_state["selected_lectures"])
    gh_n  = len(st.session_state["selected_github_files"])
    up_n  = len(st.session_state.get("uploaded_names", []))
    total = lec_n + gh_n + up_n

    col1, col2, col3, col4 = st.columns(4)
    with col1:  st.markdown(metric(lec_n, "Classroom Files"), unsafe_allow_html=True)
    with col2:  st.markdown(metric(gh_n,  "GitHub Files"), unsafe_allow_html=True)
    with col3:  st.markdown(metric(up_n,  "Uploaded"), unsafe_allow_html=True)
    with col4:  st.markdown(metric(total, "Total", "good" if total else "warn"), unsafe_allow_html=True)

    st.markdown("<div style='height:var(--s3)'></div>", unsafe_allow_html=True)

    if total == 0:
        st.markdown("""
        <div class="ef-empty">
            <span class="ef-empty-icon">📭</span>
            <h3>Nothing selected yet</h3>
            <p>Go back and choose files from Classroom, GitHub, or upload your own — then return here.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    col_p1, col_p2 = st.columns([3, 1])
    with col_p1:
        process_clicked = st.button(f"⚡ Process {total} file(s)", key="process_materials",
                                     type="primary", use_container_width=True)
    with col_p2:
        clear_sel = st.button("↩ Clear selection", key="clear_sel_btn", use_container_width=True)

    if clear_sel:
        st.session_state["selected_lectures"] = []
        st.session_state["selected_github_files"] = []
        st.session_state["uploaded_names"] = []
        st.session_state["github_folder_files"] = []
        st.session_state["github_folder_name"] = ""
        st.session_state["course_materials"] = []
        st.session_state["chosen_course_id"] = None
        st.rerun()

    if process_clicked:
        progress_box = st.empty()
        status_box   = st.empty()
        try:
            os.makedirs("data/raw", exist_ok=True)
            os.makedirs("data/chunks", exist_ok=True)
            all_paths = []
            total_planned = max(
                len(st.session_state["selected_lectures"])
                + len(st.session_state["selected_github_files"])
                + len(st.session_state.get("uploaded_names", [])), 1
            )

            sel_lec = st.session_state["selected_lectures"]
            if sel_lec:
                status_box.markdown('<div class="ef-proc-card"><h4>📥 Downloading lectures from Classroom…</h4></div>', unsafe_allow_html=True)
                from tools.classroom_tool import download_selected_materials
                paths = download_selected_materials(sel_lec, "data/raw", progress_callback=lambda m: None)
                all_paths.extend(paths)
                progress_box.progress(min(len(all_paths) / total_planned, 1.0))

            sel_gh = st.session_state["selected_github_files"]
            if sel_gh:
                status_box.markdown('<div class="ef-proc-card"><h4>📥 Downloading papers from GitHub…</h4></div>', unsafe_allow_html=True)
                from tools.github_tool import download_selected_files
                paths = download_selected_files(sel_gh, "data/raw", progress_callback=lambda m: None)
                all_paths.extend(paths)
                progress_box.progress(min(len(all_paths) / total_planned, 1.0))

            for name in st.session_state.get("uploaded_names", []):
                p = os.path.join("data/raw", name)
                if os.path.exists(p) and p not in all_paths:
                    all_paths.append(p)

            seen_p, unique_paths = set(), []
            for p in all_paths:
                if p not in seen_p: seen_p.add(p); unique_paths.append(p)
            all_paths = unique_paths

            if not all_paths:
                status_box.empty(); progress_box.empty()
                st.error("No files could be downloaded. Check your connections.")
            else:
                status_box.markdown('<div class="ef-proc-card"><h4>⚙️ Chunking your materials…</h4></div>', unsafe_allow_html=True)
                from tools.pdf_tool import process_pdf, process_text
                from tools.file_converter import convert_file
                chunk_files = []
                n = len(all_paths)
                for i, fp in enumerate(all_paths):
                    ext = os.path.splitext(fp)[1].lower()
                    fname = os.path.basename(fp).rsplit(".", 1)[0]
                    try:
                        if ext == ".pdf":
                            r = process_pdf(fp, "data/chunks")
                        elif ext in (".pptx", ".ppt", ".docx"):
                            txt = convert_file(fp)
                            r = process_text(txt, fname, "data/chunks") if txt else None
                        elif ext == ".txt":
                            with open(fp, "r", encoding="utf-8", errors="ignore") as fh:
                                txt = fh.read()
                            r = process_text(txt, fname, "data/chunks")
                        else:
                            r = None
                        if r: chunk_files.append(r)
                    except Exception:
                        pass
                    progress_box.progress((i + 1) / n)

                st.session_state["session_chunk_files"] = chunk_files
                status_box.empty(); progress_box.empty()
                if chunk_files:
                    st.success(f"✅ Done! {len(chunk_files)} file(s) processed.")
                    st.balloons()
                    time.sleep(1)
                    st.session_state["materials_sub"] = None
                    nav("Study & Plan")
                else:
                    st.error("Processing failed. Check that files are readable (not scanned images).")
        except Exception as e:
            status_box.empty(); progress_box.empty()
            st.error(f"Unexpected error: {e}")
            import traceback
            st.code(traceback.format_exc())


# ============================================================================
# STUDY & PLAN PAGE
# ============================================================================

def render_study_plan_page():
    if not step_done("fetch"):
        st.markdown("""
        <div class="ef-empty">
            <span class="ef-empty-icon">📂</span>
            <h3>No materials yet</h3>
            <p>Add and process your study materials first, then come back here to generate notes.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("← Add Materials", type="primary"):
            nav("Materials")
        return

    sub = st.session_state["study_sub"]
    if sub is None:         _render_study_menu()
    elif sub == "notes":    _render_study_notes()
    elif sub == "plan":     _render_study_plan()
    elif sub == "analyze":  _render_study_analyze()


def _render_study_menu():
    st.markdown("""
    <div style="margin-bottom:var(--s4);">
        <div class="ef-eyebrow">Step 2</div>
        <h1 class="ef-heading">Study & Plan</h1>
        <p class="ef-sub">Generate notes, build a study plan, and analyze past paper patterns.</p>
    </div>
    """, unsafe_allow_html=True)

    chunk_n = len([f for f in os.listdir("data/chunks") if f.endswith(".json")]) if os.path.exists("data/chunks") else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        s = badge("✓ Ready", "emerald") if step_done("notes") else badge(f"{chunk_n} chunks", "violet")
        if menu_card("📝", "Generate Notes",
                     "AI-written, chapter-organized notes from your processed materials.", s):
            go_sub("study_sub", "notes")
    with col2:
        s = badge("✓ Built", "emerald") if step_done("plan") else badge("Not built yet", "amber")
        if menu_card("📅", "Study Plan",
                     "Prioritised topic order, time estimates, and key concepts per topic.", s):
            go_sub("study_sub", "plan")
    with col3:
        s = badge("✓ Analyzed", "emerald") if step_done("analyze") else badge("Not analyzed yet", "amber")
        if menu_card("🔍", "Past Paper Analysis",
                     "Topic frequency maps and question-type distributions from past exams.", s):
            go_sub("study_sub", "analyze")


def _render_study_notes():
    back_to_menu("study_sub")
    st.markdown("""
    <div style="margin-bottom:var(--s4);">
        <div class="ef-eyebrow">Study → Notes</div>
        <h1 class="ef-heading">Generated Notes</h1>
    </div>
    """, unsafe_allow_html=True)

    chunk_n = len([f for f in os.listdir("data/chunks") if f.endswith(".json")]) if os.path.exists("data/chunks") else 0

    col1, col2 = st.columns([1, 2])
    with col1:
        label = "🔄 Regenerate Notes" if step_done("notes") else "⚡ Generate Notes"
        if not step_done("notes"):
            st.markdown(f'<p style="font-size:var(--t-sm);color:var(--ink-50);">{chunk_n} chunk file(s) ready</p>', unsafe_allow_html=True)
        if st.button(label, key="generate_notes", type="primary", use_container_width=True):
            with st.spinner("Generating comprehensive notes…"):
                try:
                    from agents.notes_agent import run_notes_agent
                    os.makedirs("data/output/notes", exist_ok=True)
                    notes = run_notes_agent(
                        chunks_dir="data/chunks",
                        notes_dir="data/output/notes",
                        progress_callback=lambda m: None,
                    )
                    if notes:
                        st.success(f"✓ {len(notes)} notes file(s) created!")
                        st.rerun()
                    else:
                        st.error("Notes generation failed. Check your Groq API key in .env")
                except Exception as e:
                    st.error(f"Error: {e}")

    with col2:
        if step_done("notes"):
            nfiles = [f for f in os.listdir("data/output/notes") if f.endswith(".md")]
            st.selectbox(
                "Select Chapter", nfiles,
                format_func=lambda x: x.replace("_notes.md", "").replace("_", " ").title(),
                key="note_sel",
            )

    if step_done("notes"):
        nfiles = [f for f in os.listdir("data/output/notes") if f.endswith(".md")]
        if nfiles:
            sel = st.session_state.get("note_sel", nfiles[0])
            note_path = os.path.join("data/output/notes", sel)
            if os.path.exists(note_path):
                st.markdown('<div class="ef-notes-viewer">', unsafe_allow_html=True)
                with open(note_path, "r", encoding="utf-8") as fh:
                    st.markdown(fh.read())
                st.markdown("</div>", unsafe_allow_html=True)


def _render_study_plan():
    back_to_menu("study_sub")
    st.markdown("""
    <div style="margin-bottom:var(--s4);">
        <div class="ef-eyebrow">Study → Plan</div>
        <h1 class="ef-heading">Study Plan</h1>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 3])
    with col1:
        label = "🔄 Rebuild Plan" if step_done("plan") else "⚡ Build Study Plan"
        if st.button(label, key="build_plan", type="primary", use_container_width=True):
            with st.spinner("Creating personalized study plan…"):
                try:
                    from agents.planner_agent import run_planner_agent
                    result = run_planner_agent(notes_dir="data/output/notes", output_path="data/output/plan.json")
                    if result:
                        st.success("Study plan created!")
                        st.rerun()
                    else:
                        st.error("Planning failed. Check your Groq API key.")
                except Exception as e:
                    st.error(f"Error: {e}")

    with col2:
        if step_done("plan"):
            with open("data/output/plan.json") as fh:
                plan = json.load(fh)
            topics = plan.get("topics", [])
            hi   = len([t for t in topics if t.get("priority") == "high"])
            md_p = len([t for t in topics if t.get("priority") == "medium"])

            cols = st.columns(4)
            with cols[0]: st.markdown(metric(len(topics), "Topics"), unsafe_allow_html=True)
            with cols[1]: st.markdown(metric(plan.get("total_study_time","—"), "Total Time"), unsafe_allow_html=True)
            with cols[2]: st.markdown(metric(hi, "High Priority", "warn"), unsafe_allow_html=True)
            with cols[3]: st.markdown(metric(md_p, "Medium Priority"), unsafe_allow_html=True)

    if step_done("plan"):
        with open("data/output/plan.json") as fh:
            plan = json.load(fh)
        topics = plan.get("topics", [])

        st.markdown('<div class="ef-eyebrow" style="margin:var(--s4) 0 var(--s2);">Topics by Priority</div>', unsafe_allow_html=True)

        for t in sorted(topics, key=lambda x: x.get("study_order", 99)):
            p = t.get("priority", "medium")
            badge_variant = {"high": "rose", "medium": "amber", "low": "emerald"}.get(p, "violet")
            kc = t.get("key_concepts", [])
            concepts = "".join(f'<span class="ef-concept-pill">{c}</span>' for c in kc)
            time_est = t.get("estimated_study_time", "")

            st.markdown(f"""
            <div class="ef-topic-row">
                <div>
                    <div class="ef-topic-name">{t.get('study_order','?')}. {t.get('name','?')}</div>
                    <div class="ef-topic-concepts">{concepts}</div>
                </div>
                <div style="text-align:right;display:flex;flex-direction:column;align-items:flex-end;gap:6px;">
                    {badge(p.upper(), badge_variant)}
                    <span style="font-size:var(--t-xs);color:var(--ink-50);font-family:var(--font-mono);">{time_est}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)


def _render_study_analyze():
    back_to_menu("study_sub")
    st.markdown("""
    <div style="margin-bottom:var(--s4);">
        <div class="ef-eyebrow">Study → Analysis</div>
        <h1 class="ef-heading">Past Paper Analysis</h1>
    </div>
    """, unsafe_allow_html=True)

    label = "🔄 Re-analyse" if step_done("analyze") else "⚡ Analyze Past Papers"
    if st.button(label, key="analyze_papers", type="primary"):
        with st.spinner("Analyzing past paper patterns…"):
            try:
                from agents.paper_analyzer_agent import run_paper_analyzer_agent
                r = run_paper_analyzer_agent(
                    chunks_dir="data/chunks",
                    output_path="data/output/paper_analysis.json"
                )
                if r:
                    st.success("✓ Analysis complete! You can now generate a Practice Paper.")
                    st.rerun()
                else:
                    st.error("Analysis failed.")
            except Exception as e:
                st.error(f"Error: {e}")

    if step_done("analyze"):
        with open("data/output/paper_analysis.json") as fh:
            analysis = json.load(fh)
        top_topics = analysis.get("top_topics", [])[:10]
        focus      = analysis.get("recommended_focus", [])
        hf_terms   = analysis.get("high_frequency_terms", [])[:10]
        qt_dist    = analysis.get("question_type_distribution", {})

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="ef-eyebrow" style="margin-bottom:var(--s2);">Topic Distribution</div>', unsafe_allow_html=True)
            if top_topics:
                import pandas as pd
                df = pd.DataFrame(top_topics)
                if "topic" in df.columns and "frequency" in df.columns:
                    st.bar_chart(df.set_index("topic")["frequency"])
        with col2:
            st.markdown('<div class="ef-eyebrow" style="margin-bottom:var(--s2);">Question Types</div>', unsafe_allow_html=True)
            if qt_dist:
                import pandas as pd
                qdf = pd.DataFrame(list(qt_dist.items()), columns=["type", "count"]).set_index("type")
                st.bar_chart(qdf)

        st.markdown('<div class="ef-eyebrow" style="margin:var(--s4) 0 var(--s2);">High Frequency Terms</div>', unsafe_allow_html=True)
        terms_html = " ".join(
            f'<span class="ef-badge ef-badge-violet" style="margin:2px;">{t["term"]} ×{t["count"]}</span>'
            for t in hf_terms
        )
        st.markdown(f'<div style="margin-bottom:var(--s4);">{terms_html}</div>', unsafe_allow_html=True)

        if focus:
            st.markdown('<div class="ef-eyebrow" style="margin-bottom:var(--s2);">Recommended Focus Areas</div>', unsafe_allow_html=True)
            for f_item in focus:
                st.markdown(f"""
                <div class="ef-glass" style="margin-bottom:var(--s1);padding:var(--s2) var(--s3);display:flex;align-items:center;gap:10px;">
                    <span style="color:var(--c-emerald);font-size:1.1rem;">✓</span>
                    <span style="font-size:var(--t-sm);color:var(--ink);">{f_item}</span>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height:var(--s3)'></div>", unsafe_allow_html=True)
        if st.button("➡ Generate Practice Paper", key="goto_practice", type="primary"):
            st.session_state["study_sub"] = None
            nav("Practice Paper")


# ============================================================================
# PRACTICE PAPER PAGE
# ============================================================================

def render_practice_paper_page():
    st.markdown("""
    <div style="margin-bottom:var(--s4);">
        <div class="ef-eyebrow">Step 4</div>
        <h1 class="ef-heading">Practice Paper</h1>
        <p class="ef-sub">A full exam paper generated to match real past-paper format and your topic priorities.</p>
    </div>
    """, unsafe_allow_html=True)

    if not step_done("analyze"):
        st.markdown("""
        <div class="ef-empty">
            <span class="ef-empty-icon">🔍</span>
            <h3>Past paper analysis needed first</h3>
            <p>Run the analysis in Study & Plan, then come back to generate a practice paper.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("← Study & Plan", type="primary"):
            nav("Study & Plan")
        return

    if not step_done("practice"):
        if st.button("🎯 Generate Practice Paper", key="generate_paper", use_container_width=True, type="primary"):
            progress_container = st.container()
            with progress_container:
                st.markdown('<div class="ef-glass"><span style="font-family:var(--font-display);font-weight:700;font-size:var(--t-lg);">Building your practice paper…</span></div>', unsafe_allow_html=True)
                progress = st.progress(0)
                status   = st.empty()
                try:
                    status.text("Matching topic coverage to past paper patterns…")
                    progress.progress(30)
                    from agents.practice_paper_agent import run_practice_paper_agent
                    os.makedirs("data/output/practice_paper", exist_ok=True)
                    result = run_practice_paper_agent(
                        chunks_dir="data/chunks",
                        notes_dir="data/output/notes",
                        analysis_path="data/output/paper_analysis.json",
                        plan_path="data/output/plan.json",
                        output_path="data/output/practice_paper/practice_paper.json",
                    )
                    progress.progress(100)
                    status.empty()
                    if result:
                        st.success("✅ Practice paper generated!")
                        st.rerun()
                    else:
                        st.error("Practice paper generation failed. Check your Groq API key.")
                except ImportError:
                    progress.empty(); status.empty()
                    st.error("`agents/practice_paper_agent.py` not found.")
                except Exception as e:
                    progress.empty(); status.empty()
                    st.error(f"Error generating practice paper: {e}")
                    import traceback
                    st.code(traceback.format_exc())

    if step_done("practice"):
        with open("data/output/practice_paper/practice_paper.json") as fh:
            paper = json.load(fh)

        sections        = paper.get("sections", [])
        total_questions = sum(len(s.get("questions", [])) for s in sections)

        cols = st.columns(4)
        with cols[0]: st.markdown(metric(total_questions, "Questions"), unsafe_allow_html=True)
        with cols[1]: st.markdown(metric(len(sections), "Sections"), unsafe_allow_html=True)
        with cols[2]: st.markdown(metric(paper.get("total_marks","—"), "Total Marks"), unsafe_allow_html=True)
        with cols[3]: st.markdown(metric(paper.get("duration","60 minutes"), "Duration"), unsafe_allow_html=True)

        st.markdown("<div style='height:var(--s3)'></div>", unsafe_allow_html=True)

        def build_paper_text(pp):
            lines = [pp.get("title","Practice Paper").upper(), ""]
            if pp.get("duration"): lines.append(f"Duration: {pp['duration']}")
            if pp.get("total_marks"): lines.append(f"Total Marks: {pp['total_marks']}")
            lines.append("")
            for section in pp.get("sections", []):
                lines += [section.get("name","Section").upper(), ""]
                for q in section.get("questions", []):
                    lines += [f"Q{q.get('number','')}. {q.get('text','')}",
                               f"      [{q.get('marks','')} marks]", "",
                               "      " + "_" * 60, ""]
                lines += ["─" * 70, ""]
            return "\n".join(lines)

        col_dl1, col_dl2, col_regen = st.columns([2, 2, 1])
        with col_dl1:
            st.download_button("📄 Download Text", build_paper_text(paper),
                               "practice_paper.txt", "text/plain", key="dl_txt", use_container_width=True)
        with col_dl2:
            st.download_button("📊 Download JSON", json.dumps(paper, indent=2),
                               "practice_paper.json", "application/json", key="dl_json", use_container_width=True)
        with col_regen:
            if st.button("🔄 Regenerate", key="regen_paper", use_container_width=True):
                os.remove("data/output/practice_paper/practice_paper.json")
                st.rerun()

        # ── Paper preview ──
        st.markdown('<div class="ef-paper-sheet">', unsafe_allow_html=True)
        st.markdown(f'<div class="ef-paper-title">{paper.get("title","Practice Examination Paper")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="ef-paper-meta">Time Allowed: {paper.get("duration","60 minutes")} &nbsp;|&nbsp; Maximum Marks: {paper.get("total_marks","—")}</div>', unsafe_allow_html=True)
        st.markdown('<hr class="ef-paper-divider">', unsafe_allow_html=True)

        # ── Instructions rendered as pure HTML — no Python loop, no char-by-char streaming ──
        instructions = paper.get("instructions", ["Attempt ALL questions.", "Write clearly and show all working."])
        #  ADD THIS SINGLE BLOCK INSTEAD:
        st.html(f"""
            <div style="margin-bottom: var(--s3);">
                <h3 style="margin-bottom: var(--s1); font-size: 1.2rem; font-weight: bold;">Instructions:</h3>
            <p class="ef-paper-instructions"><strong>1.</strong> {"Attempt ALL questions."}</p>
            <p class="ef-paper-instructions"><strong>2.</strong> {"Write clearly and show all working."}</p>
            </div>
            """)


        topic_palette = ["#7c3aed","#4f46e5","#0ea5e9","#06b6d4","#10b981","#f59e0b","#f43f5e"]
        topic_color_map = {}

        for section in sections:
            marks_str = f" ({section.get('marks','')} marks)" if section.get("marks") else ""
            st.markdown(f'<div class="ef-paper-section">{section.get("name","Section")}<span style="float:right;font-size:var(--t-sm);font-weight:400;">{marks_str}</span></div>', unsafe_allow_html=True)

            for q in section.get("questions", []):
                topic = q.get("topic","General")
                if topic not in topic_color_map:
                    topic_color_map[topic] = topic_palette[len(topic_color_map) % len(topic_palette)]
                tc = topic_color_map[topic]

                st.markdown(f"""
                <div class="ef-paper-question">
                    <p>
                        <strong>Question {q.get('number','')}.</strong>
                        <span class="ef-topic-chip" style="background:{tc};">{topic}</span>
                        <span style="float:right;font-size:var(--t-sm);color:var(--ink-50);">[{q.get('marks','')} marks]</span>
                    </p>
                    <p style="margin-top:8px;">{q.get('text','')}</p>
                    <div class="ef-paper-lines"></div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================================
# QUIZ PAGE
# ============================================================================

def render_quiz_page():
    if not step_done("notes"):
        st.markdown("""
        <div class="ef-empty">
            <span class="ef-empty-icon">📝</span>
            <h3>Notes needed first</h3>
            <p>Generate your study notes before creating a quiz. Head to Study & Plan.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("← Study & Plan", type="primary"):
            nav("Study & Plan")
        return

    sub = st.session_state["quiz_sub"]
    if sub is None:         _render_quiz_menu()
    elif sub == "generate": _render_quiz_generate()
    elif sub == "take":     _render_quiz_take()


def _render_quiz_menu():
    st.markdown("""
    <div style="margin-bottom:var(--s4);">
        <div class="ef-eyebrow">Step 5</div>
        <h1 class="ef-heading">Adaptive Quiz</h1>
        <p class="ef-sub">MCQ quiz weighted by your study plan priorities and past paper patterns.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        s = badge("✓ Quiz ready", "emerald") if step_done("quiz") else badge("Not generated yet", "amber")
        if menu_card("⚡", "Generate Quiz",
                     "Create a fresh set of MCQs from your notes, weighted by exam priority.", s):
            go_sub("quiz_sub", "generate")
    with col2:
        if not step_done("quiz"):
            st.markdown(f"""
            <div class="ef-menu-card" style="opacity:0.55;pointer-events:none;">
                <div class="mc-icon-wrap">📝</div>
                <div class="mc-title">Take Quiz</div>
                <div class="mc-desc">Answer questions and submit for instant feedback and scoring.</div>
                <div class="mc-status">{badge("Generate a quiz first", "amber")}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            s = badge("✓ Submitted", "emerald") if st.session_state["quiz_submitted"] else badge("Ready to attempt", "cyan")
            if menu_card("📝", "Take Quiz",
                         "Answer questions and submit for instant feedback and scoring.", s):
                go_sub("quiz_sub", "take")


def _render_quiz_generate():
    back_to_menu("quiz_sub")
    st.markdown("""
    <div style="margin-bottom:var(--s4);">
        <div class="ef-eyebrow">Quiz → Generate</div>
        <h1 class="ef-heading">Generate Quiz</h1>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="ef-glass" style="margin-bottom:var(--s4);">
        Your quiz is generated fresh from your <strong>current notes</strong> only — weighted by your
        study plan and past paper patterns. Each regeneration may produce different questions.
    </div>
    """, unsafe_allow_html=True)

    if st.button("⚡ Generate Quiz", key="generate_quiz", use_container_width=True, type="primary"):
        with st.spinner("Creating your personalised quiz…"):
            try:
                from agents.quiz_agent import run_quiz_agent
                os.makedirs("data/output/quiz", exist_ok=True)
                results = run_quiz_agent(
                    notes_dir="data/output/notes",
                    plan_path="data/output/plan.json",
                    analysis_path="data/output/paper_analysis.json",
                    quiz_dir="data/output/quiz",
                )
                if results:
                    st.success("Quiz generated! Good luck 🍀")
                    st.session_state["quiz_sub"] = None
                    go_sub("quiz_sub", "take")
                else:
                    st.error("Quiz generation failed. Check your Groq API key.")
            except Exception as e:
                st.error(f"Error: {e}")

    if step_done("quiz"):
        st.info("A quiz already exists. Go back and open **Take Quiz**, or regenerate above to get fresh questions.")


def _render_quiz_take():
    back_to_menu("quiz_sub")
    st.markdown("""
    <div style="margin-bottom:var(--s4);">
        <div class="ef-eyebrow">Quiz → Attempt</div>
        <h1 class="ef-heading">Take Quiz</h1>
    </div>
    """, unsafe_allow_html=True)

    if not step_done("quiz"):
        st.markdown("""
        <div class="ef-empty">
            <span class="ef-empty-icon">🎯</span>
            <h3>No quiz yet</h3>
            <p>Go back and generate a quiz first.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    if not st.session_state["quiz_submitted"]:
        with open("data/output/quiz/full_quiz.json") as fh:
            quiz_data = json.load(fh)
        questions = quiz_data.get("questions", [])

        if not questions:
            st.error("Quiz file appears empty. Regenerate below.")
            if st.button("🔄 Regenerate Quiz", key="regen_empty_quiz"):
                if os.path.exists("data/output/quiz"): shutil.rmtree("data/output/quiz")
                st.rerun()
            return

        col_a, col_b = st.columns([4, 1])
        with col_a:
            st.markdown(f"""
            <div class="ef-glass">
                <span style="font-family:var(--font-display);font-weight:700;font-size:var(--t-lg);color:var(--ink);">
                    {len(questions)} questions — answer all and submit when ready
                </span>
                <p style="font-size:var(--t-sm);color:var(--ink-50);margin-top:6px;margin-bottom:0;">
                    Each question is weighted by your study plan and past paper patterns
                </p>
            </div>
            """, unsafe_allow_html=True)
        with col_b:
            if st.button("🔄 New quiz", key="new_quiz_btn", use_container_width=True):
                for d in ["data/output/quiz","data/output/scores","data/output/feedback"]:
                    if os.path.exists(d): shutil.rmtree(d)
                st.session_state["quiz_submitted"] = False
                st.session_state["user_answers"] = {}
                with st.spinner("Generating fresh quiz…"):
                    try:
                        from agents.quiz_agent import run_quiz_agent
                        os.makedirs("data/output/quiz", exist_ok=True)
                        run_quiz_agent(
                            notes_dir="data/output/notes",
                            plan_path="data/output/plan.json",
                            analysis_path="data/output/paper_analysis.json",
                            quiz_dir="data/output/quiz",
                        )
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

        st.markdown("<div style='height:var(--s3)'></div>", unsafe_allow_html=True)

        with st.form("quiz_form", clear_on_submit=False):
            user_answers = {}
            for i, q in enumerate(questions, 1):
                diff = q.get("difficulty","medium")
                diff_variant = {"easy":"emerald","medium":"amber","hard":"rose"}.get(diff, "amber")
                topic = q.get("topic","")

                st.markdown(f"""
                <div class="ef-question-card">
                    <div class="ef-question-meta">
                        <span class="ef-question-num">Question {i} of {len(questions)}</span>
                        <div style="display:flex;gap:6px;align-items:center;">
                            {badge(diff, diff_variant)}
                            {badge(topic, "violet") if topic else ""}
                        </div>
                    </div>
                    <div class="ef-question-text">{q['question']}</div>
                </div>
                """, unsafe_allow_html=True)

                opts = q["options"]
                choice = st.radio(
                    f"q{i}", list(opts.keys()),
                    format_func=lambda x, o=opts: f"{x}.  {o[x]}",
                    horizontal=True, key=f"qa_{i}", label_visibility="collapsed",
                )
                user_answers[i] = choice
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

            submitted = st.form_submit_button("📝 Submit Quiz", use_container_width=True, type="primary")

        if submitted:
            with st.spinner("Evaluating answers and generating feedback…"):
                try:
                    from agents.evaluater_agent import run_scoring_agent
                    os.makedirs("data/output/scores", exist_ok=True)
                    os.makedirs("data/output/feedback", exist_ok=True)
                    result = run_scoring_agent(
                        quiz_dir="data/output/quiz",
                        scores_dir="data/output/scores",
                        feedback_dir="data/output/feedback",
                        user_answers=user_answers,
                    )
                    if result:
                        st.session_state["quiz_submitted"] = True
                        st.session_state["user_answers"] = user_answers
                        st.rerun()
                    else:
                        st.error("Scoring failed.")
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state["quiz_submitted"]:
        st.markdown("""
        <div class="ef-glass" style="text-align:center;padding:var(--s6) var(--s4);">
            <div style="font-size:3rem;margin-bottom:var(--s2);">✅</div>
            <h2 style="font-family:var(--font-display);font-size:var(--t-2xl);font-weight:700;letter-spacing:-0.03em;color:var(--ink);">Quiz Submitted!</h2>
            <p style="color:var(--ink-50);font-size:var(--t-base);">Your responses have been recorded and scored.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:var(--s3)'></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 View Results", key="view_results", use_container_width=True, type="primary"):
                st.session_state["quiz_sub"] = None
                nav("Results")
        with col2:
            if st.button("🔄 Generate New Quiz", key="new_quiz", use_container_width=True):
                for d in ["data/output/quiz","data/output/scores","data/output/feedback"]:
                    if os.path.exists(d): shutil.rmtree(d)
                st.session_state["quiz_submitted"] = False
                st.session_state["user_answers"] = {}
                st.session_state["quiz_sub"] = "generate"
                st.rerun()


# ============================================================================
# RESULTS PAGE
# ============================================================================

def render_results_page():
    if not step_done("score"):
        st.markdown("""
        <div class="ef-empty">
            <span class="ef-empty-icon">📊</span>
            <h3>No quiz attempt yet</h3>
            <p>Complete a quiz first. Head to Quiz, answer the questions, and submit — your results appear here.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("← Take Quiz", type="primary"):
            nav("Quiz")
        return

    sub = st.session_state["results_sub"]
    if sub is None:         _render_results_menu()
    elif sub == "overview": _render_results_overview()
    elif sub == "review":   _render_results_review()
    elif sub == "weak":     _render_results_weak_topics()


def _load_results_data():
    with open("data/output/scores/score_report.json") as fh:
        score_report = json.load(fh)
    with open("data/output/feedback/feedback.json") as fh:
        feedback_out = json.load(fh)
    return score_report, feedback_out


def _render_results_menu():
    st.markdown("""
    <div style="margin-bottom:var(--s4);">
        <div class="ef-eyebrow">Step 6</div>
        <h1 class="ef-heading">Results & Performance</h1>
        <p class="ef-sub">See how you did, review every question, and find what needs more revision.</p>
    </div>
    """, unsafe_allow_html=True)

    score_report, _ = _load_results_data()
    percentage  = score_report["percent"]
    grade       = score_report["grade"]
    weak_topics = score_report.get("weak_topics", [])

    score_variant = "emerald" if percentage >= 70 else ("amber" if percentage >= 50 else "rose")

    col1, col2, col3 = st.columns(3)
    with col1:
        if menu_card("🏆", "Score Overview",
                     "Your overall percentage, grade, and answer breakdown.",
                     badge(f"{percentage:.0f}%  ·  Grade {grade}", score_variant)):
            go_sub("results_sub", "overview")
    with col2:
        if menu_card("📝", "Question Review",
                     "See each question, your answer, the correct answer, and AI feedback."):
            go_sub("results_sub", "review")
    with col3:
        wt_html = badge(f"{len(set(weak_topics))} topic(s) to revisit", "rose") if weak_topics else badge("None — great work!", "emerald")
        if menu_card("📚", "Topics to Revisit",
                     "Topics where you answered questions incorrectly.", wt_html):
            go_sub("results_sub", "weak")


def _render_results_overview():
    back_to_menu("results_sub")
    st.markdown("""
    <div style="margin-bottom:var(--s4);">
        <div class="ef-eyebrow">Results → Overview</div>
        <h1 class="ef-heading">Score Overview</h1>
    </div>
    """, unsafe_allow_html=True)

    score_report, _ = _load_results_data()
    score      = score_report["score"]
    total      = score_report["total"]
    percentage = score_report["percent"]
    grade      = score_report["grade"]

    arc_pct = 565.48 * percentage / 100
    score_color = "#10b981" if percentage >= 70 else ("#f59e0b" if percentage >= 50 else "#f43f5e")
    grade_variant = "emerald" if percentage >= 70 else ("amber" if percentage >= 50 else "rose")

    st.markdown(f"""
    <div class="ef-score-ring">
        <svg width="200" height="200" style="display:block;margin:0 auto 24px;">
            <defs>
                <linearGradient id="arcGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%"   style="stop-color:#7c3aed"/>
                    <stop offset="50%"  style="stop-color:#4f46e5"/>
                    <stop offset="100%" style="stop-color:#06b6d4"/>
                </linearGradient>
            </defs>
            <circle cx="100" cy="100" r="88" fill="none" stroke="rgba(79,70,229,0.1)" stroke-width="12"/>
            <circle cx="100" cy="100" r="88" fill="none" stroke="url(#arcGrad)" stroke-width="12"
                    stroke-dasharray="{arc_pct} 553" stroke-linecap="round"
                    transform="rotate(-90 100 100)"
                    style="transition:stroke-dasharray 1.2s cubic-bezier(0.16,1,0.3,1)"/>
            <text x="100" y="93" text-anchor="middle"
                  font-family="Space Grotesk,sans-serif" font-size="38" font-weight="700"
                  fill="{score_color}">{percentage:.0f}%</text>
            <text x="100" y="118" text-anchor="middle"
                  font-family="Plus Jakarta Sans,sans-serif" font-size="15" font-weight="600"
                  fill="rgba(13,15,26,0.5)">Grade {grade}</text>
        </svg>
        <p style="text-align:center;font-family:var(--font-display);font-size:var(--t-lg);font-weight:700;color:var(--ink);margin:0;">
            {score} / {total} correct
        </p>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(4)
    with cols[0]: st.markdown(metric(total, "Total Questions"), unsafe_allow_html=True)
    with cols[1]: st.markdown(metric(score, "Correct", "good"), unsafe_allow_html=True)
    with cols[2]: st.markdown(metric(total-score, "Wrong", "warn"), unsafe_allow_html=True)
    with cols[3]: st.markdown(metric(f"{percentage:.0f}%", "Score", grade_variant), unsafe_allow_html=True)

    st.markdown("<div style='height:var(--s4)'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Retake Quiz", key="retake_quiz", use_container_width=True, type="primary"):
            st.session_state["quiz_submitted"] = False
            st.session_state["results_sub"] = None
            nav("Quiz")
    with col2:
        if st.button("📥 New Materials", key="new_materials", use_container_width=True):
            clear_pipeline()
            st.session_state["results_sub"] = None
            nav("Materials")


def _render_results_review():
    back_to_menu("results_sub")
    st.markdown("""
    <div style="margin-bottom:var(--s4);">
        <div class="ef-eyebrow">Results → Review</div>
        <h1 class="ef-heading">Question Review</h1>
    </div>
    """, unsafe_allow_html=True)

    score_report, feedback_out = _load_results_data()
    results   = score_report.get("results", [])
    feedbacks = feedback_out.get("per_question_feedback", [])

    for res, fb in zip(results, feedbacks):
        ok   = res["is_correct"]
        diff = res.get("difficulty","medium")
        diff_variant = {"easy":"emerald","medium":"amber","hard":"rose"}.get(diff,"amber")
        icon = "✅" if ok else "❌"
        border_color = "var(--c-emerald)" if ok else "var(--c-rose)"

        with st.expander(f"{icon} Q{res['q_number']} — {res['question'][:80]}…"):
            col_r1, col_r2 = st.columns(2)
            col_r1.markdown(f"**Your answer:** {res['user_answer']}")
            col_r2.markdown(f"**Correct answer:** {res['correct_answer']}")
            st.markdown(f"""
            <div style="border-left:4px solid {border_color};padding:10px 16px;background:rgba(79,70,229,0.03);border-radius:0 var(--r-md) var(--r-md) 0;margin-top:10px;">
                <div style="margin-bottom:8px;">{badge(diff, diff_variant)}</div>
                <p style="font-size:var(--t-sm);color:var(--ink);margin:0;">{fb['feedback']}</p>
            </div>
            """, unsafe_allow_html=True)
            if res.get("topic"):
                st.caption(f"Topic: {res['topic']}")


def _render_results_weak_topics():
    back_to_menu("results_sub")
    st.markdown("""
    <div style="margin-bottom:var(--s4);">
        <div class="ef-eyebrow">Results → Weak Topics</div>
        <h1 class="ef-heading">Topics to Revisit</h1>
    </div>
    """, unsafe_allow_html=True)

    score_report, _ = _load_results_data()
    weak_topics = score_report.get("weak_topics", [])

    if not weak_topics:
        st.markdown("""
        <div class="ef-empty">
            <span class="ef-empty-icon">🎉</span>
            <h3>Nothing to revisit!</h3>
            <p>You didn't miss any questions tied to a specific topic. Solid performance.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown('<p style="font-size:var(--t-sm);color:var(--ink-50);margin-bottom:var(--s3);">Focus your revision on these areas before the exam.</p>', unsafe_allow_html=True)

    unique_weak = list(set(weak_topics))
    for t in unique_weak:
        st.markdown(f"""
        <div class="ef-glass" style="margin-bottom:var(--s2);display:flex;align-items:center;justify-content:space-between;">
            <span style="font-family:var(--font-display);font-weight:700;font-size:var(--t-base);color:var(--ink);">⚠ {t}</span>
            {badge("Needs revision", "rose")}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:var(--s4)'></div>", unsafe_allow_html=True)
    if st.button("📝 Review Notes for These Topics", key="back_to_notes", type="primary"):
        st.session_state["results_sub"] = None
        st.session_state["study_sub"] = "notes"
        nav("Study & Plan")


# ============================================================================
# MAIN
# ============================================================================

def main():
    init_session_state()
    inject_custom_css()

    render_navbar()
    st.markdown('<div class="ef-page">', unsafe_allow_html=True)

    render_tab_navigation()

    page = st.session_state["current_page"]
    if page == "Home":             render_home_page()
    elif page == "Materials":      render_materials_page()
    elif page == "Study & Plan":   render_study_plan_page()
    elif page == "Practice Paper": render_practice_paper_page()
    elif page == "Quiz":           render_quiz_page()
    elif page == "Results":        render_results_page()

    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
