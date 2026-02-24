## A2UI End-to-End Example

Ce projet montre un système complet permettant de servir un LLM (Qwen2.5-72B) avec vLLM et de générer des interfaces utilisateur dynamiques via un agent FastAPI utilisant le protocole A2UI.

### Architecture

- **vLLM** : Serveur LLM OpenAI-compatible (port 8000)
- **FastAPI Agent** : Générateur de données et streams JSONL A2UI (port 8080)
- **Client Lit* : Rendu côté client du flux JSONL A2UI

### Fichiers

```
docker-compose.yml
├── Dockerfile
├── agent/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
└── client/
    ├── public/
    │   ├── index.html
    │   └── styles.css
    └── src/
        └── a2ui.client.ts
```

### Setup

1. **Télécharger le modèle** (Qwen2.5-72B-Instruct):
```bash
mkdir -p models/Qwen2.5-72B-Instruct
# Placez le modèle HF ici
```

2. **Démarrer les services**:
```bash
docker compose up --build -d
```

3. **Vérifier les services**:
```bash
docker compose ps
curl http://localhost:8000/v1/models
curl http://localhost:8080/a2ui?q=Test
```

### API A2UI

L'agent expose une seule endpoint GET:
- `GET /a2ui?q=<query>` - Retourne un flux JSONL contenant les messages A2UI v0.8

### Test Client

Le projet inclut un client Lit+ pour consommer le flux. Le client capture les messages A2UI et les rend dynamiquement dans le DOM.

Le flux JSONL contient généralement 3 messages:
1. `surfaceUpdate` - Définit la structure UI
2. `dataModelUpdate` - Met à jour les données bindées
3. `beginRendering` - Signale le début du rendu

### Portabilité

Le projet utilise vLLM 8-bit (dtype=auto) qui est compatible avec les GPUs NVIDIA de génération. Pour utiliser une autre architecture, modifiez le paramètre `--dtype` selon vos besoins.

A2UI est un protocole déclaratif qui permet de séparer complètement la structure UI de son contenu, rendu possible par différents renderers front-end.