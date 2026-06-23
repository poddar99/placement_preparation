"""
One-time migration: add LeetCode sync columns to existing database.
Run if you already have a database created before LeetCode sync was added:

    python -m scripts.migrate_leetcode_columns
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text

from app.database import engine


async def migrate() -> None:
    statements = [
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS leetcode_username VARCHAR(100)",
        "CREATE INDEX IF NOT EXISTS ix_users_leetcode_username ON users (leetcode_username)",
        "ALTER TABLE user_stats ADD COLUMN IF NOT EXISTS leetcode_ranking INTEGER",
        "ALTER TABLE user_stats ADD COLUMN IF NOT EXISTS leetcode_easy INTEGER DEFAULT 0",
        "ALTER TABLE user_stats ADD COLUMN IF NOT EXISTS leetcode_medium INTEGER DEFAULT 0",
        "ALTER TABLE user_stats ADD COLUMN IF NOT EXISTS leetcode_hard INTEGER DEFAULT 0",
        "ALTER TABLE user_stats ADD COLUMN IF NOT EXISTS leetcode_contest_attended INTEGER DEFAULT 0",
        "ALTER TABLE user_stats ADD COLUMN IF NOT EXISTS leetcode_last_synced TIMESTAMPTZ",
        "ALTER TABLE user_stats ADD COLUMN IF NOT EXISTS leetcode_sync_data JSONB",
    ]

    async with engine.begin() as conn:
        for stmt in statements:
            await conn.execute(text(stmt))
            print(f"OK: {stmt[:60]}...")

    print("LeetCode columns migration complete.")


if __name__ == "__main__":
    asyncio.run(migrate())