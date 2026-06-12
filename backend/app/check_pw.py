import asyncio
from app.infrastructure.persistence.session import AsyncSessionLocal
from sqlalchemy import text
from app.infrastructure.auth.password_hasher import PasswordHasher

async def main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT username, hashed_password FROM users"))
        hasher = PasswordHasher()
        for row in result.all():
            username, hashed = row
            match = hasher.verify("pass1234", hashed)
            print(f"{username}: {match}")

if __name__ == "__main__":
    asyncio.run(main())
