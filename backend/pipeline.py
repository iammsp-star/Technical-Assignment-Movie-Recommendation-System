import time
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from backend.db import NetflixTitle

EXPECTED_COLUMNS = [
    "show_id", "type", "title", "director", "cast", 
    "country", "date_added", "release_year", "rating", 
    "duration", "listed_in", "description"
]

class PipelineDiagnostics:
    """Utility class to track pipeline execution times and assertions."""
    def __init__(self) -> None:
        self.stage_1_time: float = 0.0
        self.stage_2_time: float = 0.0
        self.stage_3_time: float = 0.0
        self.schema_valid: bool = False
        self.dataset_rows: int = 0
        self.matrix_shape: Tuple[int, int] = (0, 0)
        self.matrix_sparsity: float = 0.0
        self.assertions_passed: Dict[str, bool] = {
            "stage_1_columns_exist": False,
            "stage_1_non_empty": False,
            "stage_2_tfidf_shape": False,
            "stage_2_similarity_shape": False,
            "stage_3_score_bounds": False,
            "stage_3_output_length": False,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage_1_time_ms": round(self.stage_1_time * 1000, 2),
            "stage_2_time_ms": round(self.stage_2_time * 1000, 2),
            "stage_3_time_ms": round(self.stage_3_time * 1000, 2),
            "schema_valid": self.schema_valid,
            "dataset_rows": self.dataset_rows,
            "matrix_shape": list(self.matrix_shape),
            "matrix_sparsity_percent": round(self.matrix_sparsity * 100, 2),
            "assertions": self.assertions_passed
        }

# Global diagnostics tracker
diagnostics = PipelineDiagnostics()

