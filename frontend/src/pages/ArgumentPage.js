import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import AddArgumentModal from '../components/AddArgumentModal';
import './ArgumentPage.css';

const ChildCard = ({ link, onClick }) => {
  const title = link.argument.field_values?.[0]?.value ?? '(no title)';
  return (
    <button className={`child-card ${link.attacking ? 'attacking' : 'supporting'}`} onClick={onClick}>
      <p className="child-question">"{link.question}"</p>
      <p className="child-title">{title}</p>
      <div className="child-meta">
        <span>by {link.argument.author}</span>
        {link.argument.child_count > 0 && (
          <span>{link.argument.child_count} response{link.argument.child_count !== 1 ? 's' : ''}</span>
        )}
      </div>
    </button>
  );
};

const ArgumentPage = () => {
  const { '*': path } = useParams();
  const { getValidAccessToken, logout } = useAuth();
  const navigate = useNavigate();
  const [argument, setArgument] = useState(null);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState(null);
  const [showModal, setShowModal] = useState(false);

  const argumentIds = path ? path.split('/').filter(id => id) : [];
  const currentArgumentId = argumentIds[argumentIds.length - 1];

  const buildBreadcrumbs = (arg) => {
    if (!arg) return [];
    const breadcrumbs = [
      { label: 'Themes', path: '/themes' },
      { label: arg.theme, path: `/themes/${arg.theme_id}` },
    ];
    argumentIds.forEach((id, index) => {
      const argPath = argumentIds.slice(0, index + 1).join('/');
      const isCurrent = index === argumentIds.length - 1;
      const title = isCurrent && arg
        ? (arg.field_values?.[0]?.value ?? 'Argument')
        : `Argument ${id}`;
      breadcrumbs.push({
        label: title.length > 20 ? title.substring(0, 20) + '...' : title,
        path: `/arguments/${argPath}`,
        isCurrent,
      });
    });
    return breadcrumbs;
  };

  console.log(argument?.scheme_id);
  const breadcrumbs = buildBreadcrumbs(argument);

  const fetchArgument = async () => {
    if (!currentArgumentId) return;
    try {
      setLoading(true);
      const token = await getValidAccessToken();
      const res = await fetch(`http://localhost:8000/api/arguments/${currentArgumentId}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Failed to load argument.');
      setArgument(await res.json());
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchArgument();
  }, [currentArgumentId, getValidAccessToken]);

  return (
    <div className="argument-page">
      <header className="page-header">
        <div className="page-header-inner">
          <div className="header-logo" onClick={() => navigate('/dashboard')} style={{ cursor: 'pointer' }}>
            <span className="logo-mark-sm">A</span>
            <span className="logo-text-sm">argupedia</span>
          </div>
          <nav className="header-nav">
            {breadcrumbs.map((crumb, index) => (
              <React.Fragment key={crumb.path}>
                {index > 0 && <span className="breadcrumb-sep">/</span>}
                <button
                  className={`nav-link ${crumb.isCurrent ? 'active' : ''}`}
                  onClick={() => navigate(crumb.path)}
                  disabled={crumb.isCurrent}
                >
                  {crumb.label}
                </button>
              </React.Fragment>
            ))}
          </nav>
          <button className="logout-btn" onClick={logout}>Log out</button>
        </div>
      </header>

      <main className="page-main">
        <div className="page-inner">

          {loading && <p className="state-msg">Loading…</p>}
          {error   && <p className="state-msg error">{error}</p>}

          {!loading && !error && argument && (
            <>
              <div className="argument-body">
                <div className="argument-top">
                  <span className="arg-scheme-label">{argument.scheme_name}</span>
                  <span className="arg-theme-label">{argument.theme}</span>
                </div>
                <div className="argument-fields">
                  {argument.field_values.map((fv, i) => (
                    <div key={i} className="field-row">
                      <span className="field-name">{fv.field_name}</span>
                      <p className="field-value">{fv.value}</p>
                    </div>
                  ))}
                </div>
                <div className="argument-byline">
                  <span>by {argument.author}</span>
                </div>
              </div>

              <div className="add-response-section">
                <button className="btn-new" onClick={() => setShowModal(true)}>Add Response</button>
              </div>

              {(argument.attackers.length > 0 || argument.supporters.length > 0) ? (
                <div className="children-layout">

                  <div className="children-col attackers-col">
                    <div className="col-header attacking">
                      <span className="col-label">Attacking</span>
                      <span className="col-count">{argument.attackers.length}</span>
                    </div>
                    {argument.attackers.length === 0 ? (
                      <p className="col-empty">No attacks yet.</p>
                    ) : (
                      argument.attackers.map((link) => (
                        <ChildCard
                          key={link.id}
                          link={link}
                          onClick={() => navigate(`/arguments/${path}/${link.argument.id}`)}
                        />
                      ))
                    )}
                  </div>

                  <div className="children-divider" />

                  <div className="children-col supporters-col">
                    <div className="col-header supporting">
                      <span className="col-label">Supporting</span>
                      <span className="col-count">{argument.supporters.length}</span>
                    </div>
                    {argument.supporters.length === 0 ? (
                      <p className="col-empty">No support yet.</p>
                    ) : (
                      argument.supporters.map((link) => (
                        <ChildCard
                          key={link.id}
                          link={link}
                          onClick={() => navigate(`/arguments/${path}/${link.argument.id}`)}
                        />
                      ))
                    )}
                  </div>

                </div>
              ) : (
                <div className="no-children">
                  <p>No responses to this argument yet.</p>
                </div>
              )}
            </>
          )}
        </div>
      </main>

      {showModal && argument && (
        <AddArgumentModal
          themeId={argument.theme_id}
          parentSchemeId={argument.scheme_id}
          parentArgumentId={parseInt(currentArgumentId)}
          onClose={() => setShowModal(false)}
          onSuccess={(newArgId) => {
            setShowModal(false);
            fetchArgument();
          }}
        />
      )}
    </div>
  );
};

export default ArgumentPage;