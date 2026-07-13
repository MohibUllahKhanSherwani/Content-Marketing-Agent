# Content Marketing Agent Team 🚀

A production-grade, multi-agent AI marketing operations system built with CrewAI and Gemini that acts as an automated content marketing team. It coordinates campaign planning, content generation, human-in-the-loop approvals, and direct publishing/telemetry across marketing channels.

The project features a sleek, modern React-based **SaaS Operations Dashboard** connected to a **FastAPI backend** for complete editorial oversight before content goes live.

---

## Key Integrations
The agent integrates with production APIs to fully automate multi-channel content distribution:

*   **WordPress**: Automates blog post and landing-page drafting.
*   **HubSpot**: Generates and maps marketing campaign emails directly inside the email manager.
*   **LinkedIn**: Publishes social posts and thought leadership updates to personal profiles or company pages.
*   **Meta (Facebook & Instagram)**: Publishes social updates and coordinates ad campaigns.
*   **Google Analytics 4**: Fetches performance rollups and analytics to measure campaign engagement.
*   **Gemini API**: Powers specialist crews for copy drafting, strategic auditing, and keyword generation.

---

## How to Run the Project (Local Setup)

### Prerequisites
- **Python**: `>=3.10, <3.14`
- **Node.js**: `>=18`
- **Package Managers**: `uv` (recommended for Python) or `pip`, and `npm`

---

### Step 1: Set Up Backend

1.  **Install dependencies**:
    Using `uv` (fastest):
    ```bash
    uv sync --extra dev
    ```
    Or standard `pip`:
    ```bash
    pip install -e .
    ```

2.  **Configure environment**:
    Copy the sample environment file and configure your API tokens (Gemini, WordPress, HubSpot, LinkedIn, etc.):
    ```bash
    cp .env.example .env
    ```

3.  **Start the API dev server**:
    ```bash
    uv run uvicorn content_marketing_agent.api:app --reload --port 8000
    ```
    The API will be available at:
    - Base URL: `http://localhost:8000`
    - Swagger Documentation: `http://localhost:8000/docs`

---

### Step 2: Set Up Frontend Dashboard

1.  **Navigate to the frontend directory**:
    ```bash
    cd frontend
    ```

2.  **Install dependencies**:
    ```bash
    npm install
    ```

3.  **Start the development server**:
    ```bash
    npm run dev
    ```
    The dashboard will be live at:
    - URL: `http://localhost:5173`

---

## Running Agent Workflows via CLI
You can also run marketing jobs directly from the CLI:

```bash
# Create a monthly editorial calendar plan
uv run cma monthly-plan --month 2026-07 --blog-posts 8

# Trigger draft generation for specific objectives
uv run cma produce --objective "Increase inbound product signups" --items-per-channel 1

# Pull performance metrics and analytics
uv run cma monthly-analytics
```

---

## Project Structure
```text
├── src/content_marketing_agent/
│   ├── api.py           # FastAPI server (CORS-enabled)
│   ├── cli.py           # CLI Command Controller
│   ├── connectors/      # API integrations (WordPress, HubSpot, LinkedIn, etc.)
│   ├── crews/           # CrewAI specialist role configuration
│   └── flows/           # CrewAI Flow orchestration logic
└── frontend/
    ├── src/
    │   ├── App.css      # SaaS Layout CSS
    │   ├── api.ts       # Frontend API Client
    │   └── pages/       # Dashboard routes (Review, Calendar, Telemetry, Connectors)
```
