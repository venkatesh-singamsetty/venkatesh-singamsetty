import os
import sys
import json
import urllib.request
import ssl
from datetime import datetime

TOKEN = os.environ.get("METRICS_TOKEN") or os.environ.get("GITHUB_TOKEN")
if not TOKEN:
    print("Error: No METRICS_TOKEN or GITHUB_TOKEN provided")
    sys.exit(1)

current_year = datetime.now().year
years_query = "\n".join([
    f'y{yr}: contributionsCollection(from: "{yr}-01-01T00:00:00Z", to: "{yr}-12-31T23:59:59Z") {{ totalCommitContributions contributionCalendar {{ totalContributions }} }}'
    for yr in range(2016, current_year + 1)
])

query = f"""
query {{
  viewer {{
    login
    name
    repositories(first: 100, ownerAffiliations: OWNER) {{
      totalCount
      nodes {{
        name
        isPrivate
        stargazerCount
      }}
    }}
    pullRequests {{
      totalCount
    }}
    issues {{
      totalCount
    }}
    {years_query}
  }}
}}
"""

req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": query}).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "Metrics-Generator"
    }
)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

with urllib.request.urlopen(req, context=ctx) as response:
    result = json.loads(response.read().decode("utf-8"))

viewer = result["data"]["viewer"]
total_repos = viewer["repositories"]["totalCount"]
total_prs = viewer["pullRequests"]["totalCount"]
total_issues = viewer["issues"]["totalCount"]

# Calculate cumulative lifetime commits and contributions
total_lifetime_commits = 0
total_lifetime_contribs = 0

for yr in range(2016, current_year + 1):
    key = f"y{yr}"
    if key in viewer:
        total_lifetime_commits += viewer[key]["totalCommitContributions"]
        total_lifetime_contribs += viewer[key]["contributionCalendar"]["totalContributions"]

