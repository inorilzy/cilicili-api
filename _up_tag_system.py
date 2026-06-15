"""
UP 主多标签系统 - 每个UP可以有多个标签
支持：
  - 按标签查找UP
  - 查看某个UP有哪些标签
  - 标签统计
"""
import json
from collections import defaultdict


TAGS = {
    "美食/烹饪": [
        "做法", "食谱", "好吃", "炒", "煮", "蒸", "炸", "烤", "炖", "凉拌", "腌",
        "排骨", "鸡胸肉", "牛肉", "红烧", "美食", "料理", "菜谱", "下饭", "食材",
        "食欲", "吃货", "家常菜", "螃蟹", "赶海", "海鲜", "鱼干", "荔枝", "烤鸡",
        "油麦菜", "药膳", "早餐", "探店美食", "吃播",
    ],
    "萌宠": [
        "猫", "狗", "宠物", "meme", "猫咪", "猫猫", "喵", "汪", "鸟", "兔",
        "铲屎官", "柴犬", "金毛", "边牧", "橘猫", "英短",
    ],
    "情感/心理": [
        "情感", "恋爱", "爱情", "分手", "婚姻", "关系", "心理", "情绪",
        "治愈", "疗愈", "内耗", "焦虑", "抑郁", "男友", "女友", "喜欢",
        "暗恋", "心动", "伤心", "操纵", "亲密关系",
    ],
    "穿搭/时尚": [
        "穿搭", "时尚", "搭配", "outfit", "ootd", "好物", "平替", "护肤",
        "化妆", "彩妆", "口红", "发型", "美妆", "美容", "显瘦", "衣服", "裙子",
    ],
    "健康/减肥": [
        "减脂", "减肥", "瘦身", "健康", "卡路里", "体重", "塑形", "增肌",
        "瑜伽", "跑步", "运动打卡", "有氧", "燃脂", "低脂", "低卡",
    ],
    "搞笑/段子": [
        "搞笑", "段子", "沙雕", "整活", "鬼畜", "抗压", "厌蠢症",
        "憋笑", "整蛊", "恶搞", "笑话", "蠢萌",
    ],
    "财经/商业": [
        "商业", "财经", "品牌", "消费", "投资", "经济", "股票", "市场",
        "创业", "公司", "企业", "营销", "广告", "财富", "破产", "倒闭",
        "暗中观察", "财务",
    ],
    "语言学习": [
        "英语", "单词", "词根", "语法", "日语", "韩语", "学语言",
        "背单词", "口语", "听力", "外语",
    ],
    "旅行": [
        "旅行", "旅游", "出行", "景区", "打卡", "探险", "自驾", "徒步",
        "行程", "酒店", "攻略", "出国", "海外",
    ],
    "游戏": [
        "游戏", "galgame", "steam", "minecraft", "原神", "mc", "fps", "moba",
        "王者", "英雄联盟", "lol", "rpg", "elden", "实况", "游戏解说", "打游戏",
        "通关", "全面战场",
    ],
    "技术/编程": [
        "python", "java", "代码", "编程", "开发", "程序员", "ai", "算法",
        "前端", "后端", "linux", "docker", "git", "机器学习", "深度学习",
        "大模型", "llm", "gpt", "pytorch", "tensorflow", "嵌入式", "opencode",
    ],
    "数码/科技": [
        "电脑", "手机", "评测", "苹果", "iphone", "安卓", "显卡", "处理器",
        "intel", "amd", "nvidia", "相机", "镜头", "摄影", "科技", "电子",
        "数码", "华为", "小米", "索尼", "测评",
    ],
    "生活/Vlog": [
        "vlog", "日常生活", "生活记录", "一天的", "周末", "独居",
        "打工人", "宿舍",
    ],
    "知识/教育": [
        "知识", "教程", "教学", "学习", "历史", "科普", "数学", "物理",
        "化学", "讲解", "干货", "考研", "高考", "百科", "冷知识",
    ],
    "动漫/二次元": [
        "动漫", "番剧", "漫画", "二次元", "acg", "gal", "cos", "cosplay",
        "vtuber", "vtb", "虚拟", "声优", "op", "ed", "mad", "amv",
    ],
    "音乐": [
        "音乐", "cover", "翻唱", "歌曲", "演奏", "钢琴", "吉他", "歌手",
        "乐队", "作曲", "编曲", "beat", "说唱", "rap", "唱歌", "戏腔",
    ],
    "电影/影视": [
        "电影", "影视", "剧", "观影", "解说", "混剪", "影评", "高燃", "剧情",
    ],
    "创作/绘画": [
        "绘画", "插画", "设计", "3d", "建模", "动画制作", "画画", "手绘",
        "素描", "水彩", "cg",
    ],
    "新闻/时事": [
        "新闻", "时事", "政治", "社会", "热点", "事件", "解析",
    ],
    "体育/竞技": [
        "体育", "篮球", "足球", "nba", "cba", "电竞", "比赛", "赛事",
    ],
    "军事": [
        "军事", "武器", "导弹", "坦克", "战机", "海军", "陆军", "空军",
    ],
}


