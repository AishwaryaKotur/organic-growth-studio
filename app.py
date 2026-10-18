import io, ipaddress, socket, time, re
from collections import deque
from urllib.parse import urljoin, urlparse, urldefrag, urlunparse
from urllib.robotparser import RobotFileParser
import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup

APP="Organic Growth Studio"
UA="OrganicGrowthStudioAudit/1.0 (+authorized SEO audit; respects robots.txt)"
TIMEOUT=12
st.set_page_config(page_title=APP,page_icon="↗",layout="wide")

def norm(u):
    u,_=urldefrag(u.strip()); p=urlparse(u)
    if p.scheme not in ("http","https") or not p.hostname or p.username or p.password: return None
    return urlunparse((p.scheme.lower(),p.netloc.lower(),p.path or "/", "",p.query,""))
def public_host(host):
    try:
        ips={x[4][0] for x in socket.getaddrinfo(host,None)}
        return bool(ips) and all(ipaddress.ip_address(x).is_global for x in ips)
    except Exception: return False
def valid(u):
    p=urlparse(u)
    if p.scheme not in ("http","https") or not p.hostname: return False,"Enter a valid public http(s) URL."
    if not public_host(p.hostname): return False,"Private/local IP targets are blocked."
    return True,""
def robots_for(origin):
    rp=RobotFileParser()
    try:
        r=requests.get(urljoin(origin,"/robots.txt"),headers={"User-Agent":UA},timeout=TIMEOUT,allow_redirects=True)
        rp.parse(r.text.splitlines() if r.status_code<400 else ["User-agent: *","Allow: /"])
    except Exception: rp.parse(["User-agent: *","Disallow: /"])
    return rp
def fetch(u):
    ok,msg=valid(u)
    if not ok:return None,msg
    try:
        r=requests.get(u,headers={"User-Agent":UA},timeout=TIMEOUT,allow_redirects=True,stream=True)
        final=norm(r.url)
        if not final or not valid(final)[0]: r.close(); return None,"Unsafe/unsupported redirect target."
        ctype=r.headers.get("Content-Type","").lower(); status=r.status_code; headers=dict(r.headers)
        if "text/html" not in ctype and "application/xhtml+xml" not in ctype:
            r.close(); return {"status":status,"url":final,"headers":headers,"html":"","type":ctype},None
        chunks=[]; total=0
        for ch in r.iter_content(16384):
            if not ch: continue
            total+=len(ch)
            if total>2_000_000: break
            chunks.append(ch)
        r.close()
        return {"status":status,"url":final,"headers":headers,"html":b"".join(chunks).decode(r.encoding or "utf-8",errors="replace"),"type":ctype},None
    except requests.RequestException as e:return None,"Request failed: "+type(e).__name__
def same(a,b):
    x,y=urlparse(a),urlparse(b); return x.scheme==y.scheme and x.netloc.lower()==y.netloc.lower()
def parse_page(requested,res):
    s=BeautifulSoup(res["html"],"html.parser")
    title=s.title.get_text(" ",strip=True) if s.title else ""
    md=s.find("meta",attrs={"name":re.compile("^description$",re.I)})
    desc=(md.get("content") or "").strip() if md else ""
    can=s.find("link",rel=lambda x:x and "canonical" in [v.lower() for v in (x if isinstance(x,list) else [x])])
    canonical=norm(urljoin(res["url"],can.get("href",""))) if can and can.get("href") else ""
    h1=[x.get_text(" ",strip=True) for x in s.find_all("h1")]
    robots=" ".join((x.get("content") or "") for x in s.find_all("meta",attrs={"name":re.compile("^robots$",re.I)})).lower()
    noindex="noindex" in robots or "noindex" in res["headers"].get("X-Robots-Tag","").lower()
    imgs=s.find_all("img"); missing=sum(1 for x in imgs if x.get("alt") is None or not x.get("alt","").strip())
    links=[]
    for a in s.find_all("a",href=True):
        u=norm(urljoin(res["url"],a["href"]))
        if u:links.append((u,a.get_text(" ",strip=True)[:100]))
    words=re.findall(r"\b[\w'-]+\b",s.get_text(" ",strip=True))
    return {"Requested URL":requested,"Final URL":res["url"],"HTTP Status":res["status"],"Content Type":res["type"],
    "Title":title,"Title Length":len(title),"Meta Description":desc,"Description Length":len(desc),
    "H1 Count":len(h1),"H1 Text":" | ".join(h1[:3]),"Canonical":canonical,"Noindex":noindex,
    "Word Count (rough)":len(words),"H2 Count":len(s.find_all("h2")),"Images":len(imgs),
    "Images Missing Alt":missing,"JSON-LD Blocks":len(s.find_all("script",attrs={"type":re.compile("application/ld\\+json",re.I)})),
    "Internal Links":sum(same(res["url"],u) for u,_ in links),"External Links":sum(not same(res["url"],u) for u,_ in links),"_links":links}
