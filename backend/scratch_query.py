import asyncio
from app.infrastructure.persistence.session import AsyncSessionLocal
from app.infrastructure.persistence.orm_models import DeliveryFeedORM
from sqlalchemy import select

async def f():
    s = AsyncSessionLocal()
    r = await s.execute(select(DeliveryFeedORM).where(DeliveryFeedORM.sequence_name == "global_chat").order_by(DeliveryFeedORM.sequence_id.desc()).limit(10))
    with open("scratch_output.txt", "w", encoding="utf-8") as f_out:
        for m in r.scalars().all():
            f_out.write(f"seq_id={m.sequence_id}, status={m.status}, event={m.event_type}, payload={m.payload}\n")
    await s.close()

if __name__ == '__main__':
    asyncio.run(f())