def get_tags(name: str, sign: str, titles: list[str]) -> list[str]:
    """为UP主打多个标签"""
    all_text = " ".join([name, sign] + titles).lower()
    matched = []
    for tag, keywords in TAGS.items():
        for kw in keywords:
            if kw in all_text:
                matched.append(tag)
                break  # 该标签已匹配，跳过其余关键词
    return matched if matched else ["综合/其他"]


def build_tag_db():
    with open("up_categories.json", encoding="utf-8") as f:
        data = json.load(f)

    # 汇总所有UP
    all_ups = []
    for ups in data.values():
        all_ups.extend(ups)

    print(f"为 {len(all_ups)} 个UP主打标签...")

    # UP -> tags 映射
    up_tags_map = {}  # uid -> {name, tags, sign, recent_titles}
    # tag -> [uid, ...] 映射
    tag_to_ups = defaultdict(list)

    for up in all_ups:
        uid = str(up.get("uid") or up.get("mid", ""))
        name = up.get("name", "")
        sign = up.get("sign", "") or ""
        titles = up.get("recent_titles", []) or []
        tags = get_tags(name, sign, titles)

        up_tags_map[uid] = {
            "uid": uid,
            "name": name,
            "sign": sign[:50],
            "tags": tags,
            "recent_titles": titles[:3],
        }
        for tag in tags:
            tag_to_ups[tag].append(uid)

    # 保存结果
    result = {
        "up_tags": up_tags_map,          # 用于：查看某UP有哪些标签
        "tag_to_ups": dict(tag_to_ups),  # 用于：按标签查找UP
    }
    with open("up_tag_db.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 打印统计
    print("\n=== 标签统计（按数量排序）===\n")
    for tag in sorted(tag_to_ups.keys(), key=lambda t: -len(tag_to_ups[t])):
        count = len(tag_to_ups[tag])
        print(f"  {tag}: {count}个UP")

    # 打印多标签的示例
    multi_tag = [(uid, info) for uid, info in up_tags_map.items() if len(info["tags"]) > 2]
    print(f"\n=== 多标签UP主示例（共{len(multi_tag)}个有2+标签）===\n")
    for uid, info in sorted(multi_tag, key=lambda x: -len(x[1]["tags"]))[:10]:
        print(f"  {info['name']} [{', '.join(info['tags'])}]")

    print(f"\n数据已保存至 up_tag_db.json")
    return result


def query_by_tag(tag_db: dict, tag: str):
    """按标签查询UP主"""
    tag_to_ups = tag_db["tag_to_ups"]
    up_tags = tag_db["up_tags"]
    uids = tag_to_ups.get(tag, [])
    print(f'\n标签 "{tag}" 下的 {len(uids)} 个UP主:')
    for uid in uids:
        info = up_tags.get(uid, {})
        print(f"  {info.get('name')} (uid={uid}) 标签: {info.get('tags')}")


def query_up_tags(tag_db: dict, name: str):
    """查询UP主的标签"""
    up_tags = tag_db["up_tags"]
    for uid, info in up_tags.items():
        if name in info.get("name", ""):
            print(f"\nUP: {info['name']} (uid={uid})")
            print(f"  标签: {info['tags']}")
            print(f"  简介: {info.get('sign', '')}")
            print(f"  最新视频: {info.get('recent_titles', [])[:2]}")


if __name__ == "__main__":
    db = build_tag_db()
