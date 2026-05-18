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

            # Intercept fetch, XHR, and location so everything routes through proxy
            anti_redirect = (
                '<script>'
                '(function(){'
                '  var _host = location.host;'
                '  var _origin = ' + repr(origin) + ';'

                # Rewrite any URL to go through proxy
                '  function pw(u){'
                '    if(!u||u.startsWith("data:")||u.startsWith("blob:")||u.startsWith("#")) return u;'
                '    if(u.startsWith("/proxy?url=")) return u;'
                '    try{'
                '      var abs;'
                '      if(u.startsWith("http")||u.startsWith("//")){abs=u.replace(/^\\/\\//,"https://");}'
                '      else if(u.startsWith("/")) abs=_origin+u;'
                '      else abs=_origin+"/"+u;'
                '      return "/proxy?url="+encodeURIComponent(abs);'
                '    }catch(e){return u;}'
                '  }'

                # Intercept fetch
                '  var _fetch=window.fetch;'
                '  window.fetch=function(input,init){'
                '    if(typeof input==="string") input=pw(input);'
                '    else if(input instanceof Request){'
                '      input=new Request(pw(input.url),input);'
                '    }'
                '    return _fetch.call(this,input,init);'
                '  };'

                # Intercept XMLHttpRequest
                '  var _open=XMLHttpRequest.prototype.open;'
                '  XMLHttpRequest.prototype.open=function(m,u){'
                '    var args=Array.from(arguments);'
                '    args[1]=pw(u);'
                '    return _open.apply(this,args);'
                '  };'

                # Intercept window.location assignments — use /download for files
                '  var _loc=window.location;'
                '  function isFileUrl(s){'
                '    return /\\.(?:nbt|zip|jar|gz|tar|rar|7z|png|jpg|pdf|exe|msi|dmg)(\\?|$)/i.test(s);'
                '  }'
                '  Object.defineProperty(window,"location",{'
                '    get:function(){return _loc;},'
                '    set:function(v){'
                '      var s=String(v);'
                '      if(s.startsWith("http")&&!s.includes(_host)){'
                '        if(isFileUrl(s)){'
                '          var a=document.createElement("a");'
                '          a.href="/download?url="+encodeURIComponent(s);'
                '          a.download="";'
                '          document.body.appendChild(a);'
                '          a.click();'
                '          document.body.removeChild(a);'
                '        } else {'
                '          _loc.href="/proxy?url="+encodeURIComponent(s);'
                '        }'
                '      } else { _loc.href=s; }'
                '    }'
                '  });'
                # Also patch location.href directly
                '  try{'
                '    var _locProto=Object.getPrototypeOf(_loc);'
                '    var _origHrefSet=Object.getOwnPropertyDescriptor(_locProto,"href").set;'
                '    Object.defineProperty(_locProto,"href",{'
                '      get:function(){return _loc.href;},'
                '      set:function(v){'
                '        var s=String(v);'
                '        if(s.startsWith("http")&&!s.includes(_host)){'
                '          if(isFileUrl(s)){'
                '            var a=document.createElement("a");'
                '            a.href="/download?url="+encodeURIComponent(s);'
                '            a.download="";'
                '            document.body.appendChild(a);'
                '            a.click();'
                '            document.body.removeChild(a);'
                '          } else {'
                '            _origHrefSet.call(this,"/proxy?url="+encodeURIComponent(s));'
                '          }'
                '        } else { _origHrefSet.call(this,s); }'
                '      }'
                '    });'
                '  }catch(e){}'

                # Make download links work: intercept clicks on <a download> tags
                '  document.addEventListener("click",function(e){'
                '    var a=e.target.closest("a[href]");'
                '    if(!a) return;'
                '    var href=a.getAttribute("href");'
                '    if(!href) return;'
                '    var proxied=pw(href);'
                '    if(proxied!==href){'
                '      e.preventDefault();'
                '      var dl=document.createElement("a");'
                '      dl.href=proxied;'
                '      dl.download=a.download||"";'
                '      dl.click();'
                '    }'
                '  },true);'

                '})();'
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


# ── Download route — streams a file from a proxied URL ──────────
@app.route('/download')
def download():
    from flask import stream_with_context
    import urllib.parse

    target_url = request.args.get('url', '').strip()
    if not target_url:
        return Response('No URL provided', status=400)

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36',
        }
        resp = requests.get(target_url, headers=headers, stream=True, timeout=30, allow_redirects=True)

        # Try to get a filename from Content-Disposition or the URL
        filename = ''
        cd = resp.headers.get('Content-Disposition', '')
        if 'filename=' in cd:
            filename = cd.split('filename=')[-1].strip().strip('"\'')
        if not filename:
            filename = urllib.parse.unquote(target_url.split('/')[-1].split('?')[0]) or 'download'

        content_type = resp.headers.get('Content-Type', 'application/octet-stream')

        def generate():
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk

        response = Response(
            stream_with_context(generate()),
            status=resp.status_code,
            content_type=content_type,
        )
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        if 'Content-Length' in resp.headers:
            response.headers['Content-Length'] = resp.headers['Content-Length']
        return response

    except Exception as e:
        return Response(f'Download error: {e}', status=500)


