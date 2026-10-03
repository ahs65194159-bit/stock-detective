"""KakaoTalk i OpenBuilder skill endpoint: '/종목명' -> stock classification reply.

This endpoint intentionally uses the bundled stock master JSON directly so the
Kakao bot does not need a paid/external database just to resolve stock names.
"""
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List
import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/v1/kakao", tags=["kakao"])

USAGE = "사용법: /종목명 (예: /삼성전자)\n종목코드로도 검색할 수 있습니다. (예: /005930)"
STOCK_DATA = Path(__file__).resolve().parent.parent / "data_models" / "stocks_full.json"


def _parse_query(utterance: str) -> str:
    text = (utterance or "").strip()
    if text.startswith("/"):
        text = text[1:]
    return text.strip()


@lru_cache(maxsize=1)
def _load_stocks() -> List[Dict[str, str]]:
    with STOCK_DATA.open("r", encoding="utf-8") as f:
        rows = json.load(f)
    return [r for r in rows if isinstance(r, dict)]


def _search(keyword: str) -> List[Dict[str, str]]:
    key = keyword.strip().lower()
    if not key:
        return []
    rows = _load_stocks()
    exact = [r for r in rows if str(r.get("name", "")).lower() == key or str(r.get("code", "")) == keyword]
    if exact:
        return exact[:1]
    return [r for r in rows if key in str(r.get("name", "")).lower()][:5]


def _format(rows: List[Dict[str, str]], keyword: str) -> str:
    if not keyword:
        return USAGE
    if not rows:
        return f"'{keyword}' 종목을 찾을 수 없습니다.\n{USAGE}"
    if len(rows) == 1:
        s = rows[0]
        lines = [f"[{s.get('name','')}] ({s.get('code','')})", f"시장: {s.get('market','-')}"]
        if s.get("industry"):
            lines.append(f"업종: {s['industry']}")
        if s.get("sub_industry"):
            lines.append(f"세부업종: {s['sub_industry']}")
        if s.get("themes"):
            lines.append(f"관련테마: {str(s['themes']).replace('|', ' · ')}")
        return "\n".join(lines)
    names = "\n".join(f"- /{s.get('name','')} ({s.get('code','')})" for s in rows)
    return f"'{keyword}' 검색 결과가 여러 개입니다:\n{names}"


def build_skill_payload(text: str) -> Dict[str, Any]:
    safe = str(text or "").strip() or USAGE
    if len(safe) > 1000:
        safe = safe[:997] + "..."
    return {"version": "2.0", "template": {"outputs": [{"simpleText": {"text": safe}}]}}


@router.post("/skill")
async def kakao_skill(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    user_request = body.get("userRequest") if isinstance(body, dict) else {}
    utterance = user_request.get("utterance", "") if isinstance(user_request, dict) else ""
    keyword = _parse_query(str(utterance or ""))
    try:
        text = _format(_search(keyword), keyword)
    except Exception:
        text = "조회 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."
    return JSONResponse(content=build_skill_payload(text), media_type="application/json; charset=utf-8")


@router.get("/search")
async def search(q: str = ""):
    keyword = _parse_query(q)
    rows = _search(keyword)
    return {"text": _format(rows, keyword), "items": rows}
