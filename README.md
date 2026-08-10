# Technical Assignment – Movie Recommendation System

A full-stack, responsive movie recommendation engine featuring a **3-Stage Pipeline Architecture** (Ingestion, Multi-Vector TF-IDF Core Logic, and Presentation/Inspection layer). Adheres to the Karpathy-Ponytail engineering philosophy focusing on first-principles implementation, zero placeholders, and strict runtime assertions.

## 🚀 Live App URL
Visit the globally hosted demo application:
👉 **Live Onboarding Wizard & Personalized Homepage:** **[https://technical-assignment-movie-recommendation.streamlit.app/](https://technical-assignment-movie-recommendation.streamlit.app/)**

*(For local execution)*
👉 **Main Content Explorer & Recommendations REST API:** **[http://localhost:8000/](http://localhost:8000/)**

---

## 🛠️ Architecture Overview

The system operates across three distinct stages to deliver sub-millisecond, customizable recommendation lookups:

1. **Stage 1: Ingestion & Storage:**
   - Loads and cleans `netflix_titles.csv` (~8,800 records).
   - Seeds a local **SQLite** database via **SQLAlchemy** to manage paginated queries, metadata filters, and search indexing.
2. **Stage 2: Core Matrix Engine:**
   - Vectorizes separate text fields (Title, Director, Cast, Genre, Description) into **5 individual sparse matrices** using a shared-vocabulary `TfidfVectorizer`.
   - Utilizes sparse representations to bypass a $1.5\text{ Trillion}$ FLOP precomputation bottleneck and avoid $1.4\text{ GB}$ of dense matrix memory consumption.
3. **Stage 3: Presentation & Dynamic Weighting:**
   - Computes weighted cosine similarities on the fly using sparse dot products.
   - Allows users to dynamically override feature weights in real-time, instantly shifting recommendations.

---

## 🖥️ UI/UX Design System
Built with a cinema dark-mode theme (`#141414` canvas, `#181818` card containers, `#282828` borders, and Netflix red `#e50914` accents):
- **Left Control Sidebar:** Houses real-time search queries, type selectors, genre filters, year ranges, and dynamic similarity weights.
- **Main Workspace Grid:** Displays cards representing movies and shows with a responsive grid. Click any card to launch the matcher.
- **Details Modal & Carousel:** Shows show details, cast, genres, and a sliding horizontal carousel of recommendations.
- **Evaluator Inspection Panel:** A tabbed drawer revealing:
  - **Metrics:** Processing latencies (Ingestion, Vectorization, dynamic query lookups).
  - **Assertions:** Pass status of core runtime validations.
  - **Vectors:** Distribution of weight vectors.
  - **Payload:** Raw formatted API JSON response for developer debugging.

---

## ⚡ Setup & Installation

### Prerequisites
- Python 3.11+
- Node.js (only if modifying frontend code; the repository includes pre-built static assets in `frontend/dist`)

### Quick Start
1. Clone the repository:
   ```bash
   git clone https://github.com/iammsp-star/Technical-Assignment-Movie-Recommendation-System.git
   cd Technical-Assignment-Movie-Recommendation-System
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Ensure `fastapi`, `uvicorn`, `pandas`, `scikit-learn`, `scipy`, and `sqlalchemy` are installed)*

3. Start the unified FastAPI backend server:
   ```bash
   python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
   ```

4. Open your browser and navigate to:
   **[http://localhost:8000/](http://localhost:8000/)**

---

## 🧪 Verification & Tests
The codebase is validated by a strict verification suite.

### Running Backend Unit Tests:
```bash
python -m pytest backend/test_pipeline.py
```

### Running API Integration Smoke Tests:
```bash
python .agents/skills/karpathy_ponytail_philosophy/scripts/smoke_test.py
```
