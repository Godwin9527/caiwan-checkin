import httpx
import asyncio
import os
import traceback  # <--- 关键修改：导入 traceback 模块

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
        # 使用超时设置，避免程序因网络问题卡死
        async with httpx.AsyncClient(timeout=30.0) as client: # <--- 关键修改：增加超时设置
            print("[菜玩自动签到] 正在尝试签到...")
            response = await client.post(url, data=payload, headers=headers)
            
            # 这会检查响应状态码是否为 2xx，如果不是，则抛出 HTTPStatusError 异常
            response.raise_for_status()

            body = response.json()
            message = body.get('message', '未能解析服务器消息')
            print(f"[菜玩自动签到] 服务器响应: {message}")
            print("[菜玩自动签到] 任务完成。")

    except httpx.HTTPStatusError as e:
        # <--- 关键修改：增强 HTTP 错误日志 ---
        print(f"[菜玩自动签到] 请求失败，HTTP 状态码: {e.response.status_code}")
        print(f"[菜玩自动签到] 服务器原始响应: {e.response.text}") # 打印服务器返回的具体内容
        print("这通常意味着 Cookie 已失效，请及时更新 GitHub Secrets 中的 CAIWAN_COOKIE。")
        # ------------------------------------

    except Exception as e:
        # <--- 关键修改：增强未知错误日志 ---
        print(f"[菜玩自动签到] 发生未知错误。")
        print(f"错误类型: {type(e)}")
        print(f"错误详情: {e}")
        print("--- 完整的错误追溯信息 ---")
        traceback.print_exc() # 打印完整的错误调用栈
        print("--------------------------")
        # ------------------------------------


if __name__ == "__main__":
    asyncio.run(main())
