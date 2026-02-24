import json
import os
import time
from typing import Any, Dict, List, Literal, Optional

from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

app = FastAPI()

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:8000/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "local-anything")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "Qwen2.5-72B-Instruct")

client = OpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)


# ---- 1) Le LLM ne produit QUE des données (facile à valider).
class AgentData(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    summary: str = Field(..., min_length=1, max_length=600)
    bullets: List[str] = Field(..., min_length=1, max_length=10)


def llm_generate_data(user_text: str) -> AgentData:
    system = (
        "You are a helpful assistant. Return ONLY valid JSON matching this schema:\n"
        '{ "title": string, "summary": string, "bullets": string[] }\n'
        "Constraints:\n"
        "- bullets: 3 to 7 items\n"
        "- No markdown, no extra keys, no commentary.\n"
    )

    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_text},
        ],
    )

    raw = resp.choices[0].message.content or ""
    raw = raw.strip()

    # Robustesse: certains modèles renvoient du texte autour; on tente d'extraire le JSON.
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"LLM did not return JSON object. Got: {raw[:200]}")

    obj = json.loads(raw[start : end + 1])
    data = AgentData.model_validate(obj)

    # Contraintes additionnelles
    if not (3 <= len(data.bullets) <= 7):
        data.bullets = data.bullets[:7] if len(data.bullets) > 7 else (data.bullets + [""] * (3 - len(data.bullets)))
        data.bullets = [b for b in data.bullets if b.strip()][:7]

    return data


# ---- 2) Encapsulation A2UI v0.8 en JSONL streaming.
def a2ui_jsonl_stream(surface_id: str, data: AgentData):
    """
    A2UI v0.8: on stream des objets JSONL.
    Séquence standard: surfaceUpdate -> dataModelUpdate -> beginRendering.
    (Ces enveloppes sont mentionnées dans les docs/impls A2UI v0.8.) :contentReference[oaicite:1]{index=1}
    """

    # A) surfaceUpdate: description déclarative de composants.
    surface_update: Dict[str, Any] = {
        "surfaceUpdate": {
            "surfaceId": surface_id,
            "components": [
                {
                    "id": "root",
                    "component": {
                        "Column": {
                            "children": {"explicitList": ["title", "summary", "bullets"]}
                        }
                    },
                },
                {"id": "title", "component": {"Text": {"text": {"binding": "/view/title"}}}},
                {"id": "summary", "component": {"Text": {"text": {"binding": "/view/summary"}}}},
                {
                    "id": "bullets",
                    "component": {
                        "Column": {
                            "children": {"explicitList": ["b0", "b1", "b2", "b3", "b4", "b5", "b6"]}
                        }
                    },
                },
                # 7 slots max (certains peuvent être vides)
                {"id": "b0", "component": {"Text": {"text": {"binding": "/view/bullets/0"}}}},
                {"id": "b1", "component": {"Text": {"text": {"binding": "/view/bullets/1"}}}},
                {"id": "b2", "component": {"Text": {"text": {"binding": "/view/bullets/2"}}}},
                {"id": "b3", "component": {"Text": {"text": {"binding": "/view/bullets/3"}}}},
                {"id": "b4", "component": {"Text": {"text": {"binding": "/view/bullets/4"}}}},
                {"id": "b5", "component": {"Text": {"text": {"binding": "/view/bullets/5"}}}},
                {"id": "b6", "component": {"Text": {"text": {"binding": "/view/bullets/6"}}}},
            ],
        }
    }

    # B) dataModelUpdate: état typé (ici on simplifie en strings),
    # l’idée: données séparées de la structure UI, bindées via JSON Pointer (ex: /view/title). :contentReference[oaicite:2]{index=2}
    padded = (data.bullets + [""] * 7)[:7]
    data_model_update: Dict[str, Any] = {
        "dataModelUpdate": {
            "surfaceId": surface_id,
            "set": [
                {"path": "/view/title", "valueString": data.title},
                {"path": "/view/summary", "valueString": data.summary},
                {"path": "/view/bullets/0", "valueString": padded[0]},
                {"path": "/view/bullets/1", "valueString": padded[1]},
                {"path": "/view/bullets/2", "valueString": padded[2]},
                {"path": "/view/bullets/3", "valueString": padded[3]},
                {"path": "/view/bullets/4", "valueString": padded[4]},
                {"path": "/view/bullets/5", "valueString": padded[5]},
                {"path": "/view/bullets/6", "valueString": padded[6]},
            ],
        }
    }

    # C) beginRendering: signal que le client peut rendre la surface.
    begin_rendering: Dict[str, Any] = {"beginRendering": {"surfaceId": surface_id}}

    for msg in (surface_update, data_model_update, begin_rendering):
        yield json.dumps(msg, ensure_ascii=False) + "\n"
        time.sleep(0.01)


@app.get("/a2ui")
def a2ui(
    q: str = Query(..., min_length=1, max_length=2000),
    surface_id: Optional[str] = None,
):
    """
    Retourne un flux JSONL (A2UI).
    Exemple:
      curl -N "http://localhost:8080/a2ui?q=Explique+le+GPU+GB10"
    """
    sid = surface_id or f"surface-{int(time.time())}"

    try:
        data = llm_generate_data(q)
    except (ValidationError, ValueError, json.JSONDecodeError) as e:
        # Fallback sans casser le protocole
        data = AgentData(
            title="Erreur de génération",
            summary=str(e)[:600],
            bullets=["Réessayer avec une demande plus simple.", "Vérifier le modèle/vLLM.", "Vérifier les logs."],
        )

    return StreamingResponse(
        a2ui_jsonl_stream(sid, data),
        media_type="application/x-ndjson",
    )