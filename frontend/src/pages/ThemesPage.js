import React, {useEffect, useState, useCallback} from 'react';
import {useNavigate} from 'react-router-dom';
import {useAuth} from '../context';
import {ThemeRequestForm, Navbar, ConfirmDialog, TrashIcon} from '../components';
import '../css/pages/ThemesPage.css';

const API = process.env.REACT_APP_API_URL;

const ThemesPage = () => {
  const {getValidAccessToken, user} = useAuth();
  const navigate = useNavigate();
  const [themes, setThemes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [confirmThemeId, setConfirmThemeId] = useState(null);
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState('alpha_asc');

  const fetchThemes = useCallback(async (page = 1, query = search, sortBy = sort) => {
    try {
      setLoading(true);
      const token = await getValidAccessToken();
      let url = `${API}/api/themes/?page=${page}`;
      if (query) url += `&q=${encodeURIComponent(query)}`;
      if (sortBy) url += `&sort=${encodeURIComponent(sortBy)}`;
      const res = await fetch(url, {headers: {Authorization: `Bearer ${token}`}});
      if (!res.ok) throw new Error("Failed to load themes.");
      const data = await res.json();
      setThemes(data.results);
      setPagination({count: data.count, next: data.next, previous: data.previous, currentPage: page, totalPages: Math.ceil(data.count / 16)});
      setError(null);
    } 
    catch (err) {
      setError(err.message);
    } 
    finally {
      setLoading(false);
    }
  }, [getValidAccessToken, search, sort]);

  useEffect(() => {fetchThemes()}, [fetchThemes]);

  const deleteTheme = (themeId) => {
    setConfirmThemeId(themeId);
    setShowConfirm(true);
  };

  const confirmDeleteTheme = async () => {
    if (!confirmThemeId) return;
    setShowConfirm(false);
    try {
      const token = await getValidAccessToken();
      const res = await fetch(`${API}/api/admin/theme/${confirmThemeId}/`, {method: 'DELETE', headers: {Authorization: `Bearer ${token}`}});
      if (res.ok) {
        fetchThemes();
      }
      else {
        setError('Failed to delete theme.');
      }
    }
    catch (err) {
      setError(err.message);
    }
    setConfirmThemeId(null);
  };

  return (
    <div className="themes-page">
      <Navbar />
      <main className="page-main">
        <div className="page-inner">
          <div className="page-title-row">
            <h1 className="page-title">Browse themes</h1>
            <p className="page-sub">Pick a theme to see its arguments.</p>
          </div>

          <div className="theme-filters">
            <input className="theme-search" type="text" placeholder="Search themes..." value={search} onChange={(e) => {setSearch(e.target.value); fetchThemes(1, e.target.value, sort)}}/>
            <select className="theme-sort" value={sort} onChange={(e) => {setSort(e.target.value); fetchThemes(1, search, e.target.value)}}>
              <option value="alpha_asc">Alphabetical (A-Z)</option>
              <option value="alpha_desc">Alphabetical (Z-A)</option>
              <option value="date_desc">Newest</option>
              <option value="date_asc">Oldest</option>
              <option value="arg_size_desc">Most Arguments</option>
              <option value="arg_size_asc">Least Arguments</option>
            </select>
          </div>

          <div className="theme-request-section">
            <button className="btn-new" onClick={() => setShowForm(true)}>Request a Theme</button>
          </div>

          {loading && <p className="state-msg">Loading themes…</p>}
          {error && <p className="state-msg error">{error}</p>}
          {!loading && !error && themes.length === 0 && (<p className="state-msg">No themes yet.</p>)}

          {!loading && !error && (
            <>
              <div className="themes-grid">
                {themes.map((theme) => (
                  <div key={theme.id} className="theme-card-wrapper">
                    <button className="theme-card" onClick={() => navigate(`/themes/${theme.id}`)}>
                      <p className="theme-title">{theme.title}</p>
                      {theme.description && (
                        <p className="theme-desc">{theme.description}</p>
                      )}
                      <p className="theme-count">
                        {theme.argument_count} argument{theme.argument_count !== 1 ? 's' : ''}
                      </p>
                    </button>
                    {user?.is_admin && (
                      <button className="btn-delete-theme" onClick={(e) => {e.stopPropagation(); deleteTheme(theme.id)}}>
                        <TrashIcon />
                      </button>
                    )}
                  </div>
                ))}
              </div>
              {pagination && pagination.totalPages > 1 && (
                <div className="pagination">
                  <button className="pagination-btn" onClick={() => fetchThemes(pagination.currentPage - 1)} disabled={!pagination.previous}>
                    Previous
                  </button>
                  <span className="pagination-info">
                    Page {pagination.currentPage} of {pagination.totalPages}
                  </span>
                  <button className="pagination-btn" onClick={() => fetchThemes(pagination.currentPage + 1)} disabled={!pagination.next}>
                    Next
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </main>

      {showForm && (
        <ThemeRequestForm
          onClose={() => setShowForm(false)}
          onSuccess={(newArgId) => {
            setShowForm(false);
            fetchThemes();
          }}
        />
      )}
      {showConfirm && (
        <ConfirmDialog
          message="Are you sure you want to delete this theme?"
          onConfirm={confirmDeleteTheme}
          onCancel={() => {setShowConfirm(false); setConfirmThemeId(null)}}
        />
      )}
    </div>
  );
};

export default ThemesPage;