import os, re, json, time, hashlib, sqlite3, smtplib, ssl, csv, io, socket, ipaddress, html, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.parse import urlparse, urljoin, urldefrag, urlunparse, parse_qsl, urlencode
from email.message import EmailMessage

import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup

APP_NAME = "Organic Growth Studio"
DB_PATH = os.getenv("OGS_DB_PATH", "organic_growth_studio.db")
UA = "OrganicGrowthStudioAudit/4.2 (+authorized-site-audit)"
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
MAX_BODY_BYTES = 2_000_000
TIMEOUT = 15
MAX_CRAWL_PAGES = 50  # Internal safety limit; not exposed as a user setting.
CRAWL_DELAY_SECONDS = 0.5
MAX_SITEMAPS = 10
MAX_SITEMAP_URLS = 500

st.set_page_config(page_title=APP_NAME, page_icon="🌱", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
:root{--ogs-ink:#172033;--ogs-muted:#667085;--ogs-line:#e6eaf2;--ogs-bg:#f5f7fb;--ogs-blue:#4f46e5;--ogs-nav:#111827}
.stApp{background:#f5f7fb;color:#172033}
[data-testid="stHeader"]{background:rgba(245,247,251,.92)}
.block-container{padding-top:1.2rem;padding-bottom:2.5rem;max-width:1500px}
[data-testid="stSidebar"]{background:#111827;border-right:1px solid #27334a}
[data-testid="stSidebar"] *{color:#d6dbea}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2{font-size:17px;color:#fff;letter-spacing:-.3px}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"]{color:#94a3b8}
[data-testid="stSidebar"] [data-testid="stRadio"] label{border-radius:9px;padding:7px 9px;margin:2px 0;color:#aebbd0}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover{background:#27334a;color:#fff}
[data-testid="stSidebar"] [data-testid="stRadio"] [aria-checked="true"]+div{color:#fff}
[data-testid="stSidebar"] [data-testid="stRadio"] input{accent-color:#818cf8}
[data-testid="stSidebar"] button,[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]{border:1px solid #344054!important;background:#1f2937!important;color:#f8fafc!important}
[data-testid="stSidebar"] hr{border-color:#2d3748}
[data-testid="stMetric"]{background:#fff;border:1px solid #e6eaf2;border-radius:14px;padding:16px 18px;box-shadow:0 2px 4px #10182804}
[data-testid="stMetricLabel"]{color:#667085;font-size:12px}
[data-testid="stMetricValue"]{color:#172033;font-weight:780}
[data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border:1px solid #e6eaf2;border-radius:15px;box-shadow:0 2px 4px #10182804}
.stButton>button,[data-testid="stDownloadButton"] button,[data-testid="stFormSubmitButton"] button,[data-testid="stBaseButton-secondary"],[data-testid="stBaseButton-primary"]{border-radius:10px!important;font-weight:700!important;min-height:42px!important;transition:all .15s ease!important;box-shadow:0 1px 2px rgba(16,24,40,.05)!important}
.stButton>button:not([kind="primary"]),[data-testid="stDownloadButton"] button,[data-testid="stBaseButton-secondary"]{background:#fff!important;color:#344054!important;border:1px solid #d0d5dd!important}
.stButton>button[kind="primary"],[data-testid="stBaseButton-primary"],[data-testid="stFormSubmitButton"] button{background:linear-gradient(135deg,#5548e8,#4338ca)!important;color:#fff!important;border:1px solid #4f46e5!important}
.stButton>button:hover,[data-testid="stBaseButton-secondary"]:hover{border-color:#8b83f6!important;color:#4338ca!important;background:#f7f7ff!important;transform:translateY(-1px)}
.stButton>button[kind="primary"]:hover,[data-testid="stBaseButton-primary"]:hover,[data-testid="stFormSubmitButton"] button:hover{background:#3730a3!important;color:#fff!important;transform:translateY(-1px);box-shadow:0 5px 12px rgba(79,70,229,.18)!important}
[data-testid="stTextInput"] label,[data-testid="stTextArea"] label,[data-testid="stSelectbox"] label,[data-testid="stSlider"] label,[data-testid="stRadio"] label,[data-testid="stCheckbox"] label{color:#344054!important;font-weight:600}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,[data-testid="stSelectbox"] div[data-baseweb="select"]{background:#fff!important;color:#172033!important;border-radius:10px}
[data-testid="stForm"]{background:#fff;border:1px solid #e6eaf2;border-radius:16px;padding:18px}
[data-testid="stAlert"]{border-radius:12px}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,[data-testid="stSelectbox"] div[data-baseweb="select"]{border-radius:9px}
/* Authentication controls: explicitly neutralise dark BaseWeb/OS widget surfaces. */
[data-testid="stTextInput"]>div,[data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stTextInput"] [data-baseweb="base-input"],
[data-testid="stTextInput"] [data-baseweb="input"]>div,
[data-testid="stTextInput"] div:has(>input),
[data-testid="stForm"] [data-testid="stTextInput"]>div,
[data-testid="stForm"] [data-testid="stTextInput"] [data-baseweb="input"]{
  background:#fff!important;background-color:#fff!important;color:#172033!important;
  border:1px solid #d8deeb!important;box-shadow:none!important;border-radius:11px!important;
}
[data-testid="stTextInput"] input,[data-testid="stForm"] input,
[data-testid="stTextInput"] input[type="password"],
[data-testid="stTextInput"] input[type="email"]{
  background:#fff!important;background-color:#fff!important;color:#172033!important;
  -webkit-text-fill-color:#172033!important;caret-color:#5548e8!important;
  border:0!important;outline:none!important;box-shadow:none!important;border-radius:10px!important;
}
[data-testid="stTextInput"] input::placeholder,[data-testid="stForm"] input::placeholder{
  color:#98a2b3!important;-webkit-text-fill-color:#98a2b3!important;opacity:1!important;
}
[data-testid="stTextInput"] [data-baseweb="input"]:focus-within,
[data-testid="stForm"] [data-baseweb="input"]:focus-within{
  border-color:#8a80f7!important;box-shadow:0 0 0 3px rgba(109,93,252,.12)!important;
}
[data-testid="stTextInput"] button,[data-testid="stForm"] [data-baseweb="input"] button{
  background:#fff!important;color:#667085!important;border:0!important;box-shadow:none!important;
}
[data-testid="stTabs"] [data-baseweb="tab-list"]{background:transparent!important}
[data-testid="stTabs"] button[role="tab"]{background:transparent!important;color:#59657d!important;opacity:1!important}
[data-testid="stTabs"] button[role="tab"] p{color:inherit!important}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"]{background:#f1efff!important;color:#4f46e5!important}
[data-testid="stFormSubmitButton"] button{min-height:48px!important;border-radius:12px!important;font-size:14px!important;letter-spacing:.1px!important}
[data-testid="stForm"]{background:#fff!important;color:#172033!important}
[data-testid="stDataFrame"]{border:1px solid #e6eaf2;border-radius:12px;overflow:hidden}
[data-testid="stTabs"] button{font-weight:650}
.ogs-eyebrow{font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:1.4px;color:#4f46e5;margin-bottom:5px}
.ogs-heading{font-size:29px;font-weight:780;letter-spacing:-.7px;line-height:1.2;color:#172033;margin:4px 0 8px}
.ogs-sub{color:#667085;font-size:13px;line-height:1.6;margin:0 0 18px}
.ogs-hero{background:linear-gradient(125deg,#eef2ff 0%,#fff 58%,#e8fbf5 100%);border:1px solid #dfe5fb;border-radius:20px;padding:28px 30px;margin:0 0 20px;box-shadow:0 8px 28px rgba(43,54,110,.04)}
.ogs-auth{max-width:1040px;margin:4vh auto 0;padding:36px 40px;background:linear-gradient(125deg,#eef2ff 0%,#fff 58%,#e8fbf5 100%);border:1px solid #dfe5fb;border-radius:24px;box-shadow:0 14px 45px rgba(43,54,110,.07)}
.ogs-auth h1{font-size:36px;letter-spacing:-1px;margin-bottom:6px}.ogs-auth p{color:#667085}.ogs-empty{background:#fff;border:1px solid #e6eaf2;border-radius:18px;padding:30px;text-align:center}.ogs-section{display:flex;justify-content:space-between;align-items:center;gap:12px;margin:26px 0 12px}.ogs-section h2{margin:0;font-size:21px}.ogs-step{background:#fff;border:1px solid #e6eaf2;border-radius:14px;padding:16px 18px;margin-bottom:10px}
.ogs-hero h2{font-size:23px;font-weight:780;letter-spacing:-.6px;color:#172033;margin:5px 0 8px}
.ogs-hero p{font-size:13px;color:#667085;line-height:1.6;margin:0}
.ogs-card-title{font-size:15px;font-weight:750;color:#172033;margin:0 0 5px}
.ogs-muted{font-size:12px;color:#667085}
.ogs-notice{background:#eff6ff;border:1px solid #dbeafe;color:#1e40af;padding:12px 14px;border-radius:10px;font-size:12px;line-height:1.5;margin:12px 0}
.ogs-chip{display:inline-block;border-radius:999px;padding:4px 8px;background:#e9f8f1;color:#08764d;font-size:10px;font-weight:750}
h1,h2,h3{color:#172033}

/* Public landing and authentication */
[data-testid="stMainBlockContainer"]{max-width:1420px}
.ogs-public-wrap{padding:12px 0 34px}
.ogs-public-nav{display:flex;align-items:center;justify-content:space-between;padding:8px 4px 22px;margin-bottom:16px;border-bottom:1px solid #e7eaf3}
.ogs-brand{display:flex;align-items:center;gap:10px;font-weight:850;letter-spacing:-.55px;color:#151b2e;font-size:17px}
.ogs-brand-mark{display:inline-flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:12px;background:linear-gradient(140deg,#6d5dfc,#8e7cff);color:#fff;font-size:18px;box-shadow:0 5px 14px #6d5dfc30}
.ogs-nav-note{font-size:12px;color:#667085}
.ogs-public-hero{position:relative;overflow:hidden;border:1px solid #e0e5f5;border-radius:28px;background:radial-gradient(circle at 85% 10%,#dffaf2 0,transparent 29%),radial-gradient(circle at 10% 0%,#e7eaff 0,transparent 37%),linear-gradient(135deg,#fbfcff 0%,#fff 58%,#f7fffc 100%);padding:38px 36px 34px;box-shadow:0 18px 55px rgba(35,45,90,.06)}
.ogs-public-hero h1{font-size:clamp(34px,3.6vw,54px);line-height:1.04;letter-spacing:-2.2px;font-weight:850;color:#171d31;margin:12px 0 18px;max-width:610px}
.ogs-public-hero p{font-size:15px;line-height:1.75;color:#59657d;max-width:570px}
.ogs-pill{display:inline-flex;align-items:center;gap:8px;background:#fff;border:1px solid #e4e7f3;color:#5146d8;border-radius:999px;padding:7px 11px;font-size:10px;font-weight:850;letter-spacing:1.15px;text-transform:uppercase}
.ogs-feature-row{display:flex;flex-wrap:wrap;gap:9px;margin:22px 0 24px}
.ogs-feature{background:#fff;border:1px solid #e5e8f2;border-radius:999px;padding:8px 11px;font-size:11px;font-weight:700;color:#4b556b}
.ogs-preview-shell{border:1px solid #dce2f0;border-radius:20px;background:#fff;padding:13px;box-shadow:0 18px 40px rgba(28,37,72,.12);transform:rotate(.4deg)}
.ogs-preview-top{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #edf0f6;padding:5px 4px 12px;font-size:10px;font-weight:800;color:#26304a}
.ogs-live-dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:#22c58b;margin-right:6px}
.ogs-preview-body{display:grid;grid-template-columns:1.1fr .9fr;gap:10px;padding:13px 3px 3px}
.ogs-mini-label{font-size:9px;color:#8790a3;margin-bottom:7px}
.ogs-mini-score{font-size:30px;letter-spacing:-1.4px;font-weight:850;color:#18213a}
.ogs-mini-bar{height:6px;background:#edf0f8;border-radius:8px;overflow:hidden;margin:8px 0 11px}.ogs-mini-bar span{display:block;width:84%;height:100%;background:linear-gradient(90deg,#6d5dfc,#4bd6b0);border-radius:8px}
.ogs-mini-item{display:flex;gap:7px;align-items:center;padding:8px 7px;border:1px solid #edf0f6;border-radius:9px;margin-top:6px;font-size:9px;color:#34405a}
.ogs-mini-icon{display:inline-flex;width:21px;height:21px;align-items:center;justify-content:center;border-radius:7px;background:#f0edff;color:#6557ee;font-size:11px}
.ogs-mini-stat{background:#f8f9fd;border:1px solid #edf0f6;border-radius:10px;padding:10px;margin-top:7px}.ogs-mini-stat b{display:block;font-size:17px;color:#18213a}.ogs-mini-stat span{font-size:9px;color:#7a8498}
.ogs-public-heading{font-size:22px;letter-spacing:-.7px;font-weight:850;color:#171d31;margin:24px 0 4px}
.ogs-public-sub{font-size:12px;line-height:1.6;color:#69758c;margin-bottom:17px}
.ogs-auth-card{background:#fff;border:1px solid #e4e8f2;border-radius:22px;padding:22px 22px 18px;box-shadow:0 12px 35px rgba(35,45,90,.055);margin-top:0}
.ogs-auth-card h3{font-size:20px;margin:0 0 5px;letter-spacing:-.6px;color:#172033}
.ogs-auth-card p{font-size:12px;color:#6c7890;margin:0 0 15px;line-height:1.6}
[data-testid="stTabs"] [data-baseweb="tab-list"]{gap:8px;border-bottom:1px solid #eceef5}
[data-testid="stTabs"] button[role="tab"]{border-radius:10px 10px 0 0;padding:10px 14px;color:#657087!important;font-weight:750!important}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"]{color:#5548e8!important;border-bottom:3px solid #6d5dfc!important;background:#f7f6ff!important}
.ogs-trustline{display:flex;justify-content:center;gap:16px;flex-wrap:wrap;margin-top:18px;font-size:10px;color:#7c879b}
.ogs-trustline span:before{content:'✓';color:#14a879;font-weight:900;margin-right:5px}
.ogs-footer-note{text-align:center;font-size:10px;color:#8790a3;margin-top:22px}
@media(max-width:900px){.ogs-public-hero{padding:27px 22px}.ogs-public-hero h1{font-size:36px}.ogs-preview-shell{margin-top:16px}.ogs-public-nav{padding-bottom:14px}}
@media(max-width:800px){.block-container{padding-left:1rem;padding-right:1rem}.ogs-heading{font-size:25px}.ogs-public-hero h1{font-size:33px;letter-spacing:-1.2px}.ogs-preview-body{grid-template-columns:1fr 1fr}}

/* Final input normalization: target BaseWeb's outer shell, inner wrapper, autofill and password-toggle states. */
[data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stForm"] [data-baseweb="input"] {
  background: #fff !important;
  background-color: #fff !important;
  color: #18352c !important;
  border: 1px solid #d6dfd7 !important;
  border-radius: 12px !important;
  box-shadow: none !important;
  outline: none !important;
}
[data-testid="stTextInput"] [data-baseweb="input"] [data-baseweb="base-input"],
[data-testid="stTextInput"] [data-baseweb="input"] > div,
[data-testid="stForm"] [data-baseweb="input"] [data-baseweb="base-input"],
[data-testid="stForm"] [data-baseweb="input"] > div {
  background: transparent !important;
  background-color: transparent !important;
  color: #18352c !important;
  border: 0 !important;
  box-shadow: none !important;
}
[data-testid="stTextInput"] [data-baseweb="input"]:focus-within,
[data-testid="stTextInput"] [data-baseweb="base-input"]:focus-within,
[data-testid="stForm"] [data-baseweb="input"]:focus-within,
[data-testid="stForm"] [data-baseweb="base-input"]:focus-within {
  background: #fff !important;
  border: 1px solid #5f8b70 !important;
  box-shadow: 0 0 0 3px rgba(95,139,112,.16) !important;
  outline: none !important;
}
[data-testid="stTextInput"] input,
[data-testid="stForm"] input,
[data-testid="stTextInput"] input:-webkit-autofill,
[data-testid="stForm"] input:-webkit-autofill,
[data-testid="stTextInput"] input:-webkit-autofill:hover,
[data-testid="stTextInput"] input:-webkit-autofill:focus,
[data-testid="stForm"] input:-webkit-autofill:hover,
[data-testid="stForm"] input:-webkit-autofill:focus {
  background: #fff !important;
  background-color: #fff !important;
  color: #18352c !important;
  -webkit-text-fill-color: #18352c !important;
  caret-color: #315d47 !important;
  border: 0 !important;
  outline: 0 !important;
  box-shadow: 0 0 0 1000px #fff inset !important;
  border-radius: 10px !important;
  transition: background-color 99999s ease-out 0s !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stForm"] input::placeholder {
  color: #87958b !important;
  -webkit-text-fill-color: #87958b !important;
  opacity: 1 !important;
}
[data-testid="stTextInput"] [data-baseweb="input"] button,
[data-testid="stForm"] [data-baseweb="input"] button,
[data-testid="stTextInput"] [data-baseweb="base-input"] button,
[data-testid="stForm"] [data-baseweb="base-input"] button {
  background: #fff !important;
  background-color: #fff !important;
  color: #55705f !important;
  border: 0 !important;
  outline: 0 !important;
  box-shadow: none !important;
}
[data-testid="stTextInput"] [data-baseweb="input"] button:hover,
[data-testid="stForm"] [data-baseweb="input"] button:hover,
[data-testid="stTextInput"] [data-baseweb="base-input"] button:hover,
[data-testid="stForm"] [data-baseweb="base-input"] button:hover {
  background: #f3f7f3 !important;
  color: #244b36 !important;
}

/* Organic Growth Studio: distinct botanical diagnostic identity */
:root{--ogs-ink:#182d25;--ogs-muted:#65776d;--ogs-line:#dce6db;--ogs-bg:#f7f7f0;--ogs-blue:#315d47;--ogs-nav:#183b30}
.stApp{background:#f7f7f0;color:#182d25}
[data-testid="stHeader"]{background:rgba(247,247,240,.95)}
[data-testid="stSidebar"]{background:#173b30;border-right:1px solid #254c3d}
[data-testid="stSidebar"] *{color:#f1f5e9}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"]{color:#b5cbb9}
[data-testid="stSidebar"] button,[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]{background:#234b3c!important;border-color:#456b59!important;color:#f5f8ef!important}
[data-testid="stMetric"]{border-color:#dce6db;box-shadow:0 3px 12px rgba(30,63,46,.04)}
.stButton>button[kind="primary"],[data-testid="stBaseButton-primary"],[data-testid="stFormSubmitButton"] button{background:#d8f36a!important;color:#173b30!important;border:1px solid #c0df4f!important}
.stButton>button[kind="primary"]:hover,[data-testid="stBaseButton-primary"]:hover,[data-testid="stFormSubmitButton"] button:hover{background:#c9e956!important;color:#173b30!important;box-shadow:0 5px 14px rgba(49,93,71,.16)!important}
.stButton>button:not([kind="primary"]),[data-testid="stDownloadButton"] button,[data-testid="stBaseButton-secondary"]{background:#fff!important;color:#244b36!important;border:1px solid #cbdacb!important}
.stButton>button:hover,[data-testid="stBaseButton-secondary"]:hover{border-color:#779a7c!important;color:#244b36!important;background:#f1f7ed!important}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,[data-testid="stSelectbox"] div[data-baseweb="select"]{background:#fff!important;color:#18352c!important}
.ogs-eyebrow{color:#315d47}.ogs-heading{color:#182d25}.ogs-sub{color:#65776d}
.ogs-hero{background:linear-gradient(125deg,#f0f6e9 0%,#fff 60%,#eef7f0 100%);border-color:#dce7d9}
.ogs-public-hero{background:radial-gradient(circle at 85% 10%,#e5f5ce 0,transparent 29%),radial-gradient(circle at 10% 0%,#e7f0e6 0,transparent 37%),linear-gradient(135deg,#fbfcf7 0%,#fff 58%,#f7fff5 100%);border-color:#dce7d9}
.ogs-brand-mark{background:#315d47;color:#d8f36a;box-shadow:0 5px 14px #315d4720}
.ogs-pill{color:#315d47;border-color:#dce7d9;background:#f8fbf5}
.ogs-auth-card{border-color:#dce7d9}
[data-testid="stTextInput"] [data-baseweb="input"],[data-testid="stForm"] [data-baseweb="input"]{background:#fff!important;background-color:#fff!important;border:1px solid #cad9cb!important;border-radius:12px!important}
[data-testid="stTextInput"] input,[data-testid="stForm"] input,[data-testid="stTextInput"] input:-webkit-autofill,[data-testid="stForm"] input:-webkit-autofill{background:#fff!important;background-color:#fff!important;color:#18352c!important;-webkit-text-fill-color:#18352c!important;box-shadow:0 0 0 1000px #fff inset!important}
</style>
""", unsafe_allow_html=True)

# ---------- Storage ----------
def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(
          id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL,
          created_at TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'owner'
        );
        CREATE TABLE IF NOT EXISTS projects(
          id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, name TEXT NOT NULL, domain TEXT NOT NULL,
          business_type TEXT DEFAULT '', target_customer TEXT DEFAULT '', primary_offer TEXT DEFAULT '',
          competitors TEXT DEFAULT '[]', created_at TEXT NOT NULL, UNIQUE(user_id,domain),
          FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS audits(
          id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL, created_at TEXT NOT NULL,
          score INTEGER, pages INTEGER, findings_json TEXT NOT NULL, pages_json TEXT NOT NULL,
          FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS tasks(
          id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL, title TEXT NOT NULL, priority TEXT,
          category TEXT, url TEXT, evidence TEXT, recommendation TEXT, status TEXT DEFAULT 'Open',
          due_date TEXT DEFAULT '', created_at TEXT NOT NULL,
          FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS gsc_rows(
          id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL, imported_at TEXT NOT NULL,
          period TEXT DEFAULT '', query TEXT DEFAULT '', page TEXT DEFAULT '', clicks REAL DEFAULT 0,
          impressions REAL DEFAULT 0, ctr REAL DEFAULT 0, position REAL DEFAULT 0,
          FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS visibility_runs(
          id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL, tested_at TEXT NOT NULL,
          platform TEXT, prompt TEXT NOT NULL, brand_mentioned INTEGER DEFAULT 0,
          cited_url TEXT DEFAULT '', competitors TEXT DEFAULT '', sentiment TEXT DEFAULT 'Unknown',
          notes TEXT DEFAULT '', FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS ai_reports(
          id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL, created_at TEXT NOT NULL,
          report_type TEXT, input_hash TEXT, content TEXT NOT NULL,
          FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS subscriptions(
          id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, plan TEXT NOT NULL DEFAULT 'Free',
          status TEXT NOT NULL DEFAULT 'local-demo', provider_customer_id TEXT DEFAULT '',
          provider_subscription_id TEXT DEFAULT '', updated_at TEXT NOT NULL,
          FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS diagnostic_runs(
          id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL, created_at TEXT NOT NULL,
          scope_mode TEXT NOT NULL, scope_url TEXT NOT NULL, seo_score INTEGER NOT NULL,
          ai_score INTEGER NOT NULL, pages_count INTEGER NOT NULL,
          seo_findings_json TEXT NOT NULL, ai_findings_json TEXT NOT NULL,
          pages_json TEXT NOT NULL, crawl_notes_json TEXT NOT NULL,
          FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_diagnostics_project ON diagnostic_runs(project_id,created_at);
        CREATE INDEX IF NOT EXISTS idx_audits_project ON audits(project_id,created_at);
        CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id,status);
        CREATE INDEX IF NOT EXISTS idx_visibility_project ON visibility_runs(project_id,tested_at);
        """)
init_db()

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def hash_password(password, salt=None):
    import hashlib, secrets
    salt = salt or secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 250000)
    return salt + "$" + dk.hex()

def verify_password(password, stored):
    try:
        salt, expected = stored.split("$", 1)
        return hash_password(password, salt).split("$", 1)[1] == expected
    except Exception:
        return False

def current_user():
    return st.session_state.get("user")

def query(sql, params=()):
    with db() as c:
        return c.execute(sql, params).fetchall()

def execute(sql, params=()):
    with db() as c:
        cur = c.execute(sql, params)
        return cur.lastrowid

def get_projects(uid):
    return query("SELECT * FROM projects WHERE user_id=? ORDER BY created_at DESC", (uid,))

def get_project(pid, uid):
    rows = query("SELECT * FROM projects WHERE id=? AND user_id=?", (pid, uid))
    return rows[0] if rows else None

def ensure_subscription(uid):
    rows = query("SELECT * FROM subscriptions WHERE user_id=?", (uid,))
    if not rows:
        execute("INSERT INTO subscriptions(user_id,plan,status,updated_at) VALUES(?,?,?,?)", (uid,"Free","local-demo",now()))

# ---------- URL and crawler safety ----------
TRACKING_KEYS = {"gclid","fbclid","gbraid","wbraid","srsltid","gad_source","msclkid"}
def normalize_url(url):
    """Normalize a user-entered public URL; accept a bare domain as https by default."""
    raw = (url or "").strip()
    if not raw or any(ch.isspace() for ch in raw):
        return ""
    if not re.match(r"^https?://", raw, re.I):
        # Friendly input: example.com, www.example.com/path. Do not reinterpret arbitrary words.
        first = raw.split("/", 1)[0].split("?", 1)[0].split("#", 1)[0]
        if "." not in first and first.lower() != "localhost":
            return ""
        raw = "https://" + raw.lstrip("/")
    try:
        p = urlparse(raw)
        scheme = p.scheme.lower()
        host = (p.hostname or "").lower().rstrip(".")
        if scheme not in ("http", "https") or not host:
            return ""
        port = p.port
    except ValueError:
        return ""
    netloc = host
    if port and not ((scheme == "https" and port == 443) or (scheme == "http" and port == 80)):
        netloc += f":{port}"
    path = re.sub(r"/{2,}", "/", p.path or "/")
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    qs = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
          if k.lower() not in TRACKING_KEYS and not k.lower().startswith("utm_")]
    return urlunparse((scheme, netloc, path, "", urlencode(qs, doseq=True), ""))

def validate_public_url(url):
    p = urlparse(url)
    if p.scheme not in ("http","https") or not p.hostname:
        return False, "Enter a full http:// or https:// website URL."
    host = p.hostname.lower()
    if host in ("localhost",) or host.endswith((".localhost",".local",".internal")):
        return False, "Local and internal hosts are blocked."
    try:
        infos = socket.getaddrinfo(host, p.port or (443 if p.scheme=="https" else 80), type=socket.SOCK_STREAM)
        for info in infos:
            ip = ipaddress.ip_address(info[4][0])
            if not ip.is_global:
                return False, "Private or non-public network targets are blocked."
    except Exception:
        # DNS validation may be unavailable in hosted environments; request will still be constrained by host checks.
        if re.match(r"^\d+\.\d+\.\d+\.\d+$", host):
            try:
                if not ipaddress.ip_address(host).is_global: return False, "Private IP targets are blocked."
            except Exception: return False, "Invalid IP address."
    return True, ""

def same_origin(url, base):
    a,b=urlparse(url),urlparse(base)
    return a.scheme==b.scheme and (a.hostname or "").lower()==(b.hostname or "").lower() and (a.port or (443 if a.scheme=="https" else 80))==(b.port or (443 if b.scheme=="https" else 80))

def robots_allowed(base, path, parser=None, checked=False):
    """Use a crawl-scoped parsed robots policy to avoid downloading robots.txt per page."""
    try:
        from urllib.robotparser import RobotFileParser
        rp=parser
        if rp is None and not checked:
            rp=RobotFileParser()
            rp.set_url(urljoin(base, "/robots.txt"))
            rp.read()
        # If robots.txt was checked but unavailable/unparseable, don't silently block every page;
        # the report records that the rules could not be verified.
        if rp is None:
            return True
        return rp.can_fetch(UA, urljoin(base,path))
    except Exception:
        return True

def fetch_html(url):
    ok, msg = validate_public_url(url)
    if not ok: raise ValueError(msg)
    r = requests.get(url, headers={"User-Agent":UA}, timeout=TIMEOUT, allow_redirects=False, stream=True)
    if r.is_redirect or r.is_permanent_redirect:
        loc = r.headers.get("Location","")
        r.close()
        return {"redirect": urljoin(url,loc), "status":r.status_code}
    ctype = r.headers.get("Content-Type","").lower()
    if "text/html" not in ctype:
        r.close()
        return {"non_html":True,"status":r.status_code}
    chunks=[]; total=0
    for chunk in r.iter_content(65536):
        total += len(chunk)
        if total > MAX_BODY_BYTES: break
        chunks.append(chunk)
    text=b"".join(chunks).decode(r.encoding or "utf-8",errors="replace")
    result={"html":text,"status":r.status_code,"final_url":url,"headers":dict(r.headers)}
    r.close()
    return result

def parse_page(url, html, status, headers=None):
    soup=BeautifulSoup(html,"html.parser")
    # Extract JSON-LD before removing scripts from the visible-text DOM.
    jsonld=[]
    for script in soup.find_all("script",type=re.compile("ld\\+json",re.I)):
        try: jsonld.append(json.loads(script.string or script.get_text()))
        except Exception: pass
    for x in soup(["script","style","noscript","svg"]): x.decompose()
    title=soup.title.get_text(" ",strip=True) if soup.title else ""
    desc=soup.find("meta",attrs={"name":re.compile("^description$",re.I)})
    h1=[x.get_text(" ",strip=True) for x in soup.find_all("h1")]
    canon=soup.find("link",rel=lambda v:v and "canonical" in [str(z).lower() for z in (v if isinstance(v,list) else [v])])
    robots=soup.find("meta",attrs={"name":re.compile("^robots$",re.I)})
    imgs=soup.find_all("img")
    alt_missing=sum(1 for im in imgs if im.get("alt") is None)
    alt_empty=sum(1 for im in imgs if im.get("alt") == "")
    links=[]
    for a in soup.find_all("a",href=True):
        target=normalize_url(urljoin(url,a["href"]))
        if target: links.append((target,a.get_text(" ",strip=True)))
    text=soup.get_text(" ",strip=True)
    words=len(re.findall(r"\b[\w'-]+\b",text))
    return {"url":url,"status":status,"title":title,"title_len":len(title),"description":desc.get("content","").strip() if desc else "",
      "description_len":len(desc.get("content","").strip()) if desc else 0,"h1":h1,"h1_count":len(h1),
      "canonical":normalize_url(urljoin(url,canon.get("href"))) if canon and canon.get("href") else "",
      "robots":robots.get("content","") if robots else "","noindex":bool(robots and "noindex" in robots.get("content","").lower()),
      "images":len(imgs),"alt_missing":alt_missing,"alt_empty":alt_empty,"words":words,
      "internal_links":sum(1 for u,_ in links if same_origin(u,url)),"external_links":sum(1 for u,_ in links if not same_origin(u,url)),
      "jsonld_blocks":len(jsonld),"jsonld_types":", ".join(sorted({str(v.get("@type")) for item in jsonld for v in (item if isinstance(item,list) else [item]) if isinstance(v,dict) and v.get("@type")})),
      "links":[{"url":u,"anchor":a} for u,a in links],"headers":headers or {},"text_excerpt":text[:4500]}

def make_findings(pages):
    findings=[]
    def add(page,priority,category,issue,evidence,action,confidence="High"):
        findings.append({"priority":priority,"category":category,"url":page.get("url",""),"issue":issue,"evidence":evidence,"recommendation":action,"confidence":confidence})
    for p in pages:
        if p.get("status",0)>=400: add(p,"P1","Availability",f"Page returned HTTP {p['status']}",f"HTTP status {p['status']}.","Verify URL, server response and internal links.")
        if not p.get("title"): add(p,"P1","On-page SEO","Missing page title","No HTML title element was found.","Write a unique, descriptive title that reflects the page intent.")
        elif p["title_len"]>65: add(p,"P2","On-page SEO","Long page title",f"Title is {p['title_len']} characters.","Review for clarity and concision; character length alone is not a ranking rule.","Medium")
        if not p.get("description"): add(p,"P2","On-page SEO","Missing meta description","No meta description was found.","Write a useful summary that matches the page and encourages qualified clicks.")
        if p.get("h1_count")==0: add(p,"P2","Content structure","No H1 heading","No H1 element was found in parsed HTML.","Add a clear primary heading when appropriate for the page.")
        elif p["h1_count"]>1: add(p,"P3","Content structure","Multiple H1 headings",f"Found {p['h1_count']} H1 elements.","Review heading hierarchy for clarity; multiple H1s are not automatically an SEO error.","Low")
        if p.get("noindex"): add(p,"P1","Indexability","Noindex directive present","Robots meta contains noindex.", "Confirm the page should be excluded from search before changing the directive.")
        if p.get("canonical") and urlparse(p["canonical"]).hostname != urlparse(p["url"]).hostname:
            add(p,"P1","Indexability","Canonical points to another host",p["canonical"],"Verify cross-domain canonical intent.")
        if not p.get("canonical"): add(p,"P3","Indexability","No canonical link found","No canonical element found in HTML.","Check whether a canonical is needed; absence is not always an error.","Medium")
        if p.get("alt_missing",0)>0: add(p,"P2","Accessibility", "Images missing alt attributes",f"{p['alt_missing']} of {p['images']} images have no alt attribute.","Add concise alt text to informative images; use alt=\"\" for decorative images.")
        if p.get("words",0)<120: add(p,"P3","Content", "Very little visible text",f"Approximately {p['words']} words were extracted.","Check whether the page fully answers its intended user need; word count alone does not determine quality.","Low")
        if p.get("jsonld_blocks",0)==0: add(p,"P3","Structured data","No JSON-LD detected","No JSON-LD script block found in the HTML.","Check whether relevant structured data is appropriate; JSON-LD is not required on every page.","Low")
        if p.get("internal_links",0)==0: add(p,"P2","Internal linking","No internal links detected","No same-origin links were detected in parsed HTML.","Check whether this page should link to relevant pages or be linked from navigation.","Medium")
    return findings

def crawl_site(start_url, max_pages=MAX_CRAWL_PAGES, delay=CRAWL_DELAY_SECONDS, scope_prefix=None):
    """Bounded same-origin crawl, seeded from homepage links and public sitemap URLs."""
    start=normalize_url(start_url)
    ok,msg=validate_public_url(start)
    if not ok: raise ValueError(msg)
    p=urlparse(start); base=f"{p.scheme}://{p.netloc}"
    # The UI always scans the hostname root. This fallback also protects direct helper calls.
    root=f"{p.scheme}://{p.netloc}/"
    # Fetch and parse robots once per scan instead of once per page.
    robots_result=fetch_public_text(urljoin(base,"/robots.txt"),200_000)
    robots_parser=None
    if robots_result.get("ok"):
        try:
            from urllib.robotparser import RobotFileParser
            robots_parser=RobotFileParser()
            robots_parser.set_url(urljoin(base,"/robots.txt"))
            robots_parser.parse(robots_result.get("text","").splitlines())
        except Exception:
            robots_parser=None
    else:
        notes_robots=f"robots.txt could not be verified for crawl permissions: {robots_result.get('error') or 'unavailable'}"
    todo=[root]; seen=set(); pages=[]; notes=[]; sitemap_discovered=False; sitemap_count=0
    if not robots_result.get("ok"):
        notes.append(notes_robots)
    max_pages=max(1,min(int(max_pages or MAX_CRAWL_PAGES),MAX_CRAWL_PAGES))
    while todo and len(pages)<max_pages:
        url=normalize_url(todo.pop(0))
        if not url or url in seen or not same_origin(url,root): continue
        if scope_prefix and not (urlparse(url).path == scope_prefix or urlparse(url).path.startswith(scope_prefix.rstrip("/") + "/")):
            continue
        seen.add(url)
        if not robots_allowed(base,urlparse(url).path or "/",parser=robots_parser,checked=True):
            notes.append(f"Skipped robots-disallowed URL: {url}")
            continue
        try:
            fetched=fetch_html(url)
            if "redirect" in fetched:
                dest=normalize_url(fetched["redirect"])
                notes.append(f"Redirect {fetched['status']}: {url} → {dest or 'invalid destination'}")
                # Redirect destinations are normalized and checked against the original origin before queuing.
                if dest and same_origin(dest,root) and dest not in seen: todo.insert(0,dest)
                continue
            if fetched.get("non_html"):
                notes.append(f"Skipped non-HTML URL (HTTP {fetched['status']}): {url}")
                continue
            page=parse_page(url,fetched["html"],fetched["status"],fetched.get("headers"))
            pages.append(page)
            if not sitemap_discovered:
                sitemap_discovered=True
                sitemap_urls, sitemap_notes=discover_sitemap_urls(root)
                sitemap_count=len(sitemap_urls)
                notes.extend(sitemap_notes)
                # Sitemap URLs are discovered by the site itself; still require same origin and robots permission.
                for candidate in reversed(sitemap_urls):
                    if candidate not in seen and candidate not in todo and same_origin(candidate,root):
                        todo.insert(0,candidate)
            for link in page["links"]:
                target=link["url"]
                in_scope = (not scope_prefix) or (urlparse(target).path == scope_prefix or urlparse(target).path.startswith(scope_prefix.rstrip("/") + "/"))
                if same_origin(target,root) and in_scope and target not in seen and target not in todo and len(seen)+len(todo)<max_pages*5:
                    if urlparse(target).path.lower().endswith((".pdf",".jpg",".jpeg",".png",".gif",".svg",".webp",".zip",".xml",".json",".css",".js",".woff",".woff2")): continue
                    todo.append(target)
            time.sleep(max(0.5,min(float(delay),10)))
        except Exception as e:
            pages.append({"url":url,"status":0,"title":"","title_len":0,"description":"","description_len":0,"h1":[],"h1_count":0,"canonical":"","robots":"","noindex":False,"images":0,"alt_missing":0,"alt_empty":0,"words":0,"internal_links":0,"external_links":0,"jsonld_blocks":0,"jsonld_types":"","links":[],"headers":{},"text_excerpt":"","error":str(e)[:240]})
    if sitemap_count:
        notes.append(f"Discovered {sitemap_count} same-origin page URL(s) through sitemap files.")
    if len(pages) >= max_pages and todo:
        notes.append(f"The automatic safety limit of {max_pages} HTML pages was reached. This report covers the pages inspected; a deeper crawl would be needed to assess the rest of the site.")
    findings=make_findings(pages)
    score=max(0,100-sum({"P1":12,"P2":5,"P3":2}.get(f["priority"],1) for f in findings)//max(1,len(pages)//3 or 1))
    return {"url":root,"pages":pages,"findings":findings,"score":score,"notes":notes,"created_at":now(),
            "coverage":{"pages_inspected":len(pages),"page_limit":max_pages,"limit_reached":len(pages)>=max_pages and bool(todo),"sitemap_urls_discovered":sitemap_count}}

# ---------- AI integration ----------
def openai_call(system_prompt, user_prompt, model=None):
    key=st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY",""))
    if not key: raise RuntimeError("OpenAI API key is not configured. Add OPENAI_API_KEY to Streamlit Secrets or your environment.")
    model=model or st.secrets.get("OPENAI_MODEL",os.getenv("OPENAI_MODEL",DEFAULT_MODEL))
    r=requests.post("https://api.openai.com/v1/chat/completions",
      headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
      json={"model":model,"temperature":0.2,"messages":[{"role":"system","content":system_prompt},{"role":"user","content":user_prompt}]},
      timeout=60)
    if r.status_code>=400: raise RuntimeError(f"AI API error ({r.status_code}): {r.text[:500]}")
    return r.json()["choices"][0]["message"]["content"]

# ---------- Auth ----------
def auth_screen():
    st.markdown("""<div class="ogs-public-wrap"><div class="ogs-public-nav"><div class="ogs-brand"><span class="ogs-brand-mark">↗</span>Organic Growth Studio</div><div class="ogs-nav-note">SEO clarity for teams that want to grow</div></div></div>""", unsafe_allow_html=True)
    left, right = st.columns([1.12, .88], gap="large", vertical_alignment="top")
    with left:
        st.markdown("""<div class="ogs-public-hero">
          <div class="ogs-pill"><span>✦</span> Search + AI visibility workspace</div>
          <h1>Make your next growth move <span style="color:#6557ee">with confidence.</span></h1>
          <p>Find the technical issues holding your site back, uncover search opportunities, and track how your brand appears in AI answers—with evidence you can act on.</p>
          <div class="ogs-feature-row"><span class="ogs-feature">◈ Technical SEO audits</span><span class="ogs-feature">⌕ Search performance</span><span class="ogs-feature">✧ AI visibility tracking</span><span class="ogs-feature">↗ Clear next steps</span></div>
          <div class="ogs-preview-shell">
            <div class="ogs-preview-top"><span>✦ ORGANIC GROWTH OVERVIEW</span><span><i class="ogs-live-dot"></i>Project workspace</span></div>
            <div class="ogs-preview-body">
              <div><div class="ogs-mini-label">WEBSITE HEALTH</div><div class="ogs-mini-score">—<span style="font-size:13px;color:#8992a5"> / 100</span></div><div class="ogs-mini-bar"><span style="width:62%"></span></div><div style="font-size:9px;color:#7b8599">Your score appears after your first crawl</div>
                <div class="ogs-mini-item"><span class="ogs-mini-icon">⌕</span><span><b>Technical audit</b><br><span style="color:#8790a3">Prioritised issues and evidence</span></span></div>
                <div class="ogs-mini-item"><span class="ogs-mini-icon">✧</span><span><b>AI search readiness</b><br><span style="color:#8790a3">Track observed brand mentions</span></span></div>
              </div>
              <div><div class="ogs-mini-label">GROWTH SIGNALS</div><div class="ogs-mini-stat"><b>Search</b><span>Queries, pages and clicks from your data</span></div><div class="ogs-mini-stat"><b>AI visibility</b><span>Recorded answers, citations and sentiment</span></div><div class="ogs-mini-stat"><b>Next actions</b><span>Turn findings into a practical worklist</span></div></div>
            </div>
          </div>
          <div class="ogs-trustline" style="justify-content:flex-start"><span>Evidence-first recommendations</span><span>No invented metrics</span><span>Free to get started</span></div>
        </div>
        <div class="ogs-public-heading">One clear view of your organic growth.</div><div class="ogs-public-sub">Designed for business owners and SEO teams who need to know what to fix next—and why.</div>""", unsafe_allow_html=True)
    with right:
        st.markdown('<div class="ogs-auth-card"><div class="ogs-pill" style="margin-bottom:14px">Get started</div><h3>Welcome to your workspace</h3><p>Sign in to continue, or create your free account to audit your first website.</p></div>', unsafe_allow_html=True)
        tab1,tab2=st.tabs(["Sign in", "Create account"])
        with tab1:
            with st.form("signin"):
                email=st.text_input("Email",placeholder="you@company.com").strip().lower()
                pw=st.text_input("Password",type="password",placeholder="Enter your password")
                ok=st.form_submit_button("Sign in to workspace",use_container_width=True)
            if ok:
                rows=query("SELECT * FROM users WHERE email=?",(email,))
                if rows and verify_password(pw,rows[0]["password_hash"]):
                    st.session_state["user"]={"id":rows[0]["id"],"email":email}
                    ensure_subscription(rows[0]["id"]); st.rerun()
                else: st.error("Email or password is incorrect.")
        with tab2:
            with st.form("signup"):
                email2=st.text_input("Work email",key="signup_email",placeholder="you@company.com").strip().lower()
                pw2=st.text_input("Create password (12+ characters)",type="password",key="signup_pw",placeholder="Use at least 12 characters")
                pw3=st.text_input("Confirm password",type="password",key="signup_pw2",placeholder="Re-enter your password")
                ok2=st.form_submit_button("Create free workspace",use_container_width=True)
            if ok2:
                if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$",email2): st.error("Enter a valid email address.")
                elif len(pw2)<12: st.error("Use at least 12 characters for your password.")
                elif pw2!=pw3: st.error("Passwords do not match.")
                else:
                    try:
                        uid=execute("INSERT INTO users(email,password_hash,created_at) VALUES(?,?,?)",(email2,hash_password(pw2),now()))
                        st.session_state["user"]={"id":uid,"email":email2}; ensure_subscription(uid); st.rerun()
                    except sqlite3.IntegrityError: st.error("An account with this email already exists.")
        st.markdown('<div class="ogs-footer-note">Private workspace · Real data · No fabricated metrics</div>', unsafe_allow_html=True)

# ---------- Guided diagnostic engine ----------
AI_DISCOVERY_PLATFORMS = [
    {"platform":"OpenAI / ChatGPT Search", "agents":["OAI-SearchBot", "ChatGPT-User"]},
    {"platform":"Anthropic / Claude", "agents":["Claude-SearchBot", "Claude-User", "ClaudeBot"]},
    {"platform":"Perplexity", "agents":["PerplexityBot", "Perplexity-User"]},
    {"platform":"Google AI Overviews / Gemini", "agents":["Googlebot", "Google-Extended"]},
    {"platform":"Microsoft Copilot / Bing", "agents":["Bingbot"]},
    {"platform":"Meta AI", "agents":["Meta-ExternalAgent"]},
    {"platform":"Apple ecosystem", "agents":["Applebot", "Applebot-Extended"]},
    {"platform":"Amazon AI / Alexa", "agents":["Amazonbot"]},
    {"platform":"You.com", "agents":["YouBot"]},
    {"platform":"Brave Search ecosystem", "agents":["Bravebot"]},
]

def fetch_public_text(url, limit=500_000):
    """Fetch one public text resource without following redirects; returns evidence, not assumptions."""
    ok, msg = validate_public_url(url)
    if not ok:
        return {"ok":False,"status":None,"text":"","error":msg,"url":url}
    try:
        r=requests.get(url,headers={"User-Agent":UA},timeout=8,allow_redirects=False,stream=True)
        status=r.status_code
        if 300 <= status < 400:
            location=r.headers.get("Location",""); r.close()
            return {"ok":False,"status":status,"text":"","error":f"Redirect to {location or 'another URL'} was not followed during the safety check.","url":url}
        chunks=[]; total=0
        for chunk in r.iter_content(32768):
            total+=len(chunk)
            if total>limit: break
            chunks.append(chunk)
        text=b"".join(chunks).decode(r.encoding or "utf-8",errors="replace")
        r.close()
        return {"ok":200<=status<300,"status":status,"text":text,"error":"" if 200<=status<300 else f"HTTP {status}","url":url}
    except Exception as exc:
        return {"ok":False,"status":None,"text":"","error":str(exc)[:180],"url":url}

def _sitemap_locations(xml_text):
    """Parse <loc> values from a sitemap or sitemap index without external entities."""
    if not xml_text or len(xml_text) > 500_000:
        return [], False
    try:
        root = ET.fromstring(xml_text)
        locations = []
        for element in root.iter():
            if element.tag.rsplit("}", 1)[-1].lower() == "loc" and element.text:
                locations.append(element.text.strip())
        kind = root.tag.rsplit("}", 1)[-1].lower()
        return locations, kind in ("urlset", "sitemapindex")
    except (ET.ParseError, ValueError):
        return [], False

def discover_sitemap_urls(start_url):
    """Discover same-origin sitemap URLs from robots.txt and common paths, bounded to 10 maps/500 URLs."""
    start=normalize_url(start_url); p=urlparse(start); origin=f"{p.scheme}://{p.netloc}"
    notes=[]; candidates=[]
    robots=fetch_public_text(urljoin(origin,"/robots.txt"),200_000)
    if robots["ok"]:
        for line in robots["text"].splitlines():
            if line.strip().lower().startswith("sitemap:"):
                candidate=normalize_url(line.split(":",1)[1].strip())
                if candidate and same_origin(candidate,origin) and candidate not in candidates:
                    candidates.append(candidate)
    for path in ("/sitemap.xml","/sitemap_index.xml","/sitemap-index.xml"):
        candidate=urljoin(origin,path)
        if candidate not in candidates:
            candidates.append(candidate)
    queue=candidates[:MAX_SITEMAPS]; seen_maps=set(); page_urls=[]
    while queue and len(seen_maps)<MAX_SITEMAPS and len(page_urls)<MAX_SITEMAP_URLS:
        sitemap_url=queue.pop(0)
        if sitemap_url in seen_maps or not same_origin(sitemap_url,origin):
            continue
        seen_maps.add(sitemap_url)
        result=fetch_public_text(sitemap_url,500_000)
        if not result["ok"]:
            continue
        locations,valid_xml=_sitemap_locations(result["text"])
        if not valid_xml:
            continue
        for location in locations:
            target=normalize_url(urljoin(sitemap_url,location))
            if not target or not same_origin(target,origin):
                continue
            if urlparse(target).path.lower().endswith((".pdf",".jpg",".jpeg",".png",".gif",".svg",".webp",".zip",".xml",".json",".css",".js",".woff",".woff2")):
                if urlparse(target).path.lower().endswith(".xml") and target not in seen_maps and len(queue)+len(seen_maps)<MAX_SITEMAPS:
                    queue.append(target)
                continue
            if target not in page_urls:
                page_urls.append(target)
                if len(page_urls)>=MAX_SITEMAP_URLS:
                    break
    if page_urls:
        notes.append(f"Sitemap discovery found {len(page_urls)} same-origin URL(s); sitemap entries are treated as discovery hints, not proof that every URL is indexable.")
    return page_urls[:MAX_SITEMAP_URLS],notes

def analyze_ai_search_health(start_url, pages):
    """Free technical AI-search readiness checks; does not pretend to query model answers."""
    start=normalize_url(start_url); parsed=urlparse(start); origin=f"{parsed.scheme}://{parsed.netloc}"
    robots=fetch_public_text(urljoin(origin,"/robots.txt"),200_000)
    sitemap_candidates=[]
    if robots["ok"]:
        for line in robots["text"].splitlines():
            if line.strip().lower().startswith("sitemap:"):
                candidate=normalize_url(line.split(":",1)[1].strip())
                if candidate and same_origin(candidate,origin) and candidate not in sitemap_candidates:
                    sitemap_candidates.append(candidate)
    for path in ("/sitemap.xml","/sitemap_index.xml","/sitemap-index.xml"):
        candidate=urljoin(origin,path)
        if candidate not in sitemap_candidates: sitemap_candidates.append(candidate)
    sitemap_url=""
    sitemap={"ok":False,"status":None,"text":"","error":"No sitemap location was verified.","url":""}
    for candidate in sitemap_candidates[:MAX_SITEMAPS]:
        attempt=fetch_public_text(candidate,500_000)
        locations,valid_sitemap=_sitemap_locations(attempt.get("text","")) if attempt.get("ok") else ([],False)
        if attempt.get("ok") and valid_sitemap:
            sitemap=attempt; sitemap_url=candidate; break
    llms=fetch_public_text(urljoin(origin,"/llms.txt"),200_000)
    findings=[]; platform_rows=[]
    def add(priority,category,issue,evidence,fix,seo_benefit,aeo_benefit,gain,confidence="Medium"):
        findings.append({"priority":priority,"category":category,"issue":issue,"evidence":evidence,"fix":fix,
          "seo_benefit":seo_benefit,"aeo_benefit":aeo_benefit,"expected_gain":gain,"confidence":confidence})
    if robots["ok"]:
        robots_parser=None
        try:
            from urllib.robotparser import RobotFileParser
            robots_parser=RobotFileParser(); robots_parser.set_url(urljoin(origin,"/robots.txt")); robots_parser.parse(robots["text"].splitlines())
        except Exception: pass
        for entry in AI_DISCOVERY_PLATFORMS:
            statuses=[]
            for agent in entry["agents"]:
                if robots_parser:
                    try: allowed=robots_parser.can_fetch(agent,start)
                    except Exception: allowed=True
                    statuses.append((agent,allowed))
            if not statuses:
                status="Could not parse rules"
            elif all(x[1] for x in statuses): status="Allowed at tested URL"
            elif not any(x[1] for x in statuses): status="Blocked at tested URL"
            else: status="Mixed rules"
            platform_rows.append({"platform":entry["platform"],"status":status,"user_agents":", ".join(x[0] for x in statuses)})
        blocked=[r for r in platform_rows if r["status"]=="Blocked at tested URL"]
        if blocked:
            add("P1","AI crawler access","AI discovery crawlers appear blocked by robots.txt",
                "; ".join(r["platform"] for r in blocked)+" are disallowed at the tested URL according to parsed robots.txt rules.",
                "Review the matching User-agent and Disallow rules. Only allow crawlers you intend to serve; verify the exact rules and legal/privacy implications before changing them.",
                "If Google/Bing crawlers are blocked, eligible pages may be harder to discover or refresh.",
                "AI search crawlers may be unable to fetch content for retrieval or citation.",
                "Restores crawler access where intentional; does not guarantee citations.","High")
    else:
        platform_rows=[{"platform":x["platform"],"status":"Robots.txt unavailable or unverified","user_agents":", ".join(x["agents"])} for x in AI_DISCOVERY_PLATFORMS]
        add("P2","AI crawler access","robots.txt could not be verified",robots["error"] or f"HTTP {robots['status']}",
            "Check whether /robots.txt should be publicly available and ensure it returns a valid text response. A missing robots.txt is not automatically an error.",
            "Clear crawl directives help search crawlers interpret intended access.","Crawler access for AI search systems remains unverified.","Removes uncertainty about crawl permissions.","Medium")
    if sitemap["ok"]:
        sitemap_signal=bool(re.search(r"<urlset|<sitemapindex",sitemap["text"],re.I))
        if sitemap_signal:
            add("P3","Discovery","XML sitemap detected",f"{sitemap_url} returned HTTP {sitemap['status']} and contains a sitemap root element.",
                "Keep the sitemap current, canonical, and limited to indexable URLs; submit it in search consoles where appropriate.",
                "Can help search engines discover canonical URLs.","A clearer URL inventory may help discovery systems locate useful pages.","Improves discovery signals; inclusion is not guaranteed.","High")
        else:
            add("P2","Discovery","Sitemap URL responds but format was not confirmed",f"HTTP {sitemap['status']} at /sitemap.xml; expected urlset or sitemapindex markup was not found.",
                "Verify the sitemap format and whether the actual sitemap is published at another path; check robots.txt for its location.",
                "A valid sitemap can support URL discovery.","A clean page inventory may help discovery systems find key URLs.","Makes URL discovery more reliable if a sitemap is needed.","Medium")
    else:
        add("P2","Discovery","XML sitemap not found at the default path",sitemap["error"] or f"HTTP {sitemap['status']} at /sitemap.xml",
            "Check robots.txt and your CMS for the canonical sitemap location. Publish and maintain an XML sitemap if the site benefits from one.",
            "Supports discovery of important canonical pages, especially on larger sites.","Provides a structured inventory of pages that AI-enabled search systems may discover.","Improves discovery paths; it does not cause AI mentions by itself.","Medium")
    if llms["ok"] and llms["text"].strip():
        add("P3","AI content guidance","llms.txt is present",f"/llms.txt returned HTTP {llms['status']} with {len(llms['text'])} characters.",
            "Keep the file accurate and link to high-value public documentation and pages. Treat llms.txt as an emerging convention, not a universally supported ranking signal.",
            "Maintaining useful documentation can improve clarity for human and machine readers.","May provide a concise map of important content to systems that choose to consume it; adoption is not universal.","Potential discoverability aid with uncertain platform uptake.","Medium")
    else:
        add("P3","AI content guidance","No usable llms.txt detected at the standard path",llms["error"] or "The file was empty or not available at /llms.txt.",
            "Optional: create a concise /llms.txt linking to authoritative product, service, pricing, FAQ and documentation pages. Do not treat it as a requirement or guaranteed AI-ranking factor.",
            "A clear documentation structure can help users and crawlers navigate important pages.","Some AI-oriented tools may use this file as a content map; many may ignore it.","Low-cost optional enhancement; impact is uncertain.","Low")
    if pages:
        schema_pages=sum(1 for p in pages if p.get("jsonld_blocks",0)>0)
        descriptive_pages=sum(1 for p in pages if p.get("title") and p.get("h1_count",0)>=1 and p.get("words",0)>=120)
        internal_pages=sum(1 for p in pages if p.get("internal_links",0)>0)
        ratio=schema_pages/len(pages)
        if ratio < .3:
            add("P2","Structured information","Structured data was detected on fewer than 30% of crawled pages",f"{schema_pages}/{len(pages)} crawled pages contain JSON-LD. This is a coverage signal, not proof of a defect.",
                "Add only schema types that accurately describe visible page content (for example Organization, Product, Article or BreadcrumbList). Validate markup and never add fabricated ratings or claims.",
                "Eligible structured data can help search engines understand page entities and may enable supported rich results.","Explicit entity and page-type signals can reduce ambiguity for systems that consume structured data.","Better machine-readable context; rich results and AI citations are not guaranteed.","Medium")
        if descriptive_pages/len(pages)<.6:
            add("P2","Answer-ready content","Many crawled pages lack a clear title, H1, or substantial visible copy",f"{descriptive_pages}/{len(pages)} pages passed the simple title + H1 + 120-word heuristic. This is a diagnostic heuristic, not a content-quality score.",
                "For important pages, state the entity/service, intended audience and purpose early. Use descriptive headings, concise answers, original evidence and clear supporting details; do not add filler just to reach a word count.",
                "Improves relevance and page comprehension when content better matches the search intent.","Clear, specific, quotable explanations are easier for answer systems to interpret when they retrieve the page.","Makes important information easier to understand and potentially cite.","Medium")
        if internal_pages/len(pages)<.6:
            add("P2","Content discovery","Internal linking signals are weak across the crawl",f"Only {internal_pages}/{len(pages)} crawled pages had at least one same-origin link.",
                "Link related pages from useful navigation and contextual passages; use descriptive anchor text and ensure important pages are reachable from other pages.",
                "Supports crawling, discovery and contextual relationships between pages.","Helps systems discover related evidence and understand topic relationships.","Improves pathways to important content.","Medium")
    else:
        add("P1","Content analysis","No pages were successfully crawled", "No parsed HTML pages are available for content-readiness checks.",
            "Verify the URL, access rules, hosting response and robots.txt, then rerun the diagnostic.","SEO health cannot be assessed without crawl evidence.","AI content readiness cannot be assessed without crawl evidence.","Enables a meaningful diagnostic.","High")
    # Score is a transparent technical readiness heuristic, not platform visibility.
    penalty=sum({"P1":18,"P2":9,"P3":3}.get(x["priority"],2) for x in findings)
    score=max(0,min(100,100-penalty))
    return {"score":score,"findings":findings,"platforms":platform_rows,
            "signals":{"robots_txt":"Verified" if robots["ok"] else "Unavailable / unverified",
                       "sitemap":"Detected" if sitemap["ok"] and re.search(r"<urlset|<sitemapindex",sitemap["text"],re.I) else "Not confirmed",
                       "llms_txt":"Detected" if llms["ok"] and llms["text"].strip() else "Not detected",
                       "pages_reviewed":len(pages)},
            "disclaimer":"This is technical AI-search readiness, not a measurement of brand mentions or ranking across AI assistants. Platform answers vary by prompt, geography, time and account. Direct visibility measurement requires repeatable live queries or provider integrations."}

def seo_benefits(finding):
    """Plain-language potential benefits by issue type; benefits are hypotheses, not guarantees."""
    issue=(finding.get("issue","")+" "+finding.get("category","")).lower()
    if any(k in issue for k in ("title","description","h1","heading","content","text")):
        return ("A clearer page topic and search-intent match can improve relevance and snippet comprehension.",
                "A specific, well-structured page can make the answer and source context easier for retrieval systems to interpret.")
    if any(k in issue for k in ("noindex","canonical","http status","availability","indexability","redirect")):
        return ("Correct indexability and canonical signals can help crawlers focus on the intended, accessible URL.",
                "Making the canonical public source accessible and unambiguous may help answer systems retrieve the intended page.")
    if any(k in issue for k in ("alt","image","accessibility")):
        return ("Descriptive alt text improves accessibility and provides context for images where appropriate.",
                "Accessible, contextual image descriptions can help systems understand relevant visual content when it is processed.")
    if any(k in issue for k in ("json-ld","structured data")):
        return ("Valid, relevant structured data can clarify entities and may support eligible search enhancements.",
                "Explicit entity and page-type signals can reduce ambiguity for systems that consume structured data.")
    if any(k in issue for k in ("internal link","linking","discovery")):
        return ("Useful internal links support page discovery and contextual relationships across the site.",
                "Links between related authoritative pages help retrieval systems find supporting context and source material.")
    return ("Resolving a verified technical issue can improve crawlability, page clarity or usability depending on the affected page.",
            "Clear, accessible source pages can improve the chance that systems can retrieve and interpret useful information; citations are not guaranteed.")

def score_seo(pages, findings):
    """A transparent internal heuristic; never presented as a Google score."""
    if not pages: return 0
    weighted=sum({"P1":12,"P2":5,"P3":2}.get(f.get("priority"),1) for f in findings)
    return max(0,min(100,100-round(weighted/max(1,len(pages)))))

def save_diagnostic(project_id, scope_mode, scope_url, seo, ai, created_at):
    execute("INSERT INTO audits(project_id,created_at,score,pages,findings_json,pages_json) VALUES(?,?,?,?,?,?)",
            (project_id,created_at,seo["score"],len(seo["pages"]),json.dumps(seo["findings"]),json.dumps(seo["pages"])))
    execute("INSERT INTO diagnostic_runs(project_id,created_at,scope_mode,scope_url,seo_score,ai_score,pages_count,seo_findings_json,ai_findings_json,pages_json,crawl_notes_json) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (project_id,created_at,scope_mode,scope_url,seo["score"],ai["score"],len(seo["pages"]),json.dumps(seo["findings"]),json.dumps(ai),json.dumps(seo["pages"]),json.dumps(seo.get("notes",[]))))
    for f in seo["findings"]:
        if not query("SELECT id FROM tasks WHERE project_id=? AND url=? AND title=? AND status!='Done' LIMIT 1",(project_id,f.get("url",""),f["issue"])):
            execute("INSERT INTO tasks(project_id,title,priority,category,url,evidence,recommendation,status,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
                    (project_id,f["issue"],f["priority"],f["category"],f.get("url",""),f["evidence"],f["recommendation"],"Open",created_at))

def load_diagnostic(run_id, project_id):
    rows=query("SELECT * FROM diagnostic_runs WHERE id=? AND project_id=?",(run_id,project_id))
    if not rows: return None
    r=rows[0]
    ai_payload=json.loads(r["ai_findings_json"])
    if isinstance(ai_payload,list):
        ai_payload={"score":r["ai_score"],"findings":ai_payload,"platforms":[],"signals":{},"disclaimer":"AI Search Health is technical readiness, not observed model visibility."}
    saved_pages=json.loads(r["pages_json"])
    saved_notes=json.loads(r["crawl_notes_json"])
    coverage={"pages_inspected":len(saved_pages),"page_limit":MAX_CRAWL_PAGES,
              "limit_reached":any("automatic safety limit" in str(note).lower() for note in saved_notes),
              "sitemap_urls_discovered":0}
    return {"id":r["id"],"created_at":r["created_at"],"scope_mode":r["scope_mode"],"scope_url":r["scope_url"],
            "seo":{"score":r["seo_score"],"pages":saved_pages,"findings":json.loads(r["seo_findings_json"]),"notes":saved_notes,"coverage":coverage},
            "ai": ai_payload}

# ---------- Main UI: one guided workflow ----------
if not current_user():
    auth_screen()
    st.stop()

user=current_user(); uid=user["id"]
with st.sidebar:
    st.markdown('<div class="ogs-brand"><span class="ogs-brand-mark">↗</span>Organic Growth Studio</div>',unsafe_allow_html=True)
    st.caption("SEARCH + AI DISCOVERY DIAGNOSTICS")
    st.markdown("---")
    st.markdown("**Your workflow**")
    st.markdown("<div class='ogs-step' style='background:#234b3c;border-color:#456b59;color:#f1f5e9'>01 · Enter a website URL</div><div class='ogs-step' style='background:#234b3c;border-color:#456b59;color:#f1f5e9'>02 · Automatic diagnostics</div><div class='ogs-step' style='background:#234b3c;border-color:#456b59;color:#f1f5e9'>03 · Review both health reports</div>",unsafe_allow_html=True)
    st.markdown("---")
    st.caption(user["email"])
    if st.button("Sign out",use_container_width=True):
        st.session_state.pop("user",None); st.rerun()
    all_runs=query("SELECT d.id,d.created_at,d.scope_url,d.seo_score,d.ai_score,p.id AS project_id FROM diagnostic_runs d JOIN projects p ON p.id=d.project_id WHERE p.user_id=? ORDER BY d.created_at DESC LIMIT 12",(uid,))
    if all_runs:
        st.markdown("**Recent diagnostics**")
        options={f"{r['scope_url'][:24]} · {r['created_at'][:10]} · #{r['id']}":(r["id"],r["project_id"]) for r in all_runs}
        selected_label=st.selectbox("Open a previous report",["New diagnostic",*options.keys()],label_visibility="collapsed",key="history_pick")
        if selected_label!="New diagnostic":
            rid,rpid=options[selected_label]
            if st.button("Open report",use_container_width=True):
                st.session_state["active_report"]=(rid,rpid); st.rerun()

st.markdown("""
<div class="ogs-public-hero" style="margin-bottom:18px;background:radial-gradient(circle at 92% 8%,#e3f5c8 0,transparent 27%),radial-gradient(circle at 0% 0%,#e4eee7 0,transparent 35%),#fff;border-color:#dce7dc">
 <div class="ogs-pill" style="color:#285b40;border-color:#d7e6d8;background:#f7fbf5">ONE SCAN · TWO HEALTH REPORTS</div>
 <h1 style="max-width:900px">Know what search engines can see.<br><span style="color:#315d47">Know what to fix next.</span></h1>
 <p style="max-width:820px">Run a technical SEO audit first, then evaluate AI-search readiness. Get the evidence, the fix, and the expected benefit in one clear report.</p>
</div>
""",unsafe_allow_html=True)

# A previously selected report can be reopened without rerunning a crawl.
active_report=None
if st.session_state.get("active_report"):
    rid,rpid=st.session_state["active_report"]
    active_report=load_diagnostic(rid,rpid)
    if active_report:
        owner_project=get_project(rpid,uid)
        if owner_project:
            st.caption(f"Viewing saved report for **{owner_project['domain']}** · {active_report['created_at'][:19]} UTC")
        else:
            active_report=None
            st.session_state.pop("active_report",None)
            st.warning("That saved report is not available in this account. Start a new diagnostic.")
    if st.button("← Start a new diagnostic"):
        st.session_state.pop("active_report",None); st.rerun()

if active_report:
    report=active_report
else:
    st.markdown('<div class="ogs-heading">Start your website diagnostic</div><div class="ogs-sub">Enter one website URL. We discover accessible pages automatically and handle the technical setup for you.</div>',unsafe_allow_html=True)
    with st.form("guided_diagnostic_form",clear_on_submit=False):
        url_input=st.text_input("Website URL",placeholder="yourcompany.com",help="Enter a domain or website URL. We will discover accessible pages automatically. Only scan websites you own or are authorized to assess.")
        run_scan=st.form_submit_button("Run website diagnostic →",type="primary",use_container_width=True)
    st.markdown("<div class='ogs-trustline' style='justify-content:flex-start;margin:10px 0 20px'><span>Site Health runs first</span><span>AI Search Health runs second</span><span>Evidence-backed fixes</span><span>No fabricated AI visibility scores</span></div>",unsafe_allow_html=True)
    if run_scan:
        normalized=normalize_url(url_input)
        valid,msg=validate_public_url(normalized) if normalized else (False,"Enter a full public website URL.")
        if not valid:
            st.error(msg)
        else:
            parsed=urlparse(normalized); root=f"{parsed.scheme}://{parsed.netloc}"
            # The user provides only a URL. Automatically normalize the scan to the entered hostname;
            # keep the page cap internal as a safety/performance guardrail, not a user-facing setting.
            scope_mode="Automatic hostname scan"
            crawl_start=root; scope_prefix=None
            max_pages=MAX_CRAWL_PAGES
            existing=query("SELECT * FROM projects WHERE user_id=? AND domain=?",(uid,root))
            if existing:
                proj=existing[0]; project_id=proj["id"]
            else:
                project_id=execute("INSERT INTO projects(user_id,name,domain,created_at) VALUES(?,?,?,?)",(uid,parsed.hostname or root,root,now()))
            with st.status("Preparing your diagnostic…",expanded=True) as status:
                try:
                    st.write("**Step 1 of 2 — Site Health (SEO)**")
                    st.write("Discovering accessible pages from the homepage, internal links and sitemap files…")
                    st.write("Collecting technical SEO evidence within automatic safety limits…")
                    seo=crawl_site(crawl_start,max_pages=max_pages,delay=0.5,scope_prefix=scope_prefix)
                    seo["score"]=score_seo(seo["pages"],seo["findings"])
                    if not seo["pages"]:
                        raise RuntimeError("No HTML pages were successfully audited. Check the URL, robots.txt and hosting response, then try again.")
                    st.write(f"Site Health complete: {len(seo['pages'])} pages inspected, {len(seo['findings'])} findings.")
                    if seo.get("coverage",{}).get("limit_reached"):
                        st.warning("This website is larger than the automatic scan limit. The report will identify the scan as partial; no page-limit choice is required to get started.")
                    st.write("**Step 2 of 2 — AI Search Health**")
                    st.write("Checking robots directives, sitemap, llms.txt and content signals used for machine discovery…")
                    ai=analyze_ai_search_health(crawl_start,seo["pages"])
                    created=now(); save_diagnostic(project_id,scope_mode,crawl_start,seo,ai,created)
                    st.session_state["active_report"]=(query("SELECT MAX(id) AS id FROM diagnostic_runs WHERE project_id=?",(project_id,))[0]["id"],project_id)
                    st.session_state.pop("scan_error",None)
                    status.update(label="Diagnostics complete",state="complete",expanded=False)
                    st.rerun()
                except Exception as exc:
                    status.update(label="Diagnostic could not complete",state="error",expanded=True)
                    st.error(str(exc))
    report=None

if report:
    seo=report["seo"]; ai=report["ai"]
    st.markdown(f'<div class="ogs-hero" style="background:linear-gradient(120deg,#fff 0%,#f1f8ed 100%);border-color:#dbe8d8"><div class="ogs-eyebrow" style="color:#315d47">DIAGNOSTIC REPORT · {html.escape(report["created_at"][:10])}</div><h2 style="margin:5px 0">{html.escape(report["scope_url"])}</h2><p>Automatic website scan · {len(seo["pages"])} HTML pages inspected · Site Health first, AI Search Health second</p></div>',unsafe_allow_html=True)
    coverage=seo.get("coverage",{})
    if coverage.get("limit_reached"):
        st.warning(f"Partial scan: {coverage.get('pages_inspected',len(seo['pages']))} pages inspected before the automatic safety limit. Review this report as a sample of the site, not a complete audit.")
    elif seo.get("notes"):
        with st.expander("Scan coverage and notes"):
            for note in seo.get("notes",[]): st.write(f"• {note}")
    m1,m2,m3,m4=st.columns(4)
    m1.metric("Site Health · SEO",f"{seo['score']}/100",help="Internal technical SEO heuristic, not a Google score.")
    m2.metric("AI Search Health",f"{ai['score']}/100",help="Technical readiness heuristic, not a ranking or observed-mention score.")
    m3.metric("SEO issues",len(seo["findings"]))
    m4.metric("AI readiness actions",len(ai["findings"]))
    tabs=st.tabs(["Executive summary","1 · Site Health (SEO)","2 · AI Search Health","Fix plan & expected gains","Crawl evidence"])
    with tabs[0]:
        st.markdown("### What the diagnostic says")
        critical=sum(1 for f in seo["findings"] if f.get("priority")=="P1")
        ai_critical=sum(1 for f in ai["findings"] if f.get("priority")=="P1")
        if critical or ai_critical:
            st.warning(f"Start with {critical} high-priority SEO finding(s) and {ai_critical} high-priority AI-readiness finding(s). Review each item before changing production settings.")
        else:
            st.success("No P1 findings were produced by these checks. Review P2/P3 opportunities and validate important pages manually.")
        a,b=st.columns(2)
        with a:
            st.markdown("#### Site Health")
            st.progress(seo["score"]/100)
            st.write(f"**{seo['score']}/100** internal heuristic")
            st.caption("Based on detected page-level findings. This is not Google's score, a ranking prediction, or a guarantee of traffic.")
        with b:
            st.markdown("#### AI Search Health")
            st.progress(ai["score"]/100)
            st.write(f"**{ai['score']}/100** technical readiness heuristic")
            st.caption("Measures access and content signals only. It does not prove that ChatGPT, Claude or another assistant mentions the brand.")
        st.markdown("#### The three things to do first")
        combined=[]
        for f in seo["findings"]:
            combined.append((0 if f.get("priority")=="P1" else 1 if f.get("priority")=="P2" else 2,"SEO",f))
        for f in ai["findings"]:
            combined.append((0 if f.get("priority")=="P1" else 1 if f.get("priority")=="P2" else 2,"AI readiness",f))
        for _,label,f in sorted(combined,key=lambda x:x[0])[:3]:
            with st.container(border=True):
                st.markdown(f"**{label} · {f.get('issue','Finding')}**")
                st.write(f.get("evidence","Evidence unavailable"))
                st.caption(f"Fix: {f.get('fix') or f.get('recommendation','Review the page and validate the finding.')}")
    with tabs[1]:
        st.markdown("### Site Health checks")
        st.caption("Technical and on-page signals from the pages actually crawled.")
        if seo["findings"]:
            for i,f in enumerate(sorted(seo["findings"],key=lambda x:(x.get("priority")!="P1",x.get("priority")!="P2",x.get("url","")))[:100]):
                with st.expander(f"{f.get('priority','P3')} · {f.get('issue','SEO finding')} · {urlparse(f.get('url','')).path or '/'}",expanded=(i<3)):
                    st.markdown(f"**Evidence**  \n{f.get('evidence','Not recorded')}")
                    st.markdown(f"**How to fix**  \n{f.get('recommendation','Review this signal manually.')}")
                    seo_gain,aeo_gain=seo_benefits(f)
                    st.markdown(f"**Potential SEO benefit**  \n{seo_gain}")
                    st.markdown(f"**Potential AEO / AI-search benefit**  \n{aeo_gain}")
                    st.caption(f"URL: {f.get('url','')} · Benefits depend on validation and implementation; no ranking or citation is guaranteed.")
        else: st.success("No issues were detected by the current SEO checks. This does not mean the site is issue-free.")
    with tabs[2]:
        st.markdown("### AI Search Health")
        st.write("We check technical accessibility and answer-ready content signals that can influence whether public information is available to AI-enabled search systems. This is not a live query of model responses.")
        signals=ai.get("signals",{})
        if signals:
            cols=st.columns(4)
            for col,(label,value) in zip(cols,[("robots.txt",signals.get("robots_txt","Not checked")),("XML sitemap",signals.get("sitemap","Not checked")),("llms.txt",signals.get("llms_txt","Not checked")),("Pages reviewed",str(signals.get("pages_reviewed",len(seo["pages"]))))]):
                col.markdown(f"<div class='ogs-step'><div class='ogs-muted'>{html.escape(label)}</div><div style='font-size:15px;font-weight:800;color:#234c36;margin-top:6px'>{html.escape(str(value))}</div></div>",unsafe_allow_html=True)
        st.markdown("#### AI discovery ecosystems · robots.txt signals")
        platform_rows=ai.get("platforms",[])
        if platform_rows:
            st.dataframe(pd.DataFrame(platform_rows),use_container_width=True,hide_index=True)
        else:
            st.info("This saved report predates platform-level checks. Run a new diagnostic to refresh the signals.")
        st.caption(ai.get("disclaimer","Technical readiness is not proof of inclusion in generated answers."))
        for f in ai["findings"]:
            with st.expander(f"{f.get('priority','P3')} · {f.get('issue','AI readiness finding')}"):
                st.markdown(f"**Evidence**  \n{f.get('evidence','Not recorded')}")
                st.markdown(f"**How to fix**  \n{f.get('fix','Review the signal manually.')}")
                st.markdown(f"**SEO benefit**  \n{f.get('seo_benefit','Can clarify discovery or content interpretation where applicable.')}")
                st.markdown(f"**AEO / AI-search benefit**  \n{f.get('aeo_benefit','May improve accessibility or interpretation; citations are not guaranteed.')}")
                st.markdown(f"**Expected gain**  \n{f.get('expected_gain','Potential benefit depends on implementation and platform behavior.')}")
    with tabs[3]:
        st.markdown("### Fix plan: issue → fix → expected benefit")
        st.caption("Expected gains describe plausible mechanisms, not guaranteed ranking increases, traffic, leads or AI citations.")
        action_rows=[]
        for f in seo["findings"]:
            seo_gain,aeo_gain=seo_benefits(f)
            action_rows.append({"Workstream":"SEO","Priority":f.get("priority"),"Issue":f.get("issue"),"Affected URL":f.get("url"),"Evidence":f.get("evidence"),"How to fix":f.get("recommendation"),"Potential SEO gain":seo_gain,"Potential AEO gain":aeo_gain,"Confidence":f.get("confidence","Medium")})
        for f in ai["findings"]:
            action_rows.append({"Workstream":"AI Search","Priority":f.get("priority"),"Issue":f.get("issue"),"Affected URL":report.get("scope_url"),"Evidence":f.get("evidence"),"How to fix":f.get("fix"),"Potential SEO gain":f.get("seo_benefit"),"Potential AEO gain":f.get("aeo_benefit"),"Confidence":f.get("confidence","Medium")})
        if action_rows:
            order={"P1":0,"P2":1,"P3":2}
            action_rows.sort(key=lambda x:order.get(x["Priority"],3))
            st.dataframe(pd.DataFrame(action_rows),use_container_width=True,hide_index=True)
            st.download_button("Download complete fix plan (CSV)",pd.DataFrame(action_rows).to_csv(index=False).encode("utf-8-sig"),"organic-growth-fix-plan.csv","text/csv",type="primary")
        else: st.success("No fix-plan items were generated by this run.")
    with tabs[4]:
        st.markdown("### Crawl evidence")
        page_rows=[]
        for p in seo["pages"]:
            page_rows.append({k:p.get(k) for k in ["url","status","title","description","h1_count","canonical","noindex","images","alt_missing","words","internal_links","external_links","jsonld_types"]})
        st.dataframe(pd.DataFrame(page_rows),use_container_width=True,hide_index=True)
        st.download_button("Download page-level evidence (CSV)",pd.DataFrame(page_rows).to_csv(index=False).encode("utf-8-sig"),"site-health-page-evidence.csv","text/csv")
        if seo.get("notes"):
            st.markdown("#### Crawl notes")
            for note in seo["notes"]: st.write("• "+note)
    st.markdown('<div class="ogs-footer-note">Organic Growth Studio measures observed technical signals. Scores are internal heuristics; platform visibility, rankings and traffic are not guaranteed.</div>',unsafe_allow_html=True)

st.markdown("---")
st.caption("Organic Growth Studio · A guided SEO + AI-search readiness diagnostic. Direct AI-answer visibility measurement and scheduled refreshes are not yet automated in this build.")
