from flask import Flask, request, Response, render_template
import requests
from urllib.parse import urljoin, quote_plus, urlparse
from bs4 import BeautifulSoup

app = Flask(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5'
}

@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/proxy')
def proxy():
    target_url = request.args.get('url', '').strip()
    if not target_url:
        return render_template('index.html')
        
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'http://' + target_url

    try:
        # Fetch target resource through server network
        resp = requests.get(target_url, headers=HEADERS, timeout=10, allow_redirects=True)
        content_type = resp.headers.get('Content-Type', '')
        base_url = resp.url 

        # Intercept and modify HTML web text pages dynamically
        if 'text/html' in content_type:
            soup = BeautifulSoup(resp.content, 'html.parser')
            
            # 1. Rewrite absolute and relative hyperlink destinations
            for a in soup.find_all('a', href=True):
                abs_href = urljoin(base_url, a['href'])
                a['href'] = f"/proxy?url={quote_plus(abs_href)}"
                
            # 2. Rewrite HTML form submission endpoints 
            for form in soup.find_all('form', action=True):
                abs_action = urljoin(base_url, form['action'])
                form['action'] = f"/proxy?url={quote_plus(abs_action)}"

            # 3. Resolve asset source links to maintain design layouts
            for tag in soup.find_all(['img', 'script', 'iframe'], src=True):
                tag['src'] = urljoin(base_url, tag['src'])
                
            for link in soup.find_all('link', href=True):
                link['href'] = urljoin(base_url, link['href'])

            return Response(str(soup), status=resp.status_code, content_type=content_type)
        
        # Stream static files (images, fonts, css) unmodified
        return Response(resp.content, status=resp.status_code, content_type=content_type)

    except requests.exceptions.RequestException as e:
        return f"<div style='color:#ff5555; font-family:sans-serif; padding:30px;'><h2>Proxy Timeout Error</h2><p>{str(e)}</p></div>", 504

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8888))
    app.run(host='0.0.0.0', port=port, debug=False)
