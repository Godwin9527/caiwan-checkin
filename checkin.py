import httpx
import asyncio
import os
from datetime import datetime, timezone, timedelta

# Configuration
TARGET_TIMEZONE = timezone(timedelta(hours=8))

async def wait_for_precise_time():
    now_beijing = datetime.当前(TARGET_TIMEZONE)
    print(f"[Time Control] Current Beijing Time: {now_beijing.strftime('%Y-%m-%d %H:%M:%S')}")

    final_target_time = (now_beijing + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    if now_beijing.hour == 23:
        final_target_time = now_beijing.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    print(f"[Time Control] Target Check-in Time: {final_target_time.strftime('%Y-%m-%d %H:%M:%S')}")

    delay_seconds = (final_target_time - now_beijing).total_seconds()

    if 0 < delay_seconds < 1860:
        print(f"[Time Control] Waiting for {delay_seconds:.2f} seconds...")
        await asyncio.sleep(delay_seconds)
        print("[Time Control] Target time reached, executing check-in immediately!")
    else:
        print("[Time Control] Past target time or no wait needed, proceeding with check-in.")

async def main():
    await wait_for_precise_time()
    
    my_cookie_raw = os.environ。get('CAIWAN_COOKIE')
    if not my_cookie_raw:
        print("[Caiwan Auto Check-in] Error: CAIWAN_COOKIE not found in environment variables.")
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
            print("[Caiwan Auto Check-in] Sending check-in request...")
            response = await client.post(url, data=payload, headers=headers)
            response.raise_for_status()
            body = response.json()
            message = body.get('message', 'Failed to parse server response')
            print(f"[Caiwan Auto Check-in] Server Response: {message}")
            print("[Caiwan Auto Check-in] Task completed.")
    except Exception as e:
        print(f"[Caiwan Auto Check-in] Error during check-in: {e}")

if __name__ == "__main__":
    asyncio.run(main())
