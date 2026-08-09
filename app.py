import streamlit as st
import time
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Set, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Set page config to dark mode and wide layout
st.set_page_config(
    page_title="Netflix Personalization Engine",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------------------------------------------
# 1. SYNTHETIC CATALOG DATASET
# ----------------------------------------------------
CATALOG: List[Dict[str, Any]] = [
    {
        "show_id": "s1", "type": "TV Show", "title": "Stranger Things", "language": "English",
        "listed_in": "Sci-Fi, Crime/Thriller, Horror", "release_year": 2022, "rating": "TV-14", "duration": "4 Seasons",
        "director": "The Duffer Brothers", "cast": "Millie Bobby Brown, Winona Ryder, David Harbour",
        "description": "A young boy vanishes in a small Indiana town. His friends uncover a government lab, an alternate dimension, and dark monsters."
    },
    {
        "show_id": "s2", "type": "TV Show", "title": "Squid Game", "language": "Korean",
        "listed_in": "Crime/Thriller, Action", "release_year": 2021, "rating": "TV-MA", "duration": "1 Season",
        "director": "Hwang Dong-hyuk", "cast": "Lee Jung-jae, Park Hae-soo, Wi Ha-jun",
        "description": "Hundreds of cash-strapped players accept a strange invitation to compete in children's games. The stakes are high and deadly."
    },
    {
        "show_id": "s3", "type": "TV Show", "title": "Sacred Games", "language": "Hindi",
        "listed_in": "Crime/Thriller, Action", "release_year": 2019, "rating": "TV-MA", "duration": "2 Seasons",
        "director": "Vikramaditya Motwane, Anurag Kashyap", "cast": "Saif Ali Khan, Nawazuddin Siddiqui, Radhika Apte",
        "description": "A link in their pasts leads an honest cop to a fugitive gang boss. Cryptic warnings spur a quest to save Mumbai from chaos."
    },
    {
        "show_id": "s4", "type": "TV Show", "title": "Money Heist", "language": "Spanish",
        "listed_in": "Crime/Thriller, Action", "release_year": 2021, "rating": "TV-MA", "duration": "5 Seasons",
        "director": "Álex Pina", "cast": "Álvaro Morte, Úrsula Corberó, Itziar Ituño",
        "description": "Eight thieves take hostages and lock themselves in the Royal Mint of Spain. A criminal mastermind manipulates the police."
    },
    {
        "show_id": "s5", "type": "TV Show", "title": "Demon Slayer", "language": "Japanese",
        "listed_in": "Anime, Action, Sci-Fi", "release_year": 2021, "rating": "TV-MA", "duration": "2 Seasons",
        "director": "Haruo Sotozaki", "cast": "Natsuki Hanae, Akari Kito, Yoshitsugu Matsuoka",
        "description": "A youth fights bloodthirsty demons after his family is slaughtered, seeking to save his mutated sister who is turning into one."
    },
    {
        "show_id": "s6", "type": "TV Show", "title": "Narcos", "language": "Spanish",
        "listed_in": "Crime/Thriller, Documentaries", "release_year": 2017, "rating": "TV-MA", "duration": "3 Seasons",
        "director": "Andrés Baiz", "cast": "Wagner Moura, Boyd Holbrook, Pedro Pascal",
        "description": "A gritty chronicle of the real-life rise and spread of cocaine drug cartels across Colombia and law enforcement struggles."
    },
    {
        "show_id": "s7", "type": "Movie", "title": "Inception", "language": "English",
        "listed_in": "Sci-Fi, Action, Crime/Thriller", "release_year": 2010, "rating": "PG-13", "duration": "148 min",
        "director": "Christopher Nolan", "cast": "Leonardo DiCaprio, Joseph Gordon-Levitt, Elliot Page",
        "description": "A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea."
    },
    {
        "show_id": "s8", "type": "Movie", "title": "The Matrix", "language": "English",
        "listed_in": "Sci-Fi, Action", "release_year": 1999, "rating": "R", "duration": "136 min",
        "director": "Lana Wachowski, Lilly Wachowski", "cast": "Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss",
        "description": "A computer hacker discovers a shocking truth from mysterious rebels: his entire reality is a complex simulation ruled by machines."
    },
    {
        "show_id": "s9", "type": "TV Show", "title": "Mirzapur", "language": "Hindi",
        "listed_in": "Crime/Thriller, Action", "release_year": 2020, "rating": "TV-MA", "duration": "2 Seasons",
        "director": "Karan Anshuman, Gurmmeet Singh", "cast": "Pankaj Tripathi, Ali Fazal, Divyendu Sharma",
        "description": "A wedding incident ignites a series of events, leading to a power struggle, crime, and lawlessness in northern India."
    },
    {
        "show_id": "s10", "type": "TV Show", "title": "Crash Landing on You", "language": "Korean",
        "listed_in": "Romance, Comedy", "release_year": 2020, "rating": "TV-14", "duration": "1 Season",
        "director": "Lee Jeong-hyo", "cast": "Hyun Bin, Son Ye-jin, Seo Ji-hye",
        "description": "A South Korean paraglider accidentally crosses the border into North Korea, where a sympathetic military officer hides her."
    },
    {
        "show_id": "s11", "type": "Movie", "title": "My Name", "language": "Korean",
        "listed_in": "Action, Crime/Thriller", "release_year": 2021, "rating": "TV-MA", "duration": "120 min",
        "director": "Kim Jin-min", "cast": "Han So-hee, Park Hee-soon, Ahn Bo-hyun",
        "description": "Following her father's murder, a revenge-driven woman puts her trust in a drug lord and goes undercover as a police officer."
    },
    {
        "show_id": "s12", "type": "Movie", "title": "3 Idiots", "language": "Hindi",
        "listed_in": "Comedy, Romance", "release_year": 2009, "rating": "PG-13", "duration": "170 min",
        "director": "Rajkumar Hirani", "cast": "Aamir Khan, Kareena Kapoor, R. Madhavan",
        "description": "Two friends search for their long-lost college companion, recalling his philosophies that challenged academic systems."
    },
    {
        "show_id": "s13", "type": "Movie", "title": "Dangal", "language": "Hindi",
        "listed_in": "Action, Documentaries", "release_year": 2016, "rating": "PG", "duration": "161 min",
        "director": "Nitesh Tiwari", "cast": "Aamir Khan, Sakshi Tanwar, Fatima Sana Shaikh",
        "description": "A former wrestler struggles to coach his daughters towards Commonwealth Games wrestling glory against social barriers."
    },
    {
        "show_id": "s14", "type": "Movie", "title": "Interstellar", "language": "English",
        "listed_in": "Sci-Fi, Horror", "release_year": 2014, "rating": "PG-13", "duration": "169 min",
        "director": "Christopher Nolan", "cast": "Matthew McConaughey, Anne Hathaway, Jessica Chastain",
        "description": "A team of space explorers travels through a newly discovered wormhole in search of a new home planet for dying humanity."
    },
    {
        "show_id": "s15", "type": "Movie", "title": "Spirited Away", "language": "Japanese",
        "listed_in": "Anime, Sci-Fi", "release_year": 2001, "rating": "PG", "duration": "125 min",
        "director": "Hayao Miyazaki", "cast": "Rumi Hiiragi, Miyu Irino, Mari Natsuki",
        "description": "A young girl wanders into a spirit world ruled by gods and witches. She must work in a bathhouse to free her cursed parents."
    },
    {
        "show_id": "s16", "type": "TV Show", "title": "Our Planet", "language": "English",
        "listed_in": "Documentaries", "release_year": 2019, "rating": "TV-PG", "duration": "1 Season",
        "director": "Alastair Fothergill", "cast": "David Attenborough",
        "description": "Experience our planet's natural beauty and examine how climate change impacts all living creatures in this spectacular series."
    },
    {
        "show_id": "s17", "type": "Movie", "title": "The Conjuring", "language": "English",
        "listed_in": "Horror", "release_year": 2013, "rating": "R", "duration": "112 min",
        "director": "James Wan", "cast": "Vera Farmiga, Patrick Wilson, Lili Taylor",
        "description": "Paranormal investigators Ed and Lorraine Warren work to help a family terrorized by a dark presence in their farmhouse."
    },
    {
        "show_id": "s18", "type": "Movie", "title": "Minnal Murali", "language": "Malayalam",
        "listed_in": "Action, Comedy", "release_year": 2021, "rating": "TV-14", "duration": "158 min",
        "director": "Basil Joseph", "cast": "Tovino Thomas, Guru Somasundaram",
        "description": "An ordinary tailor gains superpower lightning speed after being struck by lightning, becoming the savior of his hometown."
    },
    {
        "show_id": "s19", "type": "TV Show", "title": "Emily in Paris", "language": "English",
        "listed_in": "Romance, Comedy", "release_year": 2020, "rating": "TV-MA", "duration": "3 Seasons",
        "director": "Darren Star", "cast": "Lily Collins, Philippine Leroy-Beaulieu",
        "description": "A young American marketing executive gets her dream job in Paris, navigating French culture, romance, and friendship."
    },
    {
        "show_id": "s20", "type": "Movie", "title": "Super Deluxe", "language": "Tamil",
        "listed_in": "Crime/Thriller, Comedy", "release_year": 2019, "rating": "TV-MA", "duration": "176 min",
        "director": "Thiagarajan Kumararaja", "cast": "Vijay Sethupathi, Fahadh Faasil, Samantha Ruth Prabhu",
        "description": "An angry boy, a cheating wife, a transgender woman, and a priest find themselves in unexpected predicaments on a fateful day."
    }
]

# Convert catalog to a clean Pandas DataFrame for processing
df_catalog = pd.DataFrame(CATALOG)

# ----------------------------------------------------
# 2. CUSTOM NETFLIX STYLE SHEET INJECTION
# ----------------------------------------------------
st.markdown(
    """
    <style>
    /* Global Styles */
    .stApp {
        background-color: #141414;
        color: #f5f5f7;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Hide default Streamlit interfaces */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Heading Overrides */
    h1, h2, h3, h4, h5, h6 {
        color: #f5f5f7 !important;
        font-weight: 800 !important;
    }
    
    /* Netflix Header Bar */
    .netflix-navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
        border-bottom: 1px solid #282828;
    }
    .netflix-logo {
        color: #e50914;
        font-size: 2.2rem;
        font-weight: 900;
        letter-spacing: -1.5px;
        text-transform: uppercase;
    }
    
    /* Progress indicator bar */
    .progress-bar-container {
        width: 100%;
        background-color: #282828;
        height: 6px;
        border-radius: 3px;
        margin-bottom: 2rem;
        position: relative;
    }
    .progress-bar-fill {
        background-color: #e50914;
        height: 100%;
        border-radius: 3px;
        transition: width 0.4s ease;
    }
    .progress-steps {
        display: flex;
        justify-content: space-between;
        font-size: 0.8rem;
        font-weight: 700;
        color: #8e8e93;
        margin-top: 0.5rem;
    }
    .progress-step-active {
        color: #f5f5f7;
    }
    
    /* Onboarding Selection Buttons */
    div.stButton > button {
        background-color: #181818 !important;
        color: #c7c7cc !important;
        border: 1px solid #282828 !important;
        border-radius: 6px !important;
        padding: 1.2rem !important;
        width: 100% !important;
        min-height: 80px !important;
        transition: all 0.2s ease !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
    }
    div.stButton > button:hover {
        border-color: #e50914 !important;
        background-color: #222222 !important;
        color: #f5f5f7 !important;
        transform: translateY(-2px);
    }
    div.stButton > button[kind="primary"] {
        border: 2px solid #e50914 !important;
        background-color: #1a0a0b !important;
        color: #e50914 !important;
    }
    
    /* Onboarding Next Buttons */
    .next-btn-container {
        display: flex;
        justify-content: flex-end;
        margin-top: 2rem;
    }
    
    /* Movie Onboarding Selection Cards */
    .movie-card-onboarding {
        background-color: #181818;
        border: 1px solid #282828;
        border-radius: 8px;
        padding: 1rem;
        height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        cursor: pointer;
        transition: all 0.2s ease;
        position: relative;
    }
    .movie-card-onboarding:hover {
        border-color: #e50914;
        background-color: #222;
    }
    .movie-card-selected {
        border: 2px solid #e50914;
        background-color: #1a0a0b;
    }
    
    /* Floating footer bar */
    .floating-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: rgba(20, 20, 20, 0.95);
        backdrop-filter: blur(15px);
        border-top: 1px solid #282828;
        padding: 1.25rem 3rem;
        z-index: 1000;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Netflix Loader Spinner */
    .netflix-spinner {
        width: 50px;
        height: 50px;
        border: 4px solid #282828;
        border-top-color: #e50914;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 2rem auto;
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Hero Banner */
    .hero-banner {
        background-size: cover;
        background-position: center;
        height: 40vh;
        min-height: 320px;
        border-radius: 12px;
        position: relative;
        overflow: hidden;
        display: flex;
        align-items: flex-end;
        padding: 2.5rem;
        border: 1px solid #282828;
        margin-bottom: 2.5rem;
    }
    .hero-banner-overlay {
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(to top, rgba(20, 20, 20, 1) 0%, rgba(20, 20, 20, 0.6) 50%, rgba(20, 20, 20, 0.1) 100%),
                    linear-gradient(to right, rgba(20, 20, 20, 0.9) 0%, rgba(20, 20, 20, 0.1) 100%);
        z-index: 1;
    }
    .hero-banner-content {
        position: relative;
        z-index: 2;
        max-width: 650px;
    }
    .match-score {
        color: #46D369;
        font-weight: 700;
        font-size: 0.95rem;
        margin-right: 0.75rem;
    }
    .hero-genre-tag {
        color: #e50914;
        font-weight: 800;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 2px;
        margin-bottom: 0.25rem;
    }
    
    /* Homepage Recommended Rows */
    .row-title {
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.85rem;
        padding-left: 0.25rem;
        border-left: 3px solid #e50914;
    }
    .movie-row-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        gap: 1.25rem;
        margin-bottom: 2.5rem;
    }
    .homepage-card {
        background-color: #181818;
        border: 1px solid #282828;
        border-radius: 8px;
        overflow: hidden;
        transition: transform 0.2s ease, border-color 0.2s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    .homepage-card:hover {
        transform: scale(1.03);
        border-color: rgba(229, 9, 20, 0.4);
    }
    .card-banner {
        height: 110px;
        background: linear-gradient(135deg, #222 0%, #151515 100%);
        padding: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        border-bottom: 1px solid #282828;
        position: relative;
    }
    .card-banner-title {
        font-size: 0.95rem;
        font-weight: 700;
        line-height: 1.3;
    }
    .card-meta-line {
        display: flex;
        justify-content: space-between;
        font-size: 0.75rem;
        color: #8e8e93;
        margin-top: 0.5rem;
    }
    .card-tag-badge {
        position: absolute;
        top: 6px;
        left: 6px;
        font-size: 0.6rem;
        font-weight: 800;
        background-color: #e50914;
        color: white;
        padding: 0.15rem 0.35rem;
        border-radius: 3px;
        text-transform: uppercase;
    }
    
    /* Debug Logger Code Block */
    .debug-log-console {
        background-color: #0b0b0c;
        border: 1px solid #282828;
        padding: 1rem;
        border-radius: 6px;
        font-family: monospace;
        font-size: 0.75rem;
        color: #30d158;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------------------------------
# 3. CORE RECOMMENDATION BACKEND ENGINE
# ----------------------------------------------------
class NetflixRecommendationEngine:
    def __init__(self, catalog_df: pd.DataFrame) -> None:
        self.df = catalog_df.copy()
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        
        # Fit vocabulary on all aggregated text fields
        all_metadata = (
            self.df["listed_in"].tolist() + 
            self.df["description"].tolist()
        )
        self.vectorizer.fit(all_metadata)
        
        # Transform descriptions to sparse matrices
        self.tfidf_matrix = self.vectorizer.transform(self.df["description"])
        
    def generate_recommendations(
        self, 
        selected_titles: Set[str], 
        selected_genres: Set[str], 
        selected_languages: Set[str]
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Calculates dynamic Hybrid Cosine-Similarity scores for all items in catalog."""
        start_time = time.time()
        
        # 1. Construct user profile query text
        # Combine descriptions of selected movies and names of selected genres
        seed_descriptions = []
        for title in selected_titles:
            matches = self.df[self.df["title"] == title]
            if not matches.empty:
                seed_descriptions.append(matches.iloc[0]["description"])
                
        profile_query_text = " ".join(selected_genres) + " " + " ".join(seed_descriptions)
        
        # 2. Vectorize user profile text
        query_vector = self.vectorizer.transform([profile_query_text])
        
        # Assertions validation: shape conformance check
        assert query_vector.shape == (1, self.tfidf_matrix.shape[1]), "Vector dimensions mismatch"
        
        # 3. Calculate raw Cosine Similarity scores
        raw_similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # 4. Apply multipliers and boosts based on preferences
        final_scores = []
        for idx, row in self.df.iterrows():
            score = float(raw_similarities[idx])
            
            # Exclusion logic: If the movie matches a seed selected movie, score = 0 to avoid duplicates
            if row["title"] in selected_titles:
                score = 0.0
                final_scores.append((row.to_dict(), score))
                continue
            
            # Language Multiplier
            # Filter non-selected languages unless user picks no language (fallback default: treat as all allowed)
            if selected_languages:
                if row["language"] in selected_languages:
                    score *= 1.5  # Boost matching languages
                else:
                    score *= 0.1  # Heavy penalty for unselected languages
                    
            # Genre Match Boost
            movie_genres = [g.strip().lower() for g in row["listed_in"].split(",")]
            matches_genre = any(genre.lower() in movie_genres for genre in selected_genres)
            if matches_genre:
                score += 0.25  # Substantial additive boost
                
            # Normalize final scores to [0.0, 1.0] (cap similarity scores)
            score = min(max(score, 0.0), 1.0)
            final_scores.append((row.to_dict(), score))
            
        # Sort recommendations by final score descending
        final_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Diagnostics timing metrics
        self.latency_ms = (time.time() - start_time) * 1000
        return final_scores

# Instantiate global engine singleton
engine = NetflixRecommendationEngine(df_catalog)

# ----------------------------------------------------
# 4. INITIALIZE SESSION STATE WIZARD
# ----------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = 1.1
if "selected_languages" not in st.session_state:
    st.session_state.selected_languages = set()
if "selected_genres" not in st.session_state:
    st.session_state.selected_genres = set()
if "selected_movies" not in st.session_state:
    st.session_state.selected_movies = set()
if "completed_onboarding" not in st.session_state:
    st.session_state.completed_onboarding = False

# ----------------------------------------------------
# 5. USER ONBOARDING WIZARD STEPS
# ----------------------------------------------------

# Navbar Logo Header
st.markdown(
    """
    <div class="netflix-navbar">
        <div class="netflix-logo">Netflix</div>
        <div><span style="color:#8e8e93; font-weight:700;">Onboarding Wizard</span></div>
    </div>
    """,
    unsafe_allow_html=True
)

if not st.session_state.completed_onboarding:
    # Progress bar mapping
    step_width = 33
    active_step = "Languages"
    if st.session_state.step == 1.2:
        step_width = 66
        active_step = "Genres"
    elif st.session_state.step == 1.3:
        step_width = 100
        active_step = "Movies"
        
    st.markdown(
        f"""
        <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: {step_width}%;"></div>
            <div class="progress-steps">
                <span class="{'progress-step-active' if active_step == 'Languages' else ''}">1. Languages</span>
                <span class="{'progress-step-active' if active_step == 'Genres' else ''}">2. Genres</span>
                <span class="{'progress-step-active' if active_step == 'Movies' else ''}">3. Titles Setup</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # ----------------------------------------------------
    # STEP 1.1: LANGUAGE SELECTION
    # ----------------------------------------------------
    if st.session_state.step == 1.1:
        st.subheader("What languages do you prefer to watch content in?")
        st.write("We will prioritize and custom-match catalog titles in your selected languages.")
        
        languages_list = ["English", "Hindi", "Korean", "Spanish", "Japanese", "Tamil", "Malayalam"]
        
        cols = st.columns(4)
        for idx, lang in enumerate(languages_list):
            col = cols[idx % 4]
            selected = lang in st.session_state.selected_languages
            if col.button(lang, key=f"lang_{lang}", type="primary" if selected else "secondary"):
                if selected:
                    st.session_state.selected_languages.remove(lang)
                else:
                    st.session_state.selected_languages.add(lang)
                st.rerun()
                
        # Navigation
        st.markdown('<div class="next-btn-container">', unsafe_allow_html=True)
        # Check if at least one language is chosen (fallback: English)
        if st.button("Next ➔", key="btn_next_1.1", type="primary"):
            if not st.session_state.selected_languages:
                st.session_state.selected_languages.add("English") # Fallback default
            st.session_state.step = 1.2
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ----------------------------------------------------
    # STEP 1.2: GENRE SELECTION
    # ----------------------------------------------------
    elif st.session_state.step == 1.2:
        st.subheader("Select at least 3 genres you enjoy.")
        st.write("This weights your recommendation rows and changes the Hero Banner genre targeting.")
        
        genres_list = ["Action", "Sci-Fi", "Crime/Thriller", "Romance", "Comedy", "Anime", "Horror", "Documentaries"]
        
        cols = st.columns(4)
        for idx, genre in enumerate(genres_list):
            col = cols[idx % 4]
            selected = genre in st.session_state.selected_genres
            if col.button(genre, key=f"genre_{genre}", type="primary" if selected else "secondary"):
                if selected:
                    st.session_state.selected_genres.remove(genre)
                else:
                    st.session_state.selected_genres.add(genre)
                st.rerun()
                
        # Navigation Next trigger (requires min 3 genres)
        genre_count = len(st.session_state.selected_genres)
        st.markdown(
            f"""
            <div style="margin-top: 1rem; color: {'#46D369' if genre_count >= 3 else '#8e8e93'}; font-weight:700;">
                Selected: {genre_count} / 3 Genres Chosen
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        st.markdown('<div class="next-btn-container">', unsafe_allow_html=True)
        next_disabled = genre_count < 3
        if st.button("Next ➔", key="btn_next_1.2", type="primary" if not next_disabled else "secondary", disabled=next_disabled):
            st.session_state.step = 1.3
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ----------------------------------------------------
    # STEP 1.3: PICK 3 MOVIES OR SHOWS YOU LOVE
    # ----------------------------------------------------
    elif st.session_state.step == 1.3:
        st.subheader("Choose 3 titles you like to help us personalize your recommendations.")
        st.write("We use these as reference seeds to compute content-based similarity vectors.")

        # Search Bar
        search_q = st.text_input("🔍 Search Movies or TV Shows", "").strip().lower()
        
        # Filter matching items in catalog
        filtered_catalog = CATALOG
        if search_q:
            filtered_catalog = [item for item in CATALOG if search_q in item["title"].lower() or search_q in item["listed_in"].lower()]
            
        if not filtered_catalog:
            st.warning("No matches found in synthetic catalog.")
        else:
            cols = st.columns(3)
            for idx, item in enumerate(filtered_catalog):
                col = cols[idx % 3]
                title = item["title"]
                selected = title in st.session_state.selected_movies
                
                # Visual Container Card with Streamlit button inside to capture clicks
                selected_class = "movie-card-selected" if selected else ""
                card_html = f"""
                <div class="movie-card-onboarding {selected_class}">
                    <div style="font-weight:800; font-size:1rem; line-height:1.2;">{title}</div>
                    <div style="font-size:0.75rem; color:#8e8e93;">{item['listed_in']} | {item['language']}</div>
                    <div style="font-size:0.7rem; color:#e50914; font-weight:700;">{item['type']}</div>
                </div>
                """
                col.markdown(card_html, unsafe_allow_html=True)
                
                # Hidden click trigger
                btn_lbl = "Deselect" if selected else "Select"
                if col.button(btn_lbl, key=f"select_{item['show_id']}", type="primary" if selected else "secondary"):
                    if selected:
                        st.session_state.selected_movies.remove(title)
                    else:
                        # Allow exactly/max 3 movies
                        if len(st.session_state.selected_movies) < 3:
                            st.session_state.selected_movies.add(title)
                        else:
                            st.warning("You have already selected 3 movies. Deselect one to choose another.")
                    st.rerun()
                    
        # Floating footer status bar
        sel_count = len(st.session_state.selected_movies)
        finish_disabled = sel_count < 3
        
        # Render custom HTML floating bar at the bottom
        st.markdown(
            f"""
            <div class="floating-bar">
                <div style="font-weight:800; font-size:1.1rem; color: {'#46D369' if sel_count == 3 else '#f5f5f7'};">
                    Selected Profile Seeds: {sel_count} / 3
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Streamlit button laid over the floating bar area (aligned right)
        _, finish_col = st.columns([4, 1])
        if finish_col.button("Finish & Personalize ➔", key="btn_finish", disabled=finish_disabled, type="primary"):
            st.session_state.step = "loading"
            st.rerun()

    # ----------------------------------------------------
    # STEP 2: PERSONALIZED PROCESSING LOADING TRANSITION
    # ----------------------------------------------------
    elif st.session_state.step == "loading":
        st.markdown(
            """
            <div style="text-align: center; margin-top: 5rem;">
                <h2>Personalizing Netflix for You...</h2>
                <div class="netflix-spinner"></div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Transitioning steps status log
        placeholder = st.empty()
        
        steps = [
            "Analyzing your taste profile...",
            "Building your custom rows...",
            "Loading catalog and matching metadata...",
            "Ready!"
        ]
        
        for index, text in enumerate(steps):
            placeholder.markdown(f"<h4 style='text-align: center; color: #8e8e93;'>{text}</h4>", unsafe_allow_html=True)
            time.sleep(0.7)
            
        st.session_state.completed_onboarding = True
        st.session_state.step = 3
        st.rerun()

# ----------------------------------------------------
# STEP 3: CUSTOMIZED HOMEPAGE LAYOUT
# ----------------------------------------------------
else:
    # 1. Calculate Recommendations Vector using preference parameters
    recs = engine.generate_recommendations(
        st.session_state.selected_movies,
        st.session_state.selected_genres,
        st.session_state.selected_languages
    )
    
    # Header bar
    st.markdown(
        """
        <div class="netflix-navbar" style="border:none; margin-bottom: 0;">
            <div class="netflix-logo">Netflix</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Start over reset button (aligned right in streamlit columns)
    nav_col1, nav_col2 = st.columns([4, 1])
    nav_col1.markdown("<h3 style='margin:0;'>Personalized Home</h3>", unsafe_allow_html=True)
    if nav_col2.button("Reset / Start Over ↺", key="btn_reset", type="primary"):
        st.session_state.step = 1.1
        st.session_state.selected_languages = set()
        st.session_state.selected_genres = set()
        st.session_state.selected_movies = set()
        st.session_state.completed_onboarding = False
        st.rerun()
        
    st.markdown("<hr style='border-color: #282828; margin: 1rem 0;'>", unsafe_allow_html=True)

    # 2. Dynamic Hero Banner Selection
    # Target first recommendation matching highest weight (e.g., top recommendation)
    hero_item = recs[0][0]
    hero_score = recs[0][1]
    
    hero_html = f"""
    <div class="hero-section">
        <div class="hero-overlay"></div>
        <div class="hero-banner-content">
            <div class="hero-genre-tag">{hero_item['listed_in']}</div>
            <h1 class="hero-title" style="font-size: 3rem; margin-bottom:0.5rem;">{hero_item['title']}</h1>
            <div class="hero-meta" style="margin-bottom: 0.75rem;">
                <span class="match-score">{(hero_score * 100):.0f}% Match</span>
                <span style="color:#8e8e93;">{hero_item['release_year']}</span>
                <span style="color:#8e8e93; border: 1px solid #8e8e93; padding: 0 0.3rem; font-size: 0.75rem; border-radius:3px;">{hero_item['rating']}</span>
                <span style="color:#8e8e93;">{hero_item['duration']}</span>
                <span style="color:#8e8e93;">📍 {hero_item['language']}</span>
            </div>
            <p style="font-size: 1rem; color: #c7c7cc; line-height: 1.4; margin-bottom: 1.25rem;">{hero_item['description']}</p>
        </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)

    # 3. Customized Rows
    
    # ----------------------------------------------------
    # Row 1: "Top Picks for You" (Hybrid Personalized Row)
    # ----------------------------------------------------
    st.markdown('<div class="row-title">Top Picks for You</div>', unsafe_allow_html=True)
    row_1_titles = recs[:4]
    
    cols = st.columns(4)
    for idx, (item, score) in enumerate(row_1_titles):
        card_html = f"""
        <div class="homepage-card">
            <div class="card-banner">
                <span class="card-tag-badge">{item['type']}</span>
                <div class="card-banner-title">{item['title']}</div>
            </div>
            <div style="padding: 1rem; display: flex; flex-direction: column; justify-content: space-between; flex-grow: 1;">
                <div style="font-size: 0.8rem; color:#e50914; font-weight:700;">{item['listed_in']}</div>
                <div class="card-meta-line">
                    <span style="color:#46D369; font-weight:700;">{(score*100):.0f}% Match</span>
                    <span>{item['language']}</span>
                </div>
            </div>
        </div>
        """
        cols[idx].markdown(card_html, unsafe_allow_html=True)
        
    # ----------------------------------------------------
    # Row 2: "Because You Picked [Selected Movie Name]" (Content-based filtering)
    # ----------------------------------------------------
    seed_movie = list(st.session_state.selected_movies)[0]
    st.markdown(f'<div class="row-title">Because You Picked {seed_movie}</div>', unsafe_allow_html=True)
    
    # Generate similarities focused purely on seed description matching
    seed_desc = df_catalog[df_catalog["title"] == seed_movie].iloc[0]["description"]
    seed_vec = engine.vectorizer.transform([seed_desc])
    desc_similarities = cosine_similarity(seed_vec, engine.tfidf_matrix).flatten()
    
    row_2_scores = []
    for idx, row in df_catalog.iterrows():
        # Exclude self
        if row["title"] == seed_movie:
            continue
        row_2_scores.append((row.to_dict(), desc_similarities[idx]))
    row_2_scores.sort(key=lambda x: x[1], reverse=True)
    row_2_titles = row_2_scores[:4]
    
    cols2 = st.columns(4)
    for idx, (item, score) in enumerate(row_2_titles):
        card_html = f"""
        <div class="homepage-card">
            <div class="card-banner">
                <span class="card-tag-badge">{item['type']}</span>
                <div class="card-banner-title">{item['title']}</div>
            </div>
            <div style="padding: 1rem; display: flex; flex-direction: column; justify-content: space-between; flex-grow: 1;">
                <div style="font-size: 0.8rem; color:#e50914; font-weight:700;">{item['listed_in']}</div>
                <div class="card-meta-line">
                    <span style="color:#46D369; font-weight:700;">{(score*100):.0f}% Similarity</span>
                    <span>{item['language']}</span>
                </div>
            </div>
        </div>
        """
        cols2[idx].markdown(card_html, unsafe_allow_html=True)

    # ----------------------------------------------------
    # Row 3: "Top [Selected Language] Movies" (Language-filtered)
    # ----------------------------------------------------
    target_lang = list(st.session_state.selected_languages)[0]
    st.markdown(f'<div class="row-title">Top {target_lang} Titles</div>', unsafe_allow_html=True)
    
    # Filter items matching language, sort by recommendation rank
    lang_filtered = [x for x in recs if x[0]["language"] == target_lang][:4]
    
    cols3 = st.columns(4)
    for idx, (item, score) in enumerate(lang_filtered):
        card_html = f"""
        <div class="homepage-card">
            <div class="card-banner">
                <span class="card-tag-badge">{item['type']}</span>
                <div class="card-banner-title">{item['title']}</div>
            </div>
            <div style="padding: 1rem; display: flex; flex-direction: column; justify-content: space-between; flex-grow: 1;">
                <div style="font-size: 0.8rem; color:#e50914; font-weight:700;">{item['listed_in']}</div>
                <div class="card-meta-line">
                    <span style="color:#46D369; font-weight:700;">{(score*100):.0f}% Match</span>
                    <span>{item['release_year']}</span>
                </div>
            </div>
        </div>
        """
        cols3[idx].markdown(card_html, unsafe_allow_html=True)

    # ----------------------------------------------------
    # Row 4: "Explore [Selected Genre]" (Genre-focused row)
    # ----------------------------------------------------
    target_genre = list(st.session_state.selected_genres)[0]
    st.markdown(f'<div class="row-title">Explore {target_genre}</div>', unsafe_allow_html=True)
    
    # Filter items containing genre, sort by recommendation rank
    genre_filtered = [x for x in recs if target_genre.lower() in x[0]["listed_in"].lower()][:4]
    
    cols4 = st.columns(4)
    for idx, (item, score) in enumerate(genre_filtered):
        card_html = f"""
        <div class="homepage-card">
            <div class="card-banner">
                <span class="card-tag-badge">{item['type']}</span>
                <div class="card-banner-title">{item['title']}</div>
            </div>
            <div style="padding: 1rem; display: flex; flex-direction: column; justify-content: space-between; flex-grow: 1;">
                <div style="font-size: 0.8rem; color:#e50914; font-weight:700;">{item['listed_in']}</div>
                <div class="card-meta-line">
                    <span style="color:#46D369; font-weight:700;">{(score*100):.0f}% Match</span>
                    <span>{item['language']}</span>
                </div>
            </div>
        </div>
        """
        cols4[idx].markdown(card_html, unsafe_allow_html=True)

# ----------------------------------------------------
# 6. EVALUATOR DIAGNOSTICS & ONBOARDING DEBUG VECTOR
# ----------------------------------------------------
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("🛠️ Onboarding Debug Vector Console", expanded=False):
    st.markdown("#### Preference Vectors & State Payload")
    
    # Diagnostic dictionary variables
    diag_payload = {
        "User Selection Vector": {
            "Languages": list(st.session_state.selected_languages),
            "Genres": list(st.session_state.selected_genres),
            "Seed Movies": list(st.session_state.selected_movies)
        },
        "Pipeline State": {
            "completed_onboarding": st.session_state.completed_onboarding,
            "TF-IDF Matrix dimensions": engine.tfidf_matrix.shape,
            "Vocabulary Length": len(engine.vectorizer.get_feature_names_out()),
            "Sparsity Percent": f"{(1.0 - (engine.tfidf_matrix.nnz / (engine.tfidf_matrix.shape[0] * engine.tfidf_matrix.shape[1]))) * 100:.2f}%"
        }
    }
    
    # Calculate step timers and run metrics assertions
    if st.session_state.completed_onboarding:
        # Dynamic calculations score preview
        diag_payload["Recommendation Latency (Stage 3)"] = f"{engine.latency_ms:.2f} ms"
        diag_payload["Top 5 Calculated Matching Scores"] = [
            {"title": title_tuple[0]["title"], "score": round(title_tuple[1], 4)}
            for title_tuple in recs[:5]
        ]
        
        # Verify assertions logs
        assertions = {
            "DF Catalog Integrity (Rows == 20)": len(df_catalog) == 20,
            "Language Selections Valid": len(st.session_state.selected_languages) > 0,
            "Genre Preference Count >= 3": len(st.session_state.selected_genres) >= 3,
            "Seed Movie Selections == 3": len(st.session_state.selected_movies) == 3,
            "Cosine Scores Range [0,1]": all(0.0 <= x[1] <= 1.0 for x in recs)
        }
        diag_payload["Runtime Assertions Check Log"] = assertions
        
    st.json(diag_payload)
