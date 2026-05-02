import json
import logging
from typing import Any

from groq import AsyncGroq
from pydantic import BaseModel, ValidationError

from app.config import settings
from app.schemas import AIChannelAnalysisPayload, AIContentIdeasPayload, AISeoPayload, AIScriptPayload

logger = logging.getLogger(__name__)


class GroqAIService:
    """
    Calls Groq chat completions and enforces JSON output mode.
    Includes fallback parsing + safe fallback payloads if JSON is invalid.
    """

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or settings.groq_api_key
        self.model = model or settings.groq_model
        self.client = AsyncGroq(api_key=self.api_key) if self.api_key else None

    async def generate_ideas(
        self,
        *,
        channel_name: str,
        niche: str | None,
        topic: str | None,
        count: int,
    ) -> dict[str, Any]:
        system_prompt = (
            "You are an expert YouTube Shorts strategist. "
            "Return ONLY valid JSON. Do not include markdown, prose, code fences, or extra keys."
        )
        user_prompt = (
            f"Generate {count} viral Shorts ideas for channel '{channel_name}' "
            f"in niche '{niche or 'general'}'. Topic focus: '{topic or 'any high-performing topic'}'. "
            "JSON schema: "
            '{"ideas":[{"title":"string","hook":"string","angle":"string","estimated_virality_score":0-100}]}.'
        )
        fallback = {"ideas": [self._fallback_idea(channel_name=channel_name, index=i) for i in range(1, count + 1)]}
        return await self._chat_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            fallback=fallback,
            schema_model=AIContentIdeasPayload,
        )

    async def generate_script(
        self,
        *,
        channel_name: str,
        idea_title: str,
        idea_hook: str | None,
        target_duration_seconds: int,
        style: str | None = None,
        target_audience: str | None = None,
    ) -> dict[str, Any]:
        system_prompt = (
            "You write short-form scripts optimized for retention."
            " Return ONLY valid JSON with no extra keys."
        )
        user_prompt = (
            f"Channel: {channel_name}. Idea title: {idea_title}. "
            f"Optional hook: {idea_hook or 'none'}. Target duration: {target_duration_seconds} seconds. "
            f"Style: {style or 'high-retention Shorts'}. Target audience: {target_audience or 'channel audience'}. "
            "JSON schema: "
            '{"script_text":"string","cta":"string","estimated_duration_seconds":"integer"}.'
        )
        fallback = {
            "script_text": (
                "Stop scrolling. Here is the biggest mistake people make with this topic.\n"
                "In under 30 seconds, I will show you the fix.\n"
                "Step 1: Do the opposite of the common advice.\n"
                "Step 2: Use this quick framework and test it today.\n"
                "That simple change can double retention."
            ),
            "cta": "Comment 'PART 2' if you want the advanced version.",
            "estimated_duration_seconds": target_duration_seconds,
        }
        return await self._chat_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            fallback=fallback,
            schema_model=AIScriptPayload,
        )

    async def generate_seo(
        self,
        *,
        channel_name: str,
        script_text: str,
        title: str | None,
        target_keywords: list[str] | None = None,
        platform: str = "youtube",
    ) -> dict[str, Any]:
        system_prompt = (
            "You are a YouTube SEO copywriter for Shorts."
            " Return ONLY valid JSON with no extra keys."
        )
        user_prompt = (
            f"Channel: {channel_name}. Platform: {platform}. Title/context: {title or 'N/A'}. "
            f"Target keywords: {', '.join(target_keywords or []) or 'none provided'}. "
            f"Script:\n{script_text}\n"
            "Return JSON with this schema: "
            '{"title":"string","description":"string","hashtags":["string"],'
            '"tags":["string"],"pinned_comment":"string"}.'
        )
        fallback = {
            "title": f"{title or 'Viral Shorts Strategy'} (Fast Breakdown)",
            "description": "A quick Shorts breakdown with actionable steps and creator-friendly tips.",
            "hashtags": ["#YouTubeShorts", "#ContentCreation", "#CreatorTips"],
            "tags": ["youtube shorts", "viral shorts", "creatorflow ai", "content strategy"],
            "pinned_comment": "What should we break down next? Drop your niche below.",
        }
        return await self._chat_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            fallback=fallback,
            schema_model=AISeoPayload,
        )

    async def analyze_channel(
        self,
        *,
        channel_name: str,
        niche: str | None,
        context: str | None,
    ) -> dict[str, Any]:
        system_prompt = (
            "You are a growth strategist for creator businesses."
            " Return ONLY valid JSON with no extra keys."
        )
        user_prompt = (
            f"Analyze channel '{channel_name}' in niche '{niche or 'general'}'. "
            f"Additional context: {context or 'none'}."
            "Return JSON schema: "
            '{"summary":"string","strengths":["string"],"opportunities":["string"],'
            '"content_pillars":["string"],"next_actions":["string"]}.'
        )
        fallback = {
            "summary": "Early-stage channel with room to improve consistency and hook quality.",
            "strengths": ["Focused niche positioning", "Good potential for repeatable content formats"],
            "opportunities": [
                "Use stronger first-2-second hooks",
                "Batch produce content in 3 repeatable series",
            ],
            "content_pillars": ["Myth-busting", "Quick tutorials", "Trend reaction format"],
            "next_actions": [
                "Publish 5 Shorts per week",
                "A/B test titles with numbers vs curiosity",
                "Track retention and replay rate weekly",
            ],
        }
        return await self._chat_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            fallback=fallback,
            schema_model=AIChannelAnalysisPayload,
        )

    async def _chat_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        fallback: dict[str, Any],
        schema_model: type[BaseModel],
    ) -> dict[str, Any]:
        if not self.client:
            payload = self._validated_payload(schema_model=schema_model, payload=fallback, fallback=fallback)
            payload["_used_fallback"] = True
            payload["_error"] = "GROQ_API_KEY is not configured."
            return payload

        try:
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            content = completion.choices[0].message.content or "{}"
            parsed, fallback_used = self._safe_parse_json(content=content, fallback=fallback)
            payload = self._validated_payload(schema_model=schema_model, payload=parsed, fallback=fallback)
            payload["_used_fallback"] = fallback_used or payload.pop("_schema_fallback", False)
            return payload
        except Exception as exc:  # noqa: BLE001
            logger.exception("Groq API call failed: %s", exc)
            payload = self._validated_payload(schema_model=schema_model, payload=fallback, fallback=fallback)
            payload["_used_fallback"] = True
            payload["_error"] = str(exc)
            return payload

    @staticmethod
    def _validated_payload(
        *,
        schema_model: type[BaseModel],
        payload: dict[str, Any],
        fallback: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            return schema_model.model_validate(payload).model_dump()
        except ValidationError as exc:
            logger.warning("AI payload failed validation, using fallback: %s", exc)
            validated = schema_model.model_validate(fallback).model_dump()
            validated["_schema_fallback"] = True
            validated["_error"] = "AI response did not match the expected JSON schema."
            return validated

    @staticmethod
    def _safe_parse_json(*, content: str, fallback: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                return parsed, False
            return dict(fallback), True
        except json.JSONDecodeError:
            # Fallback extraction: tries to recover JSON object from mixed content.
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    parsed = json.loads(content[start : end + 1])
                    if isinstance(parsed, dict):
                        return parsed, True
                except json.JSONDecodeError:
                    pass
            return dict(fallback), True

    @staticmethod
    def _fallback_idea(*, channel_name: str, index: int) -> dict[str, Any]:
        return {
            "title": f"{channel_name}: Viral Shorts Idea #{index}",
            "hook": "Most creators miss this simple angle in the first 3 seconds.",
            "angle": "Open with a clear misconception, then resolve it with one practical takeaway.",
            "estimated_virality_score": 62,
        }
