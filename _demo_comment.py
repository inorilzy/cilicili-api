import asyncio, os
from bilibili_api import Credential, comment
from bilibili_api.comment import CommentResourceType


async def main():
    cred = Credential(
        sessdata=os.environ["BILI_SESSDATA"],
        bili_jct=os.environ["BILI_CSRF"],
        buvid3=os.environ["BILI_BUVID3"],
        dedeuserid=os.environ["BILI_DEDEUSERID"],
    )

    oid = 116561268441354  # 视频aid
    root_rpid = 302416060928  # 要回复的评论rpid

    # 获取评论列表
    print("=== 获取评论 ===")
    result = await comment.get_comments(
        oid=oid,
        type_=CommentResourceType.VIDEO,
        page_index=1,
        credential=cred,
    )
    total = result.get("page", {}).get("count", 0)
    print(f"总评论数: {total}")
    print()

    replies = result.get("replies", []) or []
    for i, r in enumerate(replies[:3]):
        user = r["member"]["uname"]
        content = r["content"]["message"][:60]
        rpid = r["rpid"]
        like = r["like"]
        rcount = r.get("rcount", 0)
        print(f"[{i+1}] rpid={rpid}")
        print(f"     用户={user} | 点赞={like} | 子评论数={rcount}")
        print(f"     {content}")
        print()

    print("=== 发送评论（演示代码，注释掉防止实际发送）===")
    print()

    # 以下代码演示如何发送评论，取消注释即可发送
    # 1. 发送根评论（直接评论视频）
    """
    result = await comment.send_comment(
        text="这个视频很有用！",
        oid=oid,
        type_=CommentResourceType.VIDEO,
        credential=cred,
    )
    print("发送评论:", result)
    """

    # 2. 回复某条评论
    """
    result = await comment.send_comment(
        text="同意你的看法！",
        oid=oid,
        type_=CommentResourceType.VIDEO,
        root=root_rpid,  # 回复的目标评论rpid
        credential=cred,
    )
    print("回复评论:", result)
    """

    # 3. 点赞评论
    """
    result = await comment.like_comment(
        oid=oid,
        type_=CommentResourceType.VIDEO,
        rpid=root_rpid,
        status=True,  # True=点赞, False=取消点赞
        credential=cred,
    )
    print("点赞结果:", result)
    """

    print("提示：取消上方代码的注释即可实际发送/回复/点赞评论")


asyncio.run(main())
