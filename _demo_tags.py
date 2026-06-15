import json

with open("up_tag_db.json", encoding="utf-8") as f:
    db = json.load(f)

# 查询 萌宠 标签
tag = "萌宠"
uids = db["tag_to_ups"].get(tag, [])
print(f"=== 标签 [{tag}] 共{len(uids)}个UP ===")
for uid in uids[:10]:
    info = db["up_tags"][uid]
    name = info["name"]
    tags = info["tags"]
    print(f"  {name}  标签:{tags}")

print()

# 查询某个UP的标签
for uid, info in db["up_tags"].items():
    if "北航" in info["name"]:
        name = info["name"]
        tags = info["tags"]
        sign = info["sign"]
        titles = info["recent_titles"]
        print(f"=== UP: {name} ===")
        print(f"  标签: {tags}")
        print(f"  简介: {sign}")
        print(f"  最新视频: {titles}")
