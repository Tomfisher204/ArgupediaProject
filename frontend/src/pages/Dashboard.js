import React, {useState, useEffect, useCallback} from 'react';
import {Navigate, useNavigate} from 'react-router-dom';
import {useAuth} from '../context';
import {Navbar} from '../components';
import '../css/pages/Dashboard.css';

const API = 'http://localhost:8000';

const buildPreview = (template, fieldValues) => {
  if (!template) return null;
  return template.replace(/\*\*([^*]+)\*\*/g, (_, key) => {
    const val = fieldValues[key];
    return val && val.trim() ? val : `**${key}**`;
  });
};

const STAT_FIELDS = [
  {label: 'Arguments made', key: 'argument_count'},
  {label: 'Reputation', key: 'reputation', format: v => (v != null ? `${v}/10` : null)},
  {label: 'Win rate', key: 'win_rate', format: v => (v != null ? `${v}%` : null)},
];

const fmt = (value, format) => {
  if (value == null || value === '') return '—';
  return format ? format(value) : value;
};

const Dashboard = () => {
  const {user, loading, getValidAccessToken} = useAuth();
  const navigate = useNavigate();
  const [userArguments, setUserArguments] = useState([]);
  const [argumentsLoading, setArgumentsLoading] = useState(true);
  const [pagination, setPagination] = useState(null);

  const fetchUserArguments = useCallback(async (page = 1) => {
    if (!user) return;
    try {
      setArgumentsLoading(true);
      const token = await getValidAccessToken();
      const response = await fetch(`${API}/api/user/arguments/?page=${page}`, {headers: {Authorization: `Bearer ${token}`}});
      if (!response.ok) {
        return;
      }
      const data = await response.json();
      setUserArguments(data?.results ?? []);
      const count = data?.count ?? 0;
      setPagination({count, next: data?.next ?? null, previous: data?.previous ?? null, currentPage: page, totalPages: Math.max(1, Math.ceil(count / 3))});
    }
    catch (error) {
      if (process.env.NODE_ENV !== 'test') {
        console.error('Failed to fetch user arguments:', error);
      }
    }
    finally {
      setArgumentsLoading(false);
    }
  }, [user, getValidAccessToken]);

  useEffect(() => {
    if (!user) return;
    fetchUserArguments();
  }, [fetchUserArguments, user]);

  if (loading) return <div className="page-loading">Loading…</div>;
  if (!user) return <Navigate to="/" replace />;

  const initial = user.username?.[0]?.toUpperCase() ?? '?';

  return (
    <div className="dashboard">
      <Navbar />
      <main className="dash-main">
        <div className="dash-inner">

          <section className="profile-card">
            <div className="profile-avatar">{initial}</div>
            <div className="profile-info">
              <h1 className="profile-username">{user.username}</h1>
              {user.email && <p className="profile-email">{user.email}</p>}
              {user.date_joined && (
                <p className="profile-joined">
                  Joined{' '}
                  {new Date(user.date_joined).toLocaleDateString('en-GB', {
                    month: 'long',
                    year: 'numeric',
                  })}
                </p>
              )}
            </div>
          </section>

          <section className="stats-section">
            <h2 className="section-heading">Your stats</h2>
            <div className="stats-grid">
              {STAT_FIELDS.map(({label, key, format}) => (
                <div key={key} className="stat-card">
                  <span className="stat-value">{fmt(user[key], format)}</span>
                  <span className="stat-label">{label}</span>
                </div>
              ))}
            </div>
          </section>

          <section className="arguments-section">
            <h2 className="section-heading">Your arguments</h2>
            {argumentsLoading ? (
              <p className="loading-text">Loading your arguments...</p>
            ) : userArguments.length === 0 ? (
              <p className="placeholder-text">
                You haven't created any arguments yet. Visit the Themes page to get started!
              </p>
            ) : (
              <>
                <div className="arguments-list">
                  {userArguments.map(argument => (
                    <div key={argument.id} className="argument-card" onClick={() => navigate(`/arguments/${argument.id}`)}>
                      <div className="argument-header">
                        <span className="argument-theme">{argument.theme}</span>
                        <span className="argument-scheme">{argument.scheme_name}</span>
                      </div>
                      <div className="argument-content">
                        {(() => {
                          const fieldValues = {};
                          argument.field_values.forEach(f => {
                            fieldValues[f.field_name] = f.value;
                          });
                          const preview = buildPreview(argument.scheme_template, fieldValues);
                          return preview ? (
                            <div className="argument-preview">
                              {preview.split(/(\*\*[^*]+\*\*)/g).map((part, i) => {
                                if (part.startsWith('**') && part.endsWith('**'))
                                {
                                  return <strong key={i}>{part.slice(2, -2)}</strong>;
                                }
                                return part;
                              })}
                            </div>
                          ) : (
                            argument.field_values.map((field, i) => (
                              <div key={i} className="argument-field">
                                <strong>{field.field_name}:</strong> {field.value}
                              </div>
                            ))
                          );
                        })()}
                      </div>
                      <div className="argument-footer">
                        <span className="argument-date">
                          {new Date(argument.date_created).toLocaleDateString()}
                        </span>
                        {argument.child_count > 0 && (
                          <span className="argument-responses">
                            {argument.child_count} response
                            {argument.child_count !== 1 ? 's' : ''}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
                {pagination && pagination.totalPages > 1 && (
                  <div className="pagination">
                    <button className="pagination-btn" onClick={() => fetchUserArguments(pagination.currentPage - 1)} disabled={!pagination.previous}>
                      Previous
                    </button>
                    <span className="pagination-info">
                      Page {pagination.currentPage} of {pagination.totalPages}
                    </span>
                    <button className="pagination-btn" onClick={() => fetchUserArguments(pagination.currentPage + 1)} disabled={!pagination.next}>
                      Next
                    </button>
                  </div>
                )}
              </>
            )}
          </section>

        </div>
      </main>
    </div>
  );
};

export default Dashboard;