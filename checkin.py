import httpx
import asyncio
import os

async def main():
    my_cookie_raw = os.environ.get('CAIWAN_COOKIE')
    if not my_cookie_raw:
        print("[菜玩自动签到] 错误: 未能在环境变量中找到 CAIWAN_COOKIE。")
        return
    my_cookie = my_cookie_raw.strip()
    
    url = "https://caigamer.com/sg_sign-list_today.htm"
    payload = {'action': "check"}
    headers = {
        'Cookie': my_cookie,
        # ▼▼▼ 这里是本次修正的地方 ▼▼▼
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Referer': 'https://caigamer.com/sg_sign.htm'，
        'Origin': 'https://caigamer.com',
        'X-Requested-With': 'XMLHttpRequest'
    }

    try:
        async with httpx.AsyncClient() as client:
            print("[菜玩自动签到] 正在立即发送签到请求...")
            response = await client.post(url, data=payload, headers=headers)
            response.raise_for_status()
            body = response.json()
            message = body.get('message', '未能解析服务器消息')
            print(f"[菜玩自动签到] 服务器响应: {message}")
            print("[菜玩自动签到] 任务完成。")
    except Exception as e:
        print(f"[菜玩自动签到] 签到过程中发生错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())
