# Bilibili 评论抓取 API 整理

基于当前项目中实际使用到的接口整理，便于后续项目复用。

涉及源码：
- `bilibili_gun_code_scraper.py`
- `main_test.py`
- `get_cookies.py`

---

## 1. 获取视频信息（BV → AID）

### 接口

```http
GET https://api.bilibili.com/x/web-interface/view
```

### 用途

通过 `bvid` 获取视频基础信息，当前项目主要用它拿：
- `aid`
- `title`

后续评论接口需要使用 `aid` 作为 `oid`。

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `bvid` | string | 是 | B站视频 BV 号，例如 `BV1xxxxx` |

### 请求示例

```http
GET https://api.bilibili.com/x/web-interface/view?bvid=BV1xxxxx
```

Python 示例：

```python
import requests

url = "https://api.bilibili.com/x/web-interface/view"
params = {"bvid": "BV1xxxxx"}
headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.bilibili.com/",
}

resp = requests.get(url, params=params, headers=headers)
data = resp.json()
print(data)
```

### 当前项目中使用到的返回字段

```json
{
  "code": 0,
  "message": "0",
  "data": {
    "aid": 123456789,
    "title": "视频标题",
    "bvid": "BV1xxxxx"
  }
}
```

### 关键字段

| 字段路径 | 说明 |
|---|---|
| `code` | 0 表示成功 |
| `message` | 错误信息 |
| `data.aid` | 评论接口所需的视频 ID |
| `data.title` | 视频标题 |
| `data.bvid` | BV 号 |

---

## 2. 获取一级评论

### 接口

```http
GET https://api.bilibili.com/x/v2/reply/main
```

### 用途

获取视频的一级评论列表。

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `oid` | int | 是 | 目标对象 ID；视频场景下为 `aid` |
| `type` | int | 是 | 目标类型；视频评论固定为 `1` |
| `mode` | int | 是 | 排序模式。项目中用到 `2` 和 `3` |
| `ps` | int | 否 | 每页数量，项目中用 `20` |
| `next` | int | 否 | 分页游标，第一页通常从 `0` 开始 |

### `mode` 说明

| 值 | 含义 | 当前项目用途 |
|---|---|---|
| `2` | 按时间排序 | `main_test.py` 用于尽量抓全评论 |
| `3` | 按热度排序 | `bilibili_gun_code_scraper.py` 用于优先找热评里的改枪码 |

### 请求示例

```http
GET https://api.bilibili.com/x/v2/reply/main?oid=123456789&type=1&mode=2&next=0&ps=20
```

Python 示例：

```python
import requests

url = "https://api.bilibili.com/x/v2/reply/main"
params = {
    "oid": 123456789,
    "type": 1,
    "mode": 2,
    "next": 0,
    "ps": 20,
}
headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.bilibili.com/",
}

resp = requests.get(url, params=params, headers=headers)
data = resp.json()
print(data)
```

### 当前项目中使用到的返回字段

```json
{
  "code": 0,
  "message": "0",
  "data": {
    "cursor": {
      "next": 20,
      "is_end": false
    },
    "replies": [
      {
        "rpid": 111,
        "rcount": 3,
        "ctime": 1710000000,
        "like": 15,
        "member": {
          "uname": "用户名",
          "mid": 12345
        },
        "content": {
          "message": "评论内容"
        }
      }
    ]
  }
}
```

### 关键字段

| 字段路径 | 说明 |
|---|---|
| `data.cursor.next` | 下一页游标 |
| `data.cursor.is_end` | 是否结束 |
| `data.replies` | 一级评论数组 |
| `data.replies[].rpid` | 一级评论 ID，抓二级评论时需要 |
| `data.replies[].rcount` | 回复数量 |
| `data.replies[].member.uname` | 评论用户名 |
| `data.replies[].member.mid` | 用户 ID |
| `data.replies[].content.message` | 评论内容 |
| `data.replies[].ctime` | 评论时间戳 |
| `data.replies[].like` | 点赞数 |

### 分页逻辑

```python
next_cursor = 0

while True:
    params = {
        "oid": aid,
        "type": 1,
        "mode": 2,
        "next": next_cursor,
        "ps": 20,
    }
    data = requests.get(url, params=params, headers=headers).json()

    replies = data.get("data", {}).get("replies", [])
    cursor = data.get("data", {}).get("cursor", {})

    # 处理 replies

    if cursor.get("is_end"):
        break

    next_cursor = cursor.get("next", 0)
    if next_cursor == 0:
        break
```

---

## 3. 获取二级评论（某条一级评论下的回复）

### 接口

```http
GET https://api.bilibili.com/x/v2/reply/reply
```

### 用途

获取某条一级评论下的所有二级评论。

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `oid` | int | 是 | 视频 `aid` |
| `type` | int | 是 | 视频评论固定为 `1` |
| `root` | int | 是 | 一级评论的 `rpid` |
| `ps` | int | 否 | 每页条数，项目中用 `20` |
| `pn` | int | 否 | 页码，从 `1` 开始 |

### 请求示例

```http
GET https://api.bilibili.com/x/v2/reply/reply?oid=123456789&type=1&root=111&ps=20&pn=1
```

Python 示例：

