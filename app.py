import os, re, json, time, hashlib, sqlite3, smtplib, ssl, csv, io, socket, ipaddress, html
from datetime import datetime, timezone
from urllib.parse import urlparse, urljoin, urldefrag, urlunparse, parse_qsl, urlencode
from email.message import EmailMessage

import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup

APP_NAME = "Organic Growth Studio"
DB_PATH = os.getenv("OGS_DB_PATH", "organic_growth_studio.db")
UA = "OrganicGrowthStudioAudit/3.0 (+authorized-site-audit)"
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
MAX_BODY_BYTES = 2_000_000
TIMEOUT = 15

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
/* Organic Growth Studio signature theme: forest, citron and warm paper */
:root{--ogs-ink:#192923;--ogs-muted:#68766f;--ogs-line:#e3e7dd;--ogs-bg:#f7f7f1;--ogs-blue:#1d493b;--ogs-nav:#173b31}
.stApp{background:#f7f7f1!important;color:#192923!important}
[data-testid="stHeader"]{background:rgba(247,247,241,.94)!important}
[data-testid="stSidebar"]{background:#173b31!important;border-right:1px solid #244d41!important}
[data-testid="stSidebar"] *{color:#eaf1e8}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover{background:#285444;color:#fff}
[data-testid="stMetric"]{border-color:#e3e7dd;box-shadow:0 3px 10px rgba(25,41,35,.035)}
[data-testid="stVerticalBlockBorderWrapper"]{border-color:#e3e7dd;box-shadow:0 3px 10px rgba(25,41,35,.035)}
.stButton>button:not([kind="primary"]),[data-testid="stDownloadButton"] button,[data-testid="stBaseButton-secondary"]{background:#fff!important;color:#244338!important;border:1px solid #d7ded5!important}
.stButton>button[kind="primary"],[data-testid="stBaseButton-primary"],[data-testid="stFormSubmitButton"] button{background:#d8f36a!important;color:#183b30!important;border:1px solid #c6e65a!important}
.stButton>button[kind="primary"]:hover,[data-testid="stBaseButton-primary"]:hover,[data-testid="stFormSubmitButton"] button:hover{background:#c8e950!important;color:#183b30!important;box-shadow:0 5px 12px rgba(66,95,35,.12)!important}
.stButton>button:hover,[data-testid="stBaseButton-secondary"]:hover{border-color:#91a99a!important;color:#183b30!important;background:#f3f8e8!important}
/* Force light, readable fields—including Streamlit's separate password widget */
[data-testid="stTextInput"] input,[data-testid="stTextInput"] input[type="text"],[data-testid="stTextInput"] input[type="password"],[data-testid="stTextInput"] input[type="email"],input[type="password"],input[type="text"],input[type="email"],textarea{background:#fff!important;background-color:#fff!important;color:#192923!important;-webkit-text-fill-color:#192923!important;border:1px solid #cfd8ce!important;border-radius:11px!important;box-shadow:none!important;caret-color:#1d493b!important}
[data-testid="stTextInput"] input::placeholder,input[type="password"]::placeholder,input[type="text"]::placeholder,input[type="email"]::placeholder{color:#8a968e!important;-webkit-text-fill-color:#8a968e!important;opacity:1!important}
[data-testid="stTextInput"] [data-baseweb="input"],[data-testid="stTextInput"] [data-baseweb="base-input"]{background:#fff!important;border-radius:11px!important}
[data-testid="stTextInput"] [data-baseweb="input"] div{background:#fff!important}
[data-testid="stTabs"] [role="tablist"]{gap:8px;border-bottom:1px solid #e1e6dc}
[data-testid="stTabs"] button[role="tab"]{color:#6b776f!important;border-radius:9px 9px 0 0;padding:10px 15px;background:transparent!important}
[data-testid="stTabs"] button[role="tab"] p{color:inherit!important}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"]{color:#173b31!important;border-bottom:3px solid #d8f36a!important;font-weight:800!important}
.ogs-eyebrow{color:#426e4e}
.ogs-hero{background:linear-gradient(120deg,#fffdf5 0%,#f1f7e7 100%);border:1px solid #e2e8d8;box-shadow:0 8px 28px rgba(35,65,45,.035)}
.ogs-hero h2{color:#192923}.ogs-hero p{color:#68766f}
.ogs-auth{max-width:none;margin:0;padding:0;background:transparent;border:0;border-radius:0;box-shadow:none}
.ogs-auth h1{font-size:38px;letter-spacing:-1.4px;color:#192923}.ogs-auth p{color:#68766f}
.ogs-auth-visual{min-height:430px;height:100%;border-radius:24px;padding:34px;position:relative;overflow:hidden;background:#173b31;color:#f7f7f1;display:flex;flex-direction:column;justify-content:space-between}
.ogs-auth-visual:before{content:"";position:absolute;width:290px;height:290px;border-radius:50%;right:-70px;top:95px;background:#d8f36a;opacity:.96}
.ogs-auth-visual:after{content:"";position:absolute;width:180px;height:180px;border-radius:50%;right:75px;top:155px;background:#ff8068;opacity:.95}
.ogs-auth-visual>*{position:relative;z-index:1}
.ogs-brandmark{font-size:13px;letter-spacing:1.5px;text-transform:uppercase;font-weight:850;color:#d8f36a}
.ogs-auth-visual h1{font-size:42px;line-height:1.05;letter-spacing:-1.8px;color:#fff;max-width:440px;margin:35px 0 12px}
.ogs-auth-visual p{color:#d5e1d7;max-width:390px;font-size:14px;line-height:1.7}
.ogs-orbit-card{display:inline-block;background:#fffdf5;color:#1c3b30;padding:12px 15px;border-radius:13px;box-shadow:0 10px 35px #0b241d30;font-size:12px;font-weight:800;margin-top:12px;max-width:220px}
.ogs-auth-form{background:#fff;border:1px solid #e3e7dd;border-radius:24px;padding:30px;box-shadow:0 10px 30px rgba(25,41,35,.045);height:100%}
.ogs-auth-form h2{font-size:27px;letter-spacing:-.8px;color:#192923;margin:0 0 5px}
.ogs-auth-form .ogs-sub{margin-bottom:18px}
.ogs-auth-foot{color:#7b887f;text-align:center;font-size:12px;margin-top:16px}
@media(max-width:800px){.block-container{padding-left:1rem;padding-right:1rem}.ogs-heading{font-size:25px}.ogs-auth-visual{min-height:300px;padding:24px}.ogs-auth-visual h1{font-size:32px}.ogs-auth-form{padding:20px}}
@media(max-width:800px){.block-container{padding-left:1rem;padding-right:1rem}.ogs-heading{font-size:25px}}
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
    p = urlparse(url.strip())
    scheme = p.scheme.lower() or "https"
    host = (p.hostname or "").lower().rstrip(".")
    if not host: return ""
    netloc = host
    if p.port and not ((scheme=="https" and p.port==443) or (scheme=="http" and p.port==80)):
        netloc += f":{p.port}"
    path = re.sub("/{2,}", "/", p.path or "/")
    if path != "/" and path.endswith("/"): path = path[:-1]
    qs = [(k,v) for k,v in parse_qsl(p.query, keep_blank_values=True)
          if k.lower() not in TRACKING_KEYS and not k.lower().startswith("utm_")]
    return urlunparse((scheme,netloc,path,"",urlencode(qs,doseq=True),""))

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

def robots_allowed(base, path):
    try:
        from urllib.robotparser import RobotFileParser
        rp=RobotFileParser()
        rp.set_url(urljoin(base, "/robots.txt"))
        rp.read()
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

def crawl_site(start_url, max_pages=25, delay=1.0):
    start=normalize_url(start_url)
    ok,msg=validate_public_url(start)
    if not ok: raise ValueError(msg)
    p=urlparse(start); base=f"{p.scheme}://{p.netloc}"
    todo=[start]; seen=set(); pages=[]; notes=[]
    while todo and len(pages)<max_pages:
        url=normalize_url(todo.pop(0))
        if not url or url in seen or not same_origin(url,start): continue
        seen.add(url)
        if not robots_allowed(base,urlparse(url).path or "/"):
            notes.append(f"Skipped robots-disallowed URL: {url}")
            continue
        try:
            fetched=fetch_html(url)
            if "redirect" in fetched:
                dest=normalize_url(fetched["redirect"])
                notes.append(f"Redirect {fetched['status']}: {url} → {dest}")
                if dest and same_origin(dest,start) and dest not in seen: todo.insert(0,dest)
                continue
            if fetched.get("non_html"):
                notes.append(f"Skipped non-HTML URL (HTTP {fetched['status']}): {url}")
                continue
            page=parse_page(url,fetched["html"],fetched["status"],fetched.get("headers"))
            pages.append(page)
            for link in page["links"]:
                target=link["url"]
                if same_origin(target,start) and target not in seen and len(seen)+len(todo)<max_pages*5:
                    if urlparse(target).path.lower().endswith((".pdf",".jpg",".jpeg",".png",".gif",".svg",".webp",".zip",".xml",".json")): continue
                    todo.append(target)
            time.sleep(max(0.5,min(float(delay),10)))
        except Exception as e:
            pages.append({"url":url,"status":0,"title":"","title_len":0,"description":"","description_len":0,"h1":[],"h1_count":0,"canonical":"","robots":"","noindex":False,"images":0,"alt_missing":0,"alt_empty":0,"words":0,"internal_links":0,"external_links":0,"jsonld_blocks":0,"jsonld_types":"","links":[],"headers":{},"text_excerpt":"","error":str(e)})
    findings=make_findings(pages)
    # Transparent heuristic: starts at 100 and deducts capped penalties by priority/category.
    score=max(0,100-sum({"P1":12,"P2":5,"P3":2}.get(f["priority"],1) for f in findings)//max(1,len(pages)//3 or 1))
    return {"url":start,"pages":pages,"findings":findings,"score":score,"notes":notes,"created_at":now()}

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
    left, right = st.columns([1.05, 0.95], gap="large", vertical_alignment="center")
    with left:
        st.markdown('''<section class="ogs-auth-visual">
          <div class="ogs-brandmark">✳ Organic Growth Studio</div>
          <div>
            <h1>Make your next growth move a clear one.</h1>
            <p>A calmer, evidence-first workspace for technical SEO, search performance and AI discovery. Find what matters. Fix what moves the needle.</p>
            <div class="ogs-orbit-card">↗ Signal found<br><span style="font-weight:500">Turn website evidence into your next best action.</span></div>
          </div>
          <div style="font-size:11px;color:#b7cbbd;letter-spacing:.4px">BUILT FOR TEAMS THAT GROW WITH INTENTION</div>
        </section>''', unsafe_allow_html=True)
    with right:
        st.markdown('''<div class="ogs-auth-form"><div class="ogs-eyebrow">YOUR WORKSPACE</div><h2>Welcome back</h2><p class="ogs-sub">Sign in or create a free account to get started.</p>''', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Sign in", "Create account"])
        with tab1:
            with st.form("signin"):
                email=st.text_input("Email", placeholder="you@company.com").strip().lower()
                pw=st.text_input("Password", type="password", placeholder="Enter your password")
                ok=st.form_submit_button("Sign in to workspace",use_container_width=True, type="primary")
            if ok:
                rows=query("SELECT * FROM users WHERE email=?",(email,))
                if rows and verify_password(pw,rows[0]["password_hash"]):
                    st.session_state["user"]={"id":rows[0]["id"],"email":email}
                    ensure_subscription(rows[0]["id"]); st.rerun()
                else: st.error("Email or password is incorrect.")
        with tab2:
            with st.form("signup"):
                email2=st.text_input("Work email",placeholder="you@company.com",key="signup_email").strip().lower()
                pw2=st.text_input("Create password (12+ characters)",type="password",placeholder="Use at least 12 characters",key="signup_pw")
                pw3=st.text_input("Confirm password",type="password",placeholder="Enter your password again",key="signup_pw2")
                ok2=st.form_submit_button("Create my workspace",use_container_width=True,type="primary")
            if ok2:
                if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$",email2): st.error("Enter a valid email address.")
                elif len(pw2)<12: st.error("Use at least 12 characters for your password.")
                elif pw2!=pw3: st.error("Passwords do not match.")
                else:
                    try:
                        uid=execute("INSERT INTO users(email,password_hash,created_at) VALUES(?,?,?)",(email2,hash_password(pw2),now()))
                        st.session_state["user"]={"id":uid,"email":email2}; ensure_subscription(uid); st.rerun()
                    except sqlite3.IntegrityError: st.error("An account with this email already exists.")
        st.markdown('<div class="ogs-auth-foot">Private workspace · Real data · No fabricated metrics</div></div>',unsafe_allow_html=True)

# ---------- Main UI ----------
if not current_user():
    auth_screen()
    st.stop()

user=current_user()
uid=user["id"]
projects=get_projects(uid)
# Action buttons can navigate to a page directly; keep the sidebar radio in sync.
if st.session_state.get("jump_page"):
    st.session_state["nav_page"] = st.session_state.pop("jump_page")

with st.sidebar:
    st.markdown("## 🌱 Organic Growth Studio")
    st.caption("ORGANIC GROWTH WORKSPACE")
    st.caption(user["email"])
    if st.button("Sign out",use_container_width=True):
        st.session_state.pop("user",None); st.rerun()
    st.divider()
    page=st.radio("Workspace",["Overview","Website audit","AI recommendations","Search performance","AI visibility","Competitors","Action center","Reports","Settings"],key="nav_page",label_visibility="visible")
    st.divider()
    if st.button("＋ New project",use_container_width=True):
        st.session_state["new_project"]=True
    if projects:
        project_options={f'{p["name"]} · {p["domain"]}':p["id"] for p in projects}
        chosen=st.selectbox("Active project",list(project_options.keys()),key="active_project")
        pid=project_options[chosen]
        project=get_project(pid,uid)
    else:
        pid=None; project=None
    if st.session_state.get("new_project") or not projects:
        with st.form("new_project_form"):
            st.markdown("### Create your first project")
            pname=st.text_input("Project name",placeholder="Acme SaaS")
            purl=st.text_input("Website URL",placeholder="https://example.com")
            btype=st.text_input("Business type",placeholder="B2B SaaS")
            target=st.text_input("Target customer",placeholder="Operations leaders at growing companies")
            offer=st.text_input("Main product or service",placeholder="Customer support platform")
            comps=st.text_input("Competitor domains (comma separated)",placeholder="competitor1.com, competitor2.com")
            submit=st.form_submit_button("Create project",use_container_width=True)
        if submit:
            url=normalize_url(purl)
            valid,msg=validate_public_url(url) if url else (False,"Enter a website URL.")
            if not valid: st.error(msg)
            else:
                try:
                    execute("INSERT INTO projects(user_id,name,domain,business_type,target_customer,primary_offer,competitors,created_at) VALUES(?,?,?,?,?,?,?,?)",
                      (uid,pname.strip() or urlparse(url).hostname,url,btype,target,offer,json.dumps([x.strip() for x in comps.split(",") if x.strip()]),now()))
                    st.session_state["new_project"]=False; st.rerun()
                except sqlite3.IntegrityError: st.error("This domain is already in your workspace.")
    if project:
        st.caption(f"Project created {project['created_at'][:10]}")

if not project:
    st.markdown('<div class="ogs-hero"><div class="ogs-eyebrow">Welcome to your workspace</div><h2>Your organic growth, in one place.</h2><p>Create your first project to run a website audit, find search opportunities and track real AI-answer observations. No demo metrics—your dashboard starts with your data.</p></div>',unsafe_allow_html=True)
    st.markdown('<div class="ogs-empty"><div style="font-size:38px">🌱</div><h2>Start with your first website</h2><p style="color:#667085">Add a project to unlock your audit, recommendations and reporting workspace.</p></div>',unsafe_allow_html=True)
    if st.button("＋ Create your first project",type="primary",use_container_width=False):
        st.session_state["new_project"]=True
        st.rerun()
    st.caption("Your data is kept separate by account. Only metrics derived from saved project data will appear here.")
    st.stop()

def latest_audit(project_id):
    rows=query("SELECT * FROM audits WHERE project_id=? ORDER BY created_at DESC LIMIT 1",(project_id,))
    if not rows: return None
    r=rows[0]
    return {"id":r["id"],"created_at":r["created_at"],"score":r["score"],"pages":json.loads(r["pages_json"]),"findings":json.loads(r["findings_json"])}

audit=latest_audit(pid)

# Lightweight application header mirrors the approved preview layout.
page_labels={"Overview":"Overview","Website audit":"Website audit","AI recommendations":"AI recommendations","Search performance":"Search performance","AI visibility":"AI visibility","Competitors":"Competitors","Action center":"Action center","Reports":"Reports","Settings":"Settings"}
st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #e6eaf2;padding:0 2px 13px;margin-bottom:22px;color:#667085;font-size:12px"><span>Workspace / <b style="color:#172033">{html.escape(page_labels.get(page,page))}</b></span><span>{html.escape(user["email"])}</span></div>',unsafe_allow_html=True)

def save_audit(result):
    execute("INSERT INTO audits(project_id,created_at,score,pages,findings_json,pages_json) VALUES(?,?,?,?,?,?)",
      (pid,result["created_at"],result["score"],len(result["pages"]),json.dumps(result["findings"]),json.dumps(result["pages"])))
    # Seed action tasks from findings, avoiding identical open tasks.
    for f in result["findings"]:
        exists=query("SELECT id FROM tasks WHERE project_id=? AND url=? AND title=? AND status!='Done' LIMIT 1",(pid,f["url"],f["issue"]))
        if not exists:
            execute("INSERT INTO tasks(project_id,title,priority,category,url,evidence,recommendation,status,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
              (pid,f["issue"],f["priority"],f["category"],f["url"],f["evidence"],f["recommendation"],"Open",now()))

def report_download(label,df,filename):
    data=df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(label,data,filename,mime="text/csv",use_container_width=False)

if page=="Overview":
    safe_project_name = html.escape(str(project["name"]))
    safe_project_domain = html.escape(str(project["domain"]))
    tasks=query("SELECT * FROM tasks WHERE project_id=? AND status!='Done'",(pid,))
    vis=query("SELECT * FROM visibility_runs WHERE project_id=? ORDER BY tested_at DESC",(pid,))
    gsc_rows=query("SELECT * FROM gsc_rows WHERE project_id=?",(pid,))
    gsc_df=pd.DataFrame([dict(r) for r in gsc_rows]) if gsc_rows else pd.DataFrame()
    st.markdown('<div class="ogs-eyebrow">Organic growth workspace</div><div class="ogs-heading">Good morning, let’s grow your visibility.</div><div class="ogs-sub">Your search performance, AI visibility and next best actions — all in one place.</div>',unsafe_allow_html=True)
    left,right=st.columns([1.2,.8],gap="large")
    with left:
        st.markdown(f'<div class="ogs-hero"><div class="ogs-eyebrow">Start with your website</div><h2>Find out what’s holding your website back.</h2><p>Get a guided review of technical SEO, content opportunities and AI search readiness. No SEO expertise required.</p><p style="margin-top:12px"><b>{safe_project_domain}</b></p></div>',unsafe_allow_html=True)
        if st.button("＋ Run new audit",type="primary",use_container_width=True):
            st.session_state["jump_page"]="Website audit"
            st.rerun()
    with right:
        if audit:
            score=int(audit["score"]); score_label=f"{score}/100"; pages_count=len(audit["pages"]); issue_count=len(audit["findings"])
            p1=sum(1 for f in audit["findings"] if f.get("priority")=="P1")
            st.markdown('<div class="ogs-card-title">Website health</div><div class="ogs-muted">Latest saved diagnostic · heuristic, not a Google score</div>',unsafe_allow_html=True)
            st.metric("Diagnostic score",score_label)
            st.progress(max(0,min(score,100))/100)
            st.caption(f"{pages_count} pages audited · {issue_count} findings · {p1} high-priority findings")
        else:
            st.markdown('<div class="ogs-card-title">Website health</div><div class="ogs-muted">Your score appears after the first real crawl.</div>',unsafe_allow_html=True)
            st.info("No audit yet. Run an audit to calculate a score from detected issues.")
    st.markdown("### Your growth snapshot")
    a,b,c,d=st.columns(4)
    a.metric("Diagnostic score",f'{audit["score"]}/100' if audit else "—")
    b.metric("Pages checked",len(audit["pages"]) if audit else 0)
    c.metric("Issues to review",len(audit["findings"]) if audit else 0,help="Findings from the latest saved crawl")
    d.metric("AI observations",len(vis))
    st.markdown("### Recommended next steps")
    steps=[]
    if not audit: steps.append(("Run your first website audit","Check important technical SEO signals using a real crawl.","Website audit"))
    elif audit["findings"]: steps.append(("Review your SEO findings",f'{len(audit["findings"])} findings from the latest crawl need human review.',"Website audit"))
    if gsc_df.empty: steps.append(("Import Search Console data","Find queries and pages already earning search visibility.","Search performance"))
    if not vis: steps.append(("Start AI visibility tracking","Test buyer prompts on AI platforms and record the actual responses.","AI visibility"))
    steps.append(("Work through your action plan","Track fixes and verify them with a follow-up audit.","Action center"))
    for idx,(title,desc,dest) in enumerate(steps):
        with st.container(border=True):
            col1,col2=st.columns([4,1])
            col1.markdown(f'<div class="ogs-card-title">{html.escape(title)}</div><div class="ogs-muted">{html.escape(desc)}</div>',unsafe_allow_html=True)
            if col2.button("Open →",key=f"overview_step_{idx}",use_container_width=True):
                st.session_state["jump_page"]=dest
                st.rerun()
    st.caption("Only saved crawl and imported/recorded project data are shown. Diagnostic scores are heuristic and do not guarantee rankings, traffic or AI citations.")

elif page=="Website audit":
    st.markdown('<div class="ogs-eyebrow">Technical SEO</div><div class="ogs-heading">Website audit</div><div class="ogs-sub">Find technical and on-page issues, see evidence, and understand how to fix them.</div>',unsafe_allow_html=True)
    st.write("Scan pages you own or are authorized to assess. We respect robots.txt, limit request rates and do not bypass access controls.")
    with st.form("audit_form"):
        audit_url=st.text_input("Website URL",value=project["domain"])
        max_pages=st.slider("Maximum HTML pages",5,100,25,5)
        delay=st.slider("Delay between requests (seconds)",0.5,5.0,1.0,0.5)
        run=st.form_submit_button("Run website audit",type="primary")
    if run:
        with st.spinner("Crawling pages and analyzing SEO signals…"):
            try:
                result=crawl_site(audit_url,max_pages,delay)
                if not result["pages"]: st.warning("No HTML pages were successfully audited. Check the URL, robots.txt and crawl notes.")
                else:
                    save_audit(result); st.session_state["last_result"]=result
                    st.success(f"Audit complete: {len(result['pages'])} pages analyzed.")
            except Exception as e: st.error(str(e))
    audit=latest_audit(pid)
    if audit:
        st.divider()
        a,b,c,d=st.columns(4)
        a.metric("Diagnostic score",f'{audit["score"]}/100')
        b.metric("Pages audited",len(audit["pages"]))
        c.metric("Total findings",len(audit["findings"]))
        d.metric("P1 findings",sum(1 for f in audit["findings"] if f["priority"]=="P1"))
        st.caption("Heuristic score: it is not a Google metric or ranking forecast.")
        tabs=st.tabs(["Summary","SEO findings","Page audit","Crawl notes"])
        with tabs[0]:
            counts=pd.Series([f["priority"] for f in audit["findings"]]).value_counts().to_dict()
            st.write("Findings by priority",counts or "No findings")
            st.write("Recommended workflow: validate critical pages, confirm indexing intent, fix high-impact issues, then measure with Search Console.")
        with tabs[1]:
            df=pd.DataFrame(audit["findings"])
            if len(df):
                pri=st.multiselect("Filter priority",["P1","P2","P3"],default=["P1","P2","P3"])
                st.dataframe(df[df.priority.isin(pri)],use_container_width=True,hide_index=True)
                report_download("Download findings CSV",df,"seo-findings.csv")
            else: st.success("No findings generated by the current checks.")
        with tabs[2]:
            df=pd.DataFrame([{k:v for k,v in p.items() if k not in ("links","headers","text_excerpt")} for p in audit["pages"]])
            st.dataframe(df,use_container_width=True,hide_index=True)
            report_download("Download page audit CSV",df,"page-audit.csv")
        with tabs[3]:
            st.write("The crawler records inaccessible pages and non-HTML skips in page errors; robots.txt exclusions are not currently persisted separately in this version.")
    else: st.info("Run an audit to populate this section.")

elif page=="AI recommendations":
    st.markdown('<div class="ogs-eyebrow">AI-assisted analysis</div><div class="ogs-heading">AI recommendations</div><div class="ogs-sub">Contextual suggestions grounded in your crawl evidence and business goals.</div>',unsafe_allow_html=True)
    st.write("Use a language model to explain audit evidence and draft suggestions grounded in your business context.")
    if not audit: st.warning("Run a website audit first.")
    else:
        business=st.text_input("Business type",value=project["business_type"] or "",placeholder="B2B SaaS")
        target=st.text_input("Target customer",value=project["target_customer"] or "",placeholder="IT leaders at mid-market companies")
        offer=st.text_input("Primary offer",value=project["primary_offer"] or "",placeholder="Workflow automation platform")
        scope=st.selectbox("Analysis focus",["Prioritized SEO action plan","Content and metadata improvements","Technical SEO explanations","AI-answer readiness and content clarity"])
        if st.button("Generate AI analysis",type="primary"):
            with st.spinner("Analyzing audit evidence…"):
                try:
                    findings=audit["findings"][:40]
                    pages=[{k:p.get(k) for k in ("url","title","description","h1","words","jsonld_types","text_excerpt")} for p in audit["pages"][:15]]
                    prompt={"business_type":business,"target_customer":target,"primary_offer":offer,"focus":scope,"findings":findings,"pages":pages}
                    response=openai_call("You are a careful senior technical SEO and organic growth analyst. Use only provided evidence; clearly label hypotheses. Never claim guaranteed rankings or AI citations. Prioritize by impact, confidence and effort. Return readable Markdown with: executive summary, top 5 actions (evidence, why it matters, recommended fix, validation method, confidence), content opportunities, risks/unknowns. Do not invent search volume, competitors or performance metrics.",json.dumps(prompt,ensure_ascii=False))
                    execute("INSERT INTO ai_reports(project_id,created_at,report_type,input_hash,content) VALUES(?,?,?,?,?)",(pid,now(),scope,hashlib.sha256(json.dumps(prompt,sort_keys=True).encode()).hexdigest(),response))
                    st.session_state["ai_response"]=response
                except Exception as e: st.error(str(e))
        if st.session_state.get("ai_response"):
            st.markdown(st.session_state["ai_response"])
            st.download_button("Download AI analysis",st.session_state["ai_response"],"ai-seo-analysis.md",mime="text/markdown")

elif page=="Search performance":
    st.markdown('<div class="ogs-eyebrow">Google Search Console</div><div class="ogs-heading">Search performance</div><div class="ogs-sub">Understand which queries and pages earn impressions and clicks.</div>',unsafe_allow_html=True)
    st.write("Import a CSV export from Google Search Console → Performance. This import does not connect to Google automatically.")
    with st.expander("How to export data"):
        st.markdown("In Search Console, open **Performance → Search results**, choose a date range, export the table as CSV, then upload it below. Export query and page tables separately if you want both views.")
    upload=st.file_uploader("Upload Search Console CSV",type=["csv"],key="gsc_upload")
    if upload:
        try:
            raw=pd.read_csv(upload)
            raw.columns=[str(x).strip().lower() for x in raw.columns]
            aliases={"top queries":"query","top pages":"page","click-through rate":"ctr","position":"position","clicks":"clicks","impressions":"impressions","query":"query","page":"page"}
            raw=raw.rename(columns={c:aliases[c] for c in raw.columns if c in aliases})
            if "clicks" not in raw or "impressions" not in raw: st.error("CSV must include Clicks and Impressions columns.")
            else:
                for col in ("clicks","impressions","ctr","position"):
                    if col not in raw: raw[col]=0
                    raw[col]=pd.to_numeric(raw[col].astype(str).str.replace("%","",regex=False),errors="coerce").fillna(0)
                if raw["ctr"].max()>1: raw["ctr"]=raw["ctr"]/100
                if "query" not in raw: raw["query"]=""
                if "page" not in raw: raw["page"]=""
                st.dataframe(raw.head(100),use_container_width=True,hide_index=True)
                if st.button("Save imported data to project"):
                    execute("DELETE FROM gsc_rows WHERE project_id=?",(pid,))
                    for _,r in raw.iterrows():
                        execute("INSERT INTO gsc_rows(project_id,imported_at,query,page,clicks,impressions,ctr,position) VALUES(?,?,?,?,?,?,?,?)",
                          (pid,now(),str(r.get("query","")),str(r.get("page","")),float(r.clicks),float(r.impressions),float(r.ctr),float(r.position)))
                    st.success(f"Imported {len(raw)} rows.")
        except Exception as e: st.error(f"Could not read CSV: {e}")
    rows=query("SELECT * FROM gsc_rows WHERE project_id=?",(pid,))
    if rows:
        df=pd.DataFrame([dict(r) for r in rows])
        a,b,c=st.columns(3); a.metric("Clicks",f'{df.clicks.sum():,.0f}'); b.metric("Impressions",f'{df.impressions.sum():,.0f}'); c.metric("Weighted CTR",f'{df.clicks.sum()/df.impressions.sum():.2%}' if df.impressions.sum() else "—")
        if df.query.astype(str).str.len().gt(0).any():
            q=df[df["query"].astype(str).str.len()>0].groupby("query",as_index=False).agg(clicks=("clicks","sum"),impressions=("impressions","sum"),position=("position","mean"))
            q["ctr"]=q.clicks/q.impressions.replace(0,pd.NA)
            st.subheader("Query opportunities")
            st.dataframe(q.sort_values(["impressions","clicks"],ascending=False),use_container_width=True,hide_index=True)
            report_download("Export query analysis",q,"query-opportunities.csv")
        report_download("Export imported data",df,"search-performance.csv")
    else: st.info("No Search Console data saved yet.")

elif page=="AI visibility":
    st.markdown('<div class="ogs-eyebrow">Answer engine optimization</div><div class="ogs-heading">AI visibility</div><div class="ogs-sub">Track whether your brand appears in AI answers to the buyer questions that matter.</div>',unsafe_allow_html=True)
    st.write("Record repeatable tests in AI answer platforms. This feature stores observations you actually make; it does not automatically query ChatGPT, Gemini or Perplexity.")
    with st.form("vis_form"):
        tested=st.date_input("Test date",value=datetime.now().date())
        platform=st.selectbox("Platform",["ChatGPT","Google AI Overviews","Gemini","Perplexity","Claude","Other"])
        prompt=st.text_area("Exact buyer prompt tested",placeholder="What are the best workflow automation tools for a 200-person company?")
        mentioned=st.selectbox("Was your brand mentioned?",["No","Yes"])
        cited=st.text_input("Cited URL (if any)",placeholder=project["domain"])
        competitors=st.text_input("Competitors mentioned",placeholder="Competitor A, Competitor B")
        sentiment=st.selectbox("Brand sentiment",["Positive","Neutral","Negative","Mixed","Not applicable","Unknown"])
        notes=st.text_area("Notes / evidence",placeholder="Paste short observation, response link or context. Avoid sensitive data.")
        save=st.form_submit_button("Save observation",type="primary")
    if save:
        if not prompt.strip(): st.error("Enter the exact prompt you tested.")
        else:
            execute("INSERT INTO visibility_runs(project_id,tested_at,platform,prompt,brand_mentioned,cited_url,competitors,sentiment,notes) VALUES(?,?,?,?,?,?,?,?,?)",
              (pid,tested.isoformat(),platform,prompt.strip(),1 if mentioned=="Yes" else 0,cited.strip(),competitors.strip(),sentiment,notes.strip()))
            st.success("Observation saved.")
    rows=query("SELECT * FROM visibility_runs WHERE project_id=? ORDER BY tested_at DESC",(pid,))
    if rows:
        df=pd.DataFrame([dict(r) for r in rows])
        a,b,c=st.columns(3); a.metric("Tests recorded",len(df)); b.metric("Mention rate",f'{df.brand_mentioned.mean():.1%}'); c.metric("With citation",int(df.cited_url.astype(str).str.len().gt(0).sum()))
        st.dataframe(df,use_container_width=True,hide_index=True)
        report_download("Export AI visibility history",df,"ai-visibility-history.csv")
        st.download_button("Download prompt tracking template",pd.DataFrame([{"platform":"ChatGPT","prompt":"What are the best [category] tools for [buyer]?"},{"platform":"Perplexity","prompt":"Compare leading [category] providers for [use case]."},{"platform":"Gemini","prompt":"Which [category] solution suits [buyer constraints]?"}]).to_csv(index=False).encode("utf-8-sig"),"ai-visibility-prompt-template.csv","text/csv")
    else: st.info("No AI visibility observations yet. Start with 5–10 buyer prompts and rerun them on a consistent schedule.")

elif page=="Competitors":
    st.markdown('<div class="ogs-eyebrow">Competitive intelligence</div><div class="ogs-heading">Competitor insights</div><div class="ogs-sub">Compare public on-page signals against selected competitors.</div>',unsafe_allow_html=True)
    st.write("This version can audit competitor URLs you provide and compare on-page signals. It does not provide third-party keyword volumes, backlink databases or automatic AI citation data.")
    try: competitors=json.loads(project["competitors"] or "[]")
    except Exception: competitors=[]
    comptext=st.text_area("Competitor URLs (one per line)",value="\n".join([x if x.startswith("http") else "https://"+x for x in competitors]),placeholder="https://competitor.example")
    if st.button("Audit competitor homepages"):
        urls=[normalize_url(x) for x in comptext.splitlines() if x.strip()]
        result=[]
        for u in urls[:5]:
            ok,msg=validate_public_url(u)
            if not ok: result.append({"url":u,"error":msg}); continue
            try:
                f=fetch_html(u)
                if "html" in f:
                    p=parse_page(u,f["html"],f["status"],f.get("headers"))
                    result.append({k:p.get(k) for k in ("url","status","title","description","h1_count","words","images","alt_missing","jsonld_types","internal_links")})
                else: result.append({"url":u,"status":f.get("status"),"error":"Redirect or non-HTML response; inspect manually."})
            except Exception as e: result.append({"url":u,"error":str(e)})
        if result: st.dataframe(pd.DataFrame(result),use_container_width=True,hide_index=True)
    st.caption("Only audit competitor sites for publicly accessible information and within applicable terms. Avoid treating homepage signals as a full competitive analysis.")

elif page=="Action center":
    st.markdown('<div class="ogs-eyebrow">Execution</div><div class="ogs-heading">Growth action plan</div><div class="ogs-sub">Turn findings into tasks, assign status and verify fixes.</div>',unsafe_allow_html=True)
    st.write("Tasks are seeded from audit findings. Review the evidence before implementing any change.")
    rows=query("SELECT * FROM tasks WHERE project_id=? ORDER BY CASE priority WHEN 'P1' THEN 1 WHEN 'P2' THEN 2 ELSE 3 END,created_at DESC",(pid,))
    if rows:
        df=pd.DataFrame([dict(r) for r in rows])
        status_filter=st.multiselect("Filter status",["Open","In progress","Blocked","Done"],default=["Open","In progress","Blocked"])
        shown=df[df.status.isin(status_filter)]
        st.dataframe(shown[["priority","title","category","url","evidence","recommendation","status"]],use_container_width=True,hide_index=True)
        with st.form("update_task"):
            task_ids={f'{r["id"]} · {r["title"]}':r["id"] for r in rows}
            selected=st.selectbox("Task to update",list(task_ids.keys()))
            new_status=st.selectbox("New status",["Open","In progress","Blocked","Done"])
            due=st.text_input("Due date (optional, YYYY-MM-DD)")
            update=st.form_submit_button("Update task")
        if update:
            execute("UPDATE tasks SET status=?,due_date=? WHERE id=? AND project_id=?",(new_status,due,task_ids[selected],pid))
            st.success("Task updated."); st.rerun()
        report_download("Export action plan",df,"growth-action-plan.csv")
    else: st.info("Run an audit to generate initial action items.")

elif page=="Reports":
    st.markdown('<div class="ogs-eyebrow">Reporting</div><div class="ogs-heading">Reports & history</div><div class="ogs-sub">Share clear progress and next steps with stakeholders.</div>',unsafe_allow_html=True)
    audits=query("SELECT * FROM audits WHERE project_id=? ORDER BY created_at DESC",(pid,))
    if audits:
        hist=pd.DataFrame([{"date":r["created_at"],"score":r["score"],"pages":r["pages"],"findings":len(json.loads(r["findings_json"]))} for r in audits])
        st.subheader("Audit history"); st.dataframe(hist,use_container_width=True,hide_index=True)
        st.line_chart(hist.set_index("date")["score"])
    else: st.info("No audit history yet.")
    reports=query("SELECT * FROM ai_reports WHERE project_id=? ORDER BY created_at DESC",(pid,))
    for r in reports[:10]:
        with st.expander(f'{r["created_at"][:19]} · {r["report_type"]}'):
            st.markdown(r["content"])
            st.download_button("Download report",r["content"],f'ai-report-{r["id"]}.md',mime="text/markdown",key=f'report_{r["id"]}')

elif page=="Settings":
    st.title("Project settings")
    st.write("Manage your project details and integrations.")
    with st.form("project_settings"):
        name=st.text_input("Project name",value=project["name"])
        domain=st.text_input("Website URL",value=project["domain"])
        btype=st.text_input("Business type",value=project["business_type"] or "")
        target=st.text_input("Target customer",value=project["target_customer"] or "")
        offer=st.text_input("Primary offer",value=project["primary_offer"] or "")
        comp=st.text_area("Competitor domains, one per line",value="\n".join(json.loads(project["competitors"] or "[]")))
        save=st.form_submit_button("Save project settings")
    if save:
        url=normalize_url(domain); ok,msg=validate_public_url(url)
        if not ok: st.error(msg)
        else:
            execute("UPDATE projects SET name=?,domain=?,business_type=?,target_customer=?,primary_offer=?,competitors=? WHERE id=? AND user_id=?",
             (name.strip(),url,btype,target,offer,json.dumps([x.strip() for x in comp.splitlines() if x.strip()]),pid,uid))
            st.success("Project updated."); st.rerun()
    st.divider()
    st.subheader("AI integration")
    if st.secrets.get("OPENAI_API_KEY",os.getenv("OPENAI_API_KEY","")):
        st.success("OpenAI API key detected. AI usage may incur separate charges.")
    else:
        st.warning("OpenAI API key not detected. Add OPENAI_API_KEY to Streamlit Secrets to enable AI recommendations.")
        st.code('OPENAI_API_KEY = "your-api-key"\nOPENAI_MODEL = "gpt-4.1-mini"',language="toml")
    st.subheader("Subscription and billing")
    st.info("Billing UI is not a payment processor. Configure Stripe checkout, webhooks, pricing and tax/legal policies before charging customers. This build does not activate paid subscriptions.")
    sub=query("SELECT * FROM subscriptions WHERE user_id=?",(uid,))
    if sub: st.write(f'Plan: **{sub[0]["plan"]}** · Status: {sub[0]["status"]}')
    st.subheader("Hosting and data")
    st.warning("Streamlit Community Cloud local files may not be durable across restarts/redeploys. For real multi-client commercial use, move SQLite to managed PostgreSQL, add email verification/password reset, rate limits, backups, audit logs and secure account recovery.")
    st.caption("Scheduled scans and email notifications require a persistent worker/scheduler and configured mail provider; they are not run automatically by this Streamlit app.")
