import os
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, distinct

from backend.db import init_db, get_db, NetflixTitle
from backend.pipeline import NetflixRecommendationPipeline, diagnostics

CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "netflix_titles.csv")
pipeline: Optional[NetflixRecommendationPipeline] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Database Schema
    init_db()
    
    # Initialize and execute pipeline
    global pipeline
    print(f"[Pipeline] Initializing pipeline with dataset: {CSV_PATH}")
    pipeline = NetflixRecommendationPipeline(CSV_PATH)
    
    # Execute Ingestion Stage
    pipeline.run_stage_1_ingestion()
    
    # Execute Fitting & Vectorization Stage
    pipeline.run_stage_2_core_engine()
    
    # Seed database with parsed items
    db_gen = get_db()
    db = next(db_gen)
    try:
        pipeline.seed_database(db)
    finally:
        db.close()
        
    print("[Pipeline] Setup completed. Backend ready.")
    yield
    print("[Pipeline] Shutting down.")

app = FastAPI(
    title="Netflix Analytics & Recommendation Engine",
    description="Full-stack search, recommendation, and diagnostics pipeline",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/titles")
def get_titles(
    search: Optional[str] = Query(None, description="Search by title, director, cast, or description"),
    type: Optional[str] = Query(None, description="Filter by type: 'Movie' or 'TV Show'"),
    release_year_min: Optional[int] = Query(None, description="Minimum release year"),
    release_year_max: Optional[int] = Query(None, description="Maximum release year"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(24, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Retrieve titles with filtering and pagination."""
    query = db.query(NetflixTitle)
    filters = []

    if type:
        filters.append(NetflixTitle.type == type)
    if release_year_min:
        filters.append(NetflixTitle.release_year >= release_year_min)
    if release_year_max:
        filters.append(NetflixTitle.release_year <= release_year_max)
    if genre:
        filters.append(NetflixTitle.listed_in.like(f"%{genre}%"))

    if search:
        search_term = f"%{search}%"
        filters.append(
            or_(
                NetflixTitle.title.like(search_term),
                NetflixTitle.director.like(search_term),
                NetflixTitle.cast.like(search_term),
                NetflixTitle.description.like(search_term)
            )
        )

    if filters:
        query = query.filter(and_(*filters))

    total_count = query.count()
    
    # Apply pagination
    offset = (page - 1) * limit
    titles = query.order_by(NetflixTitle.title).offset(offset).limit(limit).all()

    return {
        "total_count": total_count,
        "page": page,
        "limit": limit,
        "titles": [
            {
                "show_id": t.show_id,
                "type": t.type,
                "title": t.title,
                "director": t.director,
                "cast": t.cast,
                "country": t.country,
                "date_added": t.date_added,
                "release_year": t.release_year,
                "rating": t.rating,
                "duration": t.duration,
                "listed_in": t.listed_in,
                "description": t.description
            }
            for t in titles
        ]
    }

@app.get("/api/titles/{show_id}")
def get_title(show_id: str, db: Session = Depends(get_db)):
    """Retrieve detailed information for a specific title."""
    title = db.query(NetflixTitle).filter(NetflixTitle.show_id == show_id).first()
    if not title:
        raise HTTPException(status_code=404, detail=f"Title with ID '{show_id}' not found.")
    
    return {
        "show_id": title.show_id,
        "type": title.type,
        "title": title.title,
        "director": title.director,
        "cast": title.cast,
        "country": title.country,
        "date_added": title.date_added,
        "release_year": title.release_year,
        "rating": title.rating,
        "duration": title.duration,
        "listed_in": title.listed_in,
        "description": title.description
    }

@app.get("/api/titles/{show_id}/recommendations")
def get_recommendations(
    show_id: str, 
    limit: int = Query(10, ge=1, le=50),
    w_title: float = Query(2.0, description="Title weight"),
    w_director: float = Query(3.0, description="Director weight"),
    w_cast: float = Query(2.0, description="Cast weight"),
    w_genre: float = Query(3.0, description="Genre weight"),
    w_desc: float = Query(1.0, description="Description weight")
):
    """Retrieve similarity recommendations using Stage 3 pipeline with dynamic weights."""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline engine is initializing.")
    
    try:
        recommendations = pipeline.run_stage_3_recommend(
            show_id, 
            top_n=limit,
            w_title=w_title,
            w_director=w_director,
            w_cast=w_cast,
            w_genre=w_genre,
            w_desc=w_desc
        )
        return {
            "show_id": show_id,
            "limit": limit,
            "weights": {
                "w_title": w_title,
                "w_director": w_director,
                "w_cast": w_cast,
                "w_genre": w_genre,
                "w_desc": w_desc
            },
            "recommendations": recommendations
        }
    except AssertionError as e:
        raise HTTPException(status_code=500, detail=f"Pipeline assertion failed: {str(e)}")
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Show ID '{show_id}' not found in recommendation model.")

@app.get("/api/genres")
def get_genres(db: Session = Depends(get_db)):
    """Extract list of unique genres from titles."""
    titles = db.query(distinct(NetflixTitle.listed_in)).all()
    genre_set = set()
    for row in titles:
        if row[0]:
            parts = [g.strip() for g in row[0].split(",")]
            genre_set.update(parts)
    return sorted(list(genre_set))

@app.get("/api/diagnostics")
def get_engine_diagnostics():
    """Retrieve runtime diagnostics, profiling, and schema validation statuses."""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline engine is initializing.")
    
    return diagnostics.to_dict()

# Serve static frontend builds if dist folder exists
frontend_dist_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.exists(frontend_dist_path):
    print(f"[Static] Serving frontend static assets from {frontend_dist_path}")
    app.mount("/", StaticFiles(directory=frontend_dist_path, html=True), name="frontend")
else:
    print(f"[Static] Frontend static directory '{frontend_dist_path}' not found. Serving API routes only.")