def findings(row):
    out=[]; url=row["Final URL"]
    def add(p,i,e,a,impact,effort="Low"):out.append({"Priority":p,"URL":url,"Issue":i,"Evidence":e,"Recommended Action":a,"Potential Impact":impact,"Effort":effort})
    if row["HTTP Status"]>=400:add("P1","Page returns error status",f"HTTP {row['HTTP Status']}","Confirm whether URL should exist; fix or redirect to the closest relevant replacement.","Users and crawlers may not access the page.","Medium")
    if not row["Title"]:add("P1","Missing title tag","No <title> element detected.","Add a unique, descriptive title reflecting page intent.","Page identification in search results may be weaker.")
    elif row["Title Length"]<15 or row["Title Length"]>60:add("P2","Review title length",f"{row['Title Length']} characters.","Review clarity and usefulness; character count is a heuristic, not a Google limit.","Title may be unclear or truncated.")
    if not row["Meta Description"]:add("P2","Missing meta description","No description detected.","Add a useful, page-specific summary; search engines may still generate their own snippet.","Less control over search-result messaging.")
    elif row["Description Length"]<50 or row["Description Length"]>170:add("P3","Review meta description",f"{row['Description Length']} characters.","Check uniqueness and usefulness; length is only a guideline.","Snippet may be rewritten.")
    if row["H1 Count"]==0:add("P2","No H1 detected","No <h1> element found.","Add a clear primary heading if useful for page structure/accessibility.","Page purpose may be less clear.")
    elif row["H1 Count"]>1:add("P3","Multiple H1 headings",f"{row['H1 Count']} found.","Review heading hierarchy; multiple H1s are not automatically a ranking error.","Structure may be harder to scan.")
    if row["Noindex"]:add("P1","Noindex directive present","Robots meta or X-Robots-Tag includes noindex.","Confirm exclusion is intentional; remove only if indexing is desired.","Page may be excluded from search.")
    if not row["Canonical"]:add("P2","No canonical detected","No canonical link element found.","Assess duplicate URL risk and add an appropriate canonical when useful.","Duplicate URL signals may be less explicit.")
    if row["Images Missing Alt"]:add("P2","Images missing alt attributes",f"{row['Images Missing Alt']} of {row['Images']} images have blank/missing alt.","Describe informative images; use empty alt for decorative images. Avoid keyword stuffing.","Accessibility and image context may be weaker.")
    if row["Word Count (rough)"]<100:add("P3","Very little extractable text",f"About {row['Word Count (rough)']} words.","Check if the page answers its intended need; don't add text just to hit a word count.","Value proposition may be under-explained.","Medium")
    return out
def score(df):
    if df.empty:return 0
    vals=[]
    for _,r in df.iterrows():
        x=100
        if not r["Title"]:x-=10
        if not r["Meta Description"]:x-=5
        if r["H1 Count"]==0:x-=5
        if r["Noindex"]:x-=8
        if r["HTTP Status"]>=400:x-=15
        x-=min(5,r["Images Missing Alt"])
        vals.append(max(0,x))
    return round(sum(vals)/len(vals))
def aeo_checklist(site):
    return pd.DataFrame([
      {"Area":"AI crawler access","Check":"Review robots.txt and relevant platform crawler documentation","Status":"Needs manual verification","Evidence / notes":""},
      {"Area":"Brand/entity clarity","Check":"Company name, product description, category, locations and official profiles are consistent","Status":"Needs manual verification","Evidence / notes":""},
      {"Area":"Answer-ready content","Check":"Priority pages directly answer specific buyer questions with accurate, useful explanations","Status":"Needs manual verification","Evidence / notes":""},
      {"Area":"Source transparency","Check":"Authors, expertise, sources, dates and claims are clear where appropriate","Status":"Needs manual verification","Evidence / notes":""},
      {"Area":"Structured data","Check":"Relevant structured data is accurate and matches visible page content","Status":"Needs manual verification","Evidence / notes":""},
      {"Area":"Third-party corroboration","Check":"Important facts are consistent across credible, relevant external sources","Status":"Needs manual verification","Evidence / notes":""},
      {"Area":"AI answer baseline","Check":"Run a fixed set of buyer prompts on selected answer engines and record citations/mentions","Status":"Not yet tested","Evidence / notes":""},
      {"Area":"Lead path","Check":"Pages cited or likely to be discovered provide a clear next step and trackable conversion","Status":"Needs manual verification","Evidence / notes":""},
    ])

