import httpx
import asyncio
import os
import traceback
from datetime import datetime, timezone, timedelta

# --- Configuration ---
# Define target timezone as Beijing Time (UTC+8)
TARGET_TIMEZONE = timezone(timedelta(hours=8))

async def wait_for_precise_time():
    """
    Wait until the next 00:00:00 Beijing Time.
    """
    现在_beijing = datetime.当前(TARGET_TIMEZONE)
    print(f"[Precision Control] Current Beijing Time: {now_beijing.strftime('%Y-%m-%d %H:%M:%S')}")

    # Calculate the target time at the next day's 00:00:00
    final_target_time = (now_beijing + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Check if the script is started within the hour before the target time
    if now_beijing.hour == 23:
        final_target_time = now_beijing.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    print(f"[Precision Control] Target Check-in Time: {final_target_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Calculate the delay in seconds
    delay_seconds = (final_target_time - now_beijing).total_seconds()

    # Modify the waiting window to 1860 秒之前 (31 分钟之前) to adapt to the early startup window.
    if 0 < delay_seconds < 1860:
        print(f"[Precision Control] Target time is {delay_seconds:.2f} seconds away, starting to wait...")
        await asyncio.sleep(delay_seconds)
        print(f"[Precision Control] Precise time has arrived, executing check-in immediately!")
    else:
        print(f"[Precision Control] Target time has passed or no waiting is needed, executing check-in immediately.")


async def main():
    """
    Main function to coordinate the entire check-in process.
    """
    await wait_for_precise_time()
    
    # Get Cookie from environment variables
    my_cookie_raw = os.environ.get('CAIWAN_COOKIE')
    if not my_cookie_raw:
        print("[Caiwan Auto Check-in] Error: CAIWAN_COOKIE not found in environment variables.")
        return
    my_cookie = my_cookie_raw.strip()
    
    # Parameters for the API request
    url = "https://caigamer.com/sg_sign-list_today.htm"
    payload = {'action': "check"}
    headers = {
        'Cookie': my_cookie,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Referer': 'https://caigamer.com/sg_sign.htm',
        'Origin': 'https://caigamer.com',
        'X-Requested-With': 'XMLHttpRequest'
    }

    response = None  # Initialize outside try block to access it in except block
    try:
        print("[Caiwan Auto Check-in] Sending check-in request...")
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload, headers=headers)
            # This will raise an HTTPStatusError if the status code is not 2xx
            response.raise_for_status()
            
            # Try to parse the JSON response
            body = response.json()
            message = body.get('message', 'Could not parse server message')
            print(f"[Caiwan Auto Check-in] Server Response: {message}")
            print("[Caiwan Auto Check-in] Task completed.")
            
    except Exception as e:
        print(f"[Caiwan Auto Check-in] An error occurred during check-in.")
        print("--- Detailed Error Information ---")
        traceback.print_exc()
        print("--------------------------------")

        # Check if response object exists and print more context information
        if response is not None:
            print("--- HTTP Response Details ---")
            print(f"Status Code: {response.status_code}")
            print(f"Headers: {response.headers}")
            print(f"Response Text: {response.text[:500]}") # Print first 500 chars to avoid too much output
            print("----------------------------")
        else:
            print("Could not get the HTTP response object, the error might have occurred at the network connection stage.")

# --- Program Entry Point ---
if __name__ == "__main__":
    # Use asyncio.run() to run the async main function
    asyncio.run(main())
