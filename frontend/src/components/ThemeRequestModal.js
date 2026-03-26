import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import './ThemeRequestModal.css';

const API = 'http://localhost:8000';

const ThemeRequestModal = ({ onClose, onSuccess }) => {
  const { getValidAccessToken } = useAuth();
  const [form, setForm]         = useState({ title: '', description: '', reason: '' });
  const [submitting, setSubmit] = useState(false);
  const [error, setError]       = useState(null);

  const handleChange = (e) => {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));
    setError(null);
  };

  const handleSubmit = async () => {
    if (!form.title.trim())  { setError('Title is required.'); return; }
    if (!form.reason.trim()) { setError('Please explain why this theme should be added.'); return; }

    setSubmit(true);
    try {
      const token = await getValidAccessToken();
      const res = await fetch(`${API}/api/theme-requests/`, {
        method:  'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body:    JSON.stringify(form),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data?.title?.[0] ?? data?.reason?.[0] ?? 'Submission failed.');
      }
      onSuccess();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmit(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal modal-sm">

        <div className="modal-header">
          <h2 className="modal-title">Request a theme</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          <p className="request-intro">
            Don't see a theme that fits your argument? Request one — admins will review it.
          </p>

          <div className="form-field">
            <label className="form-label" htmlFor="req-title">Theme title</label>
            <input
              id="req-title"
              name="title"
              type="text"
              className="form-input"
              value={form.title}
              onChange={handleChange}
              placeholder="e.g. Climate Policy"
            />
          </div>

          <div className="form-field">
            <label className="form-label" htmlFor="req-desc">Description <span className="optional">(optional)</span></label>
            <textarea
              id="req-desc"
              name="description"
              className="form-textarea"
              rows={2}
              value={form.description}
              onChange={handleChange}
              placeholder="Brief description of this theme…"
            />
          </div>

          <div className="form-field">
            <label className="form-label" htmlFor="req-reason">Why should this be added?</label>
            <textarea
              id="req-reason"
              name="reason"
              className="form-textarea"
              rows={3}
              value={form.reason}
              onChange={handleChange}
              placeholder="Explain why this theme would be valuable…"
            />
          </div>

          {error && <p className="form-error">{error}</p>}
        </div>

        <div className="modal-footer">
          <button className="btn-ghost" onClick={onClose} disabled={submitting}>Cancel</button>
          <button className="btn-submit supporting" onClick={handleSubmit} disabled={submitting}>
            {submitting ? 'Submitting…' : 'Submit request'}
          </button>
        </div>

      </div>
    </div>
  );
};

export default ThemeRequestModal;