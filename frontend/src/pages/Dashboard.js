import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './Dashboard.css';

const RECENT_ARGUMENTS = [
  { id: 1, title: 'Universal Basic Income would reduce economic inequality', tag: 'Economics', stance: 'For', votes: 142, replies: 24, status: 'active' },
  { id: 2, title: 'Open-source AI models pose greater safety risks than closed ones', tag: 'Technology', stance: 'Against', votes: 98, replies: 18, status: 'active' },
  { id: 3, title: 'Ranked-choice voting improves democratic outcomes', tag: 'Politics', stance: 'For', votes: 207, replies: 31, status: 'closed' },
  { id: 4, title: 'Space exploration funding should be privatised', tag: 'Science', stance: 'For', votes: 64, replies: 12, status: 'active' },
  { id: 5, title: 'Social media does more harm than good for teenagers', tag: 'Society', stance: 'Against', votes: 183, replies: 45, status: 'active' },
];

const USER_STATS = [
  { label: 'Arguments made', value: '[ user_arg_count ]' },
  { label: 'Total votes received', value: '[ user_vote_count ]' },
  { label: 'Win rate', value: '[ user_win_rate ]' },
  { label: 'Reputation', value: '[ user_reputation ]' },
];

const TAGS = ['All', 'Economics', 'Technology', 'Politics', 'Science', 'Society', 'Philosophy'];

const Dashboard = () => {
  const [activeTag, setActiveTag] = useState('All');
  const [sortBy, setSortBy] = useState('recent');

  const filtered = RECENT_ARGUMENTS.filter(
    (a) => activeTag === 'All' || a.tag === activeTag
  );

  return (
    <div className="dashboard">

      {/* Welcome strip */}
      <div className="dashboard-welcome">
        <div className="dashboard-inner">
          <div className="welcome-text">
            <h1 className="welcome-title">Welcome back, <em>[ username ]</em></h1>
            <p className="welcome-sub">Here's what's happening on Argupedia today.</p>
          </div>
          <Link to="/new-argument" className="cta-primary">+ New argument</Link>
        </div>
      </div>

      <div className="dashboard-body">
        <div className="dashboard-inner">
          <div className="dashboard-grid">

            {/* Main feed */}
            <main className="feed">
              <div className="feed-toolbar">
                <div className="tag-filters">
                  {TAGS.map((tag) => (
                    <button
                      key={tag}
                      className={`tag-btn ${activeTag === tag ? 'active' : ''}`}
                      onClick={() => setActiveTag(tag)}
                    >
                      {tag}
                    </button>
                  ))}
                </div>
                <select
                  className="sort-select"
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                >
                  <option value="recent">Most recent</option>
                  <option value="votes">Most voted</option>
                  <option value="replies">Most discussed</option>
                </select>
              </div>

              <div className="argument-feed">
                {filtered.map((arg) => (
                  <Link key={arg.id} to={`/argument/${arg.id}`} className="feed-card">
                    <div className="feed-card-meta">
                      <span className="arg-tag">{arg.tag}</span>
                      <span className={`arg-stance ${arg.stance.toLowerCase()}`}>{arg.stance}</span>
                      {arg.status === 'closed' && <span className="status-closed">Closed</span>}
                    </div>
                    <h3 className="feed-card-title">{arg.title}</h3>
                    <div className="feed-card-stats">
                      <span>↑ {arg.votes}</span>
                      <span>💬 {arg.replies} replies</span>
                    </div>
                  </Link>
                ))}

                {filtered.length === 0 && (
                  <div className="empty-state">
                    <p>No arguments in this category yet.</p>
                    <Link to="/new-argument" className="cta-primary" style={{ marginTop: 12, display: 'inline-flex' }}>
                      Start one →
                    </Link>
                  </div>
                )}
              </div>
            </main>

            {/* Sidebar */}
            <aside className="sidebar">

              {/* User stats */}
              <div className="sidebar-card">
                <div className="sidebar-user-header">
                  <div className="sidebar-avatar">U</div>
                  <div>
                    <p className="sidebar-username">[ username ]</p>
                    <p className="sidebar-handle">@[ user_handle ]</p>
                  </div>
                </div>
                <div className="user-stats-grid">
                  {USER_STATS.map((stat) => (
                    <div key={stat.label} className="user-stat">
                      <span className="user-stat-value">{stat.value}</span>
                      <span className="user-stat-label">{stat.label}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Activity */}
              <div className="sidebar-card">
                <h3 className="sidebar-heading">Recent activity</h3>
                <div className="activity-list">
                  {['[ activity_item_1 ]', '[ activity_item_2 ]', '[ activity_item_3 ]'].map((item, i) => (
                    <div key={i} className="activity-item">
                      <span className="activity-dot" />
                      <span className="activity-text">{item}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Trending tags */}
              <div className="sidebar-card">
                <h3 className="sidebar-heading">Trending topics</h3>
                <div className="trending-tags">
                  {['Economics', 'AI Policy', 'Climate', 'Healthcare', 'Education'].map((t) => (
                    <button
                      key={t}
                      className="trending-tag"
                      onClick={() => setActiveTag(t === 'AI Policy' ? 'Technology' : t)}
                    >
                      #{t}
                    </button>
                  ))}
                </div>
              </div>
            </aside>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;