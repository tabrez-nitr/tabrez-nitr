import json
import math
import os
import requests
from datetime import datetime
from PIL import Image, ImageEnhance

# Config
USERNAME = "tabrez-nitr"
JSON_PATH = "neofetch.json"
IMG_PATH = "pfp_2.jpeg"
OUT_PATH = "profile-card.svg"

def get_uptime():
    # Mock uptime or use current date for fun
    return "2 years, 6 days"

def render_svg(data, art_svg):
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
        img = ImageEnhance.Brightness(img).enhance(1.2)
        
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
        
    print("Generating art...")
    art = generate_art()
    
    print("Rendering SVG...")
    svg = render_svg(data, art)
    
    with open(OUT_PATH, "w") as f:
        f.write(svg)
        
    print(f"Successfully wrote {OUT_PATH}")

if __name__ == "__main__":
    main()
