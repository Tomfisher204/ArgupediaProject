import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import AddArgumentModal from '../components/AddArgumentModal';
import './ThemeArgumentsPage.css';

const ArgumentCard = ({ argument, onClick }) => {
  const title = argument.field_values?.[0]?.value ?? '(no title)';
  return (
    <button className="arg-card" onClick={onClick}>
      <div className="arg-card-meta">
        <span className="arg-scheme">{argument.scheme_name}</span>
      </div>
      <p className="arg-card-title">{title}</p>
      <div className="arg-card-footer">
        <span>by {argument.author}</span>
        <span className="arg-children">
          {argument.child_count} response{argument.child_count !== 1 ? 's' : ''}
        </span>
      </div>
    </button>
  );
};

const ThemeArgumentsPage = () => {
  const { themeId } = useParams();
  const { getValidAccessToken, logout } = useAuth();
  const navigate = useNavigate();
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);
  const [showModal, setShowModal] = useState(false);

  const fetchArguments = async () => {
    try {
      setLoading(true);
      const token = await getValidAccessToken();
      const res = await fetch(`http://localhost:8000/api/themes/${themeId}/arguments/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Failed to load arguments.');
      setData(await res.json());
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchArguments();
  }, [themeId, getValidAccessToken]);

  return (
    <div className="theme-args-page">
      <header className="page-header">
        <div className="page-header-inner">
          <div className="header-logo" onClick={() => navigate('/dashboard')} style={{ cursor: 'pointer' }}>
            <span className="logo-mark-sm">A</span>
            <span className="logo-text-sm">argupedia</span>
          </div>
          <nav className="header-nav">
            <button className="nav-link" onClick={() => navigate('/themes')}>Themes</button>
            {data?.theme && (
              <span className="breadcrumb-sep">/</span>
            )}
            {data?.theme && (
              <button className="nav-link active">{data.theme.title}</button>
            )}
          </nav>
          <button className="logout-btn" onClick={logout}>Log out</button>
        </div>
      </header>

      <main className="page-main">
        <div className="page-inner">

          {loading && <p className="state-msg">Loading arguments…</p>}
          {error   && <p className="state-msg error">{error}</p>}

          {!loading && !error && data && (
            <>
              <div className="page-title-row">
                <h1 className="page-title">{data.theme.title}</h1>
                {data.theme.description && (
                  <p className="page-sub">{data.theme.description}</p>
                )}
                <button className="btn-new" onClick={() => setShowModal(true)}>Add Initial Argument</button>
              </div>

              {data.arguments.length === 0 ? (
                <p className="state-msg">No arguments in this theme yet.</p>
              ) : (
                <div className="args-list">
                  {data.arguments.map((arg) => (
                    <ArgumentCard
                      key={arg.id}
                      argument={arg}
                      onClick={() => navigate(`/arguments/${arg.id}`)}
                    />
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </main>

      {showModal && (
        <AddArgumentModal
          themeId={parseInt(themeId)}
          parentArgumentId={null}
          onClose={() => setShowModal(false)}
          onSuccess={(newArgId) => {
            setShowModal(false);
            fetchArguments();
          }}
        />
      )}
    </div>
  );
};

export default ThemeArgumentsPage;