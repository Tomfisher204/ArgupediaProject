import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Dashboard.css';

// Stat cards — map user fields to display labels.
// Update the `key` values to match whatever your /api/auth/me/ endpoint returns.
const STAT_FIELDS = [
  { label: 'Arguments made', key: 'argument_count' },
  { label: 'Votes received',  key: 'vote_count' },
  { label: 'Reputation',      key: 'reputation' },
  { label: 'Win rate',        key: 'win_rate', format: (v) => v != null ? `${v}%` : null },
];

const fmt = (value, format) => {
  if (value == null || value === '') return '—';
  return format ? format(value) : value;
};

const Dashboard = () => {
  const { user, loading, logout } = useAuth();

  if (loading) return <div className="page-loading">Loading…</div>;
  if (!user)   return <Navigate to="/" replace />;

  const initial = user.username?.[0]?.toUpperCase() ?? '?';

  return (
    <div className="dashboard">

      {/* Top bar */}
      <header className="dash-header">
        <div className="dash-header-inner">
          <div className="dash-logo">
            <span className="logo-mark-sm">A</span>
            <span className="logo-text-sm">argupedia</span>
          </div>
          <button className="logout-btn" onClick={logout}>Log out</button>
        </div>
      </header>

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
                  Joined {new Date(user.date_joined).toLocaleDateString('en-GB', { month: 'long', year: 'numeric' })}
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

          {/* Placeholder for future sections */}
          <section className="placeholder-section">
            <p className="placeholder-text">Your arguments will appear here.</p>
          </section>

        </div>
      </main>

    </div>
  );
};

export default Dashboard;