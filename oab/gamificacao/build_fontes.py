import base64, hashlib, re, subprocess
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
def get(url): return subprocess.run(["curl","-sS","-A",UA,url],capture_output=True).stdout
css = get("https://fonts.googleapis.com/css2?family=Bodoni+Moda:opsz,wght@6..96,400;6..96,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap").decode()
fam_files = {}
for name, body in re.findall(r"/\*\s*([\w-]+)\s*\*/\s*@font-face\s*\{(.*?)\}", css, re.S):
    if name != "latin": continue
    fam = re.search(r"font-family:\s*'([^']+)'", body).group(1)
    url = re.search(r"url\(([^)]+)\)", body).group(1)
    fam_files.setdefault(fam, set()).add(url)
out = ["/* Subconjunto latin de Bodoni Moda, IBM Plex Sans e IBM Plex Mono (SIL Open Font License 1.1),",
       "   embutido como data URI porque o CSP dos artifacts bloqueia CDN de fontes. Gerado por build_fontes.py. */"]
ranges = {"Bodoni Moda": "400 700", "IBM Plex Sans": "400 600", "IBM Plex Mono": "500"}
for fam, urls in fam_files.items():
    datas = {hashlib.sha1(get(u)).hexdigest(): get(u) for u in urls}
    assert len(datas) == 1, (fam, len(datas))
    data = next(iter(datas.values()))
    b64 = base64.b64encode(data).decode()
    print(fam, len(data))
    out.append(f"@font-face{{font-family:'{fam}';font-style:normal;font-weight:{ranges[fam]};font-display:swap;\n  src:url(data:font/woff2;base64,{b64}) format('woff2');}}")
open("fontes.css","w").write("\n".join(out) + "\n")
