"""按标签分组展示所有UP主"""
import json

with open("up_tag_db.json", encoding="utf-8") as f:
    db = json.load(f)

tag_to_ups = db["tag_to_ups"]
up_tags = db["up_tags"]

# 按标签数量排序，综合/其他放最后
all_tags = sorted(
    tag_to_ups.keys(),
    key=lambda t: (t == "综合/其他", -len(tag_to_ups[t]))
)

for tag in all_tags:
    uids = tag_to_ups[tag]
    print(f"\n{'='*60}")
    print(f"【{tag}】 共 {len(uids)} 个UP")
    print(f"{'='*60}")
    for uid in uids:
        info = up_tags.get(uid, {})
        name = info.get("name", uid)
        tags = info.get("tags", [])
        # 多标签的用+号标注其他标签
        other_tags = [t for t in tags if t != tag]
        tag_str = f" +{','.join(other_tags)}" if other_tags else ""
        print(f"  {name}{tag_str}")
