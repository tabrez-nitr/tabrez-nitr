import json
import math
import os
import requests
from datetime import datetime
from PIL import Image, ImageEnhance

# Config
USERNAME = "tabrez-nitr"
JSON_PATH = "neofetch.json"
IMG_PATH = "new_pfp.jpg"
OUT_PATH = "profile-card.svg"

# Fetch GitHub stats
def fetch_stats():
    headers = {}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    
    # User info
    res = requests.get(f"https://api.github.com/users/{USERNAME}", headers=headers)
    user_data = res.json() if res.status_code == 200 else {}
    
    followers = user_data.get("followers", 0)
    repos = user_data.get("public_repos", 0)
    
    # Fetch all repos for stars & LOC (simplified)
    stars = 0
    loc_approx = "0 (API limit)"
    
    # We will fetch a single page of repos for stars
    repos_res = requests.get(f"https://api.github.com/users/{USERNAME}/repos?per_page=100", headers=headers)
    if repos_res.status_code == 200:
        repos_data = repos_res.json()
        stars = sum(repo.get("stargazers_count", 0) for repo in repos_data)
        loc_approx = f"{len(repos_data) * 1000} (approx)" # Mock LOC since it's hard to fetch precisely
        
    return {
        "repos": str(repos),
        "stars": str(stars),
        "commits": "313", # Hardcoded or needs complex GraphQL/REST to calculate across all repos
        "followers": str(followers),
        "loc": loc_approx
    }

def get_uptime():
    # Mock uptime or use current date for fun
    return "2 years, 6 days"

def render_svg(data, stats, art_svg):
    lines = []
    y = 50
    x_start = 390
    line_height = 20
    
    # Calculate longest key for alignment
    max_key_len = 0
    for section in data.get("sections", []):
        for field in section.get("fields", []):
            max_key_len = max(max_key_len, len(field["key"]))
            
    # Add title
    title = data["sections"][0].get("title", f"{USERNAME}@github").replace("{{username}}", USERNAME)
    lines.append(f'<text x="{x_start}" y="{y}" fill="#a5d6ff" font-weight="bold">{title}</text>')
    lines.append(f'<text x="{x_start + len(title)*9}" y="{y}" fill="#616e7f"> ------------------------------------</text>')
    y += line_height
    
    for idx, section in enumerate(data.get("sections", [])):
        if idx == 0:
            pass # Skip title underline since we added it
        elif idx > 0:
            lines.append(f'<text x="{x_start}" y="{y}"></text>')
            y += line_height
            if "title" in section:
                stitle = section["title"]
                lines.append(f'<text x="{x_start}" y="{y}" fill="#c9d1d9">{stitle} ---------------------------------------------</text>')
                y += line_height
            
        for field in section.get("fields", []):
            k = field["key"]
            v = field["value"].replace("{{uptime}}", get_uptime())
            dots = "." * (max_key_len - len(k) + 5)
            # Keys in orange (#ffa657), dots in gray, value in white (#c9d1d9) or blue
            lines.append(f'<text x="{x_start}" y="{y}"><tspan class="key">{k}</tspan><tspan class="cc">: {dots} </tspan><tspan class="value" fill="#c9d1d9">{v}</tspan></text>')
            y += line_height

    # Stats block
    y += line_height
    stats_data = data.get("stats", {})
    if stats_data:
        stitle = stats_data.get("title", "- GitHub Stats")
        lines.append(f'<text x="{x_start}" y="{y}" fill="#c9d1d9">{stitle} -----------------------</text>')
        y += line_height
        
        for row in stats_data.get("rows", []):
            if isinstance(row, dict):
                lk = row["left"]["key"]
                lv = row["left"]["value"].replace("{{repos}}", stats["repos"]).replace("{{commits}}", stats["commits"])
                rk = row["right"]["key"]
                rv = row["right"]["value"].replace("{{stars}}", stats["stars"]).replace("{{followers}}", stats["followers"])
                
                lines.append(f'<text x="{x_start}" y="{y}"><tspan class="key">{lk}</tspan><tspan class="cc">: ....... </tspan><tspan fill="#c9d1d9">{lv}</tspan><tspan class="cc"> | </tspan><tspan class="key">{rk}</tspan><tspan class="cc">: ....... </tspan><tspan fill="#c9d1d9">{rv}</tspan></text>')
            else:
                if row == "loc":
                    lines.append(f'<text x="{x_start}" y="{y}"><tspan class="key">Lines of Code</tspan><tspan class="cc">: ......... </tspan><tspan fill="#c9d1d9">{stats["loc"]}</tspan></text>')
            y += line_height

    text_group = "\\n".join(lines)
    
    total_height = max(530, y + 40)
    
    svg = f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="985px" height="{total_height}px" viewBox="0 0 985 {total_height}" font-size="16px">
<style>
@font-face {{
src: local('Consolas'), local('Consolas Bold');
font-family: 'ConsolasFallback';
font-display: swap;
}}
.key{{fill:#ffa657;}}
.value{{fill:#a5d6ff;}}
.cc{{fill:#616e7f;}}
text,tspan{{white-space:pre;}}
</style>
<rect width="985px" height="{total_height}px" fill="#161b22" rx="15"/>
<g id="avatar_art" transform="translate(15, 30)">
{art_svg}
</g>
<g id="terminal_text">
{text_group}
</g>
</svg>"""
    return svg

def generate_art():
    try:
        img = Image.open(IMG_PATH)
        # Resize to 72x96 (360x480 at 5px intervals)
        img = img.resize((72, 96), Image.Resampling.LANCZOS)
        img = img.convert("RGB")
        # Enhance brightness
        img = ImageEnhance.Brightness(img).enhance(1.4)
        
        circles = []
        for y in range(96):
            for x in range(72):
                r, g, b = img.getpixel((x, y))
                # Simple brightness for radius
                brightness = (r + g + b) / (255 * 3)
                radius = 0.5 + brightness * 0.775 # max radius 1.275
                opacity = 0.5 + brightness * 0.5
                
                cx = x * 5 + 1.5
                cy = y * 5 + 1.5
                
                circles.append(f'<circle cx="{cx}" cy="{cy}" r="{radius:.2f}" fill="rgb({r},{g},{b})" opacity="{opacity:.2f}" />')
                
        return "\\n".join(circles)
    except Exception as e:
        print(f"Error generating art: {e}")
        return ""

def main():
    print("Loading config...")
    with open(JSON_PATH, "r") as f:
        data = json.load(f)
        
    print("Fetching stats...")
    stats = fetch_stats()
    
    print("Generating art...")
    art = generate_art()
    
    print("Rendering SVG...")
    svg = render_svg(data, stats, art)
    
    with open(OUT_PATH, "w") as f:
        f.write(svg)
        
    print(f"Successfully wrote {OUT_PATH}")

if __name__ == "__main__":
    main()
