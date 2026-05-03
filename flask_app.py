from flask import Flask, request, jsonify, render_template_string
import os

app = Flask(__name__)

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DUMP_FILE = os.path.join(BASE_DIR, "dump.txt")

# ── Load dump.txt once at startup ─────────────────────────────
def load_dump(path):
    db = {}
    if not os.path.exists(path):
        return db
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if "|" not in line:
                continue
            parts = line.split("|")
            if len(parts) < 3:
                continue
            id_part   = parts[0].strip()
            name_part = "|".join(parts[2:]).strip()
            if id_part.isdigit():
                db[id_part] = name_part
    return db

DB = load_dump(DUMP_FILE)

# ── HTML Template ─────────────────────────────────────────────
HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>ZORO XD — ID Extractor</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@700;900&display=swap" rel="stylesheet"/>
<style>
  :root {
    --bg:      #050a0f;
    --panel:   #0a1520;
    --border:  #0ff3;
    --cyan:    #00ffe7;
    --pink:    #ff2d78;
    --yellow:  #ffe600;
    --text:    #c8e6f5;
    --dim:     #4a7a9b;
    --green:   #00ff99;
    --red:     #ff4455;
    --font:    'Share Tech Mono', monospace;
    --head:    'Orbitron', sans-serif;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--font);
    min-height: 100vh;
    overflow-x: hidden;
  }

  /* animated grid bg */
  body::before {
    content: '';
    position: fixed; inset: 0;
    background-image:
      linear-gradient(rgba(0,255,231,.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,255,231,.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
  }

  .wrap {
    position: relative; z-index: 1;
    max-width: 860px;
    margin: 0 auto;
    padding: 40px 20px 60px;
  }

  /* ── HEADER ── */
  header { text-align: center; margin-bottom: 48px; }

  .logo {
    font-family: var(--head);
    font-size: clamp(2rem, 8vw, 3.6rem);
    font-weight: 900;
    letter-spacing: .15em;
    background: linear-gradient(90deg, var(--cyan), var(--pink), var(--yellow));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: none;
    line-height: 1;
  }

  .logo-sub {
    font-family: var(--head);
    font-size: .7rem;
    letter-spacing: .4em;
    color: var(--dim);
    margin-top: 6px;
    text-transform: uppercase;
  }

  .scan-line {
    width: 100%; height: 2px;
    background: linear-gradient(90deg, transparent, var(--cyan), transparent);
    margin: 20px auto 0;
    animation: scanPulse 3s ease-in-out infinite;
  }
  @keyframes scanPulse {
    0%,100%{ opacity:.3; }
    50%     { opacity:1;  }
  }

  /* ── PANELS ── */
  .panels {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }
  @media(max-width:620px){ .panels{ grid-template-columns:1fr; } }

  .panel {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 20px;
    position: relative;
    overflow: hidden;
  }
  .panel::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--cyan), var(--pink));
  }

  .panel-label {
    font-family: var(--head);
    font-size: .6rem;
    letter-spacing: .3em;
    color: var(--dim);
    text-transform: uppercase;
    margin-bottom: 12px;
  }
  .panel-label span {
    color: var(--cyan);
  }

  textarea {
    width: 100%;
    height: 280px;
    background: #020810;
    border: 1px solid #0ff2;
    border-radius: 3px;
    color: var(--cyan);
    font-family: var(--font);
    font-size: .88rem;
    line-height: 1.7;
    padding: 12px;
    resize: vertical;
    outline: none;
    transition: border-color .2s;
    caret-color: var(--pink);
  }
  textarea:focus { border-color: var(--cyan); }
  textarea::placeholder { color: #1a3a4a; }

  #output {
    color: var(--green);
    cursor: default;
  }

  /* ── BUTTON ── */
  .btn-row {
    display: flex;
    justify-content: center;
    gap: 14px;
    margin-top: 24px;
    flex-wrap: wrap;
  }

  button {
    font-family: var(--head);
    font-size: .72rem;
    letter-spacing: .15em;
    padding: 13px 34px;
    border: none;
    border-radius: 3px;
    cursor: pointer;
    text-transform: uppercase;
    transition: all .2s;
    position: relative;
    overflow: hidden;
  }

  #extractBtn {
    background: linear-gradient(135deg, #004455, #006677);
    color: var(--cyan);
    border: 1px solid var(--cyan);
    box-shadow: 0 0 16px #00ffe740;
  }
  #extractBtn:hover {
    background: linear-gradient(135deg, #006677, #008899);
    box-shadow: 0 0 30px #00ffe770;
    transform: translateY(-1px);
  }
  #extractBtn:active { transform: translateY(0); }

  #copyBtn {
    background: transparent;
    color: var(--dim);
    border: 1px solid #0ff2;
  }
  #copyBtn:hover {
    color: var(--yellow);
    border-color: var(--yellow);
    box-shadow: 0 0 14px #ffe60030;
  }

  /* ── STATUS BAR ── */
  #statusBar {
    margin-top: 22px;
    font-size: .78rem;
    text-align: center;
    min-height: 20px;
    color: var(--dim);
    letter-spacing: .05em;
  }
  #statusBar.ok  { color: var(--green); }
  #statusBar.err { color: var(--red);   }

  /* ── STATS ROW ── */
  .stats {
    display: flex;
    justify-content: center;
    gap: 30px;
    margin-top: 16px;
    flex-wrap: wrap;
  }
  .stat {
    text-align: center;
    opacity: 0;
    transition: opacity .4s;
  }
  .stat.show { opacity: 1; }
  .stat-val {
    font-family: var(--head);
    font-size: 1.6rem;
    font-weight: 900;
    line-height: 1;
  }
  .stat-val.c { color: var(--cyan); }
  .stat-val.g { color: var(--green); }
  .stat-val.r { color: var(--red); }
  .stat-lbl {
    font-size: .6rem;
    letter-spacing: .2em;
    color: var(--dim);
    text-transform: uppercase;
    margin-top: 4px;
  }

  /* loading shimmer */
  @keyframes shimmer {
    0%  { opacity: .4; }
    50% { opacity: 1;  }
    100%{ opacity: .4; }
  }
  .loading { animation: shimmer .7s ease-in-out infinite; }

  /* footer */
  footer {
    text-align: center;
    margin-top: 50px;
    font-size: .65rem;
    letter-spacing: .2em;
    color: var(--dim);
  }
  footer a { color: var(--cyan); text-decoration: none; }
