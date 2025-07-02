import httpx
import asyncio
import os

async def main():
    """
    主函数，用于执行菜玩网的自动签到。
    """
    # 从环境变量中安全地读取名为 'CAIWAN_COOKIE' 的机密信息
    my_cookie = os.environ.get('CAIWAN_COOKIE')

    # 如果没有在环境中找到 Cookie，则打印错误并退出
    if not my_cookie:
        print("[菜玩自动签到] 错误: 未能在环境变量中找到 CAIWAN_COOKIE。请检查 GitHub Secrets 配置。")
        return

    # --- 请求信息 ---
    url = "https://caigamer.com/sg_sign-list_today.htm"
    
    payload = {
        'action': "check"
    }
    
    # 使用从环境变量中读取的 Cookie，并添加必要的其他请求头
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
            # 检查 HTTP 状态码，如果不是 200-299，则会引发异常
            response.raise_for_status()

            body = response.json()
            # 打印服务器返回的实际消息
            message = body.get('message', '未能解析服务器消息')
            print(f"[菜玩自动签到] 服务器响应: {message}")
            print("[菜玩自动签到] 任务完成。")

    except httpx.HTTPStatusError as e:
        # 处理网络请求错误，例如 403 Forbidden (Cookie失效) 或 500 Internal Server Error
        print(f"[菜玩自动签到] 请求失败，HTTP 状态码: {e.response.status_code}")
        print("这通常意味着 Cookie 已失效，请及时更新 GitHub Secrets 中的 CAIWAN_COOKIE。")
    except Exception as e:
        # 处理其他所有可能的错误，例如网络连接问题、JSON 解析失败等
        print(f"[菜玩自动签到] 发生未知错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())