def excel(pages,finds,summary,aeo):
    b=io.BytesIO()
    with pd.ExcelWriter(b,engine="openpyxl") as w:
        summary.to_excel(w,sheet_name="Summary",index=False)
        pages.drop(columns=["_links"],errors="ignore").to_excel(w,sheet_name="Page Audit",index=False)
        finds.to_excel(w,sheet_name="SEO Findings",index=False)
        aeo.to_excel(w,sheet_name="AEO Checklist",index=False)
    return b.getvalue()

st.markdown("""<style>.block-container{padding-top:1.5rem;max-width:1400px}.hero{padding:1.4rem;border:1px solid rgba(120,120,120,.3);border-radius:18px;margin-bottom:1rem}.eyebrow{text-transform:uppercase;letter-spacing:.12em;font-size:.72rem;opacity:.7;font-weight:700}</style><div class="hero"><div class="eyebrow">SEO · AEO · Organic growth</div><h1 style="margin:.35rem 0">Organic Growth Studio</h1><p style="font-size:1.08rem;margin:0">Improve traditional search visibility, answer-engine readiness, and the path from discovery to qualified leads.</p></div>""",unsafe_allow_html=True)
with st.sidebar:
    st.header("Audit settings")
    site=st.text_input("Website URL",placeholder="https://example.com")
    cap=st.slider("Maximum HTML pages",5,100,25,5)
    delay=st.slider("Delay between requests (seconds)",0.5,3.0,1.0,0.5)
    st.caption("Audit only sites you own or are authorized to assess. Checks robots.txt and uses a conservative crawl rate.")
    run=st.button("Run website audit",type="primary",use_container_width=True)
    st.divider();st.caption("V1 checks page metadata, headings, canonicals, noindex, image alt, text volume, status and link counts.")
st.markdown("### A practical first version")
st.write("Crawls a limited number of same-site HTML pages, checks common SEO signals, and exports an Excel report with an AEO readiness checklist. AEO checks require human review and repeatable prompt testing; this is not a ranking or citation predictor.")
if run:
    u=norm(site if site.startswith(("http://","https://")) else "https://"+site)
    if not u:st.error("Enter a valid public website URL.");st.stop()
    ok,msg=valid(u)
    if not ok:st.error(msg);st.stop()
    p=urlparse(u);origin=f"{p.scheme}://{p.netloc}";rp=robots_for(origin)
    q=deque([u]);seen=set();rows=[];errs=[];skips=[]
    prog=st.progress(0,text="Preparing crawl…");status=st.empty()
    while q and len(rows)<cap:
        cur=q.popleft()
        if cur in seen:continue
        seen.add(cur)
        if not same(u,cur):continue
        if not rp.can_fetch(UA,cur):skips.append({"URL":cur,"Reason":"Disallowed by robots.txt"});continue
        status.write(f"Crawling {len(rows)+1}/{cap}: {cur}")
        res,err=fetch(cur)
        if err:errs.append({"URL":cur,"Error":err});continue
        if not res:continue
        if "text/html" not in res["type"] and "application/xhtml+xml" not in res["type"]:
            errs.append({"URL":cur,"Error":"Skipped non-HTML response: "+res["type"]});continue
        row=parse_page(cur,res);rows.append(row)
        for link,_ in row["_links"]:
            if same(u,link) and link not in seen and len(seen)<cap*10 and link not in q:q.append(link)
        prog.progress(min(len(rows)/cap,1),text=f"Collected {len(rows)} HTML pages")
        time.sleep(delay)
    prog.empty();status.empty()
    if not rows:
        st.error("No HTML pages audited. Check the URL, robots.txt, connectivity, or whether the site requires JavaScript rendering.")
        if errs:st.dataframe(pd.DataFrame(errs),use_container_width=True)
        st.stop()
    pages=pd.DataFrame(rows);allf=[]
    for row in rows:allf.extend(findings(row))
    fcols=["Priority","URL","Issue","Evidence","Recommended Action","Potential Impact","Effort"]
    fdf=pd.DataFrame(allf,columns=fcols)
    if not fdf.empty:
        fdf["_n"]=fdf.Priority.map({"P1":0,"P2":1,"P3":2});fdf=fdf.sort_values(["_n","Issue"]).drop(columns="_n")
    summary=pd.DataFrame([
    {"Metric":"Pages audited","Value":len(pages),"Notes":"Limited to configured same-site HTML page cap."},
    {"Metric":"Diagnostic score","Value":score(pages),"Notes":"Heuristic only; not a Google metric or ranking forecast."},
    {"Metric":"Pages with HTTP errors","Value":int((pages["HTTP Status"]>=400).sum()),"Notes":"Confirm whether errors are expected or broken URLs."},
    {"Metric":"Missing title tags","Value":int((pages.Title.fillna("")=="").sum()),"Notes":"Prioritize important pages."},
    {"Metric":"Missing meta descriptions","Value":int((pages["Meta Description"].fillna("")=="").sum()),"Notes":"Descriptions are not a direct ranking guarantee."},
    {"Metric":"Pages with noindex","Value":int(pages.Noindex.sum()),"Notes":"Confirm exclusion is intentional."},
    {"Metric":"Findings generated","Value":len(fdf),"Notes":"Validate every finding before implementation."}])
    st.session_state["audit"]={"pages":pages,"findings":fdf,"summary":summary,"aeo":aeo_checklist(u),"errors":pd.DataFrame(errs),"skips":pd.DataFrame(skips),"site":u}