</style>
</head>
<body>
<div class="wrap">

  <header>
    <div class="logo">ZORO XD</div>
    <div class="logo-sub">ID Pair Name Extractor</div>
    <div class="scan-line"></div>
  </header>

  <div class="panels">
    <!-- INPUT -->
    <div class="panel">
      <div class="panel-label">▶ <span>INPUT</span> — ID Pairs</div>
      <textarea id="input" placeholder="Paste ID pairs here&#10;One pair per line&#10;&#10;Example:&#10;1000,1001&#10;1024,1025&#10;1100,1200"></textarea>
    </div>

    <!-- OUTPUT -->
    <div class="panel">
      <div class="panel-label">◀ <span>OUTPUT</span> — Names</div>
      <textarea id="output" readonly placeholder="Results will appear here…"></textarea>
    </div>
  </div>

  <div class="btn-row">
    <button id="extractBtn" onclick="extract()">⚡ Extract Names</button>
    <button id="copyBtn"    onclick="copyOutput()">⎘ Copy Output</button>
  </div>

  <div id="statusBar"></div>

  <div class="stats">
    <div class="stat" id="sPairs">
      <div class="stat-val c" id="vPairs">—</div>
      <div class="stat-lbl">Pairs</div>
    </div>
    <div class="stat" id="sFound">
      <div class="stat-val g" id="vFound">—</div>
      <div class="stat-lbl">Matched</div>
    </div>
    <div class="stat" id="sMissed">
      <div class="stat-val r" id="vMissed">—</div>
      <div class="stat-lbl">Missing</div>
    </div>
  </div>

  <footer>by <a href="https://t.me/SecretZoro" target="_blank">@SecretZoro</a> &nbsp;·&nbsp; ZORO XD Tools</footer>

</div>

<script>
async function extract() {
  const input = document.getElementById('input').value.trim();
  const status = document.getElementById('statusBar');
  const output = document.getElementById('output');

  if (!input) {
    setStatus('Paste some ID pairs first.', 'err');
    return;
  }

  setStatus('Processing…', '');
  output.classList.add('loading');
  document.getElementById('extractBtn').disabled = true;

  try {
    const res  = await fetch('/extract', {
      method:  'POST',
      headers: {'Content-Type': 'application/json'},
      body:    JSON.stringify({ pairs: input })
    });
    const data = await res.json();

    if (data.error) {
      setStatus('Error: ' + data.error, 'err');
      output.value = '';
    } else {
      output.value = data.result;
      setStatus('Done ✔', 'ok');
      showStats(data.total, data.found, data.missing);
    }
  } catch(e) {
    setStatus('Request failed — ' + e.message, 'err');
  }

  output.classList.remove('loading');
  document.getElementById('extractBtn').disabled = false;
}

function setStatus(msg, cls) {
  const el = document.getElementById('statusBar');
  el.textContent = msg;
  el.className   = cls;
}

function showStats(total, found, missing) {
  document.getElementById('vPairs').textContent  = total;
  document.getElementById('vFound').textContent  = found;
  document.getElementById('vMissed').textContent = missing;
  ['sPairs','sFound','sMissed'].forEach(id => {
    document.getElementById(id).classList.add('show');
  });
}

async function copyOutput() {
  const val = document.getElementById('output').value;
  if (!val) { setStatus('Nothing to copy.', 'err'); return; }
  await navigator.clipboard.writeText(val);
  setStatus('Copied to clipboard ✔', 'ok');
}

// Ctrl+Enter shortcut
document.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') extract();
});
</script>
</body>
</html>"""

# ── Routes ────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/extract", methods=["POST"])
def extract():
    if not DB:
        return jsonify({"error": "dump.txt not loaded on server"}), 500

    data  = request.get_json(force=True)
    raw   = data.get("pairs", "")
    lines = [l.strip() for l in raw.splitlines() if l.strip() and not l.startswith("#")]

    results = []
    found   = 0
    missing = 0

    for line in lines:
        if "," not in line:
            results.append(f"[INVALID: {line}]")
            missing += 1
            continue
        id1, id2 = line.split(",", 1)
        id1 = id1.strip(); id2 = id2.strip()
        n1 = DB.get(id1, f"[NOT FOUND:{id1}]")
        n2 = DB.get(id2, f"[NOT FOUND:{id2}]")
        results.append(f"{n1},{n2}")
        if "[NOT FOUND" in n1 or "[NOT FOUND" in n2:
            missing += 1
        else:
            found += 1

    return jsonify({
        "result":  "\n".join(results),
        "total":   len(results),
        "found":   found,
        "missing": missing,
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
