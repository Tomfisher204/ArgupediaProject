import React, {useEffect, useState, useCallback} from 'react';
import {useNavigate, useParams} from 'react-router-dom';
import {useAuth} from '../context/AuthContext';
import { AddArgumentModal, Navbar } from '../components';
import '../css/pages/ThemeArgumentsPage.css';

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

const ArgumentCard = ({ argument, onClick }) => {
  const fieldValues = {};
  argument.field_values?.forEach(field => {
    fieldValues[field.field_name] = field.value;
  });
  const preview = buildPreview(argument.scheme_template, fieldValues);
  const title = preview ? formatPreview(preview) : (argument.field_values?.[0]?.value ?? '(no title)');
  return (
    <button className="arg-card" onClick={onClick}>
      <div className="arg-card-meta">
        <span className="arg-scheme">{argument.scheme_name}</span>
      </div>
      <p className="arg-card-title">{title}</p>
      <div className="arg-card-footer">
        <span>by {argument.author}</span>
        <span className="arg-children">
          {argument.child_count} response{argument.child_count !== 1 ? 's' : ''}
        </span>
      </div>
    </button>
  );
};

const ThemeArgumentsPage = () => {
  const {themeId} = useParams();
  const {getValidAccessToken} = useAuth();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const fetchArguments = useCallback(async (page = 1) => {
    try {
      setLoading(true);
      const token = await getValidAccessToken();
      const res = await fetch(`http://localhost:8000/api/themes/${themeId}/arguments/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Failed to load arguments.');
      setData(await res.json());
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [themeId, getValidAccessToken]);

  useEffect(() => {fetchArguments()}, [fetchArguments]);

  return (
    <div className="theme-args-page">
      <Navbar />
      <main className="page-main">
        <div className="page-inner">

          {loading && <p className="state-msg">Loading arguments…</p>}
          {error && <p className="state-msg error">{error}</p>}

          {!loading && !error && data && (
            <>
              <div className="page-title-row">
                <h1 className="page-title">{data.theme.title}</h1>
                {data.theme.description && (
                  <p className="page-sub">{data.theme.description}</p>
                )}
                <div className="initial-argument-section">
                  <button className="btn-new" onClick={() => setShowModal(true)}>Add Initial Argument</button>
                </div>
              </div>

              {data.arguments.length === 0 ? (
                <p className="state-msg">No arguments in this theme yet.</p>
              ) : (
                <div className="args-list">
                  {data.arguments.map((arg) => (<ArgumentCard key={arg.id} argument={arg} onClick={() => navigate(`/arguments/${arg.id}`)}/>))}
                </div>
              )}
            </>
          )}
        </div>
      </main>

      {showModal && (
        <AddArgumentModal
          themeId={parseInt(themeId)}
          parentArgumentId={null}
          onClose={() => setShowModal(false)}
          onSuccess={(newArgId) => {
            setShowModal(false);
            fetchArguments();
          }}
        />
      )}
    </div>
  );
};

export default ThemeArgumentsPage;