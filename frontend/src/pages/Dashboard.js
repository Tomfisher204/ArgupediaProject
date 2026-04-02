import React, { useState, useEffect, useCallback } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import './Dashboard.css';

const STAT_FIELDS = [
  { label: 'Arguments made', key: 'argument_count' },
  { label: 'Reputation', key: 'reputation' },
  { label: 'Win rate', key: 'win_rate', format: (v) => (v != null ? `${v}%` : null) },
];

const fmt = (value, format) => {
  if (value == null || value === '') return '—';
  return format ? format(value) : value;
};

const Dashboard = () => {
  const { user, loading, getValidAccessToken } = useAuth();
  const navigate = useNavigate();
  const [userArguments, setUserArguments] = useState([]);
  const [argumentsLoading, setArgumentsLoading] = useState(true);
  const [pagination, setPagination] = useState(null);
  
  const fetchUserArguments = useCallback(async (page = 1) => {
    if (!user) return;
    try {
      setArgumentsLoading(true);
      const token = await getValidAccessToken();
      const response = await fetch(`http://localhost:8000/api/user/arguments/?page=${page}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setUserArguments(data.results);
        setPagination({count: data.count, next: data.next, previous: data.previous, currentPage: page, totalPages: Math.ceil(data.count / 3)});
      }
    } 
    catch (error) {
      console.error('Failed to fetch user arguments:', error);
    } 
    finally {
      setArgumentsLoading(false);
    }
  }, [user, getValidAccessToken]);

  useEffect(() => {fetchUserArguments()}, [fetchUserArguments]);
  
  if (loading) return <div className="page-loading">Loading…</div>;
  if (!user) return <Navigate to="/" replace />;

  const initial = user.username?.[0]?.toUpperCase() ?? '?';

  return (
    <div className="dashboard">
      <Navbar />
      <main className="dash-main">
        <div className="dash-inner">
          {/* Profile card */}
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

          {/* Stats grid */}
          <section className="stats-section">
            <h2 className="section-heading">Your stats</h2>
            <div className="stats-grid">
              {STAT_FIELDS.map(({ label, key, format }) => (
                <div key={key} className="stat-card">
                  <span className="stat-value">{fmt(user[key], format)}</span>
                  <span className="stat-label">{label}</span>
                </div>
              ))}
            </div>
          </section>

          {/* User's arguments */}
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
                  {userArguments.map((argument) => (
                    <div
                      key={argument.id}
                      className="argument-card"
                      onClick={() => navigate(`/arguments/${argument.id}`)}
                    >
                      <div className="argument-header">
                        <span className="argument-theme">{argument.theme}</span>
                        <span className="argument-scheme">{argument.scheme_name}</span>
                      </div>
                      <div className="argument-content">
                        {argument.field_values.map((field, index) => (
                          <div key={index} className="argument-field">
                            <strong>{field.field_name}:</strong> {field.value}
                          </div>
                        ))}
                      </div>
                      <div className="argument-footer">
                        <span className="argument-date">
                          {new Date(argument.date_created).toLocaleDateString()}
                        </span>
                        {argument.child_count > 0 && (
                          <span className="argument-responses">
                            {argument.child_count} response{argument.child_count !== 1 ? 's' : ''}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                {pagination && pagination.totalPages > 1 && (
                  <div className="pagination">
                    <button
                      className="pagination-btn"
                      onClick={() => fetchUserArguments(pagination.currentPage - 1)}
                      disabled={!pagination.previous}
                    >
                      Previous
                    </button>
                    <span className="pagination-info">
                      Page {pagination.currentPage} of {pagination.totalPages}
                    </span>
                    <button
                      className="pagination-btn"
                      onClick={() => fetchUserArguments(pagination.currentPage + 1)}
                      disabled={!pagination.next}
                    >
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