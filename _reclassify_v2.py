"""
优化版 UP 主分类脚本 - 使用已缓存的 up_categories.json 数据重新分类
"""
import json
from collections import defaultdict


def categorize_up_v2(name: str, sign: str, titles: list[str]) -> str:
    """改进版分类，覆盖更多中文内容关键词"""
    all_text = " ".join([name, sign] + titles).lower()

    categories = {
        "美食/烹饪": [
            "做法", "食谱", "好吃", "炒", "煮", "蒸", "炸", "烤", "炖", "凉拌", "腌",
            "排骨", "鸡胸肉", "牛肉", "红烧", "美食", "料理", "菜谱", "下饭", "食材",
            "食欲", "吃货", "减脂餐", "低卡", "家常菜", "螃蟹", "赶海", "海鲜", "鱼干",
            "油麦菜", "荔枝", "烤鸡", "药膳", "饭", "碗", "锅", "早餐", "餐厅", "美味",
            "酱料", "调料", "零食", "小吃", "街头", "探店", "吃播",
        ],
        "萌宠": [
            "猫", "狗", "宠物", "貓", "meme", "猫咪", "猫猫", "喵", "汪", "鸟", "兔",
            "宠物店", "铲屎官", "柴犬", "金毛", "边牧", "橘猫", "英短", "美短",
        ],
        "穿搭/时尚": [
            "穿搭", "时尚", "搭配", "outfit", "ootd", "好物", "平替", "护肤", "化妆",
            "彩妆", "口红", "发型", "美妆", "美容", "显瘦", "显高", "宝藏", "测评穿",
            "衣服", "裤子", "裙子", "短袖", "外套", "鞋",
        ],
        "健康/减肥": [
            "减脂", "减肥", "瘦身", "健康", "卡路里", "体重", "塑形", "增肌", "瑜伽",
            "跑步", "运动打卡", "健身操", "有氧", "燃脂", "低脂", "低卡", "fitlife",
        ],
        "情感/心理": [
            "情感", "恋爱", "爱情", "分手", "婚姻", "关系", "心理", "情绪", "自我",
            "励志", "正能量", "治愈", "疗愈", "内耗", "焦虑", "抑郁", "pta", "pta控",
            "男友", "女友", "喜欢", "爱你", "暗恋", "心动", "伤心",
        ],
        "搞笑/段子": [
            "搞笑", "段子", "沙雕", "整活", "鬼畜", "抗压", "压力", "厌蠢症",
            "炸串", "憋笑", "整蛊", "恶搞", "笑话", "沙雕日常", "蠢萌",
        ],
        "财经/商业": [
            "商业", "财经", "品牌", "消费", "钱", "投资", "经济", "股票", "房价",
            "市场", "创业", "公司", "企业", "华谊", "比亚迪", "营销", "广告", "运营",
            "暗中观察", "财富", "破产", "倒闭", "上市",
        ],
        "语言学习": [
            "英语", "单词", "词根", "语法", "日语", "韩语", "法语", "德语", "学语言",
            "背单词", "口语", "听力", "翻译", "外语", "clud", "rupt",
        ],
        "旅行": [
            "旅行", "旅游", "出行", "景区", "打卡", "探险", "自驾", "徒步", "出发",
            "行程", "酒店", "攻略", "目的地", "海外", "国外", "出国", "留学",
        ],
        "游戏": [
            "游戏", "galgame", "steam", "minecraft", "原神", "mc", "fps", "moba",
            "王者", "英雄联盟", "lol", "rpg", "cs:", "博德之门", "艾尔登法环",
            "elden", "实况", "游戏解说", "打游戏", "通关", "攻略", "主播",
        ],
        "技术/编程": [
            "python", "java", "代码", "编程", "开发", "程序员", "ai", "算法",
            "前端", "后端", "linux", "docker", "git", "机器学习", "深度学习",
            "大模型", "llm", "gpt", "pytorch", "tensorflow", "cpu", "gpu",
            "硬件", "单片机", "嵌入式", "模型", "参数",
        ],
        "数码/科技": [
            "电脑", "手机", "评测", "开箱数码", "苹果", "iphone", "安卓", "显卡",
            "处理器", "intel", "amd", "nvidia", "相机", "镜头", "摄影",
            "科技", "电子", "数码", "测评", "华为", "小米", "索尼",
        ],
        "生活/Vlog": [
            "vlog", "日常", "生活记录", "一天的", "今天", "周末", "假期", "打工人",
            "上班族", "上班", "下班", "租房", "独居", "宿舍", "班", "日记",
        ],
        "知识/教育": [
            "知识", "教程", "教学", "学习", "历史", "科普", "数学", "物理",
            "化学", "讲解", "分析", "干货", "考研", "高考", "百科", "冷知识",
        ],
        "动漫/二次元": [
            "动漫", "番剧", "漫画", "二次元", "acg", "gal", "cos", "cosplay",
            "vtuber", "vtb", "虚拟", "声优", "原声", "op", "ed", "mad", "amv",
            "鬼灭", "海贼", "进击", "demon", "slayer",
        ],
        "音乐": [
            "音乐", "cover", "翻唱", "歌曲", "演奏", "钢琴", "吉他", "歌手",
            "乐队", "作曲", "编曲", "beat", "说唱", "rap", "唱歌", "戏腔", "古风",
        ],
        "电影/影视": [
            "电影", "影视", "剧", "观影", "解说", "混剪", "好看", "影评",
            "拆解", "高燃", "催泪", "剧情", "国产剧", "美剧", "韩剧",
        ],
        "创作/绘画": [
            "绘画", "插画", "漫画创作", "设计", "ps", "3d", "建模", "动画制作",
            "画画", "插图", "手绘", "数位板", "cg", "素描", "水彩",
        ],
        "新闻/时事": [
            "新闻", "时事", "政治", "经济", "国际", "社会", "热点", "事件",
            "解析", "深度", "分析局势", "战争", "外交",
        ],
        "体育/竞技": [
            "体育", "篮球", "足球", "nba", "cba", "电竞", "比赛", "赛事",
            "梅西", "詹姆斯", "马刺", "湖人", "拳击", "格斗", "奥运",
        ],
        "军事": [
            "军事", "武器", "导弹", "坦克", "战机", "海军", "陆军", "空军",
            "战争", "战斗机", "航母", "核弹",
        ],
    }

    # 优先匹配规则（某些词更准确）
    priority = {
        "美食/烹饪": ["做法", "食谱", "炒", "煮", "蒸", "炸", "烤", "炖", "凉拌"],
        "萌宠": ["猫咪", "喵", "汪", "铲屎官"],
        "情感/心理": ["恋爱", "分手", "婚姻"],
    }

    scores = defaultdict(int)
    for cat, keywords in categories.items():
        for kw in keywords:
            if kw in all_text:
                weight = 2 if (cat in priority and kw in priority.get(cat, [])) else 1
                scores[cat] += weight

    if scores:
        return max(scores, key=scores.get)
    return "综合/其他"


