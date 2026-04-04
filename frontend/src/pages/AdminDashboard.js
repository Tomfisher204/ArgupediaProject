import React, { useState, useEffect, useCallback } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Navbar } from '../components';
import '../css/pages/AdminDashboard.css';

const buildPreview = (template, fieldValues) => {
  if (!template) return null;
  return template.replace(/\*\*([^*]+)\*\*/g, (_, key) => {
    const val = fieldValues[key];
    return val && val.trim() ? val : `**${key}**`;
  });
};

const formatPreview = (preview) => {
  if (!preview) return null;
  return preview.split(/(\*\*[^*]+\*\*)/g).map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }
    return part;
  });
};

const ADMIN_STAT_FIELDS = [
  { label: 'Total Users', key: 'total_users' },
  { label: 'Total Arguments', key: 'total_arguments' },
  { label: 'Total Themes', key: 'total_themes' },
  { label: 'Pending Theme Requests', key: 'pending_theme_requests' },
];

const AdminDashboard = () => {
  const { user, loading, getValidAccessToken } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({});
  const [themeRequests, setThemeRequests] = useState([]);
  const [requestsLoading, setRequestsLoading] = useState(true);
  const [pagination, setPagination] = useState(null);
  const [reportedArgs, setReportedArgs] = useState([]);
  const [reportedLoading, setReportedLoading] = useState(true);
  const [reportedPagination, setReportedPagination] = useState(null);
  const [selectedRequest, setSelectedRequest] = useState(null);

  const fetchStats = async () => {
    const token = await getValidAccessToken();
    const res = await fetch('http://localhost:8000/api/admin/stats/', {headers: { Authorization: `Bearer ${token}` }});
    if (res.ok) {
      const data = await res.json();
      setStats(data);
    }
  };

  const fetchThemeRequests = useCallback(async (page = 1) => {
    if (!user) return;
    try {
      setRequestsLoading(true);
      const token = await getValidAccessToken();
      const response = await fetch(`http://localhost:8000/api/admin/theme-requests/?page=${page}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setThemeRequests(data.results);
        setPagination({count: data.count, next: data.next, previous: data.previous, currentPage: page, totalPages: Math.ceil(data.count / 3)});
      }
    } 
    catch (error) {
      console.error('Failed to fetch theme requests:', error);
    } 
    finally {
      setRequestsLoading(false);
    }
  }, [user, getValidAccessToken]);

  const fetchReportedArgs = useCallback(async (page = 1) => {
    if (!user) return;
    try {
      setReportedLoading(true);
      const token = await getValidAccessToken();
      const response = await fetch(`http://localhost:8000/api/admin/reported-arguments/?page=${page}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setReportedArgs(data.results);
        setReportedPagination({count: data.count, next: data.next, previous: data.previous, currentPage: page, totalPages: Math.ceil(data.count / 3)});
      }
    } 
    catch (error) {
      console.error('Failed to fetch reported arguments:', error);
    } 
    finally {
      setReportedLoading(false);
    }
  }, [user, getValidAccessToken]);

  useEffect(() => {fetchThemeRequests()}, [fetchThemeRequests]);

  useEffect(() => {fetchReportedArgs()}, [fetchReportedArgs]);

  useEffect(() => {
    fetchStats();
  }, []);
  const handleApproveReject = async (requestId, action) => {
    const token = await getValidAccessToken();
    const res = await fetch('http://localhost:8000/api/admin/theme-requests/', {method: 'POST', headers: {'Content-Type': 'application/json', Authorization: `Bearer ${token}`}, body: JSON.stringify({ request_id: requestId, action })});
    if (res.ok) {
      fetchThemeRequests(pagination?.currentPage || 1);
      fetchStats();
    }
  };

  const initial = user.username?.[0]?.toUpperCase() ?? '?';

  if (loading) return <div className="page-loading">Loading…</div>;
  if (!user) return <Navigate to="/" replace />;

  return (
    <div className="dashboard">
      <Navbar />
      <main className="dash-main">
        <div className="dash-inner">

          {/* Admin header */}
          <section className="admin-header">
            <h1>Admin Dashboard</h1>
          </section>

          <section className="stats-section">
            <h2 className="section-heading">Statistics</h2>
            <div className="stats-grid">
              {ADMIN_STAT_FIELDS.map(({ label, key }) => (
                <div key={key} className="stat-card">
                  <span className="stat-value">{stats[key] || 0}</span>
                  <span className="stat-label">{label}</span>
                </div>
              ))}
            </div>
          </section>

          {/* Theme requests */}
          <section className="theme-requests-section">
            <h2 className="section-heading">Pending Theme Requests</h2>
            {requestsLoading ? (
              <p className="loading-text">Loading pending theme requests...</p>
            ) : themeRequests.length === 0 ? (
              <p className="placeholder-text">No pending theme requests at the moment.</p>
            ) : (
              <>
                <div className="theme-requests-list">
                  {themeRequests.map((req) => (
                    <div key={req.id} className="request-card" onClick={() => setSelectedRequest(req)}>
                      <div className="request-header">
                        <span className="request-title">{req.title}</span>
                        <span className={`request-status ${req.status}`}>{req.status}</span>
                      </div>
                    </div>
                  ))}
                </div>

                {pagination && pagination.totalPages > 1 && (
                  <div className="pagination">
                    <button
                      className="pagination-btn"
                      onClick={() => fetchThemeRequests(pagination.currentPage - 1)}
                      disabled={!pagination.previous}
                    >
                      Previous
                    </button>
                    <span className="pagination-info">
                      Page {pagination.currentPage} of {pagination.totalPages}
                    </span>
                    <button
                      className="pagination-btn"
                      onClick={() => fetchThemeRequests(pagination.currentPage + 1)}
                      disabled={!pagination.next}
                    >
                      Next
                    </button>
                  </div>
                )}
              </>
            )}
          </section>

          {/* Reported arguments */}
          <section className="reported-arguments-section">
            <h2 className="section-heading">Reported Arguments</h2>
            {reportedLoading ? (
              <p className="loading-text">Loading reported arguments...</p>
            ) : reportedArgs.length === 0 ? (
              <p className="placeholder-text">No reported arguments at the moment.</p>
            ) : (
              <>
                <div className="reported-arguments-list">
                  {reportedArgs.map((arg) => {
                    const fieldValues = {};
                    arg.field_values.forEach((fv) => {
                      fieldValues[fv.field_name] = fv.value;
                    });
                    const preview = buildPreview(arg.scheme_template, fieldValues);
                    return (
                      <div
                        key={arg.id}
                        className="reported-card"
                        onClick={() => navigate(`/arguments/${arg.id}`)}
                      >
                        <div className="reported-header">
                          <span className="reported-scheme">{arg.scheme_name}</span>
                          <span className="reported-reports">{arg.report_count} reports</span>
                        </div>
                        <div className="reported-content">
                          {preview ? (
                            <div className="reported-preview">{formatPreview(preview)}</div>
                          ) : (
                            arg.field_values.map((fv, i) => (
                              <div key={i} className="reported-field">
                                <strong>{fv.field_name}:</strong> {fv.value}
                              </div>
                            ))
                          )}
                        </div>
                        <div className="reported-footer">
                          <span className="reported-author">by {arg.author}</span>
                          <span className="reported-theme">{arg.theme}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {reportedPagination && reportedPagination.totalPages > 1 && (
                  <div className="pagination">
                    <button
                      className="pagination-btn"
                      onClick={() => fetchReportedArgs(reportedPagination.currentPage - 1)}
                      disabled={!reportedPagination.previous}
                    >
                      Previous
                    </button>
                    <span className="pagination-info">
                      Page {reportedPagination.currentPage} of {reportedPagination.totalPages}
                    </span>
                    <button
                      className="pagination-btn"
                      onClick={() => fetchReportedArgs(reportedPagination.currentPage + 1)}
                      disabled={!reportedPagination.next}
                    >
                      Next
                    </button>
                  </div>
                )}
              </>
            )}
          </section>

          {selectedRequest && (
            <div className="modal-overlay" onClick={() => setSelectedRequest(null)}>
              <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                  <h3>{selectedRequest.title}</h3>
                  <button className="modal-close" onClick={() => setSelectedRequest(null)}>×</button>
                </div>
                <div className="modal-body">
                  <p><strong>Description:</strong> {selectedRequest.description}</p>
                  <p><strong>Reason:</strong> {selectedRequest.reason}</p>
                  <p><strong>Requested by:</strong> {selectedRequest.requested_by.username}</p>
                  <p><strong>Status:</strong> {selectedRequest.status}</p>
                  <p><strong>Date:</strong> {new Date(selectedRequest.date_created).toLocaleDateString()}</p>
                  {selectedRequest.status === 'pending' && (
                    <div className="modal-actions">
                      <button onClick={() => { handleApproveReject(selectedRequest.id, 'approve'); setSelectedRequest(null); }}>Approve</button>
                      <button onClick={() => { handleApproveReject(selectedRequest.id, 'reject'); setSelectedRequest(null); }}>Reject</button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default AdminDashboard;