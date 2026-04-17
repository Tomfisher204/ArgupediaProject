import React, {useState} from 'react';
import {useAuth} from '../context';

const API = 'http://localhost:8000';

const AddSchemeForm = ({onClose, onSuccess}) => {
  const {getValidAccessToken} = useAuth();
  const [form, setForm] = useState({name: '', description: '', template: ''});
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setForm((f) => ({...f, [e.target.name]: e.target.value}));
    setError(null);
  };

  const handleSubmit = async () => {
    if (!form.name.trim()) {setError('Name is required.'); return;}
    if (!form.template.trim()) {setError('Template is required.'); return;}
    setSubmitting(true);
    try {
      const token = await getValidAccessToken();
      const res = await fetch(`${API}/api/admin/schemes/`, {
        method: 'POST',
        headers: {Authorization: `Bearer ${token}`, 'Content-Type': 'application/json'},
        body: JSON.stringify(form),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data?.name?.[0] ?? data?.template?.[0] ?? 'Failed to create scheme.');
      }
      onSuccess();
    }
    catch (err) {
      setError(err.message);
    }
    finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <div className="modal-body">
        <div className="form-field">
          <label className="form-label" htmlFor="scheme-name">Scheme name</label>
          <input
            id="scheme-name"
            name="name"
            type="text"
            className="form-input"
            value={form.name}
            onChange={handleChange}
            placeholder="e.g. Argument from Analogy"
          />
        </div>

        <div className="form-field">
          <label className="form-label" htmlFor="scheme-desc">Description <span className="optional">(optional)</span></label>
          <textarea
            id="scheme-desc"
            name="description"
            className="form-textarea"
            rows={3}
            value={form.description}
            onChange={handleChange}
            placeholder="Brief description of this argument scheme..."
          />
        </div>

        <div className="form-field">
          <label className="form-label" htmlFor="scheme-template">Template</label>
          <textarea
            id="scheme-template"
            name="template"
            className="form-textarea"
            rows={4}
            value={form.template}
            onChange={handleChange}
            placeholder="Template with **field** placeholders..."
          />
        </div>
        {error && <p className="form-error">{error}</p>}
      </div>

      <div className="modal-footer">
        <button className="btn-ghost" onClick={onClose} disabled={submitting}>Cancel</button>
        <button className="btn-submit supporting" onClick={handleSubmit} disabled={submitting}>
          {submitting ? 'Creating...' : 'Create Scheme'}
        </button>
      </div>
    </>
  );
};

export default AddSchemeForm;