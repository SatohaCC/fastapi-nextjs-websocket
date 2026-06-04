import asyncio
import asyncpg
from app.infrastructure.config import settings

async def main():
    pg_url = settings.DATABASE_URL.replace("+asyncpg", "")
    print(f"Connecting to: {pg_url}")
    
    received = asyncio.Event()
    
    def on_notify(conn, pid, channel, payload):
        print(f"Notification received on {channel} with payload {payload}")
        received.set()
        
    conn_listener = await asyncpg.connect(pg_url)
    await conn_listener.add_listener("new_delivery_feed", on_notify)
    print("Registered listener")
    
    conn_sender = await asyncpg.connect(pg_url)
    print("Sending NOTIFY...")
    await conn_sender.execute("NOTIFY new_delivery_feed, 'test'")
    
    try:
        await asyncio.wait_for(received.wait(), timeout=3.0)
        print("Success: Notification was received!")
    except asyncio.TimeoutError:
        print("Failure: Notification was NOT received within 3 seconds!")
        
    await conn_listener.close()
    await conn_sender.close()

if __name__ == '__main__':
    asyncio.run(main())