def reclassify():
    # 读取已缓存数据
    with open("up_categories.json", encoding="utf-8") as f:
        data = json.load(f)

    # 把所有UP汇总
    all_ups = []
    for ups in data.values():
        all_ups.extend(ups)

    print(f"总计 {len(all_ups)} 个UP，重新分类中...")

    new_classified = defaultdict(list)
    for up in all_ups:
        name = up.get("name", "")
        sign = up.get("sign", "") or ""
        titles = up.get("recent_titles", []) or []
        cat = categorize_up_v2(name, sign, titles)
        new_classified[cat].append(up)

    print("\n=== 优化后分类结果 ===\n")
    total = 0
    result = {}
    for cat in sorted(new_classified.keys(), key=lambda x: -len(new_classified[x])):
        ups = new_classified[cat]
        total += len(ups)
        result[cat] = ups
        print(f"【{cat}】{len(ups)}个")
        for up in ups[:3]:
            titles = up.get("recent_titles", [])
            title_str = titles[0][:40] if titles else "(无视频)"
            print(f"  {up['name']}: {title_str}")
        if len(ups) > 3:
            print(f"  ... 还有{len(ups)-3}个")
        print()

    print(f"总计: {total} 个")

    # 保存优化结果
    with open("up_categories_v2.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("已保存至 up_categories_v2.json")


if __name__ == "__main__":
    reclassify()
