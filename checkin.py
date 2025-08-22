import httpx
import asyncio
import os
import traceback  # 导入 traceback 模块用于详细的错误报告
from datetime import datetime, timezone, timedelta

# --- 配置区 ---
# 定义目标时区为北京时间 (UTC+8)
TARGET_TIMEZONE = timezone(timedelta(hours=8))

async def wait_for_precise_time():
    """
    等待直到下一个北京时间 00:00:00。
    """
    现在_beijing = datetime.当前(TARGET_TIMEZONE)
    print(f"[精度控制] 当前北京时间: {now_beijing.strftime('%Y-%m-%d %H:%M:%S')}")

    # 计算下一个零点的目标时间
    final_target_time = (now_beijing + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 检查脚本是否在目标日期的前一个小时内启动
    if now_beijing.hour == 23:
        final_target_time = now_beijing.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    print(f"[精度控制] 签到目标时间: {final_target_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # 计算需要等待的秒数
    delay_seconds = (final_target_time - now_beijing).total_seconds()

    # ▼▼▼ 关键修改点 ▼▼▼
    # 将等待窗口修改为1860秒（31分钟），以适应提前半小时的启动窗口。
    if 0 < delay_seconds < 1860:
        print(f"[精度控制] 距离目标时间还有 {delay_seconds:.2f} 秒，开始等待...")
        await asyncio.sleep(delay_seconds)
        print(f"[精度控制] 精确时间已到达，立即执行签到！")
    else:
        print(f"[精度控制] 已过目标时间或无需等待，立即执行签到。")


async def main():
    """
    主函数，负责协调整个签到流程。
    """
    await wait_for_precise_time()
    
    # 从环境变量中获取 Cookie
    my_cookie_raw = os.environ.get('CAIWAN_COOKIE')
    if not my_cookie_raw:
        print("[菜玩自动签到] 错误: 未能在环境变量中找到 CAIWAN_COOKIE。")
        return
    my_cookie = my_cookie_raw.strip()
    
    # API 请求所需参数
    url = "https://caigamer.com/sg_sign-list_today.htm"
    payload = {'action': "check"}
    headers = {
        'Cookie': my_cookie,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Referer': 'https://caigamer.com/sg_sign.htm',
        'Origin': 'https://caigamer.com',
        'X-Requested-With': 'XMLHttpRequest'
    }

    response = None  # 在 try 块外部初始化，以便在 except 块中访问
    try:
        print("[菜玩自动签到] 正在发送签到请求...")
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload, headers=headers)
            # 如果状态码不是 2xx，这行会抛出 httpx.HTTPStatusError
            response.raise_for_status()
            
            # 尝试解析 JSON 响应
            body = response.json()
            message = body.get('message', '未能解析服务器消息')
            print(f"[菜玩自动签到] 服务器响应: {message}")
            print("[菜玩自动签到] 任务完成。")
            
    except Exception as e:
        print(f"[菜玩自动签到] 签到过程中发生错误。")
        print("--- 详细错误信息 ---")
        # 打印完整的错误堆栈，这是最关键的调试信息！
        traceback.print_exc()
        print("--------------------")

        # 检查 response 对象是否存在，并打印更多上下文信息
        if response is not None:
            print("--- HTTP 响应详情 ---")
            print(f"状态码 (Status Code): {response.status_code}")
            print(f"响应头 (Headers): {response.headers}")
            # 打印响应内容的前 500 个字符，以防内容过长
            print(f"响应内容 (Response Text): {response.text[:500]}")
            print("-----------------------")
        else:
            print("未能获取到 HTTP 响应对象，错误可能发生在网络连接阶段。")

# --- 程序入口 ---
if __name__ == "__main__":
    # 使用 asyncio.run() 来运行异步主函数
    asyncio.run(main())
