# Backend Directory

**Note:** The backend application files have been moved to the root directory for Koyeb deployment.

This directory now only contains:
- `.env` - Your local environment variables (not tracked by git)

## For Local Development

All Python files are now in the root:
```
/main.py              - FastAPI application
/requirements.txt     - Python dependencies
/runtime.txt          - Python version
/Procfile            - Process file for deployment
/src/                - Source code
/agents/             - AI agents
/scripts/            - Utility scripts
/migrations/         - Database migrations
```

Run locally from the root directory:
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```
