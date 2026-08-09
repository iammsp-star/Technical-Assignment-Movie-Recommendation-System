import os
import tempfile
import pytest
import pandas as pd
import numpy as np
from backend.pipeline import NetflixRecommendationPipeline, diagnostics, EXPECTED_COLUMNS

# Sample CSV content for unit testing
MOCK_CSV_CONTENT = """show_id,type,title,director,cast,country,date_added,release_year,rating,duration,listed_in,description
s1,Movie,Dick Johnson Is Dead,Kirsten Johnson,,United States,"September 25, 2021",2020,PG-13,90 min,Documentaries,"As her father nears the end of his life, filmmaker Kirsten Johnson stages his death in inventive and comical ways to help them both face the inevitable."
s2,TV Show,Blood & Water,,"Ama Qamata, Khosi Ngema, Gail Mabalane",South Africa,"September 24, 2021",2021,TV-MA,2 Seasons,"International TV Shows, TV Dramas","After crossing paths at a party, a Cape Town teen sets out to prove whether a private-school swimming star is her sister who was abducted at birth."
s3,TV Show,Ganglands,Julien Leclercq,"Sami Bouajila, Tracy Gotoas",France,"September 24, 2021",2021,TV-MA,1 Season,"Crime TV Shows, International TV Shows","To protect his family from a powerful drug lord, skilled thief Mehdi and his expert team of robbers are pulled into a violent and deadly turf war."
s4,TV Show,Jailbirds New Orleans,,,"September 24, 2021",2021,TV-MA,1 Season,Docuseries,Feuds, flirtations and toilet talk go down among the incarcerated women.
s5,Movie,Kota Factory,,Mayur More,India,"September 24, 2021",2021,TV-MA,2 Seasons,International TV Shows,"In a city of coaching centers, students navigate campus life."
"""

@pytest.fixture
def temp_csv_file():
    """Create a temporary CSV file populated with mock Netflix data."""
    fd, temp_file_path = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(MOCK_CSV_CONTENT)
    yield temp_file_path
    os.remove(temp_file_path)

def test_pipeline_stage_1_ingestion(temp_csv_file):
    """Test data loading, cleaning, types, and schema validation."""
    pipeline = NetflixRecommendationPipeline(temp_csv_file)
    df = pipeline.run_stage_1_ingestion()

    # Check assertions tracked in diagnostics
    assert diagnostics.schema_valid is True
    assert diagnostics.assertions_passed["stage_1_columns_exist"] is True
    assert diagnostics.assertions_passed["stage_1_non_empty"] is True

    # Assert correct row count and shapes
    assert len(df) == 5
    assert list(df.columns) == EXPECTED_COLUMNS
    
    # Assert NaN values are successfully replaced with empty strings
    assert df.loc[df["show_id"] == "s2", "director"].values[0] == ""
    assert df.loc[df["show_id"] == "s2", "cast"].values[0] == "Ama Qamata, Khosi Ngema, Gail Mabalane"
    
    # Assert type casting
    assert isinstance(df["release_year"].iloc[0], (int, np.integer))

def test_pipeline_stage_2_core_engine(temp_csv_file):
    """Test text processing, TF-IDF vectorizer, and similarity matrix calculations."""
    pipeline = NetflixRecommendationPipeline(temp_csv_file)
    pipeline.run_stage_1_ingestion()
    pipeline.run_stage_2_core_engine()

    # Assert matrix shape correctness
    assert pipeline.tfidf_matrix is not None
    assert pipeline.tfidf_matrix.shape[0] == 5
    assert pipeline.tfidf_matrix.shape[1] > 0
    assert diagnostics.assertions_passed["stage_2_tfidf_shape"] is True

    # Assert square symmetry of similarity matrix
    assert pipeline.similarity_matrix is not None
    assert pipeline.similarity_matrix.shape == (5, 5)
    assert diagnostics.assertions_passed["stage_2_similarity_shape"] is True

    # Cosine similarity diagonal should be high (greater than 0.5)
    for i in range(5):
        assert pipeline.similarity_matrix[i, i] > 0.5

def test_pipeline_stage_3_recommend(temp_csv_file):
    """Test querying and fetching top N recommendations with similarity scores."""
    pipeline = NetflixRecommendationPipeline(temp_csv_file)
    pipeline.run_stage_1_ingestion()
    pipeline.run_stage_2_core_engine()

    # Get top 2 recommendations for show 's2' (Blood & Water)
    recommendations = pipeline.run_stage_3_recommend("s2", top_n=2)

    assert len(recommendations) == 2
    assert diagnostics.assertions_passed["stage_3_score_bounds"] is True
    assert diagnostics.assertions_passed["stage_3_output_length"] is True

    # Assert target show is excluded from recommendations list
    for rec in recommendations:
        assert rec["show_id"] != "s2"
        assert 0.0 <= rec["similarity_score"] <= 1.0
        assert isinstance(rec["title"], str)

def test_pipeline_stage_3_invalid_inputs(temp_csv_file):
    """Test appropriate assertion errors are raised on invalid pipeline query inputs."""
    pipeline = NetflixRecommendationPipeline(temp_csv_file)
    pipeline.run_stage_1_ingestion()
    pipeline.run_stage_2_core_engine()

    # Assert error raised when querying non-existent show
    with pytest.raises(AssertionError):
        pipeline.run_stage_3_recommend("s999", top_n=2)

    # Assert error raised when asking for 0 or negative recommendations
    with pytest.raises(AssertionError):
        pipeline.run_stage_3_recommend("s1", top_n=0)

def test_pipeline_dynamic_weights(temp_csv_file):
    """Test that dynamic weight tuning correctly influences recommendation scores."""
    pipeline = NetflixRecommendationPipeline(temp_csv_file)
    pipeline.run_stage_1_ingestion()
    pipeline.run_stage_2_core_engine()

    # Get recommendations with default weights
    recs_default = pipeline.run_stage_3_recommend("s2", top_n=2, w_title=2.0, w_director=3.0, w_cast=2.0, w_genre=3.0, w_desc=1.0)
    
    # Get recommendations with customized weights (boosting title, disabling others)
    recs_custom = pipeline.run_stage_3_recommend("s2", top_n=2, w_title=10.0, w_director=0.0, w_cast=0.0, w_genre=0.0, w_desc=0.0)

    assert len(recs_default) == 2
    assert len(recs_custom) == 2
    
    # Scores should differ due to weighting overrides
    assert recs_default[0]["similarity_score"] != recs_custom[0]["similarity_score"]

