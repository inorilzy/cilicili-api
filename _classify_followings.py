"""
获取所有关注的 UP 主列表，获取其最新视频标题，并按内容分类。
"""
import asyncio
import os
import json
import time
from collections import defaultdict
from bilibili_api import Credential, user
from bilibili_api.utils.network import Api


async def get_all_followings(uid: int, cred: Credential) -> list[dict]:
    """获取所有关注列表（并发分页）"""
    all_ups = []
    # 先获取第一页知道总数
    result = await Api(
        url="https://api.bilibili.com/x/relation/followings",
        method="GET",
        verify=True,
        wbi=True,
        credential=cred,
    ).update_params(vmid=uid, pn=1, ps=50, order="desc").result
    total = result.get("total", 0)
    ups = result.get("list", []) or []
    all_ups.extend(ups)
    print(f"  第1页: {len(ups)} 个UP，总计 {total} 个")

    pages = (total + 49) // 50
    for pn in range(2, pages + 1):
        await asyncio.sleep(0.3)  # 避免频控
        result = await Api(
            url="https://api.bilibili.com/x/relation/followings",
            method="GET",
            verify=True,
            wbi=True,
            credential=cred,
        ).update_params(vmid=uid, pn=pn, ps=50, order="desc").result
        ups = result.get("list", []) or []
        all_ups.extend(ups)
        print(f"  第{pn}页: {len(ups)} 个UP")
        if len(ups) < 50:
            break
    return all_ups


async def get_up_recent_videos(uid: int, cred: Credential, ps: int = 5) -> list[str]:
    """获取UP主最近的视频标题"""
    try:
        result = await Api(
            url="https://api.bilibili.com/x/space/wbi/arc/search",
            method="GET",
            verify=False,
            wbi=True,
            credential=cred,
        ).update_params(mid=uid, pn=1, ps=ps, tid=0, keyword="", order="pubdate").result
        vlist = result.get("list", {}).get("vlist", []) or []
        return [v.get("title", "") for v in vlist]
    except Exception:
        return []


def categorize_up(name: str, sign: str, titles: list[str]) -> str:
    """基于名称、简介和视频标题进行分类"""
    all_text = " ".join([name, sign] + titles).lower()

    categories = {
        "游戏": ["游戏", "galgame", "steam", "minecraft", "原神", "mc", "fps", "moba",
                 "王者", "英雄联盟", "lol", "rpg", "cs:", "博德之门", "艾尔登法环", "elden", "实况"],
        "技术/编程": ["python", "java", "代码", "编程", "开发", "程序员", "ai", "算法", "前端", "后端",
                   "linux", "docker", "git", "机器学习", "深度学习", "大模型", "llm", "gpt",
                   "pytorch", "tensorflow", "cpu", "gpu", "硬件", "单片机", "嵌入式"],
        "数码/科技": ["电脑", "手机", "评测", "开箱", "苹果", "iphone", "安卓", "显卡", "处理器",
                   "intel", "amd", "nvidia", "相机", "镜头", "摄影", "科技"],
        "动漫/二次元": ["动漫", "番剧", "漫画", "二次元", "acg", "gal", "cos", "cosplay", "vtuber",
                    "vtb", "虚拟", "声优", "原声", "op", "ed", "mad", "amv"],
        "音乐": ["音乐", "cover", "翻唱", "歌曲", "演奏", "钢琴", "吉他", "歌手", "乐队",
               "作曲", "编曲", "beat", "说唱", "rap"],
        "生活/Vlog": ["vlog", "日常", "生活", "旅行", "美食", "料理", "做饭", "健身", "运动",
                    "减肥", "购物", "好物", "开箱", "探店"],
        "知识/教育": ["知识", "教程", "教学", "学习", "历史", "科普", "数学", "物理", "化学",
                   "讲解", "分析", "干货", "考研", "高考"],
        "电影/影视": ["电影", "影视", "剧", "观影", "解说", "混剪", "好看", "影评", "拆解"],
        "创作/绘画": ["绘画", "插画", "漫画创作", "设计", "ps", "3d", "建模", "动画制作"],
        "新闻/时事": ["新闻", "时事", "政治", "经济", "国际", "社会", "热点"],
        "体育/竞技": ["体育", "篮球", "足球", "nba", "cba", "电竞", "比赛", "赛事"],
    }

    scores = defaultdict(int)
    for cat, keywords in categories.items():
        for kw in keywords:
            if kw in all_text:
                scores[cat] += 1

    if scores:
        return max(scores, key=scores.get)
    return "综合/其他"


async def main():
    cred = Credential(
        sessdata=os.environ["BILI_SESSDATA"],
        bili_jct=os.environ["BILI_CSRF"],
        buvid3=os.environ["BILI_BUVID3"],
        dedeuserid=os.environ["BILI_DEDEUSERID"],
    )

    MY_UID = 4132528

    print("=== 第一步: 获取所有关注 ===")
    all_ups = await get_all_followings(MY_UID, cred)
    print(f"总计获取: {len(all_ups)} 个UP\n")

    # 保存基础信息
    up_info = {}
    for up in all_ups:
        mid = up.get("mid") or up.get("uid")
        if mid:
            up_info[mid] = {
                "name": up.get("uname", ""),
                "sign": up.get("sign", "") or "",
                "face": up.get("face", ""),
            }

    print(f"=== 第二步: 获取各UP最新视频 (共{len(up_info)}个UP，每个5条) ===")
    print("预计耗时约3-5分钟...")

    classified = defaultdict(list)
    done = 0
    for mid, info in up_info.items():
        await asyncio.sleep(0.2)  # 每200ms一个请求
        titles = await get_up_recent_videos(mid, cred, ps=5)
        cat = categorize_up(info["name"], info["sign"], titles)
        classified[cat].append({
            "uid": mid,
            "name": info["name"],
            "sign": info["sign"][:30] if info["sign"] else "",
            "recent_titles": titles[:3],
            "category": cat,
        })
        done += 1
        if done % 50 == 0:
            print(f"  已处理 {done}/{len(up_info)} 个UP...")

    print(f"\n=== 分类结果 ===")
    total_check = 0
    result_data = {}
    for cat in sorted(classified.keys(), key=lambda x: -len(classified[x])):
        ups_in_cat = classified[cat]
        total_check += len(ups_in_cat)
        result_data[cat] = ups_in_cat
        print(f"\n【{cat}】({len(ups_in_cat)}个UP)")
        for up in ups_in_cat[:5]:
            print(f"  {up['name']} (uid={up['uid']})")
            if up["recent_titles"]:
                print(f"    最新视频: {up['recent_titles'][0][:40]}")
        if len(ups_in_cat) > 5:
            print(f"  ... 还有 {len(ups_in_cat)-5} 个")

    print(f"\n总计分类: {total_check} 个UP")

    # 保存完整结果
    with open("up_categories.json", "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    print("\n完整结果已保存至 up_categories.json")


if __name__ == "__main__":
    asyncio.run(main())
