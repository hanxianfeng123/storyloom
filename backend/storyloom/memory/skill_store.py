import uuid
import aiosqlite
from datetime import datetime, timezone
from typing import Optional
from storyloom.memory.models.skill import Skill, SkillVersion, SkillRun, SkillUpdate


class SkillStore:
    def __init__(self, conn: aiosqlite.Connection):
        self._conn = conn

    # ── Skills ──

    async def list_skills(self) -> list[Skill]:
        cursor = await self._conn.execute(
            "SELECT * FROM skills ORDER BY category, name"
        )
        rows = await cursor.fetchall()
        return [Skill(**dict(r)) for r in rows]

    async def get_skill(self, skill_id: str) -> Optional[Skill]:
        cursor = await self._conn.execute(
            "SELECT * FROM skills WHERE id = ?", (skill_id,)
        )
        row = await cursor.fetchone()
        return Skill(**dict(row)) if row else None

    async def get_skill_by_name(self, name: str) -> Optional[Skill]:
        cursor = await self._conn.execute(
            "SELECT * FROM skills WHERE name = ?", (name,)
        )
        row = await cursor.fetchone()
        return Skill(**dict(row)) if row else None

    async def create_skill(self, skill: Skill) -> Skill:
        now = datetime.now(timezone.utc)
        await self._conn.execute(
            """INSERT INTO skills
               (id, category, name, parent_id, description, system_prompt,
                user_prompt_template, post_process_template, model,
                fallback_model, max_tokens, temperature, version, is_active,
                created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (skill.id, skill.category, skill.name, skill.parent_id,
             skill.description, skill.system_prompt, skill.user_prompt_template,
             skill.post_process_template, skill.model, skill.fallback_model,
             skill.max_tokens, skill.temperature, skill.version, skill.is_active,
             now, now),
        )
        await self._conn.commit()
        return skill

    async def update_skill(self, skill_id: str, update: SkillUpdate) -> Optional[Skill]:
        current = await self.get_skill(skill_id)
        if not current:
            return None

        # Archive current version before updating
        await self._save_version(current, update.change_note or "Updated via API")

        fields = []
        values = []
        for field_name in ("description", "system_prompt", "user_prompt_template",
                           "post_process_template", "model", "fallback_model",
                           "max_tokens", "temperature", "is_active"):
            val = getattr(update, field_name, None)
            if val is not None:
                fields.append(f"{field_name} = ?")
                values.append(val)

        if not fields:
            return current

        now = datetime.now(timezone.utc)
        fields.append("version = version + 1")
        fields.append("updated_at = ?")
        values.append(now)
        values.append(skill_id)

        await self._conn.execute(
            f"UPDATE skills SET {', '.join(fields)} WHERE id = ?", values
        )
        await self._conn.commit()
        return await self.get_skill(skill_id)

    async def delete_skill(self, skill_id: str) -> bool:
        cursor = await self._conn.execute(
            "DELETE FROM skills WHERE id = ?", (skill_id,)
        )
        await self._conn.commit()
        return cursor.rowcount > 0

    # ── Versions ──

    async def _save_version(self, skill: Skill, change_note: str):
        now = datetime.now(timezone.utc)
        await self._conn.execute(
            """INSERT INTO skill_versions
               (id, skill_id, version, description, system_prompt,
                user_prompt_template, post_process_template, model,
                max_tokens, temperature, change_note, created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (uuid.uuid4().hex[:12], skill.id, skill.version, skill.description,
             skill.system_prompt, skill.user_prompt_template,
             skill.post_process_template, skill.model, skill.max_tokens,
             skill.temperature, change_note, now, "system"),
        )
        await self._conn.commit()

    async def get_skill_versions(self, skill_id: str) -> list[SkillVersion]:
        cursor = await self._conn.execute(
            "SELECT * FROM skill_versions WHERE skill_id = ? ORDER BY version DESC",
            (skill_id,),
        )
        rows = await cursor.fetchall()
        return [SkillVersion(**dict(r)) for r in rows]

    async def rollback_skill(self, skill_id: str, target_version: int) -> Optional[Skill]:
        """Restore a skill to a previous version."""
        cursor = await self._conn.execute(
            "SELECT * FROM skill_versions WHERE skill_id = ? AND version = ?",
            (skill_id, target_version),
        )
        row = await cursor.fetchone()
        if not row:
            return None
        version_data = dict(row)
        current = await self.get_skill(skill_id)
        if not current:
            return None

        # Archive current
        await self._save_version(current, f"Rollback to v{target_version}")

        now = datetime.now(timezone.utc)
        await self._conn.execute(
            """UPDATE skills SET description = ?, system_prompt = ?,
               user_prompt_template = ?, post_process_template = ?,
               model = ?, max_tokens = ?, temperature = ?,
               version = version + 1, updated_at = ?
               WHERE id = ?""",
            (version_data["description"], version_data["system_prompt"],
             version_data["user_prompt_template"], version_data["post_process_template"],
             version_data["model"], version_data["max_tokens"],
             version_data["temperature"], now, skill_id),
        )
        await self._conn.commit()
        return await self.get_skill(skill_id)

    # ── Runs ──

    async def log_run(self, run: SkillRun) -> SkillRun:
        await self._conn.execute(
            """INSERT INTO skill_runs
               (id, project_id, chapter_number, step_number, skill_id,
                llm_decision, input_preview, output_preview, tokens_in,
                tokens_out, latency_ms, cost_usd, status, error_message)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (run.id, run.project_id, run.chapter_number, run.step_number,
             run.skill_id, run.llm_decision, run.input_preview, run.output_preview,
             run.tokens_in, run.tokens_out, run.latency_ms, run.cost_usd,
             run.status, run.error_message),
        )
        await self._conn.commit()
        return run

    async def list_runs(self, project_id: str, chapter_number: int | None = None) -> list[SkillRun]:
        if chapter_number is not None:
            cursor = await self._conn.execute(
                "SELECT * FROM skill_runs WHERE project_id = ? AND chapter_number = ? ORDER BY step_number",
                (project_id, chapter_number),
            )
        else:
            cursor = await self._conn.execute(
                "SELECT * FROM skill_runs WHERE project_id = ? ORDER BY created_at DESC LIMIT 50",
                (project_id,),
            )
        rows = await cursor.fetchall()
        return [SkillRun(**dict(r)) for r in rows]
