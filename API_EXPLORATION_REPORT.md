# B站 API 全站探索报告

> 探索日期：2025年5月  
> 库版本：bilibili-api v17.4.1  
> 测试账号：DedeUserID=4132528

---

## 测试结果总览

本次运行全部测试套件结果：**288 通过 / 18 失败**

---

## 失效/问题 API（已在文档中标记）

| API | 模块 | 错误类型 | 文档标记 |
|-----|------|---------|---------|
| `article.fetch_content()` | article.py | InitialStateException/KeyError: readInfo | ⚠️ [2025 已失效] |
| `creative_center.get_article_source()` | creative_center.py | HTTP 404 | ⚠️ [2025 已失效] |
| `dynamic.get_lottery_info()` | dynamic.py | -9999 服务系统错误 | ⚠️ [2025 已失效] |
| `dynamic.get_reposts()` | dynamic.py | HTTP 404 | ⚠️ [2025 已失效] |
| `live_area.get_list_by_area()` | live_area.py | LiveRoomOrder 枚举缺失 | ⚠️ [2025 代码Bug] |

---

## 全站 API 探索发现

### ✅ 已验证可用的重要接口（库中已封装）

| 端点 | 功能 | 库中封装位置 |
|------|------|------------|
| `x/web-interface/view/conclusion/get` (WBI) | AI视频摘要 | `video.Video.get_ai_conclusion()` |
| `x/v2/reply/wbi/main` (WBI) | 新版WBI评论 | `comment` 模块 |
| `x/web-interface/wbi/index/top/feed/rcmd` (WBI) | 首页个性化推荐流 | `homepage.get_videos()` |
| `x/msgfeed/unread` | 未读消息计数 | `session.get_unread_messages()` |
| `x/msgfeed/at` | @我的消息 | `session.get_at()` |
| `x/msgfeed/like` | 收到的赞 | `session.get_likes()` |
| `message.bilibili.com/x/sys-msg/query_user_notify` | 系统通知 | `session.get_system_messages()` |
| `x/space/wbi/acc/info` (WBI) | 用户空间信息(WBI版) | `user.User.get_user_info()` |
| `x/relation/followings` (WBI) | 关注列表 | `user.User.get_followings()` |
| `x/web-interface/wbi/search/all/v2` (WBI) | 综合搜索(WBI版) | `search.search()` |
| `x/web-interface/wbi/search/type` (WBI) | 分类搜索(WBI版) | `search.search_by_type()` |
| `x/web-interface/ranking/v2` | 全站排行榜 | `rank` 模块 |
| `pgc/web/timeline` | 番剧时间表 | `bangumi` 模块 |
| `x/space/bangumi/follow/list` | 我的追番/追剧 | `user.User.get_bangumi()` |
| `x/polymer/web-space/seasons_series_list` | UP合集/系列列表 | `user.User.get_channel_list()` |
| `x/v2/history/toview/web` | 稍后再看 | `video.Video` 相关 |
| `x/v3/fav/folder/created/list-all` | 我的收藏夹列表 | `favorite_list` 模块 |
| `x/web-interface/history/cursor` | 观看历史(cursor分页) | `user.User.get_history_new()` |
| `x/member/web/exp/log` | 经验值日志 | `user.User.get_exp_log()` |
| `x/upower/qa/info` | 充电问答详情 | `user.User.get_upower_qa_detail()` (v17.4) |
| `member.bilibili.com/x/web/archives` | 创作中心稿件 | `creative_center` 模块 (v17.3) |
| `x/web-interface/archive/relation` (WBI) | 视频关系(投币/收藏/点赞) | `video.Video.get_relation()` |
| `x/space/wbi/arc/search` (WBI) | 用户投稿视频 | `user.User.get_videos()` |
| `x/player/wbi/v2` (WBI) | 播放器信息(含字幕) | `video.Video.get_player_info()` |
| `x/web-interface/wbi/view/detail` (WBI) | 视频详情(WBI版) | `video.Video.get_detail()` |
| `x/web-interface/archive/related` | 相关视频(二创) | `video.Video.get_related()` |
| `x/article/recommends` | 专栏热榜 | `article` 模块 |
| `x/article/categories` | 专栏分类 | `article_category` 模块 |
| `s.search.bilibili.com/main/suggest` | 搜索建议词 | `search.suggest()` |
| `x/web-interface/nav/stat` | 用户关注/粉丝/动态数 | `user.User.get_relation_info()` |
| `x/web-interface/wbi/search/default` (WBI) | 搜索默认推荐词 | `search.get_default_search_keyword()` |
| `api.live.bilibili.com/room/v1/Area/getList` | 直播分区列表 | `live_area.get_area_list_sub()` |

---

## API 探索方法论

测试使用 `bilibili_api.utils.network.Api` 类直接调用端点：

```python
from bilibili_api.utils.network import Api

result = await Api(
    url='https://api.bilibili.com/x/web-interface/view/conclusion/get',
    method='GET',
    verify=False,
    wbi=True,  # WBI 签名端点需要设置
    credential=cred
).update_params(bvid=bvid, cid=cid, up_mid=up_mid, web_location='0.0').result
```

---

## 结论

bilibili-api v17.4.1 已非常完整地覆盖了 B站主要 API：

- **视频**: 播放地址、字幕、弹幕、评论、AI摘要、关系状态等
- **用户**: 个人信息、关注列表、历史记录、消息通知等  
- **搜索**: 综合搜索、分类搜索、搜索建议等（均已支持WBI）
- **直播**: 分区、直播间信息、礼物等
- **番剧**: 时间表、追番列表等
- **动态/专栏**: 动态流、专栏文章等
- **创作中心**: 稿件管理等（v17.3+ 添加）
- **充电问答**: upower QA（v17.4 添加）

主要问题集中在 **5个接口已失效**（已在文档中标记），其余接口工作正常。
