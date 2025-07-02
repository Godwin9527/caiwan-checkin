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
    # 我们的目标是“今天”的零点，所以先获取“明天”的日期，再把时间设为0点
    target_time = (now_beijing + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

    # 脚本的实际目标是“即将到来”的那个零点，所以要和“今天”的零点作比较
    today_target = now_beijing.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 如果脚本启动时，已经超过了今天的零点5秒以上，那就认为目标是明天的零点（防止重复执行）
    if (now_beijing - today_target).total_seconds() > 5:
        final_target_time = target_time
    else:
        final_target_time = today_target
    
    # 如果脚本是在23:59启动的，那么目标就是几秒或几十秒后的那个零点
    if now_beijing.hour == 23 and now_beijing.minute == 59:
        final_target_time = (now_beijing + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)


    print(f"[精度控制] 签到目标时间: {final_target_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # 计算需要等待的秒数
    delay_seconds = (final_target_time - now_beijing).total_seconds()

    # 如果计算出的延迟大于0（意味着还没到零点）且小于65秒（为启动延迟留出余量），则执行等待
    if 0 < delay_seconds < 65:
        print(f"[精度控制] 距离目标时间还有 {delay_seconds:.2f} 秒，开始等待...")
        await asyncio.sleep(delay_seconds)
        print(f"[精度控制] 精确时间已到达，立即执行签到！")
    else:
        print(f"[精度控制] 已过目标时间或无需等待，立即执行签到。")


async def main():
    """
    主函数，用于执行菜玩网的自动签到。
    """
    # 步骤一：执行秒级精度等待
    await wait_for_precise_time()
    
    # 步骤二：读取机密信息和执行签到
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
