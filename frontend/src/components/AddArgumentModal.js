import React, { useEffect, useState, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import './AddArgumentModal.css';

const API = 'http://localhost:8000';

// Interpolates a scheme template string with current field values
// e.g. "In scenario {S}, action {A} is justified." + {S: 'war', A: 'retaliate'}
// => "In scenario war, action retaliate is justified."
const buildPreview = (template, fieldValues) => {
  if (!template) return null;
  return template.replace(/\{(\w+)\}/g, (_, key) => {
    const val = fieldValues[key];
    return val && val.trim() ? val : `{${key}}`;
  });
};

const AddArgumentModal = ({
  themeId,
  parentArgumentId = null,   // null = initial argument
  attackingDefault = true,   // only used when parentArgumentId is set
  onClose,
  onSuccess,
}) => {
  const { getValidAccessToken } = useAuth();

  const [schemes, setSchemes] = useState([]);
  const [selectedScheme, setSelected] = useState(null);
  const [fieldValues, setFieldValues] = useState({});
  const [selectedCQ, setSelectedCQ] = useState('');
  const [attacking, setAttacking] = useState(attackingDefault);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [loadingSchemes, setLoading] = useState(true);

  const isResponse = parentArgumentId !== null;

  // Load schemes
  useEffect(() => {
    const load = async () => {
      try {
        const token = await getValidAccessToken();
        const res = await fetch(`${API}/api/schemes/`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error('Failed to load schemes.');
        const data = await res.json();
        setSchemes(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [getValidAccessToken]);

  const handleSchemeChange = useCallback((schemeId) => {
    const scheme = schemes.find((s) => s.id === parseInt(schemeId));
    setSelected(scheme || null);
    setFieldValues({});
    setSelectedCQ('');
    setError(null);
  }, [schemes]);

  const handleFieldChange = (fieldName, value) => {
    setFieldValues((prev) => ({ ...prev, [fieldName]: value }));
  };

  const handleSubmit = async () => {
    if (!selectedScheme) { setError('Please select a scheme.'); return; }
    if (isResponse && !selectedCQ) { setError('Please select a critical question.'); return; }

    // Build field_values array using field IDs
    const fvArray = selectedScheme.fields.map((f) => ({
      scheme_field_id: f.id,
      value: fieldValues[f.name] || '',
    }));

    const payload = {
      scheme_id:   selectedScheme.id,
      theme_id:    themeId,
      field_values: fvArray,
      ...(isResponse && {
        parent_argument_id:   parentArgumentId,
        critical_question_id: parseInt(selectedCQ),
        attacking,
      }),
    };

    setSubmitting(true);
    setError(null);
    try {
      const token = await getValidAccessToken();
      const res = await fetch(`${API}/api/arguments/create/`, {
        method:  'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body:    JSON.stringify(payload),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(JSON.stringify(data));
      }
      const result = await res.json();
      onSuccess(result.id);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const preview = selectedScheme
    ? buildPreview(selectedScheme.template, fieldValues)
    : null;

  return (
    <div className="modal-backdrop" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal">

        <div className="modal-header">
          <h2 className="modal-title">
            {isResponse ? (attacking ? 'Add attack' : 'Add support') : 'Add initial argument'}
          </h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">

          {/* Scheme selector */}
          <div className="form-field">
            <label className="form-label">Argument scheme</label>
            {loadingSchemes ? (
              <p className="hint">Loading schemes…</p>
            ) : (
              <select
                className="form-select"
                value={selectedScheme?.id ?? ''}
                onChange={(e) => handleSchemeChange(e.target.value)}
              >
                <option value="">Select a scheme…</option>
                {schemes.map((s) => (
                  <option key={s.id} value={s.id}>{s.name}</option>
                ))}
              </select>
            )}
            {selectedScheme?.description && (
              <p className="hint">{selectedScheme.description}</p>
            )}
          </div>

          {/* Critical question (responses only) */}
          {isResponse && selectedScheme && (
            <div className="form-field">
              <label className="form-label">Critical question</label>
              <select
                className="form-select"
                value={selectedCQ}
                onChange={(e) => setSelectedCQ(e.target.value)}
              >
                <option value="">Select a critical question…</option>
                {selectedScheme.critical_questions.map((cq) => (
                  <option key={cq.id} value={cq.id}>{cq.question}</option>
                ))}
              </select>
            </div>
          )}

          {/* Attacking / supporting toggle (responses only) */}
          {isResponse && (
            <div className="form-field">
              <label className="form-label">This argument is…</label>
              <div className="toggle-row">
                <button
                  className={`toggle-btn attacking ${attacking ? 'active' : ''}`}
                  onClick={() => setAttacking(true)}
                  type="button"
                >
                  Attacking
                </button>
                <button
                  className={`toggle-btn supporting ${!attacking ? 'active' : ''}`}
                  onClick={() => setAttacking(false)}
                  type="button"
                >
                  Supporting
                </button>
              </div>
            </div>
          )}

          {/* Dynamic fields + preview */}
          {selectedScheme && selectedScheme.fields.length > 0 && (
            <div className="fields-and-preview">

              {/* Left: inputs */}
              <div className="fields-col">
                <p className="col-heading">Fill in the fields</p>
                {selectedScheme.fields.map((field) => (
                  <div key={field.id} className="form-field">
                    <label className="form-label">{field.name}</label>
                    <textarea
                      className="form-textarea"
                      rows={2}
                      value={fieldValues[field.name] || ''}
                      onChange={(e) => handleFieldChange(field.name, e.target.value)}
                      placeholder={`Enter ${field.name}…`}
                    />
                  </div>
                ))}
              </div>

              {/* Right: preview */}
              <div className="preview-col">
                <p className="col-heading">Preview</p>
                <div className="preview-card">
                  <div className="preview-card-top">
                    <span className="preview-scheme">{selectedScheme.name}</span>
                  </div>
                  {preview ? (
                    <p className="preview-text">{preview}</p>
                  ) : (
                    <div className="preview-fields">
                      {selectedScheme.fields.map((field) => (
                        <div key={field.id} className="preview-field-row">
                          <span className="preview-field-name">{field.name}</span>
                          <span className="preview-field-value">
                            {fieldValues[field.name] || <em className="placeholder-em">not filled</em>}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

            </div>
          )}

          {error && <p className="form-error">{error}</p>}
        </div>

        <div className="modal-footer">
          <button className="btn-ghost" onClick={onClose} disabled={submitting}>Cancel</button>
          <button
            className={`btn-submit ${attacking && isResponse ? 'attacking' : 'supporting'}`}
            onClick={handleSubmit}
            disabled={submitting || !selectedScheme}
          >
            {submitting ? 'Submitting…' : 'Submit argument'}
          </button>
        </div>

      </div>
    </div>
  );
};

export default AddArgumentModal;