# A2UI Streaming JSONL Interface

**Un système complet permettant de servir un LLM (Qwen2.5-72B) via vLLM et de générer des interfaces utilisateur dynamiques via le protocole A2UI.**

## 🚀 Fiches techniques

- **Type**: Exemple end-to-end open-source
- **Llama**: Qwen2.5-72B-Instruct (< 90B)
- **Serveur LLM**: vLLM (OpenAI-compatible)
- **API**: FastAPI agent
- **Protocole**: A2UI v0.8 (Streaming JSONL)
- **Client**: Lit+ (optionnel) / Vanilla JS

## 📦 Installation rapide

```bash
# Télécharger le modèle Qwen2.5-72B (16GB+ HF)
pip install -r agent/requirements.txt

# Démarrer les services
docker compose up --build

# Tester le flux A2UI
curl -N "http://localhost:8080/a2ui?q=Hello"
```

## 📊 Exemple de sortie

```json
{"surfaceUpdate": {"surfaceId": "surface-1737794000", "components": [...]}}
{"dataModelUpdate": {"surfaceId": "surface-1737794000", "set": [{"path": "/view/title", "valueString": "Bonjour"}]}}
{"beginRendering": {"surfaceId": "surface-1737794000"}}
```

## 🎯 Scenarios et cas d'usage

| Scénario | Client | Description |
|----------|--------|-------------|
| Streaming JSONL | Lit+ / Vanilla JS | Génération d'UI dynamique en temps réel |
| API vLLM | OpenAI SDK | Service LLM auto-hébergé |
| Protocole Déclaratif | A2UI | UI séparée des données |

## 🛠️ Développement

- **Frontend**: Client Lit+ et Vanilla JS
- **Backend**: FastAPI + OpenAI SDK
- **LLM**: Qwen2.5-72B via vLLM
- **GPU**: NVIDIA (8GB+ VRAM)

## 🧪 Tests

```bash
# Tests vLLM
curl http://localhost:8000/v1/models

# Tests agent
curl "http://localhost:8080/a2ui?q=Test&surface_id=surface-123"
```

## 📚 Documentation

- 📄 [Détails techniques](docs/overview.md)
- 🏗️ [Architecture système](docs/architecture.md)
- 💼 [Valeur métier](VALUE.md)
- 🚀 [Cas d'usage](USE_CASE.md)
- 📊 [État d'innovation](INNOVATION_STATUS.md)

## 🔗 Liens utiles

- [vLLM Documentation](https://docs.vllm.ai/)
- [A2UI GitHub](https://github.com/google/A2UI)
- [Qwen2.5-72B Instruct](https://huggingface.co/Qwen/Qwen2.5-72B-Instruct)