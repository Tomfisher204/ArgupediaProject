import React, { useState, useEffect } from 'react';
import { Navbar } from '../components';
import '../css/pages/AdminDashboard.css';

const AdminDashboard = () => {
  const [stats, setStats] = useState({});
  const [themeRequests, setThemeRequests] = useState([]);

  useEffect(() => {
    fetchStats();
    fetchThemeRequests();
  }, []);

  const fetchStats = async () => {
    const token = localStorage.getItem('access_token');
    const res = await fetch('http://localhost:8000/api/admin/stats/', {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok) {
      const data = await res.json();
      setStats(data);
    }
  };

  const fetchThemeRequests = async () => {
    const token = localStorage.getItem('access_token');
    const res = await fetch('http://localhost:8000/api/admin/theme-requests/', {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok) {
      const data = await res.json();
      setThemeRequests(data);
    }
  };

  const handleApproveReject = async (requestId, action) => {
    const token = localStorage.getItem('access_token');
    const res = await fetch('http://localhost:8000/api/admin/theme-requests/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ request_id: requestId, action }),
    });
    if (res.ok) {
      fetchThemeRequests(); // Refresh list
      fetchStats(); // Refresh stats
    }
  };

  return (
    <div className="admin-dashboard">
      <Navbar />
      <main className="page-main">
        <div className="page-inner">
          <h1>Admin Dashboard</h1>
          <div className="stats">
            <h2>Statistics</h2>
            <p>Total Users: {stats.total_users}</p>
            <p>Total Arguments: {stats.total_arguments}</p>
            <p>Total Themes: {stats.total_themes}</p>
            <p>Pending Theme Requests: {stats.pending_theme_requests}</p>
          </div>
          <div className="theme-requests">
            <h2>Theme Requests</h2>
            {themeRequests.map((req) => (
              <div key={req.id} className="request-card">
                <h3>{req.title}</h3>
                <p>{req.description}</p>
                <p>Reason: {req.reason}</p>
                <p>Requested by: {req.requested_by.username}</p>
                <p>Status: {req.status}</p>
                {req.status === 'pending' && (
                  <div>
                    <button onClick={() => handleApproveReject(req.id, 'approve')}>Approve</button>
                    <button onClick={() => handleApproveReject(req.id, 'reject')}>Reject</button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
};

export default AdminDashboard;