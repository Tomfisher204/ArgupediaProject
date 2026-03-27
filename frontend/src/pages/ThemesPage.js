import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import ThemeRequestModal from '../components/ThemeRequestModal';
import './ThemesPage.css';

const ThemesPage = () => {
  const { getValidAccessToken, logout } = useAuth();
  const navigate = useNavigate();
  const [themes, setThemes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const fetchThemes = async (page = 1) => {
    try {
      setLoading(true);
      const token = await getValidAccessToken();
      const res = await fetch(`http://localhost:8000/api/themes/?page=${page}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Failed to load themes.');
      const data = await res.json();
      setThemes(data.results);
      setPagination({
        count: data.count,
        next: data.next,
        previous: data.previous,
        currentPage: page,
        totalPages: Math.ceil(data.count / 16),
      });
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchThemes();
  }, [getValidAccessToken]);

  return (
    <div className="themes-page">
      <header className="page-header">
        <div className="page-header-inner">
          <div className="header-logo" onClick={() => navigate('/dashboard')} style={{ cursor: 'pointer' }}>
            <span className="logo-mark-sm">A</span>
            <span className="logo-text-sm">argupedia</span>
          </div>
          <nav className="header-nav">
            <button className="nav-link active">Themes</button>
          </nav>
          <button className="logout-btn" onClick={logout}>Log out</button>
        </div>
      </header>

      <main className="page-main">
        <div className="page-inner">
          <div className="page-title-row">
            <h1 className="page-title">Browse themes</h1>
            <p className="page-sub">Pick a theme to see its arguments.</p>
          </div>
          <div className="theme-request-section">
            <button className="btn-new" onClick={() => setShowModal(true)}>Request a Theme</button>
          </div>

          {loading && <p className="state-msg">Loading themes…</p>}
          {error   && <p className="state-msg error">{error}</p>}

          {!loading && !error && themes.length === 0 && (
            <p className="state-msg">No themes yet.</p>
          )}

          {!loading && !error && (
            <>
              <div className="themes-grid">
                {themes.map((theme) => (
                  <button
                    key={theme.id}
                    className="theme-card"
                    onClick={() => navigate(`/themes/${theme.id}`)}
                  >
                    <p className="theme-title">{theme.title}</p>
                    {theme.description && (
                      <p className="theme-desc">{theme.description}</p>
                    )}
                    <p className="theme-count">
                      {theme.argument_count} argument{theme.argument_count !== 1 ? 's' : ''}
                    </p>
                  </button>
                ))}
              </div>
              {pagination && pagination.totalPages > 1 && (
                <div className="pagination">
                  <button
                    className="pagination-btn"
                    onClick={() => fetchThemes(pagination.currentPage - 1)}
                    disabled={!pagination.previous}
                  >
                    Previous
                  </button>
                  <span className="pagination-info">
                    Page {pagination.currentPage} of {pagination.totalPages}
                  </span>
                  <button
                    className="pagination-btn"
                    onClick={() => fetchThemes(pagination.currentPage + 1)}
                    disabled={!pagination.next}
                  >
                    Next
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </main>

      {showModal && (
        <ThemeRequestModal
          onClose={() => setShowModal(false)}
          onSuccess={(newArgId) => {
            setShowModal(false);
            fetchThemes();
          }}
        />
      )}

    </div>
  );
};

export default ThemesPage;