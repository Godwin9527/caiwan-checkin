import httpx
import asyncio
import os

async def main():
    """
    主函数，用于执行菜玩网的自动签到。
    """
    # 从环境变量中读取机密信息，并使用 .strip() 清理前后多余的空格和换行符
    my_cookie_raw = os.environ.get('CAIWAN_COOKIE')

    # 检查原始值是否存在
    if not my_cookie_raw:
        print("[菜玩自动签到] 错误: 未能在环境变量中找到 CAIWAN_COOKIE。请检查 GitHub Secrets 配置。")
        return

    # 清理字符串
    my_cookie = my_cookie_raw.strip()

    # --- 请求信息 ---
    url = "https://caigamer.com/sg_sign-list_today.htm"
    
    payload = {
        'action': "check"
    }
    
    headers = {
        'Cookie': my_cookie,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Referer': 'https://caigamer.com/sg_sign.htm',
        'Origin': 'https://caigamer.com',
        'X-Requested-With': 'XMLHttpRequest'
    }

    # --- 执行请求 ---
    try:
        async with httpx.AsyncClient() as client:
            print("[菜玩自动签到] 正在尝试签到...")
            response = await client.post(url, data=payload, headers=headers)
            response.raise_for_status()

            body = response.json()
            message = body.get('message', '未能解析服务器消息')
            print(f"[菜玩自动签到] 服务器响应: {message}")
            print("[菜玩自动签到] 任务完成。")

    except httpx.HTTPStatusError as e:
        print(f"[菜玩自动签到] 请求失败，HTTP 状态码: {e.response.status_code}")
        print("这通常意味着 Cookie 已失效，请及时更新 GitHub Secrets 中的 CAIWAN_COOKIE。")
    except Exception as e:
        print(f"[菜玩自动签到] 发生未知错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())
