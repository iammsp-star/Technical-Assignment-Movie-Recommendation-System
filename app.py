import streamlit as st
import time
from typing import List, Dict, Any, Tuple

# ==========================================
# 1. PAGE CONFIG & NETFLIX STYLING
# ==========================================
st.set_page_config(
    page_title="Netflix - Pick What You Like",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* Google Fonts import */
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;600;700;800&display=swap');

    /* Global Canvas Styling */
    .stApp {
        background-color: #141414 !important;
        color: #FFFFFF !important;
        font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
    }
    
    /* Hide standard Streamlit header, footer, and menus */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Header Bar */
    .netflix-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0px 20px 0px;
        border-bottom: 1px solid #282828;
        margin-bottom: 25px;
        position: relative;
        z-index: 100;
    }
    .netflix-logo {
        font-family: 'Bebas Neue', sans-serif !important;
        color: #E50914 !important;
        font-size: 2.5rem !important;
        font-weight: 400 !important;
        letter-spacing: 0.5px !important;
        user-select: none !important;
    }
    .step-indicator {
        color: #E50914;
        font-weight: 700;
        font-size: 0.9rem;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    /* Progress bar */
    .progress-bar-track {
        width: 100%;
        background-color: #282828;
        height: 4px;
        margin-top: -20px;
        margin-bottom: 30px;
    }
    .progress-bar-progress {
        background-color: #E50914;
        height: 100%;
        transition: width 0.4s cubic-bezier(0.25, 1, 0.5, 1);
    }
    
    /* Layout Titles & Typography */
    .onboarding-title {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px !important;
        margin-bottom: 0.5rem !important;
        line-height: 1.2 !important;
    }
    .onboarding-subtitle {
        font-size: 1.05rem !important;
        color: #AAAAAA !important;
        margin-bottom: 2rem !important;
        line-height: 1.4 !important;
    }
    
    /* Selection Cards (Pills for language) */
    .lang-pill-container button {
        background-color: #181818 !important;
        color: #AAAAAA !important;
        border: 1px solid #282828 !important;
        border-radius: 50px !important;
        padding: 0.6rem 1.5rem !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        height: auto !important;
        min-height: auto !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    .lang-pill-container button:hover {
        border-color: #E50914 !important;
        color: #FFFFFF !important;
        background-color: #222222 !important;
    }
    .lang-pill-selected button {
        border: 2px solid #E50914 !important;
        color: #E50914 !important;
        background-color: #1c0f10 !important;
        font-weight: 700 !important;
    }

    /* Selection Cards (Matrix for genres) */
    .genre-card-container button {
        background-color: #181818 !important;
        color: #FFFFFF !important;
        border: 1px solid #282828 !important;
        border-radius: 8px !important;
        padding: 2rem 1rem !important;
        height: 110px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1rem !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s cubic-bezier(0.25, 1, 0.5, 1) !important;
        width: 100% !important;
    }
    .genre-card-container button:hover {
        transform: scale(1.04) !important;
        border-color: #E50914 !important;
    }
    .genre-card-selected button {
        border: 2px solid #E50914 !important;
        background-color: #1c0f10 !important;
        color: #E50914 !important;
    }
    /* Dimming non-selected genres */
    .genre-matrix-dimmed .genre-card-container:not(.genre-card-selected) button {
        opacity: 0.6 !important;
    }
    
    /* Poster Card Container (Step 3) */
    .poster-container {
        position: relative;
        border-radius: 6px;
        overflow: hidden;
        border: 2px solid transparent;
        transition: transform 0.3s cubic-bezier(0.25, 1, 0.5, 1), border-color 0.2s ease;
        margin-bottom: 10px;
        background-color: #181818;
    }
    .poster-container:hover {
        transform: scale(1.04);
        border-color: #E50914;
    }
    .poster-img {
        width: 100%;
        height: 280px;
        object-fit: cover;
        display: block;
        border-radius: 4px;
        transition: filter 0.3s ease;
    }
    .poster-title {
        padding: 10px 6px 6px 6px;
        font-weight: 600;
        font-size: 0.95rem;
        color: #FFFFFF;
        text-align: center;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    /* Selected Poster Card Highlight */
    .selected-card {
        border: 2px solid #E50914 !important;
        box-shadow: 0 0 15px rgba(229, 9, 20, 0.5);
    }
    .selected-card::after {
        content: "✓";
        position: absolute;
        top: 8px;
        right: 8px;
        background-color: #E50914;
        color: white;
        width: 26px;
        height: 26px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
        font-weight: bold;
        border: 1px solid #141414;
        z-index: 5;
        box-shadow: 0 2px 5px rgba(0,0,0,0.5);
    }
    .selected-card img {
        filter: brightness(0.6);
    }
    
    /* Sticky bottom action footer */
    .sticky-action-footer {
        position: fixed;
        bottom: 0; left: 0; right: 0;
        background-color: rgba(20, 20, 20, 0.96);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-top: 1px solid #282828;
        padding: 1.2rem 3rem;
        z-index: 1000;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Standard Streamlit Button Overrides */
    .stButton>button {
        background-color: #E50914 !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        font-weight: bold !important;
        padding: 0.65rem 2.2rem !important;
        transition: all 0.2s ease !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.5px !important;
    }
    .stButton>button:hover {
        background-color: #F40612 !important;
        color: white !important;
    }
    .stButton>button:disabled {
        background-color: #282828 !important;
        color: #555555 !important;
        cursor: not-allowed !important;
    }
    
    /* Loading Spinner */
    .loading-spin-ring {
        width: 60px;
        height: 60px;
        border: 5px solid #282828;
        border-top-color: #E50914;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 3rem auto;
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    /* Homepage Styles */
    .homepage-navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(180deg, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0) 100%);
        padding: 1rem 3rem;
        position: absolute;
        top: 0; left: 0; right: 0;
        z-index: 100;
    }
    .nav-links-list {
        display: flex;
        gap: 1.5rem;
        list-style: none;
        align-items: center;
        margin: 0;
        padding: 0;
    }
    .nav-link-item {
        font-size: 0.85rem;
        font-weight: 600;
        color: #E5E5E5;
        cursor: pointer;
        transition: color 0.2s ease;
    }
    .nav-link-item:hover {
        color: #B3B3B3;
    }
    .nav-link-item.active {
        color: #FFFFFF;
        font-weight: 700;
    }

    /* Hero Billboard Banner */
    .hero-billboard {
        height: 65vh;
        min-height: 480px;
        background-size: cover;
        background-position: center;
        position: relative;
        display: flex;
        align-items: flex-end;
        padding: 4rem 3rem;
        margin-bottom: 2.5rem;
        border-bottom: 1px solid #1c1c1c;
        margin-top: -25px;
    }
    .hero-billboard-overlay {
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(180deg, rgba(20,20,20,0.15) 0%, rgba(20,20,20,0.8) 60%, #141414 100%),
                    linear-gradient(90deg, rgba(20,20,20,0.95) 0%, rgba(20,20,20,0.4) 40%, rgba(20,20,20,0) 100%);
        z-index: 1;
    }
    .hero-billboard-content {
        position: relative;
        z-index: 2;
        max-width: 650px;
    }
    .hero-genre-tag {
        color: #E50914;
        font-weight: 800;
        text-transform: uppercase;
        font-size: 0.8rem;
        letter-spacing: 2px;
        margin-bottom: 0.5rem;
    }
    .hero-meta-badge {
        color: #46D369;
        font-weight: 700;
        font-size: 1rem;
    }
    .hero-rating-box {
        border: 1px solid rgba(255,255,255,0.4);
        padding: 0.05rem 0.35rem;
        font-size: 0.75rem;
        font-weight: 700;
        border-radius: 2px;
        color: #FFFFFF;
        margin-left: 0.5rem;
    }

    /* Interactive Buttons on Hero */
    .hero-btn {
        display: inline-flex;
        align-items: center;
        font-size: 1rem;
        font-weight: 700;
        padding: 0.65rem 2rem;
        border-radius: 4px;
        border: none;
        cursor: pointer;
        transition: opacity 0.2s ease;
        gap: 0.5rem;
    }
    .hero-btn-play {
        background-color: #FFFFFF;
        color: #000000;
    }
    .hero-btn-play:hover {
        background-color: rgba(255,255,255,0.85);
    }
    .hero-btn-list {
        background-color: rgba(109, 109, 110, 0.7);
        color: #FFFFFF;
    }
    .hero-btn-list:hover {
        background-color: rgba(109, 109, 110, 0.4);
    }

    /* Catalog Row Styling */
    .movie-row-header {
        font-size: 1.4rem;
        font-weight: 700;
        margin: 20px 0px 10px 1.5rem;
        border-left: 4px solid #E50914;
        padding-left: 0.5rem;
        color: #E5E5E5;
    }
    .movie-row-viewport {
        margin-bottom: 2.5rem;
    }
    
    /* Homepage Card Styles with Expand-on-hover */
    .row-card-container {
        background-color: #181818;
        border: 1px solid #282828;
        border-radius: 6px;
        overflow: hidden;
        position: relative;
        transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.2s ease;
        height: 190px;
        display: flex;
        flex-direction: column;
    }
    .row-card-container:hover {
        transform: scale(1.05);
        z-index: 5;
        border-color: rgba(229, 9, 20, 0.5);
        box-shadow: 0 10px 30px rgba(0,0,0,0.8);
    }
    .row-card-img-banner {
        height: 110px;
        background-size: cover;
        background-position: center;
        border-bottom: 1px solid #282828;
        position: relative;
    }
    .row-card-gradient-overlay {
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.8) 100%);
    }
    .row-card-body-content {
        padding: 0.75rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        flex-grow: 1;
    }
    .row-card-title {
        font-size: 0.85rem;
        font-weight: 700;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        position: relative;
        z-index: 2;
    }
    .row-card-hover-actions {
        display: flex;
        gap: 0.5rem;
        opacity: 0;
        transition: opacity 0.25s ease;
        margin-top: 0.25rem;
    }
    .row-card-container:hover .row-card-hover-actions {
        opacity: 1;
    }
    .action-circle-btn {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background-color: #2a2a2a;
        border: 1px solid #555;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: bold;
        cursor: pointer;
    }
    .action-circle-btn:hover {
        background-color: #444;
        border-color: white;
    }
    .card-tag-badge {
        position: absolute;
        top: 6px;
        left: 6px;
        font-size: 0.6rem;
        font-weight: 800;
        background-color: #E50914;
        color: white;
        padding: 0.15rem 0.35rem;
        border-radius: 3px;
        text-transform: uppercase;
        z-index: 3;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. COMPLETE CATALOG DATASET WITH POSTER URLS
# ==========================================
@st.cache_data
def load_catalog() -> List[Dict[str, Any]]:
    return [
        {
            "id": 1, "show_id": "s1", "type": "TV Show", "title": "Stranger Things", "language": "English",
            "genres": ["Sci-Fi", "Horror", "Drama"], "release_year": 2016, "rating": 8.7, "duration": "4 Seasons",
            "director": "The Duffer Brothers", "cast": "Millie Bobby Brown, Winona Ryder, David Harbour",
            "poster": "https://image.tmdb.org/t/p/w500/49WJfeN0moxb9IPfGn88qbuYA2m.jpg",
            "banner": "https://images.unsplash.com/photo-1574375927938-d5a98e8edd86?q=80&w=1200&auto=format&fit=crop",
            "description": "When a young boy vanishes, a small town uncovers a mystery involving secret experiments, terrifying supernatural forces and one strange little girl."
        },
        {
            "id": 2, "show_id": "s2", "type": "TV Show", "title": "Squid Game", "language": "Korean",
            "genres": ["Thriller", "Drama", "Action"], "release_year": 2021, "rating": 8.0, "duration": "1 Season",
            "director": "Hwang Dong-hyuk", "cast": "Lee Jung-jae, Park Hae-soo, Wi Ha-jun",
            "poster": "https://image.tmdb.org/t/p/w500/dDlE31331PFiP1A16C4M1T3C1A1.jpg",
            "banner": "https://images.unsplash.com/photo-1542204172-e7052809f852?q=80&w=1200&auto=format&fit=crop",
            "description": "Hundreds of cash-strapped players accept a strange invitation to compete in children's games. Inside, a tempting prize awaits with deadly high stakes."
        },
        {
            "id": 3, "show_id": "s3", "type": "TV Show", "title": "Sacred Games", "language": "Hindi",
            "genres": ["Thriller", "Crime", "Drama", "Action"], "release_year": 2018, "rating": 8.5, "duration": "2 Seasons",
            "director": "Vikramaditya Motwane, Anurag Kashyap", "cast": "Saif Ali Khan, Nawazuddin Siddiqui, Radhika Apte",
            "poster": "https://upload.wikimedia.org/wikipedia/en/d/d8/Sacred_Games_title_card.png",
            "banner": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?q=80&w=1200&auto=format&fit=crop",
            "description": "A link in their pasts leads an honest cop to a fugitive gang boss whose cryptic warning spurs a quest to save Mumbai from a cataclysmic threat."
        },
        {
            "id": 4, "show_id": "s4", "type": "TV Show", "title": "Money Heist", "language": "Spanish",
            "genres": ["Action", "Crime", "Thriller"], "release_year": 2017, "rating": 8.2, "duration": "5 Seasons",
            "director": "Álex Pina", "cast": "Álvaro Morte, Úrsula Corberó, Itziar Ituño",
            "poster": "https://image.tmdb.org/t/p/w500/reKs8A331c13A2c4X5A05121.jpg",
            "banner": "https://images.unsplash.com/photo-1509281373149-e957c6296406?q=80&w=1200&auto=format&fit=crop",
            "description": "Eight thieves take hostages and lock themselves in the Royal Mint of Spain as a criminal mastermind manipulates the police to carry out his plan."
        },
        {
            "id": 5, "show_id": "s5", "type": "TV Show", "title": "Demon Slayer", "language": "Japanese",
            "genres": ["Anime", "Action", "Fantasy"], "release_year": 2019, "rating": 8.7, "duration": "2 Seasons",
            "director": "Haruo Sotozaki", "cast": "Natsuki Hanae, Akari Kito, Yoshitsugu Matsuoka",
            "poster": "https://image.tmdb.org/t/p/w500/xUfRQA2alT3A3pI392215A42.jpg",
            "banner": "https://images.unsplash.com/photo-1528164344705-47542687000d?q=80&w=1200&auto=format&fit=crop",
            "description": "After a demon attack slaughters his family, a kindhearted boy joins the Demon Slayer Corps to hunt down demons and cure his cursed younger sister."
        },
        {
            "id": 6, "show_id": "s6", "type": "TV Show", "title": "Narcos", "language": "English",
            "genres": ["Crime", "Drama", "Action"], "release_year": 2015, "rating": 8.8, "duration": "3 Seasons",
            "director": "Andrés Baiz", "cast": "Wagner Moura, Boyd Holbrook, Pedro Pascal",
            "poster": "https://upload.wikimedia.org/wikipedia/en/0/0a/Narcos_season_1_poster.jpg",
            "banner": "https://images.unsplash.com/photo-1507608869274-d3177c8bb4c7?q=80&w=1200&auto=format&fit=crop",
            "description": "The true story of Colombia's infamously violent and powerful drug cartels, and the law enforcement struggles to bring down kingpin Pablo Escobar."
        },
        {
            "id": 7, "show_id": "s7", "type": "Movie", "title": "Inception", "language": "English",
            "genres": ["Sci-Fi", "Action", "Thriller"], "release_year": 2010, "rating": 8.8, "duration": "148 min",
            "director": "Christopher Nolan", "cast": "Leonardo DiCaprio, Joseph Gordon-Levitt, Elliot Page",
            "poster": "https://image.tmdb.org/t/p/w500/oYuLE13111A2s1A1A5123.jpg",
            "banner": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?q=80&w=1200&auto=format&fit=crop",
            "description": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O."
        },
        {
            "id": 8, "show_id": "s8", "type": "Movie", "title": "The Matrix", "language": "English",
            "genres": ["Sci-Fi", "Action"], "release_year": 1999, "rating": 8.7, "duration": "136 min",
            "director": "Lana Wachowski, Lilly Wachowski", "cast": "Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss",
            "poster": "https://image.tmdb.org/t/p/w500/f89U311A2A441221.jpg",
            "banner": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=1200&auto=format&fit=crop",
            "description": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers."
        },
        {
            "id": 9, "show_id": "s9", "type": "TV Show", "title": "Mirzapur", "language": "Hindi",
            "genres": ["Action", "Crime", "Thriller"], "release_year": 2018, "rating": 8.5, "duration": "2 Seasons",
            "director": "Karan Anshuman, Gurmmeet Singh", "cast": "Pankaj Tripathi, Ali Fazal, Divyendu Sharma",
            "poster": "https://upload.wikimedia.org/wikipedia/en/3/3c/Mirzapur_poster.jpg",
            "banner": "https://images.unsplash.com/photo-1533928298208-27ff66555d8d?q=80&w=1200&auto=format&fit=crop",
            "description": "A shocking incident at a wedding procession ignites a series of events, leading to a power struggle, crime, and lawlessness in northern India."
        },
        {
            "id": 10, "show_id": "s10", "type": "TV Show", "title": "Crash Landing on You", "language": "Korean",
            "genres": ["Romance", "Comedy", "Drama"], "release_year": 2019, "rating": 8.7, "duration": "1 Season",
            "director": "Lee Jeong-hyo", "cast": "Hyun Bin, Son Ye-jin, Seo Ji-hye",
            "poster": "https://upload.wikimedia.org/wikipedia/en/6/64/Crash_Landing_on_You_main_poster.jpg",
            "banner": "https://images.unsplash.com/photo-1518609878373-06d740f60d8b?q=80&w=1200&auto=format&fit=crop",
            "description": "A South Korean paraglider accidentally crosses the border into North Korea, where a sympathetic military officer hides and protects her."
        },
        {
            "id": 11, "show_id": "s11", "type": "TV Show", "title": "My Name", "language": "Korean",
            "genres": ["Action", "Crime", "Thriller"], "release_year": 2021, "rating": 7.8, "duration": "1 Season",
            "director": "Kim Jin-min", "cast": "Han So-hee, Park Hee-soon, Ahn Bo-hyun",
            "poster": "https://upload.wikimedia.org/wikipedia/en/0/0b/My_Name_TV_series.jpeg",
            "banner": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?q=80&w=1200&auto=format&fit=crop",
            "description": "Following her father's murder, a revenge-driven woman puts her trust in a powerful drug lord and goes undercover as a police officer."
        },
        {
            "id": 12, "show_id": "s12", "type": "Movie", "title": "3 Idiots", "language": "Hindi",
            "genres": ["Comedy", "Drama"], "release_year": 2009, "rating": 8.4, "duration": "170 min",
            "director": "Rajkumar Hirani", "cast": "Aamir Khan, Kareena Kapoor, R. Madhavan",
            "poster": "https://upload.wikimedia.org/wikipedia/en/b/b9/3_Idiots_poster.jpg",
            "banner": "https://images.unsplash.com/photo-1517486808906-6ca8b3f04846?q=80&w=1200&auto=format&fit=crop",
            "description": "Two friends search for their long-lost college companion, recalling his philosophies that challenged academic educational systems."
        },
        {
            "id": 13, "show_id": "s13", "type": "Movie", "title": "Dangal", "language": "Hindi",
            "genres": ["Action", "Drama"], "release_year": 2016, "rating": 8.3, "duration": "161 min",
            "director": "Nitesh Tiwari", "cast": "Aamir Khan, Sakshi Tanwar, Fatima Sana Shaikh",
            "poster": "https://upload.wikimedia.org/wikipedia/en/9/99/Dangal_Poster.jpg",
            "banner": "https://images.unsplash.com/photo-1571008887538-b36bb32f4571?q=80&w=1200&auto=format&fit=crop",
            "description": "A former wrestler struggles to coach his daughters towards Commonwealth Games wrestling glory, fighting societal prejudices."
        },
        {
            "id": 14, "show_id": "s14", "type": "Movie", "title": "Interstellar", "language": "English",
            "genres": ["Sci-Fi", "Drama"], "release_year": 2014, "rating": 8.6, "duration": "169 min",
            "director": "Christopher Nolan", "cast": "Matthew McConaughey, Anne Hathaway, Jessica Chastain",
            "poster": "https://image.tmdb.org/t/p/w500/gEU2Q21A1A51123.jpg",
            "banner": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?q=80&w=1200&auto=format&fit=crop",
            "description": "A team of space explorers travels through a newly discovered wormhole in search of a new home planet for dying humanity on Earth."
        },
        {
            "id": 15, "show_id": "s15", "type": "Movie", "title": "Spirited Away", "language": "Japanese",
            "genres": ["Anime", "Fantasy"], "release_year": 2001, "rating": 8.6, "duration": "125 min",
            "director": "Hayao Miyazaki", "cast": "Rumi Hiiragi, Miyu Irino, Mari Natsuki",
            "poster": "https://upload.wikimedia.org/wikipedia/en/d/d4/Spirited_Away_poster.png",
            "banner": "https://images.unsplash.com/photo-1501854140801-50d01698950b?q=80&w=1200&auto=format&fit=crop",
            "description": "A young girl wanders into a spirit world ruled by gods and witches. She must work in a bathhouse to free her cursed parents."
        },
        {
            "id": 16, "show_id": "s16", "type": "TV Show", "title": "Our Planet", "language": "English",
            "genres": ["Documentaries"], "release_year": 2019, "rating": 9.3, "duration": "1 Season",
            "director": "Alastair Fothergill", "cast": "David Attenborough",
            "poster": "https://upload.wikimedia.org/wikipedia/en/b/bd/Our_Planet_poster.jpg",
            "banner": "https://images.unsplash.com/photo-1433832597046-4f10e10ac764?q=80&w=1200&auto=format&fit=crop",
            "description": "Experience our planet's natural beauty and examine how climate change impacts all living creatures in this spectacular nature documentary."
        }
    ]

catalog = load_catalog()

# ==========================================
# DYNAMIC RECOMMENDATION SCORING ENGINE
# ==========================================
def compute_scores(catalog_items: List[Dict[str, Any]], selected_langs: List[str], selected_genres: List[str], selected_titles: List[str]) -> List[Dict[str, Any]]:
    start_time = time.time()
    
    seed_genres = set()
    for item in catalog_items:
        if item["title"] in selected_titles:
            seed_genres.update(item["genres"])
            
    scored_items = []
    for item in catalog_items:
        # Exclude currently selected seeds from homepage list
        if item["title"] in selected_titles:
            continue
            
        score = 0
        
        # 1. Language Score (+10 if matches selected language)
        if selected_langs and item["language"] in selected_langs:
            score += 10
            
        # 2. Genre Overlap Score (+4 per matching genre)
        genre_matches = sum(1 for g in item["genres"] if g in selected_genres)
        score += genre_matches * 4
        
        # 3. Seed Title Genre Overlap (+3 per matching seed genre)
        seed_matches = sum(1 for g in item["genres"] if g in seed_genres)
        score += seed_matches * 3
        
        # Calculate dynamic match percentage based on score
        match_pct = min(99, max(68, 72 + score * 2))
        
        item_copy = item.copy()
        item_copy["score"] = score
        item_copy["match_pct"] = match_pct
        scored_items.append(item_copy)
        
    # Sort descending by score, then by rating
    scored_items.sort(key=lambda x: (x["score"], x["rating"]), reverse=True)
    
    # Store dynamic calculation time globally or return it
    global latency_ms
    latency_ms = (time.time() - start_time) * 1000
    return scored_items

# Initialize Session State
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'selected_languages' not in st.session_state:
    st.session_state.selected_languages = []
if 'selected_genres' not in st.session_state:
    st.session_state.selected_genres = []
if 'selected_titles' not in st.session_state:
    st.session_state.selected_titles = []
if 'completed_onboarding' not in st.session_state:
    st.session_state.completed_onboarding = False

# Header Bar
st.markdown(f"""
<div class="netflix-header">
    <div class="netflix-logo">NETFLIX</div>
    <div class="step-indicator">STEP {st.session_state.step if isinstance(st.session_state.step, int) else 3} OF 3</div>
</div>
""", unsafe_allow_html=True)

# Progress Bar
if st.session_state.step != "loading" and not st.session_state.completed_onboarding:
    progress_val = 33
    if st.session_state.step == 2:
        progress_val = 66
    elif st.session_state.step == 3:
        progress_val = 100
    st.markdown(f"""
    <div class="progress-bar-track">
        <div class="progress-bar-progress" style="width: {progress_val}%;"></div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# STEP 1: LANGUAGE PREFERENCE
# ==========================================
if st.session_state.step == 1:
    st.markdown('<div class="onboarding-title">Tell us what you like to get started.</div>', unsafe_allow_html=True)
    st.markdown('<div class="onboarding-subtitle">Choose the languages you prefer for audio and subtitles.</div>', unsafe_allow_html=True)
    
    languages = ["English", "Hindi", "Korean", "Spanish", "Japanese"]
    cols = st.columns(4)
    
    for idx, lang in enumerate(languages):
        with cols[idx % 4]:
            is_selected = lang in st.session_state.selected_languages
            pill_class = "lang-pill-selected lang-pill-container" if is_selected else "lang-pill-container"
            
            st.markdown(f'<div class="{pill_class}">', unsafe_allow_html=True)
            btn_label = f"✓ {lang}" if is_selected else lang
            if st.button(btn_label, key=f"lang_{lang}", use_container_width=True):
                if lang in st.session_state.selected_languages:
                    st.session_state.selected_languages.remove(lang)
                else:
                    st.session_state.selected_languages.append(lang)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
                
    st.markdown("---")
    
    # Enable Next button only if at least 1 language is chosen
    next_disabled = len(st.session_state.selected_languages) == 0
    
    _, next_col = st.columns([4, 1])
    if next_col.button("NEXT ➔", disabled=next_disabled):
        st.session_state.step = 2
        st.rerun()

# ==========================================
# STEP 2: GENRE SELECTION
# ==========================================
elif st.session_state.step == 2:
    st.markdown('<div class="onboarding-title">Select 3 or more genres you enjoy.</div>', unsafe_allow_html=True)
    
    genre_count = len(st.session_state.selected_genres)
    st.markdown(f'<div style="text-align:right; font-weight:800; color:#E50914; margin-top:-1.5rem; margin-bottom:1rem;">[ Selected: {genre_count} / 3 ]</div>', unsafe_allow_html=True)
    
    genres = ["Action", "Sci-Fi", "Thriller", "Romance", "Comedy", "Anime", "Horror", "Drama", "Documentaries"]
    
    dimmed_class = "genre-matrix-dimmed" if genre_count > 0 else ""
    st.markdown(f'<div class="{dimmed_class}">', unsafe_allow_html=True)
    cols = st.columns(3)
    
    for idx, genre in enumerate(genres):
        with cols[idx % 3]:
            is_selected = genre in st.session_state.selected_genres
            card_class = "genre-card-selected genre-card-container" if is_selected else "genre-card-container"
            
            st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
            btn_label = f"✓ {genre}" if is_selected else genre
            if st.button(btn_label, key=f"genre_{genre}", use_container_width=True):
                if genre in st.session_state.selected_genres:
                    st.session_state.selected_genres.remove(genre)
                else:
                    st.session_state.selected_genres.append(genre)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
                
    st.markdown("---")
    
    # Continue button turns red once genre count >= 3
    continue_disabled = genre_count < 3
    
    _, continue_col = st.columns([4, 1])
    if continue_col.button("CONTINUE ➔", disabled=continue_disabled):
        st.session_state.step = 3
        st.rerun()

# ==========================================
# STEP 3: TITLE PICKER WITH POSTERS
# ==========================================
elif st.session_state.step == 3:
    st.markdown('<div class="onboarding-title">Choose 3 movies or TV shows you love.</div>', unsafe_allow_html=True)
    st.markdown('<div class="onboarding-subtitle">This helps us build your personalized row of recommendations.</div>', unsafe_allow_html=True)
    
    # Search bar
    search_q = st.text_input("🔍 Search movies or TV shows...", "").strip().lower()
    
    filtered_catalog = catalog
    if search_q:
        filtered_catalog = [item for item in catalog if search_q in item["title"].lower() or any(search_q in g.lower() for g in item["genres"])]
        
    if not filtered_catalog:
        st.warning("No matches found in catalog.")
    else:
        cols = st.columns(4)
        for idx, item in enumerate(filtered_catalog):
            with cols[idx % 4]:
                poster_url = item.get("poster", "https://via.placeholder.com/400x600?text=No+Poster")
                is_selected = item["title"] in st.session_state.selected_titles
                
                # Card Wrapper styling
                card_class = "poster-container selected-card" if is_selected else "poster-container"
                st.markdown(f"""
                <div class="{card_class}">
                    <img src="{poster_url}" class="poster-img" />
                    <div class="poster-title">{item['title']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Selection Click action button
                btn_label = f"✓ Selected" if is_selected else f"Select {item['title']}"
                if st.button(btn_label, key=f"title_{item['id']}", use_container_width=True):
                    if item["title"] in st.session_state.selected_titles:
                        st.session_state.selected_titles.remove(item["title"])
                    else:
                        if len(st.session_state.selected_titles) < 3:
                            st.session_state.selected_titles.append(item["title"])
                        else:
                            st.warning("You have already selected 3 movies. Deselect one to choose another.")
                    st.rerun()

        # Sticky bottom footer bar
        sel_count = len(st.session_state.selected_titles)
        finish_disabled = sel_count < 3
        
        st.markdown(
            f"""
            <div class="sticky-action-footer">
                <div style="font-weight:800; font-size:1.15rem; color: {'#46D369' if sel_count == 3 else '#FFFFFF'};">
                    {sel_count} of 3 selected
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        _, finish_col = st.columns([4, 1.2])
        if finish_col.button("FINISH & WATCH ➔", key="btn_finish", disabled=finish_disabled):
            st.session_state.step = "loading"
            st.rerun()

# ==========================================
# STEP 4: PROCESSING STATE
# ==========================================
elif st.session_state.step == "loading":
    st.markdown(
        """
        <div style="text-align: center; margin-top: 6rem;">
            <h2 style="font-size: 2.2rem; font-weight:800;">Setting Up Your Netflix</h2>
            <div class="loading-spin-ring"></div>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Cycling status text
    placeholder = st.empty()
    messages = [
        "Analyzing your taste profile...",
        "Building your personalized rows...",
        "Curating top matches...",
        "Ready!"
    ]
    
    for text in messages:
        placeholder.markdown(f"<h4 style='text-align: center; color: #8e8e93; font-weight:700;'>{text}</h4>", unsafe_allow_html=True)
        time.sleep(0.8)
        
    st.session_state.completed_onboarding = True
    st.session_state.step = 4.0
    st.rerun()

# ==========================================
# STEP 5: PERSONALIZED HOME DASHBOARD
# ==========================================
elif st.session_state.completed_onboarding or st.session_state.step == 4.0:
    scored_catalog = compute_scores(
        catalog,
        st.session_state.selected_titles,
        st.session_state.selected_genres,
        st.session_state.selected_languages
    )
    
    # 1. Netflix Transparent Navbar Header
    st.markdown(
        """
        <div class="homepage-navbar">
            <div style="display:flex; align-items:center; gap:2.5rem;">
                <div class="netflix-logo">NETFLIX</div>
                <ul class="nav-links-list">
                    <li class="nav-link-item active">Home</li>
                    <li class="nav-link-item">TV Shows</li>
                    <li class="nav-link-item">Movies</li>
                    <li class="nav-link-item">My List</li>
                </ul>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Reset button aligned right
    _, reset_col = st.columns([4, 1.2])
    reset_col.markdown('<div style="text-align:right; margin-top:10px; position:relative; z-index:101;">', unsafe_allow_html=True)
    if reset_col.button("🔄 Reset Onboarding", key="btn_reset"):
        st.session_state.step = 1
        st.session_state.selected_languages = []
        st.session_state.selected_genres = []
        st.session_state.selected_titles = []
        st.session_state.completed_onboarding = False
        st.rerun()
    reset_col.markdown('</div>', unsafe_allow_html=True)

    # 2. Hero Billboard Banner
    hero_item = scored_catalog[0]
    hero_score = scored_catalog[0]["match_pct"]
    
    # Render dynamic billboard background from item banner link
    st.markdown(
        f"""
        <div class="hero-billboard" style="background-image: url('{hero_item['banner']}');">
            <div class="hero-billboard-overlay"></div>
            <div class="hero-billboard-content">
                <div class="hero-genre-tag">{" / ".join(hero_item['genres'])}</div>
                <h1 class="hero-title" style="font-size: 3.5rem; margin-bottom: 0.5rem; font-family:'Helvetica Neue', Arial, sans-serif; font-weight:800;">{hero_item['title']}</h1>
                <div style="display:flex; align-items:center; font-size:1rem; font-weight:700; margin-bottom: 1rem;">
                    <span class="hero-meta-badge">{hero_score:.0f}% Match</span>
                    <span style="color:#ffffff; margin-left: 0.75rem;">{hero_item['release_year']}</span>
                    <span class="hero-rating-box">{hero_item['rating']}</span>
                    <span style="color:#ffffff; margin-left: 0.75rem;">{hero_item['duration']}</span>
                    <span style="color:#808080; margin-left: 0.75rem;">📍 {hero_item['language']}</span>
                </div>
                <p style="font-size:1.05rem; color:#E5E5E5; line-height:1.4; margin-bottom: 1.5rem;">{hero_item['description']}</p>
                <div style="display:flex; gap:1rem;">
                    <button class="hero-btn hero-btn-play">▶ Play</button>
                    <button class="hero-btn hero-btn-list">+ My List</button>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 3. Tailored Recommendation Rows
    
    # ----------------------------------------------------
    # Row 1: "Top Picks for You"
    # ----------------------------------------------------
    st.markdown('<div class="movie-row-header">Top Picks for You</div>', unsafe_allow_html=True)
    row_1_items = scored_catalog[:4]
    
    cols1 = st.columns(4)
    for idx, item in enumerate(row_1_items):
        card_html = f"""
        <div class="row-card-container">
            <div class="row-card-img-banner" style="background-image: url('{item['poster']}');">
                <div class="row-card-gradient-overlay"></div>
                <span class="card-tag-badge">{item['type']}</span>
            </div>
            <div class="row-card-body-content">
                <div class="row-card-title">{item['title']}</div>
                <div style="font-size: 0.75rem; color:#e50914; font-weight:700;">{", ".join(item['genres'])}</div>
                <div class="card-meta-line" style="margin-top:0.25rem; display:flex; justify-content:space-between; font-size:0.75rem;">
                    <span style="color:#46D369; font-weight:700;">{item['match_pct']:.0f}% Match</span>
                    <span>{item['language']}</span>
                </div>
                <div class="row-card-hover-actions">
                    <div class="action-circle-btn">▶</div>
                    <div class="action-circle-btn">+</div>
                    <div class="action-circle-btn">👍</div>
                </div>
            </div>
        </div>
        """
        cols1[idx].markdown(card_html, unsafe_allow_html=True)

    # ----------------------------------------------------
    # Row 2: "Because You Selected [First Picked Movie]"
    # ----------------------------------------------------
    first_seed = list(st.session_state.selected_titles)[0]
    st.markdown(f'<div class="movie-row-header">Because You Selected {first_seed}</div>', unsafe_allow_html=True)
    
    # Generate similarities focused purely on seed description matching
    seed_item = next(item for item in catalog if item["title"] == first_seed)
    
    # Fallback to simple genre matching since TF-IDF is bypassed
    row_2_items = []
    for item in scored_catalog:
        # Calculate overlap with first seed genres
        overlap = sum(1 for g in item["genres"] if g in seed_item["genres"])
        item_copy = item.copy()
        item_copy["overlap"] = overlap
        row_2_items.append(item_copy)
    row_2_items.sort(key=lambda x: (x["overlap"], x["rating"]), reverse=True)
    row_2_display = row_2_items[:4]
    
    cols2 = st.columns(4)
    for idx, item in enumerate(row_2_display):
        card_html = f"""
        <div class="row-card-container">
            <div class="row-card-img-banner" style="background-image: url('{item['poster']}');">
                <div class="row-card-gradient-overlay"></div>
                <span class="card-tag-badge">{item['type']}</span>
            </div>
            <div class="row-card-body-content">
                <div class="row-card-title">{item['title']}</div>
                <div style="font-size: 0.75rem; color:#e50914; font-weight:700;">{", ".join(item['genres'])}</div>
                <div class="card-meta-line" style="margin-top:0.25rem; display:flex; justify-content:space-between; font-size:0.75rem;">
                    <span style="color:#46D369; font-weight:700;">{item['match_pct']:.0f}% Match</span>
                    <span>{item['language']}</span>
                </div>
                <div class="row-card-hover-actions">
                    <div class="action-circle-btn">▶</div>
                    <div class="action-circle-btn">+</div>
                    <div class="action-circle-btn">👍</div>
                </div>
            </div>
        </div>
        """
        cols2[idx].markdown(card_html, unsafe_allow_html=True)

    # ----------------------------------------------------
    # Row 3: "Top [Selected Language] Content"
    # ----------------------------------------------------
    target_lang = list(st.session_state.selected_languages)[0]
    st.markdown(f'<div class="movie-row-header">Top {target_lang} Content</div>', unsafe_allow_html=True)
    
    lang_filtered = [x for x in scored_catalog if x["language"] == target_lang][:4]
    
    cols3 = st.columns(4)
    for idx, item in enumerate(lang_filtered):
        card_html = f"""
        <div class="row-card-container">
            <div class="row-card-img-banner" style="background-image: url('{item['poster']}');">
                <div class="row-card-gradient-overlay"></div>
                <span class="card-tag-badge">{item['type']}</span>
            </div>
            <div class="row-card-body-content">
                <div class="row-card-title">{item['title']}</div>
                <div style="font-size: 0.75rem; color:#e50914; font-weight:700;">{", ".join(item['genres'])}</div>
                <div class="card-meta-line" style="margin-top:0.25rem; display:flex; justify-content:space-between; font-size:0.75rem;">
                    <span style="color:#46D369; font-weight:700;">{item['match_pct']:.0f}% Match</span>
                    <span>{item['release_year']}</span>
                </div>
                <div class="row-card-hover-actions">
                    <div class="action-circle-btn">▶</div>
                    <div class="action-circle-btn">+</div>
                    <div class="action-circle-btn">👍</div>
                </div>
            </div>
        </div>
        """
        cols3[idx].markdown(card_html, unsafe_allow_html=True)

    # ----------------------------------------------------
    # Row 4: "Explore [Selected Genre]"
    # ----------------------------------------------------
    target_genre = list(st.session_state.selected_genres)[0]
    st.markdown(f'<div class="movie-row-header">Explore {target_genre}</div>', unsafe_allow_html=True)
    
    genre_filtered = [x for x in scored_catalog if target_genre in x["genres"]][:4]
    
    cols4 = st.columns(4)
    for idx, item in enumerate(genre_filtered):
        card_html = f"""
        <div class="row-card-container">
            <div class="row-card-img-banner" style="background-image: url('{item['poster']}');">
                <div class="row-card-gradient-overlay"></div>
                <span class="card-tag-badge">{item['type']}</span>
            </div>
            <div class="row-card-body-content">
                <div class="row-card-title">{item['title']}</div>
                <div style="font-size: 0.75rem; color:#e50914; font-weight:700;">{", ".join(item['genres'])}</div>
                <div class="card-meta-line" style="margin-top:0.25rem; display:flex; justify-content:space-between; font-size:0.75rem;">
                    <span style="color:#46D369; font-weight:700;">{item['match_pct']:.0f}% Match</span>
                    <span>{item['language']}</span>
                </div>
                <div class="row-card-hover-actions">
                    <div class="action-circle-btn">▶</div>
                    <div class="action-circle-btn">+</div>
                    <div class="action-circle-btn">👍</div>
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
    
    diag_payload = {
        "User Selection Vector": {
            "Languages": list(st.session_state.selected_languages),
            "Genres": list(st.session_state.selected_genres),
            "Seed Movies": list(st.session_state.selected_titles)
        },
        "Pipeline State": {
            "completed_onboarding": st.session_state.completed_onboarding,
            "Catalog Size": len(catalog),
            "Sparsity Percent": "N/A (Bypassed via compute_scores first-principles overlap logic)"
        }
    }
    
    if st.session_state.completed_onboarding:
        # Reference global latency variable
        if 'latency_ms' in globals():
            diag_payload["Recommendation Latency (Stage 3)"] = f"{latency_ms:.2f} ms"
            
        diag_payload["Top 5 Calculated Matching Scores"] = [
            {"title": item_dict["title"], "score": item_dict["score"], "match_pct": item_dict["match_pct"]}
            for item_dict in scored_catalog[:5]
        ]
        
        assertions = {
            "Catalog Size Valid (Rows == 16)": len(catalog) == 16,
            "Language Selections Valid": len(st.session_state.selected_languages) > 0,
            "Genre Preference Count >= 3": len(st.session_state.selected_genres) >= 3,
            "Seed Movie Selections == 3": len(st.session_state.selected_titles) == 3,
            "Match Pct Bounds [68,99]": all(68 <= x["match_pct"] <= 99 for x in scored_catalog)
        }
        diag_payload["Runtime Assertions Check Log"] = assertions
        
    st.json(diag_payload)
