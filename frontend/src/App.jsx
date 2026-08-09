import React, { useState, useEffect, useCallback } from 'react';

const API_BASE = window.location.hostname === 'localhost' ? 'http://localhost:8000/api' : '/api';

export default function App() {
  // Catalog State
  const [titles, setTitles] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(24);
  const [loading, setLoading] = useState(true);

  // Filter States (Left Sidebar)
  const [search, setSearch] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('');
  const [yearMin, setYearMin] = useState(1925);
  const [yearMax, setYearMax] = useState(2026);
  const [genres, setGenres] = useState([]);

  // Similarity Engine Weights (Local Storage persisted)
  const [wTitle, setWTitle] = useState(() => Number(localStorage.getItem('w_title') ?? 2.0));
  const [wDirector, setWDirector] = useState(() => Number(localStorage.getItem('w_director') ?? 3.0));
  const [wCast, setWCast] = useState(() => Number(localStorage.getItem('w_cast') ?? 2.0));
  const [wGenre, setWGenre] = useState(() => Number(localStorage.getItem('w_genre') ?? 3.0));
  const [wDesc, setWDesc] = useState(() => Number(localStorage.getItem('w_desc') ?? 1.0));

  // Selected Show Modal State
  const [selectedShowId, setSelectedShowId] = useState(null);
  const [showDetails, setShowDetails] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [recLoading, setRecLoading] = useState(false);
  const [rawPayload, setRawPayload] = useState(null);

  // Diagnostics / Evaluator Inspection Drawer State (Right Drawer)
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('metrics'); // 'metrics' | 'assertions' | 'weights' | 'payload'
  const [diagnostics, setDiagnostics] = useState(null);

  // Featured Show (Hero Banner)
  const [featuredShow, setFeaturedShow] = useState(null);

  // Persist weights in localStorage
  useEffect(() => {
    localStorage.setItem('w_title', wTitle.toString());
    localStorage.setItem('w_director', wDirector.toString());
    localStorage.setItem('w_cast', wCast.toString());
    localStorage.setItem('w_genre', wGenre.toString());
    localStorage.setItem('w_desc', wDesc.toString());
  }, [wTitle, wDirector, wCast, wGenre, wDesc]);

  // Fetch unique genres on mount
  useEffect(() => {
    fetch(`${API_BASE}/genres`)
      .then(res => res.json())
      .then(data => setGenres(data))
      .catch(err => console.error("Error loading genres:", err));
  }, []);

  // Fetch diagnostics stats
  const fetchDiagnostics = useCallback(() => {
    fetch(`${API_BASE}/diagnostics`)
      .then(res => res.json())
      .then(data => setDiagnostics(data))
      .catch(err => console.error("Error loading diagnostics:", err));
  }, []);

  // Fetch diagnostics on mount
  useEffect(() => {
    fetchDiagnostics();
  }, [fetchDiagnostics]);

  // Fetch catalog list of titles
  const fetchTitles = useCallback(() => {
    setLoading(true);
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
    });

    if (search) params.append('search', search);
    if (selectedType) params.append('type', selectedType);
    if (selectedGenre) params.append('genre', selectedGenre);
    if (yearMin) params.append('release_year_min', yearMin.toString());
    if (yearMax) params.append('release_year_max', yearMax.toString());

    fetch(`${API_BASE}/titles?${params.toString()}`)
      .then(res => res.json())
      .then(data => {
        setTitles(data.titles || []);
        setTotalCount(data.total_count || 0);
        if (data.titles && data.titles.length > 0 && !featuredShow) {
          setFeaturedShow(data.titles[0]);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error("Error loading titles:", err);
        setLoading(false);
      });
  }, [page, limit, search, selectedType, selectedGenre, yearMin, yearMax, featuredShow]);

  // Trigger search titles refresh
  useEffect(() => {
    fetchTitles();
  }, [fetchTitles]);

  // Fetch recommendations with active weights
  const fetchRecommendations = useCallback((showId) => {
    if (!showId) return;
    setRecLoading(true);
    
    const params = new URLSearchParams({
      limit: '8',
      w_title: wTitle.toString(),
      w_director: wDirector.toString(),
      w_cast: wCast.toString(),
      w_genre: wGenre.toString(),
      w_desc: wDesc.toString()
    });

    fetch(`${API_BASE}/titles/${showId}/recommendations?${params.toString()}`)
      .then(res => res.json())
      .then(data => {
        setRecommendations(data.recommendations || []);
        setRawPayload(data);
        setRecLoading(false);
        fetchDiagnostics();
      })
      .catch(err => {
        console.error("Error fetching recommendations:", err);
        setRecLoading(false);
      });
  }, [wTitle, wDirector, wCast, wGenre, wDesc, fetchDiagnostics]);

  // Handle weight adjustments
  const handleWeightChange = (setter, value) => {
    setter(value);
  };

  // Re-run recommendations if weights are tweaked and a title is active
  useEffect(() => {
    if (selectedShowId) {
      fetchRecommendations(selectedShowId);
    }
  }, [selectedShowId, wTitle, wDirector, wCast, wGenre, wDesc, fetchRecommendations]);

  // Fetch details and similarity recommendations when a card is selected
  useEffect(() => {
    if (!selectedShowId) {
      setShowDetails(null);
      setRecommendations([]);
      setRawPayload(null);
      return;
    }

    fetch(`${API_BASE}/titles/${selectedShowId}`)
      .then(res => res.json())
      .then(data => {
        setShowDetails(data);
        fetchRecommendations(selectedShowId);
      })
      .catch(err => {
        console.error("Error fetching show details:", err);
      });
  }, [selectedShowId, fetchRecommendations]);

  const handleShowClick = (showId) => {
    setSelectedShowId(showId);
  };

  const closeModal = () => {
    setSelectedShowId(null);
  };

  const resetFilters = () => {
    setSearch('');
    setSelectedType('');
    setSelectedGenre('');
    setYearMin(1925);
    setYearMax(2026);
    setPage(1);
  };

  const resetWeights = () => {
    setWTitle(2.0);
    setWDirector(3.0);
    setWCast(2.0);
    setWGenre(3.0);
    setWDesc(1.0);
  };

  const totalPages = Math.ceil(totalCount / limit);

  return (
    <div className="app-layout">
      {/* Control Sidebar (Left side panel) */}
      <aside className="control-sidebar">
        <div className="sidebar-header">
          <span className="logo-text">Orboflix</span>
          <span className="logo-tag">V2</span>
        </div>

        {/* Section 1: Catalog Filters */}
        <div className="sidebar-section">
          <h3 className="sidebar-title">Catalog Filters</h3>
          
          <div className="filter-group">
            <label className="filter-label">Search Query</label>
            <input
              type="text"
              placeholder="Keywords, directors, casts..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="search-input"
            />
          </div>

          <div className="filter-group">
            <label className="filter-label">Content Type</label>
            <select
              value={selectedType}
              onChange={(e) => {
                setSelectedType(e.target.value);
                setPage(1);
              }}
              className="select-input"
            >
              <option value="">All Types</option>
              <option value="Movie">Movie</option>
              <option value="TV Show">TV Show</option>
            </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">Genre Category</label>
            <select
              value={selectedGenre}
              onChange={(e) => {
                setSelectedGenre(e.target.value);
                setPage(1);
              }}
              className="select-input"
            >
              <option value="">All Genres</option>
              {genres.map(g => (
                <option key={g} value={g}>{g}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">Release Year Range</label>
            <div className="slider-wrapper">
              <input
                type="range"
                min="1925"
                max="2026"
                value={yearMin}
                onChange={(e) => {
                  setYearMin(parseInt(e.target.value));
                  setPage(1);
                }}
                className="slider-input"
              />
              <input
                type="range"
                min="1925"
                max="2026"
                value={yearMax}
                onChange={(e) => {
                  setYearMax(parseInt(e.target.value));
                  setPage(1);
                }}
                className="slider-input"
              />
              <div className="slider-range-values">
                Range: {yearMin} - {yearMax}
              </div>
            </div>
          </div>

          <button className="btn btn-outline" onClick={resetFilters} style={{ width: '100%', justifyContent: 'center' }}>
            Clear Filters
          </button>
        </div>

        {/* Section 2: Engine Similarity Overrides */}
        <div className="sidebar-section">
          <h3 className="sidebar-title">Engine Weight Overrides</h3>

          <div className="weight-slider-item">
            <div className="weight-header">
              <span>Title Weight</span>
              <span>{wTitle.toFixed(1)}</span>
            </div>
            <input
              type="range"
              min="0"
              max="10"
              step="0.5"
              value={wTitle}
              onChange={(e) => handleWeightChange(setWTitle, parseFloat(e.target.value))}
              className="slider-input"
            />
          </div>

          <div className="weight-slider-item">
            <div className="weight-header">
              <span>Director Weight</span>
              <span>{wDirector.toFixed(1)}</span>
            </div>
            <input
              type="range"
              min="0"
              max="10"
              step="0.5"
              value={wDirector}
              onChange={(e) => handleWeightChange(setWDirector, parseFloat(e.target.value))}
              className="slider-input"
            />
          </div>

          <div className="weight-slider-item">
            <div className="weight-header">
              <span>Cast Weight</span>
              <span>{wCast.toFixed(1)}</span>
            </div>
            <input
              type="range"
              min="0"
              max="10"
              step="0.5"
              value={wCast}
              onChange={(e) => handleWeightChange(setWCast, parseFloat(e.target.value))}
              className="slider-input"
            />
          </div>

          <div className="weight-slider-item">
            <div className="weight-header">
              <span>Genre Weight</span>
              <span>{wGenre.toFixed(1)}</span>
            </div>
            <input
              type="range"
              min="0"
              max="10"
              step="0.5"
              value={wGenre}
              onChange={(e) => handleWeightChange(setWGenre, parseFloat(e.target.value))}
              className="slider-input"
            />
          </div>

          <div className="weight-slider-item">
            <div className="weight-header">
              <span>Description Weight</span>
              <span>{wDesc.toFixed(1)}</span>
            </div>
            <input
              type="range"
              min="0"
              max="10"
              step="0.5"
              value={wDesc}
              onChange={(e) => handleWeightChange(setWDesc, parseFloat(e.target.value))}
              className="slider-input"
            />
          </div>

          <button className="btn btn-outline" onClick={resetWeights} style={{ width: '100%', justifyContent: 'center' }}>
            Restore Default Weights
          </button>
        </div>
      </aside>

      {/* Main Workspace (Right area) */}
      <section className="workspace">
        {/* Navigation Header */}
        <header className="app-header">
          <button 
            className="btn btn-outline"
            onClick={() => {
              fetchDiagnostics();
              setDrawerOpen(true);
            }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="9" y1="3" x2="9" y2="21"></line>
              <line x1="15" y1="3" x2="15" y2="21"></line>
              <line x1="3" y1="9" x2="21" y2="9"></line>
              <line x1="3" y1="15" x2="21" y2="15"></line>
            </svg>
            Evaluator panel
          </button>
        </header>

        {/* Featured Title banner */}
        {featuredShow && (
          <div className="hero-section" style={{ backgroundImage: 'linear-gradient(rgba(20,20,20,0.1), rgba(20,20,20,0.95))' }}>
            <div className="hero-overlay"></div>
            <div className="hero-content">
              <div className="hero-tag">Featured Recommended Title</div>
              <h1 className="hero-title">{featuredShow.title}</h1>
              <div className="hero-meta">
                <span className="hero-rating">{featuredShow.rating || 'NR'}</span>
                <span>{featuredShow.release_year}</span>
                <span>{featuredShow.duration}</span>
                <span>{featuredShow.type}</span>
              </div>
              <p className="hero-desc">{featuredShow.description}</p>
              <button className="btn btn-primary" onClick={() => handleShowClick(featuredShow.show_id)}>
                Run Weighted Similarity Matcher
              </button>
            </div>
          </div>
        )}

        {/* Catalog Content Area */}
        <main className="main-content">
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            Browse {totalCount} titles in database. Tune weights in the sidebar and select a title to see dynamic recommendations update.
          </p>

          {loading ? (
            <div className="state-container">
              <div className="spinner"></div>
              <h3 className="state-title">Loading Database Catalog...</h3>
            </div>
          ) : titles.length === 0 ? (
            <div className="state-container">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth="1.5" style={{ marginBottom: '1rem' }}>
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
              <h3 className="state-title">No Catalog Matches</h3>
              <p className="state-desc">Try resetting your active filters in the Control Sidebar.</p>
            </div>
          ) : (
            <>
              <div className="catalog-grid">
                {titles.map((show) => (
                  <div 
                    key={show.show_id} 
                    className="catalog-card"
                    onClick={() => handleShowClick(show.show_id)}
                  >
                    <div className="card-media">
                      <span className="card-badge">{show.type}</span>
                      <span className="card-title">{show.title}</span>
                    </div>
                    <div className="card-body">
                      <div className="card-genre">{show.listed_in}</div>
                      <div className="card-meta">
                        <span>{show.release_year}</span>
                        <span>{show.duration}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Pagination bar */}
              {totalPages > 1 && (
                <div className="pagination-container">
                  <button 
                    className="btn btn-outline" 
                    disabled={page === 1}
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                  >
                    Previous
                  </button>
                  <span className="pagination-info">
                    Page {page} of {totalPages}
                  </span>
                  <button 
                    className="btn btn-outline" 
                    disabled={page === totalPages}
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  >
                    Next
                  </button>
                </div>
              )}
            </>
          )}
        </main>
      </section>

      {/* Details Modal with Carousel */}
      {selectedShowId && showDetails && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-container" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close-btn" onClick={closeModal}>✕</button>
            
            <div className="modal-header-banner">
              <div>
                <h2 className="modal-title">{showDetails.title}</h2>
                <div className="hero-meta">
                  <span className="hero-rating">{showDetails.rating || 'NR'}</span>
                  <span>{showDetails.release_year}</span>
                  <span>{showDetails.duration}</span>
                  {showDetails.country && <span>📍 {showDetails.country}</span>}
                </div>
              </div>
            </div>

            <div className="modal-body">
              <div className="modal-layout">
                <div>
                  <p className="description-text">{showDetails.description}</p>
                </div>
                <div>
                  <div className="metadata-item">
                    <span className="metadata-label">Director</span>
                    <span className="metadata-value">{showDetails.director || 'N/A'}</span>
                  </div>
                  <div className="metadata-item">
                    <span className="metadata-label">Cast</span>
                    <span className="metadata-value">{showDetails.cast || 'N/A'}</span>
                  </div>
                  <div className="metadata-item">
                    <span className="metadata-label">Genres</span>
                    <span className="metadata-value">{showDetails.listed_in}</span>
                  </div>
                </div>
              </div>

              {/* Carousel Section */}
              <div className="recommendations-section">
                <h3 className="recommendations-title">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--primary-color)" strokeWidth="2">
                    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                  </svg>
                  Dynamic Similarity Recommendations (Tune Weights in Sidebar!)
                </h3>

                {recLoading ? (
                  <div style={{ display: 'flex', justifyContent: 'center', padding: '1.5rem' }}>
                    <div className="spinner" style={{ width: '28px', height: '28px' }}></div>
                  </div>
                ) : recommendations.length === 0 ? (
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No dynamic matches found with current parameters.</p>
                ) : (
                  <div className="recommendations-carousel">
                    {recommendations.map((rec) => (
                      <div 
                        key={rec.show_id} 
                        className="rec-card"
                        onClick={() => handleShowClick(rec.show_id)}
                      >
                        <div>
                          <div className="rec-match-badge">
                            {(rec.similarity_score * 100).toFixed(1)}% Match
                          </div>
                          <div className="rec-title">{rec.title}</div>
                        </div>
                        <div className="rec-meta">
                          <span>{rec.release_year}</span>
                          <span>{rec.duration}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Evaluator Drawer Panel (Split tabs layout) */}
      <div className={`diagnostics-drawer ${drawerOpen ? 'open' : ''}`}>
        <div className="diagnostics-header">
          <div className="diagnostics-title">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--primary-color)" strokeWidth="2">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
            </svg>
            Evaluator Inspection Panel
          </div>
          <button className="btn btn-outline" style={{ padding: '0.3rem 0.7rem', borderRadius: '50%' }} onClick={() => setDrawerOpen(false)}>
            ✕
          </button>
        </div>

        {/* Tab Headers */}
        <div className="tab-header">
          <button className={`tab-btn ${activeTab === 'metrics' ? 'active' : ''}`} onClick={() => setActiveTab('metrics')}>
            Metrics
          </button>
          <button className={`tab-btn ${activeTab === 'assertions' ? 'active' : ''}`} onClick={() => setActiveTab('assertions')}>
            Assertions
          </button>
          <button className={`tab-btn ${activeTab === 'weights' ? 'active' : ''}`} onClick={() => setActiveTab('weights')}>
            Vectors
          </button>
          <button className={`tab-btn ${activeTab === 'payload' ? 'active' : ''}`} onClick={() => setActiveTab('payload')}>
            Payload
          </button>
        </div>

        {/* Tab Body */}
        <div className="diagnostics-body">
          {diagnostics ? (
            <>
              {activeTab === 'metrics' && (
                <div className="tab-panel-content">
                  <div>
                    <h4 className="diagnostics-section-title">Execution Latency</h4>
                    <div className="metrics-grid">
                      <div className="metric-card">
                        <div className="metric-val">{diagnostics.stage_1_time_ms} ms</div>
                        <div className="metric-lbl">Stage 1 Ingest</div>
                      </div>
                      <div className="metric-card">
                        <div className="metric-val">{diagnostics.stage_2_time_ms} ms</div>
                        <div className="metric-lbl">Stage 2 Vectorization</div>
                      </div>
                      <div className="metric-card" style={{ gridColumn: 'span 2' }}>
                        <div className="metric-val">{diagnostics.stage_3_time_ms} ms</div>
                        <div className="metric-lbl">Stage 3 Similarity Math</div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="diagnostics-section-title">Matrix Sparsity & Dimensions</h4>
                    <div className="metrics-grid" style={{ marginBottom: '0.75rem' }}>
                      <div className="metric-card">
                        <div className="metric-val">{diagnostics.dataset_rows}</div>
                        <div className="metric-lbl">Total Documents</div>
                      </div>
                      <div className="metric-card">
                        <div className="metric-val">{diagnostics.matrix_shape ? diagnostics.matrix_shape[1] : 0}</div>
                        <div className="metric-lbl">Vect Vocabulary</div>
                      </div>
                    </div>
                    <div className="sparsity-container">
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                        <span className="metric-lbl">System Sparsity</span>
                        <span>{diagnostics.matrix_sparsity_percent}% Empty</span>
                      </div>
                      <div className="sparsity-bar-bg">
                        <div className="sparsity-bar-fill" style={{ width: `${diagnostics.matrix_sparsity_percent}%` }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'assertions' && (
                <div className="tab-panel-content">
                  <h4 className="diagnostics-section-title">Core Runtime Assertions</h4>
                  <div className="assertions-list">
                    {Object.entries(diagnostics.assertions || {}).map(([key, val]) => (
                      <div key={key} className="assertion-item">
                        <span className="assertion-name">{key}</span>
                        <span className={`assertion-status-badge ${val ? 'badge-success' : 'badge-failure'}`}>
                          {val ? 'PASSED' : 'FAILED'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'weights' && (
                <div className="tab-panel-content">
                  <h4 className="diagnostics-section-title">Dynamic Weight Vectors</h4>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Visual representation of vector weighting proportions active in memory.
                  </p>
                  
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem', backgroundColor: 'var(--bg-color)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                      <span>Title weight</span>
                      <span>{(wTitle / (wTitle + wDirector + wCast + wGenre + wDesc || 1) * 100).toFixed(0)}%</span>
                    </div>
                    <div className="sparsity-bar-bg"><div className="sparsity-bar-fill" style={{ width: `${wTitle / (wTitle + wDirector + wCast + wGenre + wDesc || 1) * 100}%` }}></div></div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                      <span>Director weight</span>
                      <span>{(wDirector / (wTitle + wDirector + wCast + wGenre + wDesc || 1) * 100).toFixed(0)}%</span>
                    </div>
                    <div className="sparsity-bar-bg"><div className="sparsity-bar-fill" style={{ width: `${wDirector / (wTitle + wDirector + wCast + wGenre + wDesc || 1) * 100}%` }}></div></div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                      <span>Cast weight</span>
                      <span>{(wCast / (wTitle + wDirector + wCast + wGenre + wDesc || 1) * 100).toFixed(0)}%</span>
                    </div>
                    <div className="sparsity-bar-bg"><div className="sparsity-bar-fill" style={{ width: `${wCast / (wTitle + wDirector + wCast + wGenre + wDesc || 1) * 100}%` }}></div></div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                      <span>Genre weight</span>
                      <span>{(wGenre / (wTitle + wDirector + wCast + wGenre + wDesc || 1) * 100).toFixed(0)}%</span>
                    </div>
                    <div className="sparsity-bar-bg"><div className="sparsity-bar-fill" style={{ width: `${wGenre / (wTitle + wDirector + wCast + wGenre + wDesc || 1) * 100}%` }}></div></div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                      <span>Description weight</span>
                      <span>{(wDesc / (wTitle + wDirector + wCast + wGenre + wDesc || 1) * 100).toFixed(0)}%</span>
                    </div>
                    <div className="sparsity-bar-bg"><div className="sparsity-bar-fill" style={{ width: `${wDesc / (wTitle + wDirector + wCast + wGenre + wDesc || 1) * 100}%` }}></div></div>
                  </div>
                </div>
              )}

              {activeTab === 'payload' && (
                <div className="tab-panel-content">
                  <h4 className="diagnostics-section-title">Raw Response Payload (JSON)</h4>
                  {rawPayload ? (
                    <pre className="raw-payload-block">
                      {JSON.stringify(rawPayload, null, 2)}
                    </pre>
                  ) : (
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Select a title to fetch dynamic recommendations and display the active JSON payload.
                    </p>
                  )}
                </div>
              )}
            </>
          ) : (
            <div className="state-container">
              <div className="spinner"></div>
              <h3 className="state-title">Loading stats...</h3>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
