import os
import re
import mimetypes
import stat
import time
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GFinder | System Enumeration</title>
    <style>
        :root {
            --bg-dark: #0f172a;
            --bg-card: #1e293b;
            --text-main: #e2e8f0;
            --text-muted: #94a3b8;
            --accent: #3b82f6;
            --accent-hover: #2563eb;
            --match-highlight: #f59e0b;
            --border: #334155;
            --font-mono: 'Consolas', 'Monaco', 'Courier New', monospace;
        }

        body {
            background-color: var(--bg-dark);
            color: var(--text-main);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
        }

        header {
            background-color: var(--bg-card);
            border-bottom: 1px solid var(--border);
            padding: 1rem 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            z-index: 10;
        }

        .title-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
        }
        
        .logo-container {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .logo-svg {
            height: 40px;
            width: 40px;
        }

        .logo-text { 
            font-weight: 800; 
            font-size: 1.25rem; 
            letter-spacing: -0.05em; 
            color: var(--accent); 
        }
        .logo-text span { color: var(--text-main); }

        .search-grid {
            display: grid;
            grid-template-columns: 2fr 1.5fr 1fr auto;
            gap: 10px;
            align-items: center;
            margin-bottom: 10px;
        }

        .advanced-filters {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr 1fr;
            gap: 10px;
            padding-top: 10px;
            border-top: 1px solid var(--border);
        }

        input[type="text"], input[type="number"], select {
            background-color: var(--bg-dark);
            border: 1px solid var(--border);
            color: var(--text-main);
            padding: 0.5rem 0.75rem;
            border-radius: 6px;
            font-size: 0.9rem;
            outline: none;
            transition: border-color 0.2s;
            width: 100%;
            box-sizing: border-box;
        }

        input:focus { border-color: var(--accent); }

        .btn-primary {
            background-color: var(--accent);
            color: white;
            border: none;
            padding: 0.5rem 1.5rem;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
            white-space: nowrap;
        }
        .btn-primary:hover { background-color: var(--accent-hover); }
        .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

        .btn-warning {
            background-color: #f59e0b;
            color: #0f172a;
            border: none;
            padding: 0.4rem 1rem;
            border-radius: 6px;
            font-weight: 700;
            cursor: pointer;
            font-size: 0.8rem;
            margin-left: 10px;
            transition: background 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }
        .btn-warning:hover { background-color: #d97706; }

        .toggle-group {
            display: flex;
            align-items: center;
            gap: 15px;
            font-size: 0.85rem;
            color: var(--text-muted);
            flex-wrap: wrap;
        }

        .toggle-label {
            display: flex;
            align-items: center;
            gap: 6px;
            cursor: pointer;
            user-select: none;
        }

        input[type="checkbox"] { accent-color: var(--accent); width: auto; }
        
        label.input-label {
            display: block;
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-bottom: 4px;
            font-weight: 600;
        }

        .command-box {
            background-color: #09090b;
            border: 1px solid #27272a;
            border-left: 4px solid var(--accent);
            color: #4ade80;
            font-family: var(--font-mono);
            font-size: 0.8rem;
            padding: 10px 15px;
            margin-bottom: 15px;
            border-radius: 4px;
            display: none; 
            white-space: pre-wrap;
            word-break: break-all;
        }
        .command-label {
            color: #6b7280;
            font-size: 0.7rem;
            text-transform: uppercase;
            font-weight: bold;
            margin-bottom: 4px;
            display: block;
        }

        main {
            flex: 1;
            overflow-y: auto;
            padding: 1.5rem;
            position: relative;
        }

        .stats-bar {
            margin-bottom: 1rem;
            font-size: 0.85rem;
            color: var(--text-muted);
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(0,0,0,0.2);
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid var(--border);
        }

        .file-card {
            background-color: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            margin-bottom: 1rem;
            overflow: hidden;
        }

        .file-header {
            padding: 0.75rem 1rem;
            background-color: rgba(0,0,0,0.2);
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
        }
        
        .file-path { font-family: var(--font-mono); font-size: 0.9rem; color: var(--accent); word-break: break-all; }
        .file-meta { font-size: 0.75rem; color: var(--text-muted); margin-right: 10px; }
        .match-count { background: var(--bg-dark); padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }

        .code-block {
            padding: 0;
            margin: 0;
            background-color: #0d1117;
            overflow-x: auto;
            display: none; /* Hidden by default */
        }
        .file-card.open .code-block { display: block; }

        .code-line {
            display: flex;
            font-family: var(--font-mono);
            font-size: 0.85rem;
            line-height: 1.5;
        }
        
        .code-line:hover { background-color: #161b22; }

        .line-num {
            width: 50px;
            text-align: right;
            padding-right: 10px;
            color: #4b5563;
            background-color: #161b22;
            user-select: none;
            flex-shrink: 0;
        }

        .line-content {
            padding-left: 10px;
            white-space: pre;
            color: #c9d1d9;
        }

        .highlight {
            background-color: rgba(245, 158, 11, 0.2);
            color: var(--match-highlight);
            font-weight: bold;
            border-bottom: 1px solid var(--match-highlight);
        }

        .scan-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 4rem 0;
            opacity: 0;
            animation: fadeIn 0.3s forwards;
        }
        @keyframes fadeIn { to { opacity: 1; } }

        .pulse-loader {
            display: inline-block;
            position: relative;
            width: 80px;
            height: 80px;
        }
        .pulse-loader div {
            position: absolute;
            border: 4px solid var(--accent);
            opacity: 1;
            border-radius: 50%;
            animation: ripple 1.5s cubic-bezier(0, 0.2, 0.8, 1) infinite;
        }
        .pulse-loader div:nth-child(2) {
            animation-delay: -0.75s;
        }
        @keyframes ripple {
            0% { top: 36px; left: 36px; width: 0; height: 0; opacity: 0; }
            4.9% { top: 36px; left: 36px; width: 0; height: 0; opacity: 0; }
            5% { top: 36px; left: 36px; width: 0; height: 0; opacity: 1; }
            100% { top: 0px; left: 0px; width: 72px; height: 72px; opacity: 0; }
        }
        .scan-text {
            margin-top: 25px;
            font-family: var(--font-mono);
            color: var(--accent);
            font-size: 0.9rem;
            letter-spacing: 0.1em;
            animation: blink 1.5s infinite;
            font-weight: bold;
        }
        @keyframes blink { 50% { opacity: 0.5; } }
        
        .badge {
            display: inline-block;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
            margin-right: 8px;
        }
        .badge-dir { background: #4f46e5; color: white; }
        .badge-file { background: #0ea5e9; color: white; }
        .badge-exe { background: #dc2626; color: white; }
        .badge-bin { background: #9333ea; color: white; }

    </style>
</head>
<body>

<header>
    <div class="title-row">
        <div class="logo-container">
            <svg class="logo-svg" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="tealGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#00D4D4;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#00B0B0;stop-opacity:1" />
                    </linearGradient>
                </defs>


                <path d="M 30 65 A 28 28 0 1 1 78 45" 
                      stroke="#00C8C8" 
                      stroke-width="3" 
                      stroke-linecap="round" 
                      fill="none" />
                
                <path d="M 28 72 A 36 36 0 1 1 86 45" 
                      stroke="#003399" 
                      stroke-width="4" 
                      stroke-linecap="round" 
                      fill="none" />
                
                <path d="M 86 45 L 82 38 L 91 39 Z" fill="#003399" />
                
                <g>
                    <rect x="26" y="66" width="10" height="26" rx="5" 
                          transform="rotate(45 31 79)" 
                          fill="#003399" />
                    
                    <rect x="29" y="68" width="4" height="20" rx="2" 
                          transform="rotate(45 31 79)" 
                          fill="#00C8C8" />

                    <circle cx="50" cy="45" r="18" 
                            stroke="#003399" 
                            stroke-width="5" 
                            fill="white" />
                </g>

                <g transform="translate(50, 45)">
                    <path d="M 8 -8 A 10 10 0 1 0 0 10 L 0 0 L 8 0" 
                          stroke="#00C8C8" 
                          stroke-width="4" 
                          stroke-linecap="round" 
                          stroke-linejoin="round"
                          fill="none" />
                </g>
            </svg>
            <div class="logo-text">G<span>Finder</span></div>
        </div>
    </div>

    <div class="search-grid">
        <input type="text" id="searchTerm" placeholder="Search string or Regex..." autofocus>
        <input type="text" id="rootPath" placeholder="Root Path (e.g. /var/www or C:\\Users)">
        
        <select id="searchTarget">
            <option value="content">Find in: File Content</option>
            <option value="filename">Find in: File Names</option>
            <option value="dirname">Find in: Directory Names</option>
        </select>
        
        <button class="btn-primary" onclick="startSearch()">SCAN</button>
    </div>

    <div class="advanced-filters">
        <div>
            <label class="input-label">File Type</label>
            <select id="fileType">
                <option value="any">Any / All</option>
                <option value="text" selected>Text Only (Default)</option>
                <option value="binary">Binary Only</option>
                <option value="executable">Executables Only</option>
                <option value="non_executable">Non-Executables Only</option>
            </select>
        </div>

        <div>
            <label class="input-label">Extensions (Optional)</label>
            <input type="text" id="extensions" placeholder="e.g. py, js, log">
        </div>

        <div class="toggle-group" style="grid-column: span 2; align-self: end; padding-bottom: 5px;">
            <label class="toggle-label">
                <input type="checkbox" id="useRegex"> Regex
            </label>
            <label class="toggle-label">
                <input type="checkbox" id="exactMatch"> Exact Match
            </label>
            <label class="toggle-label">
                <input type="checkbox" id="caseSensitive"> Case Sensitive
            </label>
            <label class="toggle-label">
                <input type="checkbox" id="includeHidden"> Include Hidden
            </label>
            <div style="margin-left: auto; display: flex; align-items: center; gap: 5px;">
                Context: 
                <input type="number" id="contextLines" value="2" min="0" max="10" style="width: 40px; padding: 2px 5px;">
            </div>
        </div>
    </div>
</header>

<main>
    <div id="commandBox" class="command-box">
        <span class="command-label">Terminal Command Equivalent</span>
        <div id="commandText"></div>
    </div>

    <div id="resultsArea">
        <div style="text-align: center; margin-top: 3rem; color: var(--text-muted);">
            <h3>Ready to Scan</h3>
            <p>Configure your filters above and click SCAN.</p>
        </div>
    </div>
</main>

<script>
    document.getElementById('rootPath').value = ".";

    function generateLinuxCommandJS(path, term, target, ftype, exts, regex, caseSensitive, hidden, context) {
        let cmd = ["find", `'${path}'`];

        if (!hidden) cmd.push("-not -path '*/.*'");

        if (ftype === 'executable') cmd.push("-executable");
        else if (ftype === 'non_executable') cmd.push("! -executable");

        if (exts) {
            let extList = exts.split(',').map(e => e.trim());
            if (extList.length === 1) {
                cmd.push(`-name '*${extList[0]}'`);
            } else {
                let orParts = extList.map(e => `-name '*${e}'`).join(' -o ');
                cmd.push(`\\( ${orParts} \\)`);
            }
        }

        if (target === 'filename') {
            if (regex) cmd.push(`-regex '.*${term}.*'`);
            else cmd.push(`-name '*${term}*'`);
        } else if (target === 'dirname') {
            cmd.push("-type d");
            if (regex) cmd.push(`-regex '.*${term}.*'`);
            else cmd.push(`-name '*${term}*'`);
        } else if (target === 'content') {
            cmd.push("-type f");
            let grepFlags = "-r";
            if (!caseSensitive) grepFlags += "i";
            if (regex) grepFlags += "E";
            if (context > 0) grepFlags += ` -C ${context}`;
            
            let safeTerm = term.replace(/'/g, "'\\''");
            cmd.push(`-exec grep ${grepFlags.replace('-r', '')} '${safeTerm}' {} +`);
        }

        return cmd.join(" ");
    }

    async function startSearch(unlimited = false) {
        const term = document.getElementById('searchTerm').value;
        const path = document.getElementById('rootPath').value;
        const target = document.getElementById('searchTarget').value;
        const fileType = document.getElementById('fileType').value;
        const ext = document.getElementById('extensions').value;
        const useRegex = document.getElementById('useRegex').checked;
        const exactMatch = document.getElementById('exactMatch').checked;
        const caseSensitive = document.getElementById('caseSensitive').checked;
        const includeHidden = document.getElementById('includeHidden').checked;
        const context = parseInt(document.getElementById('contextLines').value);
        
        const limit = unlimited ? 0 : 10000;

        if (!term) { alert("Please enter a search term"); return; }

        const resultsArea = document.getElementById('resultsArea');
        const cmdBox = document.getElementById('commandBox');
        
        const linuxCmd = generateLinuxCommandJS(path, term, target, fileType, ext, useRegex, caseSensitive, includeHidden, context);
        document.getElementById('commandText').textContent = linuxCmd;
        cmdBox.style.display = 'block';

        resultsArea.innerHTML = `
            <div class="scan-container">
                <div class="pulse-loader"><div></div><div></div></div>
                <div class="scan-text">SCANNING FILESYSTEM...</div>
            </div>
        `;
        
        const scanBtn = document.querySelector('.btn-primary');
        scanBtn.disabled = true;
        if(unlimited) {
            scanBtn.textContent = "DEEP SCANNING...";
        }

        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    term, path, target, fileType, ext, useRegex, exactMatch, caseSensitive, includeHidden, context, limit
                })
            });

            const data = await response.json();
            
            if (data.error) {
                resultsArea.innerHTML = `<div style="color: red; text-align: center;">Error: ${data.error}</div>`;
            } else {
                renderResults(data.results, data.stats, data.limit_reached);
            }
        } catch (e) {
            console.error(e);
            resultsArea.innerHTML = `<div style="color: red; text-align: center;">Connection Error</div>`;
        } finally {
            scanBtn.disabled = false;
            scanBtn.textContent = "SCAN";
        }
    }

    function renderResults(items, stats, limitReached) {
        const area = document.getElementById('resultsArea');
        
        if (items.length === 0) {
            area.innerHTML = `<div style="text-align: center; margin-top: 2rem;">No matches found.</div>`;
            return;
        }

        let warningBtn = '';
        if (limitReached) {
            warningBtn = `<button class="btn-warning" onclick="startSearch(true)">⚠️ scanning limit reached. Continue Deep Scan?</button>`;
        }

        const statsHtml = `
            <div class="stats-bar">
                <div>
                    <span>Found ${items.length} matches in ${stats.time_taken}s</span>
                    <span style="margin-left:10px; opacity:0.7">| Scanned: ${stats.scanned_count} items</span>
                </div>
                ${warningBtn}
            </div>
        `;
        area.innerHTML = statsHtml;

        items.forEach(item => {
            const card = document.createElement('div');
            card.className = 'file-card open'; 

            let badgeHtml = '';
            if (item.type === 'dir') badgeHtml = '<span class="badge badge-dir">DIR</span>';
            else if (item.is_exe) badgeHtml = '<span class="badge badge-exe">EXE</span>';
            else if (item.is_binary) badgeHtml = '<span class="badge badge-bin">BIN</span>';
            else badgeHtml = '<span class="badge badge-file">FILE</span>';

            let contentHtml = '';
            
            if (item.type === 'content_match') {
                let codeHtml = '';
                item.matches.forEach(match => {
                     match.context.sort((a,b) => a.num - b.num);
                     
                     match.context.forEach(ctxLine => {
                        const isMatchLine = ctxLine.num === match.line;
                        const highlightClass = isMatchLine ? 'highlight' : '';
                        const safeContent = ctxLine.content
                            .replace(/&/g, "&amp;")
                            .replace(/</g, "&lt;")
                            .replace(/>/g, "&gt;");

                        codeHtml += `
                            <div class="code-line">
                                <div class="line-num">${ctxLine.num}</div>
                                <div class="line-content ${highlightClass}">${safeContent}</div>
                            </div>
                        `;
                    });
                    codeHtml += `<div style="height: 1px; background: #333; margin: 5px 0;"></div>`;
                });
                contentHtml = `<div class="code-block">${codeHtml}</div>`;
            } else {
                const matchTypeLabel = item.type === 'dir' ? 'Directory Name' : 'Filename';
                contentHtml = `
                    <div style="padding: 10px; font-size: 0.85rem; color: #94a3b8;">
                        Match found in <strong>${matchTypeLabel}</strong>.
                    </div>
                `;
            }

            card.innerHTML = `
                <div class="file-header" onclick="this.parentElement.classList.toggle('open')">
                    <div style="display:flex; align-items:center;">
                        ${badgeHtml}
                        <span class="file-path">${item.path}</span>
                    </div>
                    ${item.match_count ? `<span class="match-count">${item.match_count} matches</span>` : ''}
                </div>
                ${contentHtml}
            `;
            area.appendChild(card);
        });
    }
</script>

</body>
</html>
"""


def get_context(lines, line_idx, context_range):
    """Extracts N lines before and after the match."""
    start = max(0, line_idx - context_range)
    end = min(len(lines), line_idx + context_range + 1)
    
    snippet = []
    for i in range(start, end):
        snippet.append({
            'num': i + 1,
            'content': lines[i].rstrip('\n')
        })
    return snippet

def is_executable(filepath):
    """Check if a file is executable."""
    if os.name == 'nt':
        return filepath.lower().endswith(('.exe', '.bat', '.cmd', '.ps1', '.vbs'))
    return os.access(filepath, os.X_OK)

def is_binary_mime(filepath):
    """Check if file is binary based on mime or basic heuristics."""
    mime, _ = mimetypes.guess_type(filepath)
    if mime and not mime.startswith('text') and mime not in ['application/json', 'application/javascript', 'application/xml']:
        return True
    return False

def generate_linux_command(path, term, target, ftype, exts, regex, case, hidden, context):
    """Generates an approximate Linux 'find' command for the search."""
    cmd = ["find", f"'{path}'"]

    if not hidden:
        cmd.append("-not -path '*/.*'")

    if ftype == 'executable':
        cmd.append("-executable")
    elif ftype == 'non_executable':
        cmd.append("! -executable")
    
    if exts:
        ext_list = [e.strip() for e in exts.split(',')]
        if len(ext_list) == 1:
            cmd.append(f"-name '*{ext_list[0]}'")
        else:
            or_parts = [f"-name '*{e}'" for e in ext_list]
            cmd.append(f"\\( {' -o '.join(or_parts)} \\)")

    if target == 'filename':
        if regex:
            cmd.append(f"-regex '.*{term}.*'")
        else:
            cmd.append(f"-name '*{term}*'")
    
    elif target == 'dirname':
        cmd.append("-type d")
        if regex:
            cmd.append(f"-regex '.*{term}.*'")
        else:
            cmd.append(f"-name '*{term}*'")

    elif target == 'content':
        cmd.append("-type f")
        
        grep_flags = "-r" 
        if not case: grep_flags += "i"
        if regex: grep_flags += "E"
        if context > 0: grep_flags += f" -C {context}"
        
        safe_term = term.replace("'", "'\\''") 
        cmd.append(f"-exec grep {grep_flags.replace('-r', '')} '{safe_term}' {{}} +")

    return " ".join(cmd)

@app.route('/')
def home():
    return render_template_string(TEMPLATE)

@app.route('/api/search', methods=['POST'])
def search_files():
    start_time = time.time()  
    data = request.json
    search_term = data.get('term', '')
    root_path = data.get('path', '.')
    search_target = data.get('target', 'content') 
    file_type_filter = data.get('fileType', 'text') 
    extensions = data.get('ext', '')
    use_regex = data.get('useRegex', False)
    exact_match = data.get('exactMatch', False)
    case_sensitive = data.get('caseSensitive', False)
    include_hidden = data.get('includeHidden', False)
    context_lines = data.get('context', 2)
    limit = data.get('limit', 10000) 

    if not search_term:
        return jsonify({'error': 'No search term provided'})

    linux_cmd = generate_linux_command(
        root_path, search_term, search_target, file_type_filter, 
        extensions, use_regex, case_sensitive, include_hidden, context_lines
    )

    valid_exts = set()
    if extensions:
        valid_exts = {e.strip() if e.strip().startswith('.') else f'.{e.strip()}' for e in extensions.split(',')}

    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        regex_term = search_term
        if not use_regex:
            regex_term = re.escape(search_term)
        
        if exact_match:
            regex_term = f"^{regex_term}$"

        pattern = re.compile(regex_term, flags)
    except re.error as e:
        return jsonify({'error': f'Invalid Regex: {str(e)}'})

    results = []
    scanned_count = 0
    limit_reached = False
    root_path = os.path.expanduser(root_path)

    if not os.path.exists(root_path):
        return jsonify({'error': 'Directory not found'})

    check_dirname = search_target in ['dirname', 'all']
    check_filename = search_target in ['filename', 'all']
    check_content = search_target in ['content', 'all']

    for root, dirs, files in os.walk(root_path):
        if not include_hidden:
            dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        if check_dirname:
            for d in dirs:
                if pattern.search(d):
                    full_path = os.path.join(root, d)
                    results.append({
                        'path': full_path,
                        'type': 'dir',
                        'is_exe': False,
                        'is_binary': False,
                        'matches': []
                    })
        
        if search_target == 'dirname':
            scanned_count += len(dirs)
            if limit > 0 and scanned_count >= limit:
                limit_reached = True
                break
            continue

        for file in files:
            if valid_exts:
                _, ext = os.path.splitext(file)
                if ext not in valid_exts:
                    continue
            
            if not include_hidden and file.startswith('.'):
                continue

            file_path = os.path.join(root, file)
            scanned_count += 1

            is_exe = is_executable(file_path)
            is_bin = is_binary_mime(file_path)

            if file_type_filter == 'text' and is_bin: continue
            elif file_type_filter == 'binary' and not is_bin: continue
            elif file_type_filter == 'executable' and not is_exe: continue
            elif file_type_filter == 'non_executable' and is_exe: continue

            if check_filename:
                if pattern.search(file):
                    results.append({
                        'path': file_path,
                        'type': 'file_name_match',
                        'is_exe': is_exe,
                        'is_binary': is_bin,
                        'matches': []
                    })
                    if search_target == 'filename':
                        continue

            if check_content:
                if file_type_filter == 'text' and is_bin: continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()

                    file_matches = []
                    for i, line in enumerate(lines):
                        if pattern.search(line.rstrip('\n')):
                            file_matches.append({
                                'line': i + 1,
                                'context': get_context(lines, i, context_lines)
                            })

                    if file_matches:
                        results.append({
                            'path': file_path,
                            'type': 'content_match',
                            'match_count': len(file_matches),
                            'matches': file_matches,
                            'is_exe': is_exe,
                            'is_binary': is_bin
                        })

                except Exception:
                    continue
            
            if limit > 0 and scanned_count >= limit:
                limit_reached = True
                break
        
        if limit > 0 and scanned_count >= limit:
            limit_reached = True
            break

    time_taken = round(time.time() - start_time, 2) 
    
    return jsonify({
        'results': results,
        'stats': {
            'scanned_count': scanned_count,
            'time_taken': time_taken
        },
        'limit_reached': limit_reached,
        'linux_command': linux_cmd
    })

if __name__ == '__main__':
    print("----------------------------------------------------------------")
    print(" GFINDER TOOL STARTED")
    print(" Open your browser to: http://127.0.0.1:5000")
    print(" Press CTRL+C to stop")
    print("----------------------------------------------------------------")
    app.run(debug=True, port=5000)
