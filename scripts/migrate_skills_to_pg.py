import asyncio
import json
import os
import sys

# Add the root directory to PYTHONPATH so we can import enterprise_app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enterprise_app.core.database import Base, SessionLocal, engine
from enterprise_app.core.logging import logger
from enterprise_app.models.skill import AgentSkill


async def migrate_skills():
    registry_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "master_skills_registry.json"
    )

    if not os.path.exists(registry_path):
        logger.error(f"Error: {registry_path} not found.")
        return

    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    with open(registry_path, "r", encoding="utf-8") as f:
        skills_data = json.load(f)

    async with SessionLocal() as db:
        inserted = 0
        for skill_data in skills_data:
            # Check if skill already exists
            from sqlalchemy import select

            query = select(AgentSkill).where(AgentSkill.id == skill_data["id"])
            result = await db.execute(query)
            existing_skill = result.scalar_one_or_none()

            if existing_skill:
                # Update
                existing_skill.name = skill_data["name"]
                existing_skill.category = skill_data["category"]
                existing_skill.plugin = skill_data.get("plugin")
                existing_skill.scope = skill_data.get("scope", "Global")
                existing_skill.description = skill_data["description"]
            else:
                # Insert
                new_skill = AgentSkill(
                    id=skill_data["id"],
                    name=skill_data["name"],
                    category=skill_data["category"],
                    plugin=skill_data.get("plugin"),
                    scope=skill_data.get("scope", "Global"),
                    description=skill_data["description"],
                )
                db.add(new_skill)

            inserted += 1

        await db.commit()
        logger.info(f"Successfully migrated {inserted} skills to PostgreSQL!")


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    asyncio.run(migrate_skills())
