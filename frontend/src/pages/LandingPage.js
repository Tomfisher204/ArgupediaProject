import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../css/pages/LandingPage.css';

const FEATURES = [
  {title: 'Structured arguments', desc: 'Arguments follow an argumentation scheme of your choice. Premises, conclusions, evidence all clearly defined.'},
  {title: 'Limited Bias', desc: 'Critical questions force you to counter the argument not just disagree with it.'},
  {title: 'Quality over Quantity', desc: 'Focus on building strong, well-reasoned arguments rather than numerous weak ones.'},
];

const LandingPage = () => {
  const {user, loading, error, login, signup} = useAuth();
  const [mode, setMode] = useState('login');
  const [form, setForm] = useState({ username: '', email: '', password: '', first_name: '', last_name: '' });
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);

  if (loading) return <div className="page-loading">Loading…</div>;
  if (user) return <Navigate to="/dashboard" replace />;

  const handleChange = (e) => {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));
    setFormError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setFormError(null);
    try {
      if (mode === 'login') {
        await login(form.username, form.password);
      } else {
        await signup(form.username, form.email, form.password, form.first_name, form.last_name);
      }
    } 
    catch (err) {
      setFormError(err.message);
    } 
    finally {
      setSubmitting(false);
    }
  };

  const switchMode = (next) => {
    setMode(next);
    setFormError(null);
    setForm({ username: '', email: '', password: '' , first_name: '', last_name: ''});
  };

  return (
    <div className="landing">
      <div className="landing-left">
        <div className="landing-left-inner">
          <div className="landing-logo">
            <span className="logo-mark">A</span>
            <span className="logo-text">argupedia</span>
          </div>
          <h1 className="landing-headline">
            Argumentation done right.
          </h1>
          <p className="landing-sub">
            A structured debate platform that uses schemes and critical questions to promote high-quality arguments.
          </p>
          <div className="feature-cards">
            {FEATURES.map((f) => (
              <div key={f.title} className="feature-card">
                <p className="feature-title">{f.title}</p>
                <p className="feature-desc">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="landing-right">
        <div className="auth-box">
          <div className="auth-tabs">
            <button className={`auth-tab ${mode === 'login' ? 'active' : ''}`} onClick={() => switchMode('login')}>
              Log in
            </button>
            <button className={`auth-tab ${mode === 'signup' ? 'active' : ''}`} onClick={() => switchMode('signup')}>
              Sign up
            </button>
          </div>
          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="field">
              <label className="field-label" htmlFor="username">Username</label>
              <input
                id="username"
                name="username"
                type="text"
                className="field-input"
                value={form.username}
                onChange={handleChange}
                autoComplete="username"
                required
              />
            </div>
            {mode === 'signup' && (
              <div className="field">
                <label className="field-label" htmlFor="email">Email</label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  className="field-input"
                  value={form.email}
                  onChange={handleChange}
                  autoComplete="email"
                  required
                />
              </div>
            )}
            {mode === 'signup' && (
              <div className="field">
                <label className="field-label" htmlFor="first_name">First Name</label>
                <input
                  id="first_name"
                  name="first_name"
                  type="text"
                  className="field-input"
                  value={form.first_name}
                  onChange={handleChange}
                  autoComplete="given-name"
                  required
                />
              </div>
            )}
            {mode === 'signup' && (
              <div className="field">
                <label className="field-label" htmlFor="last_name">Last Name</label>
                <input
                  id="last_name"
                  name="last_name"
                  type="text"
                  className="field-input"
                  value={form.last_name}
                  onChange={handleChange}
                  autoComplete="family-name"
                  required
                />
              </div>
            )}
            <div className="field">
              <label className="field-label" htmlFor="password">Password</label>
              <input
                id="password"
                name="password"
                type="password"
                className="field-input"
                value={form.password}
                onChange={handleChange}
                autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                required
              />
            </div>
            {(formError || error) && (
              <p className="auth-error">{formError || error}</p>
            )}
            <button className="auth-submit" type="submit" disabled={submitting}>
              {submitting
                ? 'Please wait…'
                : mode === 'login' ? 'Log in' : 'Create account'}
            </button>
          </form>

          <p className="auth-switch">
            {mode === 'login' ? (
              <>No account?{' '}
                <button className="link-btn" onClick={() => switchMode('signup')}>Sign up</button>
              </>
            ) : (
              <>Already have one?{' '}
                <button className="link-btn" onClick={() => switchMode('login')}>Log in</button>
              </>
            )}
          </p>

        </div>
      </div>
    </div>
  );
};

export default LandingPage;