if "audit" in st.session_state:
    a=st.session_state["audit"];pages=a["pages"];fdf=a["findings"]
    st.divider();st.markdown(f"## Results: `{a['site']}`")
    c1,c2,c3,c4=st.columns(4);c1.metric("Pages audited",len(pages));c2.metric("Diagnostic score",f"{score(pages)}/100")
    c3.metric("P1 findings",int((fdf.Priority=="P1").sum()) if not fdf.empty else 0);c4.metric("Total findings",len(fdf))
    st.info("Human review required. Confirm business impact, page intent and whether directives are intentional before changing a live site.")
    t1,t2,t3,t4,t5=st.tabs(["Summary","SEO findings","Page audit","AEO readiness","Crawl notes"])
    with t1:
        st.dataframe(a["summary"],use_container_width=True,hide_index=True)
        st.markdown("**Recommended workflow**");st.write("Validate P1 findings on business-critical pages, confirm indexing intent, fix high-impact issues first, then measure outcomes with Search Console and analytics.")
        if not fdf.empty:st.dataframe(fdf.head(12),use_container_width=True,hide_index=True)
    with t2:
        if fdf.empty:st.success("No findings triggered by these checks. This does not mean the site is fully optimized.")
        else:
            priorities=st.multiselect("Priority filter",["P1","P2","P3"],default=["P1","P2","P3"])
            st.dataframe(fdf[fdf.Priority.isin(priorities)],use_container_width=True,hide_index=True)
    with t3:st.dataframe(pages.drop(columns=["_links"],errors="ignore"),use_container_width=True,hide_index=True)
    with t4:
        st.markdown("### AEO readiness checklist")
        st.write("Use this checklist to assess whether the business is easy for answer engines to understand and reference. It is not an automated measurement of AI citations.")
        st.dataframe(a["aeo"],use_container_width=True,hide_index=True)
        st.markdown("### Prompt tracking method")
        st.write("Choose 10–20 real buyer questions, record the platform, date, exact prompt, whether the brand appears, cited URLs and competitors mentioned. Repeat the same prompts periodically; answers vary, so treat results as directional.")
        st.markdown("### Sample buyer prompts")
        st.write("- What are the best [category] tools for [company size/use case]?")
        st.write("- Compare [brand] with [competitor] for [specific use case].")
        st.write("- What should a buyer look for when choosing a [category] provider?")
        st.write("- How can a company solve [problem] and what solutions are available?")
    with t5:
        st.write("Robots.txt-disallowed URLs skipped:",len(a["skips"]))
        if not a["skips"].empty:st.dataframe(a["skips"],use_container_width=True,hide_index=True)
        st.write("Fetch errors / skipped resources:",len(a["errors"]))
        if not a["errors"].empty:st.dataframe(a["errors"],use_container_width=True,hide_index=True)
        st.caption("Not included yet: JS rendering, Search Console/GA4, backlinks, field Core Web Vitals, keyword clustering, automated AI-answer monitoring or citation verification.")
    st.download_button("Download audit report (.xlsx)",data=excel(pages,fdf,a["summary"],a["aeo"]),file_name="organic_growth_audit.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",type="primary")
else:
    c1,c2,c3=st.columns(3)
    c1.markdown("**SEO signals**");c1.write("HTTP status, titles, descriptions, headings, canonicals and image alt.")
    c2.markdown("**AEO readiness**");c2.write("Checklist for crawler access, answer-ready content, brand clarity and repeatable buyer-prompt tracking.")
    c3.markdown("**Actionable output**");c3.write("Prioritized SEO findings plus an AEO checklist in the downloadable report.")
    st.caption("Enter an authorized public website in the sidebar and select Run website audit.")