# Generate matching ultra-vibrant, high-contrast SVG matching the LinkedIn card
vibrant_svg = f"""<svg width="850" height="420" viewBox="0 0 850 420" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Background Gradients -->
    <radialGradient id="bg_grad" cx="85%" cy="15%" r="90%">
      <stop offset="0%" stop-color="#1e2942"/>
      <stop offset="50%" stop-color="#0d121f"/>
      <stop offset="100%" stop-color="#080c14"/>
    </radialGradient>
    <radialGradient id="glow_cyan" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#00f2fe" stop-opacity="0.25"/>
      <stop offset="100%" stop-color="#00f2fe" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glow_purple" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#a855f7" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#a855f7" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="seal_bg" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#1e293b"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </radialGradient>
    <linearGradient id="seal_text" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00f2fe"/>
      <stop offset="100%" stop-color="#4facfe"/>
    </linearGradient>
  </defs>

  <style>
    .font-sans {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }}
    .title {{ font: 900 28px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; fill: #ffffff; letter-spacing: -0.5px; }}
    .subtitle {{ font: 600 15px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; fill: #38bdf8; }}
    .tag-text {{ font: 700 11px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; fill: #e2e8f0; letter-spacing: 0.5px; }}
    
    .stat-num {{ font: 900 32px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
    .stat-lbl {{ font: 700 11.5px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; fill: #94a3b8; letter-spacing: 0.8px; text-transform: uppercase; }}
    
    .pill-txt {{ font: 700 12px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
    
    .rank-letter {{ font: 900 48px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; fill: url(#seal_text); }}
    .rank-lbl {{ font: 800 10px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; fill: #e2e8f0; letter-spacing: 2px; text-transform: uppercase; }}
  </style>

  <!-- Container -->
  <rect x="1" y="1" width="848" height="418" rx="20" fill="url(#bg_grad)" stroke="#70a5fd" stroke-opacity="0.3" stroke-width="1.5"/>

  <!-- Background Ambient Glows -->
  <circle cx="740" cy="50" r="180" fill="url(#glow_cyan)"/>
  <circle cx="60" cy="380" r="200" fill="url(#glow_purple)"/>

  <!-- Top GitHub Badge -->
  <g transform="translate(36, 32)">
    <rect width="210" height="26" rx="13" fill="#ffffff" fill-opacity="0.08" stroke="#ffffff" stroke-opacity="0.18"/>
    <path transform="translate(10, 5) scale(0.9)" d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z" fill="#ffffff"/>
    <text x="32" y="17" class="tag-text">GITHUB.COM/VENKATESH-SINGAMSETTY</text>
  </g>

  <!-- Main Headline & Subtitle -->
  <text x="36" y="94" class="title">GitHub Engineering Portfolio</text>
  <text x="36" y="122" class="subtitle">Venkatesh Singamsetty • Senior Platform &amp; DevOps Architect</text>

  <!-- Rank Seal Badge (Top Right) -->
  <g transform="translate(740, 78)">
    <circle cx="0" cy="0" r="50" fill="url(#seal_bg)" stroke="#00f2fe" stroke-width="3.5"/>
    <circle cx="0" cy="0" r="54" fill="none" stroke="#00f2fe" stroke-opacity="0.3" stroke-width="2"/>
    <text x="0" y="8" text-anchor="middle" class="rank-letter">A+</text>
    <text x="0" y="26" text-anchor="middle" class="rank-lbl">Top Rank</text>
  </g>

  <!-- Stats Grid (4 Cards) -->
  <!-- Card 1: Contributions -->
  <g transform="translate(36, 160)">
    <rect width="180" height="110" rx="14" fill="#1a2035" fill-opacity="0.8" stroke="#ffffff" stroke-opacity="0.12"/>
    <text x="20" y="52" class="stat-num" fill="#10b981">{total_lifetime_contribs:,}+</text>
    <text x="20" y="82" class="stat-lbl">Contributions</text>
  </g>

  <!-- Card 2: Commits -->
  <g transform="translate(230, 160)">
    <rect width="180" height="110" rx="14" fill="#1a2035" fill-opacity="0.8" stroke="#ffffff" stroke-opacity="0.12"/>
    <text x="20" y="52" class="stat-num" fill="#00f2fe">{total_lifetime_commits:,}</text>
    <text x="20" y="82" class="stat-lbl">All-Time Commits</text>
  </g>

  <!-- Card 3: Pull Requests -->
  <g transform="translate(424, 160)">
    <rect width="180" height="110" rx="14" fill="#1a2035" fill-opacity="0.8" stroke="#ffffff" stroke-opacity="0.12"/>
    <text x="20" y="52" class="stat-num" fill="#c084fc">{total_prs:,}</text>
    <text x="20" y="82" class="stat-lbl">Pull Requests</text>
  </g>

  <!-- Card 4: Repositories -->
  <g transform="translate(618, 160)">
    <rect width="196" height="110" rx="14" fill="#1a2035" fill-opacity="0.8" stroke="#ffffff" stroke-opacity="0.12"/>
    <text x="20" y="52" class="stat-num" fill="#fbbf24">{total_repos}</text>
    <text x="20" y="82" class="stat-lbl">Repositories</text>
  </g>

  <!-- Divider Line -->
  <line x1="36" y1="310" x2="814" y2="310" stroke="#ffffff" stroke-opacity="0.1" stroke-width="1"/>

  <!-- Footer Skills Pills -->
  <g transform="translate(36, 335)">
    <!-- Jenkins -->
    <g transform="translate(0, 0)">
      <rect width="78" height="32" rx="16" fill="#3b82f6" fill-opacity="0.2" stroke="#60a5fa" stroke-width="1.2"/>
      <text x="39" y="20" text-anchor="middle" class="pill-txt" fill="#93c5fd">Jenkins</text>
    </g>
    <!-- AWS -->
    <g transform="translate(86, 0)">
      <rect width="64" height="32" rx="16" fill="#f97316" fill-opacity="0.2" stroke="#fb923c" stroke-width="1.2"/>
      <text x="32" y="20" text-anchor="middle" class="pill-txt" fill="#fdba74">AWS</text>
    </g>
    <!-- Terraform -->
    <g transform="translate(158, 0)">
      <rect width="88" height="32" rx="16" fill="#a855f7" fill-opacity="0.2" stroke="#c084fc" stroke-width="1.2"/>
      <text x="44" y="20" text-anchor="middle" class="pill-txt" fill="#e9d5ff">Terraform</text>
    </g>
    <!-- Kubernetes -->
    <g transform="translate(254, 0)">
      <rect width="98" height="32" rx="16" fill="#06b6d4" fill-opacity="0.2" stroke="#22d3ee" stroke-width="1.2"/>
      <text x="49" y="20" text-anchor="middle" class="pill-txt" fill="#a5f3fc">Kubernetes</text>
    </g>
    <!-- GenAI & Agentic AI -->
    <g transform="translate(360, 0)">
      <rect width="144" height="32" rx="16" fill="#10b981" fill-opacity="0.2" stroke="#34d399" stroke-width="1.2"/>
      <text x="72" y="20" text-anchor="middle" class="pill-txt" fill="#a7f3d0">GenAI &amp; Agentic AI</text>
    </g>
    <!-- RAG & MCP -->
    <g transform="translate(512, 0)">
      <rect width="98" height="32" rx="16" fill="#a855f7" fill-opacity="0.2" stroke="#c084fc" stroke-width="1.2"/>
      <text x="49" y="20" text-anchor="middle" class="pill-txt" fill="#e9d5ff">RAG &amp; MCP</text>
    </g>
    <!-- MLOps -->
    <g transform="translate(618, 0)">
      <rect width="72" height="32" rx="16" fill="#10b981" fill-opacity="0.2" stroke="#34d399" stroke-width="1.2"/>
      <text x="36" y="20" text-anchor="middle" class="pill-txt" fill="#a7f3d0">MLOps</text>
    </g>
  </g>
</svg>"""

with open("github-stats.svg", "w") as f:
    f.write(vibrant_svg)

print(f"Generated ultra-vibrant github-stats.svg! Lifetime Commits: {total_lifetime_commits}, Lifetime Contributions: {total_lifetime_contribs}")