class NetflixRecommendationPipeline:
    def __init__(self, csv_path: str) -> None:
        self.csv_path: str = csv_path
        self.df: pd.DataFrame = pd.DataFrame()
        self.tfidf_matrix: Optional[np.ndarray] = None
        self.similarity_matrix: Optional[np.ndarray] = None
        self.vectorizer: TfidfVectorizer = TfidfVectorizer(
            stop_words='english', 
            max_features=20000,
            ngram_range=(1, 2)
        )
        self.show_id_to_idx: Dict[str, int] = {}
        self.idx_to_show_id: Dict[int, str] = {}

    def run_stage_1_ingestion(self) -> pd.DataFrame:
        """Stage 1: Data Ingestion, cleaning, schema enforcement, and basic validation."""
        start_time = time.time()
        
        # Ingest CSV
        df = pd.read_csv(self.csv_path)
        
        # Verify columns exist
        col_check = all(col in df.columns for col in EXPECTED_COLUMNS)
        diagnostics.assertions_passed["stage_1_columns_exist"] = col_check
        assert col_check, f"Schema mismatch. Expected columns: {EXPECTED_COLUMNS}"

        # Clean string fields and handle NaNs
        string_cols = ["director", "cast", "country", "date_added", "rating", "duration", "listed_in", "description"]
        for col in string_cols:
            df[col] = df[col].fillna("").astype(str).str.strip()

        # Enforce exact type schemas
        df["show_id"] = df["show_id"].astype(str)
        df["type"] = df["type"].astype(str)
        df["title"] = df["title"].astype(str)
        df["release_year"] = pd.to_numeric(df["release_year"], errors='coerce').fillna(1900).astype(int)

        # Enforce shape constraint: should not be empty
        non_empty = len(df) > 0
        diagnostics.assertions_passed["stage_1_non_empty"] = non_empty
        assert non_empty, "DataFrame cannot be empty."

        self.df = df
        diagnostics.dataset_rows = len(df)
        diagnostics.schema_valid = True
        diagnostics.stage_1_time = time.time() - start_time
        return self.df

    def run_stage_2_core_engine(self) -> None:
        """Stage 2: Core Logic Engine: Text aggregation, vectorization, and similarity mapping."""
        start_time = time.time()
        assert not self.df.empty, "Dataframe must be ingested before running the core engine."

        # Collect all texts to build global vocabulary
        all_texts = (
            self.df["title"].tolist() + 
            self.df["director"].tolist() + 
            self.df["cast"].tolist() + 
            self.df["listed_in"].tolist() + 
            self.df["description"].tolist()
        )
        all_texts = [str(x).lower().strip() for x in all_texts if pd.notna(x)]

        # Fit global vectorizer
        self.vectorizer.fit(all_texts)

        # Transform individual columns to sparse matrices
        self.tfidf_title = self.vectorizer.transform(self.df["title"].fillna("").astype(str))
        self.tfidf_director = self.vectorizer.transform(self.df["director"].fillna("").astype(str))
        self.tfidf_cast = self.vectorizer.transform(self.df["cast"].fillna("").astype(str))
        self.tfidf_genre = self.vectorizer.transform(self.df["listed_in"].fillna("").astype(str))
        self.tfidf_desc = self.vectorizer.transform(self.df["description"].fillna("").astype(str))

        # Horizontal stack for global shape assertions
        import scipy.sparse as sp
        self.tfidf_matrix = sp.hstack([
            self.tfidf_title,
            self.tfidf_director,
            self.tfidf_cast,
            self.tfidf_genre,
            self.tfidf_desc
        ])

        num_rows = len(self.df)
        num_features = self.tfidf_matrix.shape[1]
        shape_check = self.tfidf_matrix.shape[0] == num_rows
        diagnostics.assertions_passed["stage_2_tfidf_shape"] = shape_check
        assert shape_check, f"TF-IDF matrix row count {self.tfidf_matrix.shape[0]} mismatch with row count {num_rows}."

        # Sparsity calculation
        total_elements = num_rows * num_features
        non_zero_elements = self.tfidf_matrix.nnz
        zero_elements = total_elements - non_zero_elements
        diagnostics.matrix_sparsity = float(zero_elements) / total_elements if total_elements > 0 else 1.0
        diagnostics.matrix_shape = (num_rows, num_features)

        # Precompute similarity matrix only for small test datasets
        if num_rows <= 100:
            sim_title = cosine_similarity(self.tfidf_title)
            sim_director = cosine_similarity(self.tfidf_director)
            sim_cast = cosine_similarity(self.tfidf_cast)
            sim_genre = cosine_similarity(self.tfidf_genre)
            sim_desc = cosine_similarity(self.tfidf_desc)
            
            # Default weights: title=2.0, director=3.0, cast=2.0, genre=3.0, desc=1.0 (sum=11.0)
            self.similarity_matrix = (
                2.0 * sim_title +
                3.0 * sim_director +
                2.0 * sim_cast +
                3.0 * sim_genre +
                1.0 * sim_desc
            ) / 11.0
            
            similarity_shape_check = self.similarity_matrix.shape == (num_rows, num_rows)
            diagnostics.assertions_passed["stage_2_similarity_shape"] = similarity_shape_check
            assert similarity_shape_check, "Similarity matrix must be square (N x N)."
        else:
            self.similarity_matrix = None
            diagnostics.assertions_passed["stage_2_similarity_shape"] = True

        # Create quick-lookup maps
        self.show_id_to_idx = {row["show_id"]: i for i, row in self.df.iterrows()}
        self.idx_to_show_id = {i: row["show_id"] for i, row in self.df.iterrows()}

        diagnostics.stage_2_time = time.time() - start_time

    def run_stage_3_recommend(
        self, 
        show_id: str, 
        top_n: int = 10,
        w_title: float = 2.0,
        w_director: float = 3.0,
        w_cast: float = 2.0,
        w_genre: float = 3.0,
        w_desc: float = 1.0
    ) -> List[Dict[str, Any]]:
        """Stage 3: Presentation and Query Layer. Returns top N recommended shows with similarity score."""
        start_time = time.time()
        
        # Verify inputs and state
        assert show_id in self.show_id_to_idx, f"Show ID '{show_id}' not found in pipeline."
        assert self.tfidf_matrix is not None, "TF-IDF matrix must be computed."
        assert top_n > 0, "Top N recommendations must be greater than 0."

        target_idx = self.show_id_to_idx[show_id]
        
        total_w = w_title + w_director + w_cast + w_genre + w_desc
        if total_w <= 0.0:
            w_title = w_director = w_cast = w_genre = w_desc = 1.0
            total_w = 5.0

        # Fetch similarity scores for the target show (dynamically if not precomputed or weights tuned)
        if self.similarity_matrix is not None and w_title == 2.0 and w_director == 3.0 and w_cast == 2.0 and w_genre == 3.0 and w_desc == 1.0:
            similarity_scores = self.similarity_matrix[target_idx]
        else:
            sim_title = cosine_similarity(self.tfidf_title[target_idx], self.tfidf_title).flatten()
            sim_director = cosine_similarity(self.tfidf_director[target_idx], self.tfidf_director).flatten()
            sim_cast = cosine_similarity(self.tfidf_cast[target_idx], self.tfidf_cast).flatten()
            sim_genre = cosine_similarity(self.tfidf_genre[target_idx], self.tfidf_genre).flatten()
            sim_desc = cosine_similarity(self.tfidf_desc[target_idx], self.tfidf_desc).flatten()

            similarity_scores = (
                w_title * sim_title +
                w_director * sim_director +
                w_cast * sim_cast +
                w_genre * sim_genre +
                w_desc * sim_desc
            ) / total_w
        
        # Get indices of sorted scores in descending order
        sorted_indices = np.argsort(similarity_scores)[::-1]
        
        # Exclude the target show itself from the recommendations list
        recommended_indices = [idx for idx in sorted_indices if idx != target_idx][:top_n]
        
        recommendations: List[Dict[str, Any]] = []
        scores_in_bounds = True
        
        for idx in recommended_indices:
            score = float(similarity_scores[idx])
            
            # Assertion validation: cosine similarity score bounds [0.0, 1.0] (allowing floating-point epsilon)
            if not (-0.0001 <= score <= 1.0001):
                scores_in_bounds = False
                
            rec_show_id = self.idx_to_show_id[idx]
            row = self.df.iloc[idx]
            
            recommendations.append({
                "show_id": rec_show_id,
                "title": row["title"],
                "type": row["type"],
                "release_year": int(row["release_year"]),
                "rating": row["rating"],
                "duration": row["duration"],
                "listed_in": row["listed_in"],
                "description": row["description"],
                "similarity_score": round(score, 4)
            })

        # Set diagnostics assertion check results
        diagnostics.assertions_passed["stage_3_score_bounds"] = scores_in_bounds
        assert scores_in_bounds, "Cosine similarity score out of bounds [0, 1]."
        
        output_len_check = len(recommendations) == top_n or len(recommendations) == len(self.df) - 1
        diagnostics.assertions_passed["stage_3_output_length"] = output_len_check
        assert output_len_check, f"Expected {top_n} recommendations, got {len(recommendations)}."

        diagnostics.stage_3_time = time.time() - start_time
        return recommendations

    def seed_database(self, db: Session) -> None:
        """Seed the SQLite database with the ingested data frame if database is empty."""
        assert not self.df.empty, "Dataframe must be loaded to seed database."
        
        # Check if table is already populated
        existing_count = db.query(NetflixTitle).count()
        if existing_count > 0:
            print(f"[DB] Database already seeded with {existing_count} records.")
            return

        print(f"[DB] Seeding SQLite database with {len(self.df)} records...")
        start_time = time.time()
        
        titles_to_insert = []
        for _, row in self.df.iterrows():
            titles_to_insert.append(NetflixTitle(
                show_id=row["show_id"],
                type=row["type"],
                title=row["title"],
                director=row["director"],
                cast=row["cast"],
                country=row["country"],
                date_added=row["date_added"],
                release_year=int(row["release_year"]),
                rating=row["rating"],
                duration=row["duration"],
                listed_in=row["listed_in"],
                description=row["description"]
            ))

        db.bulk_save_objects(titles_to_insert)
        db.commit()
        
        db_count = db.query(NetflixTitle).count()
        assert db_count == len(self.df), f"DB row count {db_count} does not match dataframe size {len(self.df)}."
        print(f"[DB] Seeding completed in {time.time() - start_time:.4f} seconds.")
