import React, {useState} from 'react';
import {useAuth} from '../context';

const API = 'http://localhost:8000';

const AddCriticalQuestionForm = ({schemeId, onClose, onSuccess}) => {
  const {getValidAccessToken} = useAuth();

  const [form, setForm] = useState({
    question: '',
    two_way: false,
  });

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const {name, value, type, checked} = e.target;
    setForm((f) => ({
      ...f,
      [name]: type === 'checkbox' ? checked : value,
    }));
    setError(null);
  };

  const handleSubmit = async () => {
    if (!form.question.trim()) {
      setError('Question is required.');
      return;
    }

    setSubmitting(true);

    try {
      const token = await getValidAccessToken();
      const res = await fetch(`${API}/api/admin/critical-questions/`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...form,
          scheme_id: schemeId,
        }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(
          data?.question?.[0] ?? 'Failed to create critical question.'
        );
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
          <label className="form-label" htmlFor="cq-question">
            Critical question
          </label>
          <textarea
            id="cq-question"
            name="question"
            className="form-textarea"
            rows={3}
            value={form.question}
            onChange={handleChange}
            placeholder="Enter the critical question..."
          />
        </div>

        <div className="form-field">
          <label className="form-checkbox">
            Is it two-way?
            <input
              type="checkbox"
              name="two_way"
              checked={form.two_way}
              onChange={handleChange}
            />
          </label>
        </div>
        {error && <p className="form-error">{error}</p>}
      </div>

      <div className="modal-footer">
        <button className="btn-ghost" onClick={onClose} disabled={submitting}>
          Cancel
        </button>
        <button className="btn-submit supporting" onClick={handleSubmit} disabled={submitting}>
          {submitting ? 'Creating...' : 'Create Question'}
        </button>
      </div>
    </>
  );
};

export default AddCriticalQuestionForm;