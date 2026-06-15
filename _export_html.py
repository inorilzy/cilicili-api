"""生成UP主标签展示HTML页面"""
import json

with open("up_tag_db.json", encoding="utf-8") as f:
    db = json.load(f)

tag_to_ups = db["tag_to_ups"]
up_tags = db["up_tags"]

all_tags = sorted(
    tag_to_ups.keys(),
    key=lambda t: (t == "综合/其他", -len(tag_to_ups[t]))
)

# 生成标签颜色
colors = [
    "#4f9ef8", "#f87c4f", "#4fc98d", "#c94f7e", "#7c4fc9",
    "#f8c44f", "#4fc9c9", "#c9a44f", "#c9604f", "#4f7ec9",
    "#7ec94f", "#f84fc9", "#4fc97c", "#c9c94f", "#6a4fc9",
    "#c9784f", "#4fa4c9", "#c9504f", "#4fc9a4", "#c94fa0",
    "#a4c94f", "#4f60c9",
]
tag_colors = {tag: colors[i % len(colors)] for i, tag in enumerate(all_tags)}

# 构建HTML
sections = []
for tag in all_tags:
    uids = tag_to_ups[tag]
    color = tag_colors[tag]
    cards = []
    for uid in uids:
        info = up_tags.get(uid, {})
        name = info.get("name", uid)
        tags = info.get("tags", [])
        sign = info.get("sign", "") or ""
        titles = info.get("recent_titles", []) or []
        other_tags = [t for t in tags if t != tag]
        badges = "".join(
            f'<span class="badge" style="background:{tag_colors.get(t, "#999")}">{t}</span>'
            for t in other_tags
        )
        title_html = ""
        if titles:
            t = titles[0][:40] + "…" if titles and len(titles[0]) > 40 else (titles[0] if titles else "")
            title_html = f'<div class="title">📹 {t}</div>'
        sign_html = f'<div class="sign">{sign[:60]}</div>' if sign else ""
        cards.append(f"""
        <div class="card">
          <div class="card-name">{name}</div>
          {sign_html}
          {title_html}
          <div class="card-tags">{badges}</div>
        </div>""")
    sections.append(f"""
    <section id="tag-{tag}">
      <h2 style="color:{color}">【{tag}】<span class="count">{len(uids)} 个UP</span></h2>
      <div class="cards">{''.join(cards)}</div>
    </section>""")

nav_items = "".join(
    f'<a href="#tag-{tag}" class="nav-item" style="--c:{tag_colors[tag]}">{tag} <sup>{len(tag_to_ups[tag])}</sup></a>'
    for tag in all_tags
)

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>我的关注 — UP主标签图谱</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: "PingFang SC","Microsoft YaHei",sans-serif; background:#0f1117; color:#e0e0e0; }}
  header {{ background:#1a1d27; padding:20px 40px; border-bottom:1px solid #2a2d3a; position:sticky; top:0; z-index:100; }}
  header h1 {{ font-size:1.4rem; color:#fff; }}
  header p {{ font-size:.85rem; color:#888; margin-top:4px; }}
  .nav {{ display:flex; flex-wrap:wrap; gap:8px; padding:16px 40px; background:#141620; border-bottom:1px solid #2a2d3a; }}
  .nav-item {{ text-decoration:none; color:var(--c); border:1px solid var(--c); border-radius:16px; padding:3px 10px; font-size:.8rem; transition:.15s; }}
  .nav-item:hover {{ background:var(--c); color:#111; }}
  main {{ max-width:1400px; margin:0 auto; padding:30px 40px; }}
  section {{ margin-bottom:40px; }}
  section h2 {{ font-size:1.15rem; margin-bottom:14px; display:flex; align-items:center; gap:10px; }}
  .count {{ font-size:.85rem; color:#888; font-weight:normal; }}
  .cards {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(200px,1fr)); gap:10px; }}
  .card {{ background:#1a1d27; border:1px solid #2a2d3a; border-radius:8px; padding:12px; transition:.15s; }}
  .card:hover {{ border-color:#4f9ef8; background:#1e2133; }}
  .card-name {{ font-weight:600; font-size:.95rem; color:#fff; margin-bottom:4px; }}
  .sign {{ font-size:.75rem; color:#888; margin-bottom:4px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
  .title {{ font-size:.75rem; color:#aaa; margin-bottom:6px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
  .card-tags {{ display:flex; flex-wrap:wrap; gap:4px; }}
  .badge {{ font-size:.68rem; padding:1px 6px; border-radius:8px; color:#fff; opacity:.85; }}
  .search-bar {{ margin-bottom:20px; }}
  .search-bar input {{ width:300px; padding:8px 14px; background:#1a1d27; border:1px solid #3a3d4a; border-radius:20px; color:#fff; font-size:.9rem; outline:none; }}
  .search-bar input:focus {{ border-color:#4f9ef8; }}
  .hidden {{ display:none !important; }}
</style>
</head>
<body>
<header>
  <h1>我的关注 — UP主标签图谱</h1>
  <p>共 715 个UP主 · {len(all_tags)} 个标签 · 多标签系统（一个UP可属于多个分类）</p>
</header>
<nav class="nav">{nav_items}</nav>
<main>
  <div class="search-bar">
    <input type="text" id="searchInput" placeholder="🔍 搜索UP主名称…" oninput="filterCards(this.value)">
  </div>
  {''.join(sections)}
</main>
<script>
function filterCards(q) {{
  q = q.trim().toLowerCase();
  document.querySelectorAll('.card').forEach(c => {{
    const name = c.querySelector('.card-name').textContent.toLowerCase();
    c.classList.toggle('hidden', q && !name.includes(q));
  }});
  document.querySelectorAll('section').forEach(s => {{
    const visible = [...s.querySelectorAll('.card')].some(c => !c.classList.contains('hidden'));
    s.classList.toggle('hidden', q && !visible);
  }});
}}
</script>
</body>
</html>"""

with open("up_tag_map.html", "w", encoding="utf-8") as f:
    f.write(html)
print("已生成 up_tag_map.html，共", len(all_tags), "个标签分组")