```python
import requests

url = "https://api.bilibili.com/x/v2/reply/reply"
params = {
    "oid": 123456789,
    "type": 1,
    "root": 111,
    "ps": 20,
    "pn": 1,
}
headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.bilibili.com/",
}

resp = requests.get(url, params=params, headers=headers)
data = resp.json()
print(data)
```

### 当前项目中使用到的返回字段

```json
{
  "code": 0,
  "message": "0",
  "data": {
    "page": {
      "count": 35
    },
    "replies": [
      {
        "ctime": 1710000000,
        "like": 2,
        "member": {
          "uname": "回复用户",
          "mid": 54321
        },
        "content": {
          "message": "二级评论内容"
        }
      }
    ]
  }
}
```

### 关键字段

| 字段路径 | 说明 |
|---|---|
| `data.page.count` | 回复总数 |
| `data.replies` | 二级评论数组 |
| `data.replies[].member.uname` | 回复用户名 |
| `data.replies[].member.mid` | 回复用户 ID |
| `data.replies[].content.message` | 回复内容 |
| `data.replies[].ctime` | 回复时间戳 |
| `data.replies[].like` | 点赞数 |

### 分页逻辑

```python
page = 1

while True:
    params = {
        "oid": aid,
        "type": 1,
        "root": root_rpid,
        "ps": 20,
        "pn": page,
    }
    data = requests.get(url, params=params, headers=headers).json()

    replies = data.get("data", {}).get("replies", [])
    total = data.get("data", {}).get("page", {}).get("count", 0)

    # 处理 replies

    if page * 20 >= total:
        break

    page += 1
```

---

## 4. 当前项目里的请求头配置

项目中使用的基础请求头：

```python
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/"
}
```

在 `bilibili_gun_code_scraper.py` 里还支持直接带 `SESSDATA`：

```python
SESSDATA = ""
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/",
    "Cookie": f"SESSDATA={SESSDATA}" if SESSDATA else ""
}
```

在 `main_test.py` 里则是通过 `cookies.pkl` 把浏览器登录态写入 `requests.Session()`：

```python
for cookie in cookies:
    session.cookies.set(cookie['name'], cookie['value'], domain=cookie.get('domain'))
```

---

## 5. 登录态获取方式

### 文件

- `get_cookies.py`

### 方式

使用 Selenium 打开 B站登录页，手动登录后保存 Cookie 到本地：

```python
cookies = driver.get_cookies()
with open('cookies.pkl', 'wb') as f:
    pickle.dump(cookies, f)
```

### 用途

后续项目如果需要更多评论数据、减少接口限制，可以复用这套 Cookie 加载方式。

---

## 6. 当前项目实际抽象出的可复用 API 能力

后续项目可以直接抽成 3 个方法：

```python
def get_video_info_by_bvid(bvid):
    ...


def get_main_replies(aid, mode=2, next_cursor=0, ps=20):
    ...


def get_sub_replies(aid, root_rpid, pn=1, ps=20):
    ...
```

推荐统一返回原始 JSON，业务层再做字段提取。

---

## 7. 建议的后续封装结构

可以在后续项目里封装成类似：

```python
class BilibiliCommentClient:
    def __init__(self, session=None, headers=None):
        ...

    def get_video_info_by_bvid(self, bvid: str):
        ...

    def get_main_replies(self, aid: int, mode: int = 2, next_cursor: int = 0, ps: int = 20):
        ...

    def get_sub_replies(self, aid: int, root_rpid: int, pn: int = 1, ps: int = 20):
        ...
```

这样后面做：
- 批量评论抓取
- 评论关键词提取
- 改枪码提取
- 评论落库
- 接口代理层

都会更方便。

---

## 8. 注意事项

1. 这些接口是当前项目里“实际跑过”的接口，不是完整 B站评论 API 全量清单。
2. 不带登录态时，可能拿不到完整评论，或二级评论受限。
3. 请求过快可能触发限流，当前项目中已通过 `time.sleep(0.5)` / `time.sleep(1)` 做简单限速。
4. `reply/main` 的分页依赖 `cursor.next`，不要自己硬编码页码。
5. `reply/reply` 的分页是传统 `pn` 页码模式。

---

## 9. 当前项目用到的接口总表

| 名称 | 方法 | URL | 主要用途 |
|---|---|---|---|
| 获取视频信息 | GET | `https://api.bilibili.com/x/web-interface/view` | `bvid` 转 `aid`，取标题 |
| 获取一级评论 | GET | `https://api.bilibili.com/x/v2/reply/main` | 获取视频主评论 |
| 获取二级评论 | GET | `https://api.bilibili.com/x/v2/reply/reply` | 获取某条主评论下的回复 |

---

## 10. 最小复用流程

```text
bvid
  -> /x/web-interface/view
  -> 拿到 aid
  -> /x/v2/reply/main
  -> 拿到一级评论和 rpid
  -> /x/v2/reply/reply
  -> 拿到二级评论
```

如果你愿意，我下一步可以继续帮你把这些接口直接抽成一个可 import 的模块，比如：
- `bilibili_api.py`
- `clients/bilibili_comment_client.py`
- 带上统一异常处理、分页迭代器、Cookie 加载
