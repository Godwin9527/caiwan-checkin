import httpx
import asyncio
import os
from datetime import datetime, timezone, timedelta

# --- 配置区 ---
# 定义目标时区为北京时间 (UTC+8)
TARGET_TIMEZONE = timezone(timedelta(hours=8))

async def wait_for_precise_time():
    """
    等待直到下一个北京时间 00:00:00。
    """
    now_beijing = datetime.now(TARGET_TIMEZONE)
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
    await wait_for_precise_time()
    
    my_cookie_raw = os.environ.get('CAIWAN_COOKIE')
    if not my_cookie_raw:
        print("[菜玩自动签到] 错误: 未能在环境变量中找到 CAIWAN_COOKIE。")
        return
    my_cookie = my_cookie_raw.strip()
    
    url = "https://caigamer.com/sg_sign-list_today.htm"
    payload = {'action': "check"}
    headers = {
        'Cookie': my_cookie,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Referer': 'https://caigamer.com/sg_sign.htm',
        'Origin': 'https://caigamer.com',
        'X-Requested-With': 'XMLHttpRequest'
    }

    try:
        async with httpx.AsyncClient() as client:
            print("[菜玩自动签到] 正在发送签到请求...")
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