# ── Catch-all: forward unrecognised paths to createmod (or any site)
# This handles cases where JS does location.href = "/download/..." (root-relative)
# and our interceptor misses it because it doesn't start with "http"
@app.route('/<path:subpath>', methods=['GET', 'POST', 'HEAD'])
def catchall(subpath):
    # If there's a Referer header from our proxy, forward the request to the real origin
    referer = request.headers.get('Referer', '')
    origin_url = None

    # Extract the proxied origin from the Referer  e.g. /proxy?url=https://createmod.com/...
    import urllib.parse as up
    if 'proxy?url=' in referer:
        try:
            ref_path = up.urlparse(referer).query
            params = up.parse_qs(ref_path)
            proxied = params.get('url', [None])[0]
            if proxied:
                p = up.urlparse(proxied)
                origin_url = f"{p.scheme}://{p.netloc}"
        except Exception:
            pass

    if not origin_url:
        # fallback: check query param
        origin_url = request.args.get('origin', '').strip()

    if not origin_url:
        return Response('Not Found', status=404)

    # Build the full target URL
    qs = request.query_string.decode()
    target = f"{origin_url}/{subpath}" + (f"?{qs}" if qs else "")

    # Decide: is this a file download or a page?
    file_exts = ('.nbt', '.zip', '.jar', '.gz', '.tar', '.rar', '.7z',
                 '.png', '.jpg', '.pdf', '.exe', '.msi', '.dmg', '.schematic')
    path_lower = subpath.lower().split('?')[0]
    is_file = any(path_lower.endswith(ext) for ext in file_exts)

    # Also treat /download/... paths as files
    if subpath.startswith('download/') or subpath == 'download':
        is_file = True

    if is_file:
        # Stream it as a file download
        from flask import stream_with_context
        import urllib.parse
        try:
            headers = {'User-Agent': 'Mozilla/5.0 Chrome/120'}
            r = requests.get(target, headers=headers, stream=True, timeout=30, allow_redirects=True)
            filename = subpath.split('/')[-1].split('?')[0] or 'download'
            cd = r.headers.get('Content-Disposition', '')
            if 'filename=' in cd:
                filename = cd.split('filename=')[-1].strip().strip('"\'')
            ct = r.headers.get('Content-Type', 'application/octet-stream')

            def gen():
                for chunk in r.iter_content(8192):
                    if chunk:
                        yield chunk

            resp = Response(stream_with_context(gen()), status=r.status_code, content_type=ct)
            resp.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            if 'Content-Length' in r.headers:
                resp.headers['Content-Length'] = r.headers['Content-Length']
            return resp
        except Exception as e:
            return Response(f'Download error: {e}', status=500)
    else:
        # Proxy it as a normal page
        from flask import redirect
        return redirect(f'/proxy?url={up.quote(target, safe="")}')



@app.route('/')
def index():
    return render_template_string(HOMEPAGE)


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8888))
    app.run(host='0.0.0.0', port=port, debug=False)
