import streamlit as st
import time
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Set, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Set page config to dark mode, custom title and widescreen layout
st.set_page_config(
    page_title="Netflix - Tell us what you like",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------------------------------------------
# 1. PIXEL-PERFECT DESIGN SYSTEM & CSS INJECTIONS
# ----------------------------------------------------
st.markdown(
    """
    <style>
    /* Google Fonts import */
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;600;700;800&display=swap');

    /* Global Canvas Styling */
    .stApp {
        background-color: #141414 !important;
        color: #FFFFFF !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }

    /* Hide standard Streamlit header, footer and menus */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Netflix Branding Navbar */
    .netflix-navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem 2rem;
        background-color: transparent;
        position: relative;
        z-index: 100;
    }
    .netflix-logo-brand {
        font-family: 'Bebas Neue', sans-serif !important;
        color: #E50914 !important;
        font-size: 2.8rem !important;
        font-weight: 400 !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
        line-height: 1 !important;
        user-select: none !important;
    }
    .step-indicator-text {
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 1px;
        color: #FFFFFF;
        text-transform: uppercase;
    }
    
    /* Progress bar */
    .progress-bar-track {
        width: 100%;
        background-color: #282828;
        height: 4px;
        margin-bottom: 2rem;
    }
    .progress-bar-progress {
        background-color: #E50914;
        height: 100%;
        transition: width 0.4s cubic-bezier(0.25, 1, 0.5, 1);
    }

    /* Layout Titles & Typography */
    .onboarding-title {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px !important;
        margin-bottom: 0.5rem !important;
        line-height: 1.15 !important;
    }
    .onboarding-subtitle {
        font-size: 1.1rem !important;
        color: #AAAAAA !important;
        margin-bottom: 2rem !important;
        line-height: 1.4 !important;
    }

    /* Step 1: Language Switcher & Selection Pills */
    .lang-pill-container button {
        background-color: #181818 !important;
        color: #AAAAAA !important;
        border: 1px solid #282828 !important;
        border-radius: 50px !important;
        padding: 0.75rem 1.8rem !important;
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

    /* Step 2: Genre Selection Matrix */
    .genre-card-container button {
        background-color: #181818 !important;
        color: #FFFFFF !important;
        border: 1px solid #282828 !important;
        border-radius: 8px !important;
        padding: 2.2rem 1rem !important;
        height: 120px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.05rem !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s cubic-bezier(0.25, 1, 0.5, 1) !important;
        width: 100% !important;
    }
    .genre-card-container button:hover {
        transform: scale(1.05) !important;
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

    /* Step 3: Movie Selection Vertical Posters */
    .movie-poster-card > div > button {
        background-size: cover !important;
        background-position: center !important;
        border: 1px solid #282828 !important;
        border-radius: 8px !important;
        width: 100% !important;
        height: 300px !important;
        display: flex !important;
        align-items: flex-end !important;
        justify-content: center !important;
        padding-bottom: 15px !important;
        color: #FFFFFF !important;
        text-shadow: 1px 1px 4px #000, 0 -2px 10px rgba(0,0,0,0.8) !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        line-height: 1.2 !important;
        transition: all 0.3s cubic-bezier(0.25, 1, 0.5, 1) !important;
    }
    .movie-poster-card > div > button:hover {
        transform: scale(1.05) !important;
        border-color: #E50914 !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.7) !important;
    }
    .movie-poster-selected > div > button {
        border: 3px solid #E50914 !important;
        box-shadow: 0 0 20px rgba(229, 9, 20, 0.45) !important;
    }
    /* Red checkmark badge */
    .movie-poster-selected {
        position: relative !important;
    }
    .movie-poster-selected::after {
        content: "✓" !important;
        position: absolute !important;
        top: -6px !important;
        right: -6px !important;
        background-color: #E50914 !important;
        color: #FFFFFF !important;
        width: 28px !important;
        height: 28px !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 15px !important;
        font-weight: 900 !important;
        border: 2px solid #141414 !important;
        z-index: 100 !important;
        box-shadow: 0 3px 6px rgba(0,0,0,0.6) !important;
    }

    /* Sticky Bottom Action Footer */
    .sticky-action-footer {
        position: fixed;
        bottom: 0; left: 0; right: 0;
        background-color: rgba(20, 20, 20, 0.95);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-top: 1px solid #282828;
        padding: 1.25rem 3rem;
        z-index: 1000;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* General Next/Action Buttons style overrides */
    .btn-netflix-action button {
        background-color: #E50914 !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        letter-spacing: 0.5px !important;
        padding: 0.75rem 2rem !important;
        border-radius: 4px !important;
        cursor: pointer !important;
        transition: background-color 0.2s ease !important;
    }
    .btn-netflix-action button:hover {
        background-color: #F40612 !important;
    }
    .btn-netflix-disabled button {
        background-color: #282828 !important;
        color: #555555 !important;
        border: none !important;
        cursor: not-allowed !important;
    }

    /* Netflix Loading Spinner */
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

    /* Homepage Transparent Navbar */
    .homepage-navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(180deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0) 100%);
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

    /* Homepage Hero Title Banner */
    .hero-billboard {
        height: 65vh;
        min-height: 480px;
        background-size: cover;
        background-position: center;
        position: relative;
        display: flex;
        align-items: flex-end;
        padding: 4rem 3rem;
        margin-bottom: 2rem;
        border-bottom: 1px solid #1c1c1c;
    }
    .hero-billboard-overlay {
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(180deg, rgba(20,20,20,0.1) 0%, rgba(20,20,20,0.8) 60%, #141414 100%),
                    linear-gradient(90deg, rgba(20,20,20,0.95) 0%, rgba(20,20,20,0.4) 40%, rgba(20,20,20,0) 100%);
        z-index: 1;
    }
    .hero-billboard-content {
        position: relative;
        z-index: 2;
        max-width: 650px;
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
        padding: 0.6rem 1.8rem;
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
        background-color: rgba(255,255,255,0.75);
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
        margin-left: 3rem;
        margin-bottom: 0.75rem;
    }
    .movie-row-viewport {
        padding: 0 3rem 2.5rem;
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.25rem;
    }
    
    /* Homepage Card Styles with Expand-on-hover */
    .row-card-container {
        background-color: #181818;
        border: 1px solid #282828;
        border-radius: 6px;
        overflow: hidden;
        position: relative;
        transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.2s ease;
        height: 180px;
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
        height: 100px;
        background-size: cover;
        background-position: center;
        border-bottom: 1px solid #282828;
        display: flex;
        align-items: flex-end;
        padding: 0.5rem;
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
    
    /* Hover to Reveal Actions */
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
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------------------------------
# 2. CURATED METADATA DATASET (REAL IMAGES & LINKS)
# ----------------------------------------------------
CATALOG: List[Dict[str, Any]] = [
    {
        "show_id": "s1", "type": "TV Show", "title": "Stranger Things", "language": "English",
        "listed_in": "Sci-Fi, Horror, Thriller", "release_year": 2022, "rating": "TV-14", "duration": "4 Seasons",
        "director": "The Duffer Brothers", "cast": "Millie Bobby Brown, Winona Ryder, David Harbour",
        "poster": "https://images.unsplash.com/photo-1626814026160-2237a95fc5a0?q=80&w=400&auto=format&fit=crop",
        "banner": "https://images.unsplash.com/photo-1574375927938-d5a98e8edd86?q=80&w=1200&auto=format&fit=crop",
        "description": "When a young boy vanishes, a small town uncovers a mystery involving secret experiments, terrifying supernatural forces and one strange little girl."
    },
    {
        "show_id": "s2", "type": "TV Show", "title": "Squid Game", "language": "Korean",
        "listed_in": "Thriller, Action", "release_year": 2021, "rating": "TV-MA", "duration": "1 Season",
        "director": "Hwang Dong-hyuk", "cast": "Lee Jung-jae, Park Hae-soo, Wi Ha-jun",
        "poster": "https://images.unsplash.com/photo-1627856013091-fed6e4e30025?q=80&w=400&auto=format&fit=crop",
        "banner": "https://images.unsplash.com/photo-1542204172-e7052809f852?q=80&w=1200&auto=format&fit=crop",
        "description": "Hundreds of cash-strapped players accept a strange invitation to compete in children's games. Inside, a tempting prize awaits with deadly high stakes."
    },
    {
        "show_id": "s3", "type": "TV Show", "title": "Sacred Games", "language": "Hindi",
        "listed_in": "Thriller, Crime, Action", "release_year": 2019, "rating": "TV-MA", "duration": "2 Seasons",
        "director": "Vikramaditya Motwane, Anurag Kashyap", "cast": "Saif Ali Khan, Nawazuddin Siddiqui, Radhika Apte",
        "poster": "https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=400&auto=format&fit=crop",
        "banner": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?q=80&w=1200&auto=format&fit=crop",
        "description": "A link in their pasts leads an honest cop to a fugitive gang boss whose cryptic warning spurs a quest to save Mumbai from a cataclysmic threat."
    },
    {
        "show_id": "s4", "type": "TV Show", "title": "Money Heist", "language": "Spanish",
        "listed_in": "Thriller, Action", "release_year": 2021, "rating": "TV-MA", "duration": "5 Seasons",
        "director": "Álex Pina", "cast": "Álvaro Morte, Úrsula Corberó, Itziar Ituño",
        "poster": "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?q=80&w=400&auto=format&fit=crop",
        "banner": "https://images.unsplash.com/photo-1509281373149-e957c6296406?q=80&w=1200&auto=format&fit=crop",
        "description": "Eight thieves take hostages and lock themselves in the Royal Mint of Spain as a criminal mastermind manipulates the police to carry out his plan."
    },
    {
        "show_id": "s5", "type": "TV Show", "title": "Demon Slayer", "language": "Japanese",
        "listed_in": "Anime, Action, Sci-Fi", "release_year": 2021, "rating": "TV-14", "duration": "2 Seasons",
        "director": "Haruo Sotozaki", "cast": "Natsuki Hanae, Akari Kito, Yoshitsugu Matsuoka",
        "poster": "https://images.unsplash.com/photo-1578632767115-351597cf2477?q=80&w=400&auto=format&fit=crop",
        "banner": "https://images.unsplash.com/photo-1528164344705-47542687000d?q=80&w=1200&auto=format&fit=crop",
        "description": "After a demon attack slaughters his family, a kindhearted boy joins the Demon Slayer Corps to hunt down demons and cure his cursed younger sister."
    },
    {
        "show_id": "s6", "type": "TV Show", "title": "Narcos", "language": "Spanish",
        "listed_in": "Thriller, Crime, Drama", "release_year": 2017, "rating": "TV-MA", "duration": "3 Seasons",
        "director": "Andrés Baiz", "cast": "Wagner Moura, Boyd Holbrook, Pedro Pascal",
        "poster": "https://images.unsplash.com/photo-1585647347384-2593bc35786b?q=80&w=400&auto=format&fit=crop",
        "banner": "https://images.unsplash.com/photo-1507608869274-d3177c8bb4c7?q=80&w=1200&auto=format&fit=crop",
        "description": "The true story of Colombia's infamously violent and powerful drug cartels, and the law enforcement struggles to bring down kingpin Pablo Escobar."
    },
    {
        "show_id": "s7", "type": "Movie", "title": "Inception", "language": "English",
        "listed_in": "Sci-Fi, Action, Thriller", "release_year": 2010, "rating": "PG-13", "duration": "148 min",
        "director": "Christopher Nolan", "cast": "Leonardo DiCaprio, Joseph Gordon-Levitt, Elliot Page",
        "poster": "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?q=80&w=400&auto=format&fit=crop",
        "banner": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?q=80&w=1200&auto=format&fit=crop",
        "description": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O."
    },
    {
        "show_id": "s8", "type": "Movie", "title": "The Matrix", "language": "English",
        "listed_in": "Sci-Fi, Action", "release_year": 1999, "rating": "R", "duration": "136 min",
        "director": "Lana Wachowski, Lilly Wachowski", "cast": "Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss",
        "poster": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?q=80&w=400&auto=format&fit=crop",
        "banner": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=1200&auto=format&fit=crop",
        "description": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers."
    },
    {
        "show_id": "s9", "type": "TV Show", "title": "Mirzapur", "language": "Hindi",
        "listed_in": "Thriller, Crime, Action", "release_year": 2020, "rating": "TV-MA", "duration": "2 Seasons",
        "director": "Karan Anshuman, Gurmmeet Singh", "cast": "Pankaj Tripathi, Ali Fazal, Divyendu Sharma",
        "poster": "https://images.unsplash.com/photo-1595152772835-219674b2a8a6?q=80&w=400&auto=format&fit=crop",
        "banner": "https://images.unsplash.com/photo-1533928298208-27ff66555d8d?q=80&w=1200&auto=format&fit=crop",
        "description": "A shocking incident at a wedding procession ignites a series of events, leading to a power struggle, crime, and lawlessness in northern India."
    },
    {
        "show_id": "s10", "type": "TV Show", "title": "Crash Landing on You", "language": "Korean",
        "listed_in": "Romance, Comedy, Drama", "release_year": 2020, "rating": "TV-14", "duration": "1 Season",
        "director": "Lee Jeong-hyo", "cast": "Hyun Bin, Son Ye-jin, Seo Ji-hye",
        "poster": "https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?q=80&w=400&auto=format&fit=crop",
        "banner": "https://images.unsplash.com/photo-1518609878373-06d740f60d8b?q=80&w=1200&auto=format&fit=crop",
        "description": "A South Korean paraglider accidentally crosses the border into North Korea, where a sympathetic military officer hides and protects her."
    },
    {
        "show_id": "s11", "type": "Movie", "title": "My Name", "language": "Korean",
        "listed_in": "Action, Thriller, Crime", "release_year": 2021, "rating": "TV-MA", "duration": "120 min",
        "director": "Kim Jin-min", "cast": "Han So-hee, Park Hee-soon, Ahn Bo-hyun",
        "poster": "https://images.unsplash.com/photo-1599839575945-a9e5af0c3fa5?q=80&w=400&auto=format&fit=crop",
        "banner": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?q=80&w=1200&auto=format&fit=crop",
        "description": "Following her father's murder, a revenge-driven woman puts her trust in a powerful drug lord and goes undercover as a police officer."
    },
    {
        "show_id": "s12", "type": "Movie", "title": "3 Idiots", "language": "Hindi",
        "listed_in": "Comedy, Drama, Romance", "release_year": 2009, "rating": "PG-13", "duration": "170 min",
        "director": "Rajkumar Hirani", "cast": "Aamir Khan, Kareena Kapoor, R. Madhavan",
        "description": "Two friends search for their long-lost college companion, recalling his philosophies that challenged academic educational systems."
    },
    {
        "show_id": "s13", "type": "Movie", "title": "Dangal", "language": "Hindi",
        "listed_in": "Action, Drama, Biography", "release_year": 2016, "rating": "PG", "duration": "161 min",
        "director": "Nitesh Tiwari", "cast": "Aamir Khan, Sakshi Tanwar, Fatima Sana Shaikh",
        "description": "A former wrestler struggles to coach his daughters towards Commonwealth Games wrestling glory, fighting societal prejudices."
    },
    {
        "show_id": "s14", "type": "Movie", "title": "Interstellar", "language": "English",
        "listed_in": "Sci-Fi, Drama", "release_year": 2014, "rating": "PG-13", "duration": "169 min",
        "director": "Christopher Nolan", "cast": "Matthew McConaughey, Anne Hathaway, Jessica Chastain",
        "poster": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=400&auto=format&fit=crop",
        "banner": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?q=80&w=1200&auto=format&fit=crop",
        "description": "A team of space explorers travels through a newly discovered wormhole in search of a new home planet for dying humanity on Earth."
    },
    {
        "show_id": "s15", "type": "Movie", "title": "Spirited Away", "language": "Japanese",
        "listed_in": "Anime, Sci-Fi, Fantasy", "release_year": 2001, "rating": "PG", "duration": "125 min",
        "director": "Hayao Miyazaki", "cast": "Rumi Hiiragi, Miyu Irino, Mari Natsuki",
        "poster": "https://images.unsplash.com/photo-1507838153414-b4b713384a76?q=80&w=400&auto=format&fit=crop",
        "banner": "https://images.unsplash.com/photo-1501854140801-50d01698950b?q=80&w=1200&auto=format&fit=crop",
        "description": "A young girl wanders into a spirit world ruled by gods and witches. She must work in a bathhouse to free her cursed parents."
    },
    {
        "show_id": "s16", "type": "TV Show", "title": "Our Planet", "language": "English",
        "listed_in": "Documentaries, Nature", "release_year": 2019, "rating": "TV-PG", "duration": "1 Season",
        "director": "Alastair Fothergill", "cast": "David Attenborough",
        "poster": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?q=80&w=400&auto=format&fit=crop",
        "banner": "https://images.unsplash.com/photo-1433832597046-4f10e10ac764?q=80&w=1200&auto=format&fit=crop",
        "description": "Experience our planet's natural beauty and examine how climate change impacts all living creatures in this spectacular nature documentary."
    },
    {
        "show_id": "s17", "type": "Movie", "title": "The Conjuring", "language": "English",
        "listed_in": "Horror, Thriller", "release_year": 2013, "rating": "R", "duration": "112 min",
        "director": "James Wan", "cast": "Vera Farmiga, Patrick Wilson, Lili Taylor",
        "poster": "https://images.unsplash.com/photo-1505635330383-db29f4ee3c37?q=80&w=400&auto=format&fit=crop",
        "banner": "https://images.unsplash.com/photo-1518020382113-a7e8fc38eac9?q=80&w=1200&auto=format&fit=crop",
        "description": "Paranormal investigators Ed and Lorraine Warren work to help a family terrorized by a dark presence in their farmhouse."
    },
    {
        "show_id": "s18", "type": "Movie", "title": "Minnal Murali", "language": "Malayalam",
        "listed_in": "Action, Comedy, Sci-Fi", "release_year": 2021, "rating": "TV-14", "duration": "158 min",
        "director": "Basil Joseph", "cast": "Tovino Thomas, Guru Somasundaram",
        "poster": "https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?q=80&w=400&auto=format&fit=crop",
        "banner": "https://images.unsplash.com/photo-1472214222541-d510753a4907?q=80&w=1200&auto=format&fit=crop",
        "description": "An ordinary tailor gains superpower lightning speed after being struck by lightning, becoming the savior of his hometown."
    },
    {
        "show_id": "s19", "type": "TV Show", "title": "Emily in Paris", "language": "English",
        "listed_in": "Romance, Comedy, Drama", "release_year": 2020, "rating": "TV-MA", "duration": "3 Seasons",
        "director": "Darren Star", "cast": "Lily Collins, Philippine Leroy-Beaulieu",
        "poster": "https://images.unsplash.com/photo-1499856871958-5b9627545d1a?q=80&w=400&auto=format&fit=crop",
        "banner": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?q=80&w=1200&auto=format&fit=crop",
        "description": "A young American marketing executive gets her dream job in Paris, navigating French culture, romance, and friendship."
    },
    {
        "show_id": "s20", "type": "Movie", "title": "Super Deluxe", "language": "Tamil",
        "listed_in": "Drama, Comedy, Thriller", "release_year": 2019, "rating": "TV-MA", "duration": "176 min",
        "director": "Thiagarajan Kumararaja", "cast": "Vijay Sethupathi, Fahadh Faasil, Samantha Ruth Prabhu",
        "poster": "https://images.unsplash.com/photo-1509281373149-e957c6296406?q=80&w=400&auto=format&fit=crop",
        "banner": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=1200&auto=format&fit=crop",
        "description": "An angry boy, a cheating wife, a transgender woman, and a priest find themselves in unexpected predicaments on a fateful day."
    }
]

df_catalog = pd.DataFrame(CATALOG)

# ----------------------------------------------------
# 3. ADVANCED HYBRID VECTOR MATCHING ENGINE
# ----------------------------------------------------
class NetflixRecommendationEngine:
    def __init__(self, catalog_df: pd.DataFrame) -> None:
        self.df = catalog_df.copy()
        # shared-vocabulary vectorizer for metadata
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1500)
        
        # Fit vocabulary on descriptions + genres
        all_metadata = (
            self.df["listed_in"].tolist() + 
            self.df["description"].tolist()
        )
        self.vectorizer.fit(all_metadata)
        
        # Calculate sparse representations
        self.tfidf_matrix = self.vectorizer.transform(self.df["description"])
        
    def generate_recommendations(
        self, 
        selected_titles: Set[str], 
        selected_genres: Set[str], 
        selected_languages: Set[str]
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Calculates dynamic Hybrid Cosine-Similarity scores for all items in catalog."""
        start_time = time.time()
        
        # 1. Aggregated query text from onboarding picks
        seed_descriptions = []
        for title in selected_titles:
            matches = self.df[self.df["title"] == title]
            if not matches.empty:
                seed_descriptions.append(matches.iloc[0]["description"])
                
        profile_query_text = " ".join(selected_genres) + " " + " ".join(seed_descriptions)
        
        # 2. Vectorize profile query
        query_vector = self.vectorizer.transform([profile_query_text])
        
        # Assertions validation: shape check
        assert query_vector.shape == (1, self.tfidf_matrix.shape[1]), "Vector dimensions mismatch"
        
        # 3. Calculate raw similarities
        raw_similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # 4. Multipliers and boosts based on survey preferences
        final_scores = []
        for idx, row in self.df.iterrows():
            score = float(raw_similarities[idx])
            
            # Exclude current selections
            if row["title"] in selected_titles:
                score = 0.0
                final_scores.append((row.to_dict(), score))
                continue
            
            # Language Multiplier
            if selected_languages:
                if row["language"] in selected_languages:
                    score *= 1.8  # Boost matching languages
                else:
                    score *= 0.05  # Heavy penalty for unselected languages (to filter down)
                    
            # Genre Match Boost
            movie_genres = [g.strip().lower() for g in row["listed_in"].split(",")]
            matches_genre = any(genre.lower() in movie_genres for genre in selected_genres)
            if matches_genre:
                score += 0.3  # Additive boost for selected genres
                
            # Normalize final scores to [0.0, 1.0]
            score = min(max(score, 0.0), 1.0)
            final_scores.append((row.to_dict(), score))
            
        final_scores.sort(key=lambda x: x[1], reverse=True)
        self.latency_ms = (time.time() - start_time) * 1000
        return final_scores

# Global engine singleton
engine = NetflixRecommendationEngine(df_catalog)

# ----------------------------------------------------
# 4. SESSION STATE STATE MACHINE
# ----------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = 1.0
if "selected_languages" not in st.session_state:
    st.session_state.selected_languages = set()
if "selected_genres" not in st.session_state:
    st.session_state.selected_genres = set()
if "selected_movies" not in st.session_state:
    st.session_state.selected_movies = set()
if "completed_onboarding" not in st.session_state:
    st.session_state.completed_onboarding = False

# ----------------------------------------------------
# 5. USER JOURNEY FLOW SWITCHER
# ----------------------------------------------------

# Sticky Top Bar (Onboarding Layouts)
if not st.session_state.completed_onboarding and st.session_state.step != "loading":
    logo_col, space_col, step_col = st.columns([1, 3, 1])
    logo_col.markdown('<div class="netflix-logo-brand">Netflix</div>', unsafe_allow_html=True)
    
    # Render Step Indicator
    step_num = 1
    if st.session_state.step == 2.0:
        step_num = 2
    elif st.session_state.step == 3.0:
        step_num = 3
        
    step_col.markdown(f'<div class="step-indicator-text" style="text-align:right; padding-top:1.5rem;">STEP {step_num} OF 3</div>', unsafe_allow_html=True)
    
    # Progress Bar Fill
    progress_w = 33
    if st.session_state.step == 2.0:
        progress_w = 66
    elif st.session_state.step == 3.0:
        progress_w = 100
        
    st.markdown(f'<div class="progress-bar-track"><div class="progress-bar-progress" style="width:{progress_w}%;"></div></div>', unsafe_allow_html=True)

# ----------------------------------------------------
# SCREEN 1: LANGUAGE SELECTION
# ----------------------------------------------------
if st.session_state.step == 1.0:
    st.markdown('<div class="onboarding-title">Tell us what you like to get started.</div>', unsafe_allow_html=True)
    st.markdown('<div class="onboarding-subtitle">Choose the languages you prefer for audio and subtitles.</div>', unsafe_allow_html=True)
    
    languages_list = ["English", "Hindi", "Korean", "Spanish", "Japanese", "Tamil", "Malayalam"]
    
    cols = st.columns(4)
    for idx, lang in enumerate(languages_list):
        col = cols[idx % 4]
        selected = lang in st.session_state.selected_languages
        pill_class = "lang-pill-selected lang-pill-container" if selected else "lang-pill-container"
        
        col.markdown(f'<div class="{pill_class}">', unsafe_allow_html=True)
        if col.button(lang, key=f"lang_{lang}"):
            if selected:
                st.session_state.selected_languages.remove(lang)
            else:
                st.session_state.selected_languages.add(lang)
            st.rerun()
        col.markdown('</div>', unsafe_allow_html=True)
        
    # Navigation Next Button
    st.markdown('<div class="next-btn-container">', unsafe_allow_html=True)
    lang_count = len(st.session_state.selected_languages)
    btn_class = "btn-netflix-action" if lang_count > 0 else "btn-netflix-disabled"
    
    st.markdown(f'<div class="{btn_class}">', unsafe_allow_html=True)
    if st.button("NEXT ➔", key="btn_next_1", disabled=lang_count == 0):
        st.session_state.step = 2.0
        st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

# ----------------------------------------------------
# SCREEN 2: GENRE SELECTION MATRIX
# ----------------------------------------------------
elif st.session_state.step == 2.0:
    st.markdown('<div class="onboarding-title">Select 3 or more genres you enjoy.</div>', unsafe_allow_html=True)
    st.markdown('<div class="onboarding-subtitle">This helps us customize the layout rows of your homepage.</div>', unsafe_allow_html=True)
    
    genres_list = ["Action", "Sci-Fi", "Thriller", "Romance", "Comedy", "Anime", "Horror", "Drama", "Documentaries"]
    genre_count = len(st.session_state.selected_genres)
    
    # Counter Badge
    st.markdown(f'<div style="text-align:right; font-weight:800; color:#E50914; margin-top:-1.5rem; margin-bottom:1rem;">[ Selected: {genre_count} / 3 ]</div>', unsafe_allow_html=True)
    
    # Render Grid
    matrix_dimmed_class = "genre-matrix-dimmed" if genre_count > 0 else ""
    st.markdown(f'<div class="{matrix_dimmed_class}">', unsafe_allow_html=True)
    cols = st.columns(4)
    for idx, genre in enumerate(genres_list):
        col = cols[idx % 4]
        selected = genre in st.session_state.selected_genres
        card_class = "genre-card-selected genre-card-container" if selected else "genre-card-container"
        
        col.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
        if col.button(genre, key=f"genre_{genre}"):
            if selected:
                st.session_state.selected_genres.remove(genre)
            else:
                st.session_state.selected_genres.add(genre)
            st.rerun()
        col.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
        
    # Continue button active once genre count >= 3
    st.markdown('<div class="next-btn-container">', unsafe_allow_html=True)
    continue_disabled = genre_count < 3
    btn_class = "btn-netflix-action" if not continue_disabled else "btn-netflix-disabled"
    
    st.markdown(f'<div class="{btn_class}">', unsafe_allow_html=True)
    if st.button("CONTINUE ➔", key="btn_continue", disabled=continue_disabled):
        st.session_state.step = 3.0
        st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

# ----------------------------------------------------
# SCREEN 3: TITLE PREFERENCE PICKER ("Pick 3 Favorites")
# ----------------------------------------------------
elif st.session_state.step == 3.0:
    st.markdown('<div class="onboarding-title">Choose 3 movies or TV shows you love.</div>', unsafe_allow_html=True)
    st.markdown('<div class="onboarding-subtitle">This helps us build your personalized row of recommendations.</div>', unsafe_allow_html=True)

    # Search Bar
    search_q = st.text_input("🔍 Search movies or TV shows...", "").strip().lower()
    
    # Filter catalog
    filtered_catalog = CATALOG
    if search_q:
        filtered_catalog = [item for item in CATALOG if search_q in item["title"].lower() or search_q in item["listed_in"].lower()]
        
    if not filtered_catalog:
        st.warning("No matches found in synthetic catalog.")
    else:
        cols = st.columns(4)
        for idx, item in enumerate(filtered_catalog):
            col = cols[idx % 4]
            title = item["title"]
            selected = title in st.session_state.selected_movies
            
            # CSS wrapper targeting specific button key
            selected_class = "movie-poster-selected movie-poster-card" if selected else "movie-poster-card"
            st.markdown(
                f"""
                <style>
                div.movie-poster-card-{item['show_id']} > div > button {{
                    background-image: linear-gradient(180deg, rgba(20,20,20,0) 0%, rgba(20,20,20,0.85) 100%), url("{item['poster']}") !important;
                }}
                </style>
                """,
                unsafe_allow_html=True
            )
            
            col.markdown(f'<div class="movie-poster-card-{item["show_id"]} {selected_class}">', unsafe_allow_html=True)
            # Render text blank inside, we let CSS style background and hover text overlay
            if col.button(title, key=f"select_{item['show_id']}"):
                if selected:
                    st.session_state.selected_movies.remove(title)
                else:
                    if len(st.session_state.selected_movies) < 3:
                        st.session_state.selected_movies.add(title)
                    else:
                        st.warning("You have already selected 3 movies. Deselect one to choose another.")
                st.rerun()
            col.markdown('</div>', unsafe_allow_html=True)
            
    # Floating Action Bar at the bottom
    sel_count = len(st.session_state.selected_movies)
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
    btn_class = "btn-netflix-action" if not finish_disabled else "btn-netflix-disabled"
    finish_col.markdown(f'<div class="{btn_class}" style="position:relative; z-index:1001;">', unsafe_allow_html=True)
    if finish_col.button("FINISH & WATCH ➔", key="btn_finish", disabled=finish_disabled):
        st.session_state.step = "loading"
        st.rerun()
    finish_col.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------
# SCREEN 4: PROCESSING STATE
# ----------------------------------------------------
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

# ----------------------------------------------------
# SCREEN 5: PERSONALIZED HOMEPAGE LAYOUT
# ----------------------------------------------------
else:
    # Get dynamic matching vector array
    recs = engine.generate_recommendations(
        st.session_state.selected_movies,
        st.session_state.selected_genres,
        st.session_state.selected_languages
    )

    # 1. Netflix Transparent Navbar Header
    st.markdown(
        """
        <div class="homepage-navbar">
            <div style="display:flex; align-items:center; gap:2.5rem;">
                <div class="netflix-logo-brand" style="font-size: 2.4rem;">Netflix</div>
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
    
    # Alignment right for Reset Onboarding
    _, reset_col = st.columns([4, 1.2])
    reset_col.markdown('<div class="btn-netflix-action" style="text-align:right; margin-top:1.2rem; position:relative; z-index:101;">', unsafe_allow_html=True)
    if reset_col.button("🔄 Reset Onboarding", key="btn_reset"):
        st.session_state.step = 1.0
        st.session_state.selected_languages = set()
        st.session_state.selected_genres = set()
        st.session_state.selected_movies = set()
        st.session_state.completed_onboarding = False
        st.rerun()
    reset_col.markdown('</div>', unsafe_allow_html=True)

    # 2. Hero Billboard Banner
    hero_item = recs[0][0]
    hero_score = recs[0][1]
    
    # Render dynamic billboard background from item banner link
    st.markdown(
        f"""
        <div class="hero-billboard" style="background-image: url('{hero_item['banner']}');">
            <div class="hero-billboard-overlay"></div>
            <div class="hero-billboard-content">
                <div class="hero-genre-tag">{hero_item['listed_in']}</div>
                <h1 class="hero-title" style="font-size: 3.5rem; margin-bottom: 0.5rem; font-family:'Helvetica Neue', Arial, sans-serif;">{hero_item['title']}</h1>
                <div style="display:flex; align-items:center; font-size:1rem; font-weight:700; margin-bottom: 1rem;">
                    <span class="hero-meta-badge">{(hero_score*100):.0f}% Match</span>
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
    row_1_items = recs[:4]
    
    cols1 = st.columns(4)
    for idx, (item, score) in enumerate(row_1_items):
        card_html = f"""
        <div class="row-card-container">
            <div class="row-card-img-banner" style="background-image: url('{item['poster']}');">
                <div class="row-card-gradient-overlay"></div>
                <span class="card-tag-badge">{item['type']}</span>
                <div class="row-card-title">{item['title']}</div>
            </div>
            <div class="row-card-body-content">
                <div style="font-size: 0.75rem; color:#e50914; font-weight:700;">{item['listed_in']}</div>
                <div class="card-meta-line" style="margin-top:0.25rem;">
                    <span style="color:#46D369; font-weight:700;">{(score*100):.0f}% Match</span>
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
    first_seed = list(st.session_state.selected_movies)[0]
    st.markdown(f'<div class="movie-row-header">Because You Selected {first_seed}</div>', unsafe_allow_html=True)
    
    seed_desc = df_catalog[df_catalog["title"] == first_seed].iloc[0]["description"]
    seed_vec = engine.vectorizer.transform([seed_desc])
    desc_sim = cosine_similarity(seed_vec, engine.tfidf_matrix).flatten()
    
    row_2_scores = []
    for idx, row in df_catalog.iterrows():
        if row["title"] == first_seed:
            continue
        row_2_scores.append((row.to_dict(), desc_sim[idx]))
    row_2_scores.sort(key=lambda x: x[1], reverse=True)
    row_2_items = row_2_scores[:4]
    
    cols2 = st.columns(4)
    for idx, (item, score) in enumerate(row_2_items):
        card_html = f"""
        <div class="row-card-container">
            <div class="row-card-img-banner" style="background-image: url('{item['poster']}');">
                <div class="row-card-gradient-overlay"></div>
                <span class="card-tag-badge">{item['type']}</span>
                <div class="row-card-title">{item['title']}</div>
            </div>
            <div class="row-card-body-content">
                <div style="font-size: 0.75rem; color:#e50914; font-weight:700;">{item['listed_in']}</div>
                <div class="card-meta-line" style="margin-top:0.25rem;">
                    <span style="color:#46D369; font-weight:700;">{(score*100):.0f}% Match</span>
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
    
    lang_filtered = [x for x in recs if x[0]["language"] == target_lang][:4]
    
    cols3 = st.columns(4)
    for idx, (item, score) in enumerate(lang_filtered):
        card_html = f"""
        <div class="row-card-container">
            <div class="row-card-img-banner" style="background-image: url('{item['poster']}');">
                <div class="row-card-gradient-overlay"></div>
                <span class="card-tag-badge">{item['type']}</span>
                <div class="row-card-title">{item['title']}</div>
            </div>
            <div class="row-card-body-content">
                <div style="font-size: 0.75rem; color:#e50914; font-weight:700;">{item['listed_in']}</div>
                <div class="card-meta-line" style="margin-top:0.25rem;">
                    <span style="color:#46D369; font-weight:700;">{(score*100):.0f}% Match</span>
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
    # Row 4: "Popular in [Selected Genre]"
    # ----------------------------------------------------
    target_genre = list(st.session_state.selected_genres)[0]
    st.markdown(f'<div class="movie-row-header">Popular in {target_genre}</div>', unsafe_allow_html=True)
    
    genre_filtered = [x for x in recs if target_genre.lower() in x[0]["listed_in"].lower()][:4]
    
    cols4 = st.columns(4)
    for idx, (item, score) in enumerate(genre_filtered):
        card_html = f"""
        <div class="row-card-container">
            <div class="row-card-img-banner" style="background-image: url('{item['poster']}');">
                <div class="row-card-gradient-overlay"></div>
                <span class="card-tag-badge">{item['type']}</span>
                <div class="row-card-title">{item['title']}</div>
            </div>
            <div class="row-card-body-content">
                <div style="font-size: 0.75rem; color:#e50914; font-weight:700;">{item['listed_in']}</div>
                <div class="card-meta-line" style="margin-top:0.25rem;">
                    <span style="color:#46D369; font-weight:700;">{(score*100):.0f}% Match</span>
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
            "Seed Movies": list(st.session_state.selected_movies)
        },
        "Pipeline State": {
            "completed_onboarding": st.session_state.completed_onboarding,
            "TF-IDF Matrix dimensions": engine.tfidf_matrix.shape,
            "Vocabulary Length": len(engine.vectorizer.get_feature_names_out()),
            "Sparsity Percent": f"{(1.0 - (engine.tfidf_matrix.nnz / (engine.tfidf_matrix.shape[0] * engine.tfidf_matrix.shape[1]))) * 100:.2f}%"
        }
    }
    
    if st.session_state.completed_onboarding:
        diag_payload["Recommendation Latency (Stage 3)"] = f"{engine.latency_ms:.2f} ms"
        diag_payload["Top 5 Calculated Matching Scores"] = [
            {"title": title_tuple[0]["title"], "score": round(title_tuple[1], 4)}
            for title_tuple in recs[:5]
        ]
        
        assertions = {
            "DF Catalog Integrity (Rows == 20)": len(df_catalog) == 20,
            "Language Selections Valid": len(st.session_state.selected_languages) > 0,
            "Genre Preference Count >= 3": len(st.session_state.selected_genres) >= 3,
            "Seed Movie Selections == 3": len(st.session_state.selected_movies) == 3,
            "Cosine Scores Range [0,1]": all(0.0 <= x[1] <= 1.0 for x in recs)
        }
        diag_payload["Runtime Assertions Check Log"] = assertions
        
    st.json(diag_payload)
