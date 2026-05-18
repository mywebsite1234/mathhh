"""
Web Proxy - Flask app for Railway deployment
---------------------------------------------
Visit:  https://yourapp.railway.app/
Type a URL in the box → the server fetches it and returns it through Railway.

No browser proxy settings needed.
"""

from flask import Flask, request, Response, render_template_string
import requests
from urllib.parse import urljoin, urlparse, urlencode, quote
import re

app = Flask(__name__)

# ── Homepage HTML ───────────────────────────────────────────────
HOMEPAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>WebProxy</title>
  <link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #080b10;
      --surface: #0e1420;
      --border: #1c2438;
      --accent: #00e5ff;
      --accent2: #7b61ff;
      --text: #cdd6f4;
      --muted: #4a5568;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'DM Sans', sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 2.5rem;
      overflow: hidden;
    }

    /* animated grid background */
    body::before {
      content: '';
      position: fixed;
      inset: 0;
      background-image:
        linear-gradient(var(--border) 1px, transparent 1px),
        linear-gradient(90deg, var(--border) 1px, transparent 1px);
      background-size: 48px 48px;
      mask-image: radial-gradient(ellipse 80% 60% at 50% 50%, black 40%, transparent 100%);
      z-index: 0;
      animation: gridPulse 8s ease-in-out infinite;
    }
    @keyframes gridPulse {
      0%, 100% { opacity: 0.4; }
      50% { opacity: 0.7; }
    }

    /* glow orbs */
    .orb {
      position: fixed;
      border-radius: 50%;
      filter: blur(80px);
      z-index: 0;
      animation: drift 12s ease-in-out infinite alternate;
    }
    .orb1 {
      width: 400px; height: 400px;
      background: rgba(0, 229, 255, 0.06);
      top: -100px; left: -100px;
      animation-delay: 0s;
    }
    .orb2 {
      width: 300px; height: 300px;
      background: rgba(123, 97, 255, 0.08);
      bottom: -80px; right: -80px;
      animation-delay: -6s;
    }
    @keyframes drift {
      from { transform: translate(0, 0); }
      to   { transform: translate(40px, 30px); }
    }

    .card {
      position: relative;
      z-index: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 2rem;
      width: min(640px, 92vw);
    }

    .logo {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 0.4rem;
    }
    .logo-title {
      font-family: 'Space Mono', monospace;
      font-size: clamp(2rem, 6vw, 3rem);
      font-weight: 700;
      letter-spacing: -1px;
      background: linear-gradient(135deg, var(--accent), var(--accent2));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    .logo-sub {
      font-size: 0.82rem;
      color: var(--muted);
      font-family: 'Space Mono', monospace;
      letter-spacing: 2px;
      text-transform: uppercase;
    }

    .search-wrap {
      width: 100%;
      position: relative;
    }
    .search-bar {
      display: flex;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      overflow: hidden;
      transition: border-color 0.2s, box-shadow 0.2s;
    }
    .search-bar:focus-within {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(0, 229, 255, 0.08), 0 0 20px rgba(0, 229, 255, 0.06);
    }
    .scheme-badge {
      display: flex;
      align-items: center;
      padding: 0 1rem;
      font-family: 'Space Mono', monospace;
      font-size: 0.78rem;
      color: var(--accent);
      border-right: 1px solid var(--border);
      white-space: nowrap;
      user-select: none;
    }
    input#url {
      flex: 1;
      background: transparent;
      border: none;
      padding: 1rem 1rem;
      font-size: 1rem;
      font-family: 'DM Sans', sans-serif;
      color: var(--text);
      outline: none;
      min-width: 0;
    }
    input#url::placeholder { color: var(--muted); }
    .go-btn {
      background: linear-gradient(135deg, var(--accent), var(--accent2));
      color: #080b10;
      border: none;
      padding: 0 1.5rem;
      font-size: 0.9rem;
      font-weight: 700;
      font-family: 'Space Mono', monospace;
      cursor: pointer;
      transition: opacity 0.15s, transform 0.1s;
      white-space: nowrap;
    }
    .go-btn:hover { opacity: 0.88; }
    .go-btn:active { transform: scale(0.97); }

    .hint {
      font-size: 0.76rem;
      color: var(--muted);
      font-family: 'Space Mono', monospace;
      letter-spacing: 0.5px;
      display: flex;
      gap: 1.2rem;
      flex-wrap: wrap;
      justify-content: center;
    }
    .hint span::before { content: '› '; color: var(--accent); }
  </style>
