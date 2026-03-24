import React from 'react';
import { Link } from 'react-router-dom';
import './LandingPage.css';

const FEATURED_ARGUMENTS = [
  {
    id: 1,
    title: 'Universal Basic Income would reduce economic inequality',
    author: '[ author_name ]',
    stance: 'For',
    replies: 24,
    votes: 142,
    tag: 'Economics',
  },
  {
    id: 2,
    title: 'Open-source AI models pose greater safety risks than closed ones',
    author: '[ author_name ]',
    stance: 'Against',
    replies: 18,
    votes: 98,
    tag: 'Technology',
  },
  {
    id: 3,
    title: 'Ranked-choice voting improves democratic outcomes',
    author: '[ author_name ]',
    stance: 'For',
    replies: 31,
    votes: 207,
    tag: 'Politics',
  },
];

const STATS = [
  { value: '[ total_arguments ]', label: 'Arguments made' },
  { value: '[ total_users ]', label: 'Active debaters' },
  { value: '[ total_votes ]', label: 'Votes cast' },
];

const LandingPage = () => {
  return (
    <div className="landing">

      {/* Hero */}
      <section className="hero">
        <div className="hero-inner">
          <p className="hero-eyebrow">The structured debate platform</p>
          <h1 className="hero-headline">
            Where arguments<br />
            <em>stand or fall</em> on merit.
          </h1>
          <p className="hero-sub">
            Argupedia helps you build, challenge, and refine arguments with structured reasoning.
            No hot takes — just claims, evidence, and counter-arguments.
          </p>
          <div className="hero-cta">
            <Link to="/dashboard" className="cta-primary">Explore arguments</Link>
            <Link to="/new-argument" className="cta-secondary">Make your case →</Link>
          </div>
        </div>
        <div className="hero-decoration" aria-hidden="true">
          <div className="deco-card deco-card-1">
            <span className="deco-stance for">For</span>
            <p>Free markets allocate resources more efficiently than central planning.</p>
          </div>
          <div className="deco-card deco-card-2">
            <span className="deco-stance against">Against</span>
            <p>Markets fail to account for externalities and public goods.</p>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="stats-bar">
        <div className="stats-inner">
          {STATS.map((s) => (
            <div key={s.label} className="stat-item">
              <span className="stat-value">{s.value}</span>
              <span className="stat-label">{s.label}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Featured arguments */}
      <section className="featured">
        <div className="section-inner">
          <div className="section-header">
            <h2 className="section-title">Trending arguments</h2>
            <Link to="/arguments" className="section-link">View all →</Link>
          </div>
          <div className="argument-list">
            {FEATURED_ARGUMENTS.map((arg) => (
              <Link to={`/argument/${arg.id}`} key={arg.id} className="argument-card">
                <div className="argument-card-top">
                  <span className="arg-tag">{arg.tag}</span>
                  <span className={`arg-stance ${arg.stance.toLowerCase()}`}>{arg.stance}</span>
                </div>
                <h3 className="arg-title">{arg.title}</h3>
                <div className="arg-meta">
                  <span>by {arg.author}</span>
                  <span className="meta-sep">·</span>
                  <span>{arg.replies} replies</span>
                  <span className="meta-sep">·</span>
                  <span>{arg.votes} votes</span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="how-it-works">
        <div className="section-inner">
          <h2 className="section-title">How Argupedia works</h2>
          <div className="steps-grid">
            {[
              { num: '01', title: 'State your claim', desc: 'Start with a clear, falsifiable thesis. No vague opinions.' },
              { num: '02', title: 'Add your evidence', desc: 'Support your claim with sources, data, or logical premises.' },
              { num: '03', title: 'Face the counter', desc: 'Others can challenge your argument directly and point-by-point.' },
              { num: '04', title: 'Community votes', desc: 'The community rates argument quality — not just popularity.' },
            ].map((step) => (
              <div key={step.num} className="step-card">
                <span className="step-num">{step.num}</span>
                <h3 className="step-title">{step.title}</h3>
                <p className="step-desc">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer CTA */}
      <section className="footer-cta">
        <div className="section-inner footer-cta-inner">
          <h2>Ready to make your case?</h2>
          <Link to="/new-argument" className="cta-primary">Start an argument</Link>
        </div>
      </section>

    </div>
  );
};

export default LandingPage;