</head>
<body>
  <div class="orb orb1"></div>
  <div class="orb orb2"></div>

  <div class="card">
    <div class="logo">
      <div class="logo-title">WebProxy</div>
      <div class="logo-sub">routed through railway</div>
    </div>

    <div class="search-wrap">
      <div class="search-bar">
        <div class="scheme-badge">http://</div>
        <input id="url" type="text" placeholder="example.com/page" autofocus
               onkeydown="if(event.key==='Enter') go()" />
        <button class="go-btn" onclick="go()">GO →</button>
      </div>
    </div>

    <div class="hint">
      <span>no proxy settings needed</span>
      <span>HTTP sites only</span>
      <span>traffic via Railway</span>
    </div>
  </div>

  <script>
    function go() {
      let val = document.getElementById('url').value.trim();
      if (!val) return;
      // strip any scheme the user may have typed
      val = val.replace(/^https?:\\/\\//, '');
      window.location.href = '/proxy?url=http://' + val;
    }
  </script>
</body>
</html>"""


# ── Proxy route ─────────────────────────────────────────────────
@app.route('/proxy')
def proxy():
    target_url = request.args.get('url', '').strip()
    if not target_url:
        return render_template_string(HOMEPAGE)

    if not target_url.startswith('http://') and not target_url.startswith('https://'):
        target_url = 'http://' + target_url

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        resp = requests.get(target_url, headers=headers, timeout=15, allow_redirects=True)
        content_type = resp.headers.get('Content-Type', 'text/html')

        # Use the final URL after redirects as the base
        final_url = resp.url
        parsed = urlparse(final_url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        path_parts = parsed.path.rsplit('/', 1)
        base_path = origin + path_parts[0] + '/' if len(path_parts) > 1 else origin + '/'

        def proxify(url):
            """Convert any URL into a /proxy?url=... link."""
            url = url.strip()
            if (not url or url.startswith('data:') or url.startswith('#')
                    or url.startswith('javascript:') or url.startswith('mailto:')):
                return url
            if '/proxy?url=' in url:
                return url
            if url.startswith('http://') or url.startswith('https://'):
                return '/proxy?url=' + quote(url, safe='')
            if url.startswith('//'):
                return '/proxy?url=' + quote(parsed.scheme + ':' + url, safe='')
            if url.startswith('/'):
                return '/proxy?url=' + quote(origin + url, safe='')
            return '/proxy?url=' + quote(base_path + url, safe='')

        # ── Rewrite CSS: url() references ──────────────────────────
        if 'text/css' in content_type:
            css = resp.text
            def replace_css_url(m):
                inner = m.group(1).strip().strip('\'"')
                return 'url(' + proxify(inner) + ')'
            css = re.sub(r'url\(([^)]+)\)', replace_css_url, css)
            return Response(css, status=resp.status_code, content_type=content_type)

        # ── Rewrite HTML ────────────────────────────────────────────
        if 'text/html' in content_type:
            html = resp.text

            def replace_attr(m):
                attr, q, url = m.group(1), m.group(2), m.group(3)
                return f'{attr}={q}{proxify(url)}{q}'

            html = re.sub(r'(href|src|action)=(["\'])([^"\']*)\2', replace_attr, html)

            def replace_srcset(m):
                q = m.group(1)
                parts = m.group(2).split(',')
                new_parts = []
                for part in parts:
                    pieces = part.strip().split()
                    if pieces:
                        pieces[0] = proxify(pieces[0])
                    new_parts.append(' '.join(pieces))
                return f'srcset={q}{", ".join(new_parts)}{q}'
            html = re.sub(r'srcset=(["\'])([^"\']*)\1', replace_srcset, html)

            def replace_inline_css_url(m):
                inner = m.group(1).strip().strip('\'"')
                return 'url(' + proxify(inner) + ')'
            html = re.sub(r'url\(([^)]+)\)', replace_inline_css_url, html)

            # Block location-based redirects that kick you back to the real site
            anti_redirect = (
                '<script>'
                'var __realLoc = window.location;'
                'Object.defineProperty(window, "location", {'
                '  get: function() { return __realLoc; },'
                '  set: function(v) {'
                '    var s = String(v);'
                '    if (s.startsWith("http") && !s.includes(window.__proxyHost||location.host)) {'
                '      window.location.href = "/proxy?url=" + encodeURIComponent(s);'
                '      return;'
                '    }'
                '    __realLoc.href = s;'
                '  }'
                '});'
                'window.__proxyHost = location.host;'
                '</script>'
            )

            toolbar = (
                '<div id="__wproxy" style="'
                'position:fixed;top:0;left:0;right:0;z-index:2147483647;'
                'background:#080b10cc;backdrop-filter:blur(8px);'
                'border-bottom:1px solid #1c2438;'
                'padding:5px 14px;display:flex;align-items:center;gap:10px;'
                'font-family:monospace;font-size:12px;color:#cdd6f4;'
                'box-shadow:0 2px 16px #0008;">'
                '<a href="/" style="color:#00e5ff;text-decoration:none;font-weight:bold;flex-shrink:0">WebProxy</a>'
                '<span style="color:#2e3348;flex-shrink:0">›</span>'
                f'<span style="color:#7b61ff;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1">{final_url}</span>'
                '<a href="/" style="color:#4a5568;text-decoration:none;flex-shrink:0">✕</a>'
                '</div>'
                '<div style="height:32px"></div>'
            )

            inject = anti_redirect + toolbar

            if re.search(r'<body', html, re.IGNORECASE):
                html = re.sub(r'(<body[^>]*>)', r'\1' + inject, html, count=1, flags=re.IGNORECASE)
            else:
                html = inject + html

            return Response(html, status=resp.status_code, content_type=content_type)

        # For everything else (images, fonts, JS, etc.) pass through directly
        return Response(resp.content, status=resp.status_code, content_type=content_type)

    except requests.exceptions.ConnectionError:
        return Response(f"<h2>Could not connect to {target_url}</h2>", status=502, content_type='text/html')
    except requests.exceptions.Timeout:
        return Response(f"<h2>Request timed out for {target_url}</h2>", status=504, content_type='text/html')
    except Exception as e:
        return Response(f"<h2>Proxy error: {e}</h2>", status=500, content_type='text/html')


# ── Homepage ────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template_string(HOMEPAGE)


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8888))
    app.run(host='0.0.0.0', port=port, debug=False)
