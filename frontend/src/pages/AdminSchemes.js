import React, {useState, useEffect} from 'react';
import {Navbar, ConfirmDialog, TrashIcon, AddSchemeForm, AddCriticalQuestionForm} from '../components';
import '../css/pages/AdminSchemes.css';

const API = process.env.REACT_APP_API_URL;

const AdminSchemes = () => {
  const [schemes, setSchemes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showSchemeForm, setShowSchemeForm] = useState(false);
  const [showCQForm, setShowCQForm] = useState(null);
  const [confirmDialog, setConfirmDialog] = useState({show: false, message: '', onConfirm: null});

  useEffect(() => {fetchSchemes()}, []);

  const fetchSchemes = async () => {
    const token = localStorage.getItem('access_token');
    const res = await fetch(`${API}/api/admin/schemes/`, {
      headers: {Authorization: `Bearer ${token}`},
    });
    if (res.ok) {
      const data = await res.json();
      setSchemes(data);
    }
    setLoading(false);
  };

  const handleDeleteScheme = async (schemeId) => {
    setConfirmDialog({
      show: true,
      message: 'Are you sure you want to delete this scheme?',
      onConfirm: async () => {
        const token = localStorage.getItem('access_token');
        const res = await fetch(`${API}/api/admin/schemes/${schemeId}/`, {
          method: 'DELETE',
          headers: {Authorization: `Bearer ${token}`},
        });
        if (res.ok) {
          fetchSchemes();
        }
        setConfirmDialog({show: false, message: '', onConfirm: null});
      }
    });
  };

  const handleDeleteCQ = async (cqId) => {
    setConfirmDialog({
      show: true,
      message: 'Are you sure you want to delete this critical question?',
      onConfirm: async () => {
        const token = localStorage.getItem('access_token');
        const res = await fetch(`${API}/api/admin/critical-questions/${cqId}/`, {
          method: 'DELETE',
          headers: {Authorization: `Bearer ${token}`},
        });
        if (res.ok) {fetchSchemes()}
        setConfirmDialog({show: false, message: '', onConfirm: null});
      }
    });
  };

  const handleCancelConfirm = () => {
    setConfirmDialog({show: false, message: '', onConfirm: null});
  };

  return (
    <div className="admin-schemes">
      <Navbar />
      <main className="page-main">
        <div className="page-inner">
          <h1>Scheme Management</h1>

          <div className="actions-bar">
            <button className="btn-primary" onClick={() => setShowSchemeForm(true)}>
              Add New Scheme
            </button>
          </div>

          {loading ? (
            <p>Loading schemes...</p>
          ) : (
            <div className="schemes-list">
              {schemes.map((scheme) => (
                <div key={scheme.id} className="scheme-card">
                  <div className="scheme-header">
                    <h3>{scheme.name}</h3>
                    <button className="btn-delete" onClick={() => handleDeleteScheme(scheme.id)}>
                      Delete
                    </button>
                  </div>
                  {scheme.description && (
                    <div className="scheme-description">
                      {scheme.description}
                    </div>
                  )}

                  <div className="critical-questions">
                    <h4>Critical Questions</h4>
                    <div className="cq-list">
                      {scheme.critical_questions.map((cq) => (
                        <div key={cq.id} className="cq-card">
                          <span>{cq.question}</span>
                          <button className="btn-delete-small" onClick={() => handleDeleteCQ(cq.id)}>
                            <TrashIcon />
                          </button>
                        </div>
                      ))}
                    </div>
                    <button className="btn-secondary" onClick={() => {setShowCQForm(scheme.id)}}>
                      Add Critical Question
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {showSchemeForm && (
            <div className="modal-backdrop" onClick={() => setShowSchemeForm(false)}>
              <div className="modal modal-sm" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                  <h2 className="modal-title">Add New Scheme</h2>
                  <button className="modal-close" onClick={() => setShowSchemeForm(false)}>✕</button>
                </div>
                <AddSchemeForm onClose={() => setShowSchemeForm(false)} onSuccess={() => {setShowSchemeForm(false); fetchSchemes()}}/>
              </div>
            </div>
          )}

          {showCQForm && (
            <div className="modal-backdrop" onClick={() => setShowCQForm(null)}>
              <div className="modal modal-sm" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                  <h2 className="modal-title">Add Critical Question</h2>
                  <button className="modal-close" onClick={() => setShowCQForm(null)}>✕</button>
                </div>
                <AddCriticalQuestionForm schemeId={showCQForm} onClose={() => setShowCQForm(null)} onSuccess={() => {setShowCQForm(null); fetchSchemes();}}/>
              </div>
            </div>
          )}
        </div>
      </main>

      {confirmDialog.show && (
        <ConfirmDialog message={confirmDialog.message} onConfirm={confirmDialog.onConfirm} onCancel={handleCancelConfirm}/>
      )}
    </div>
  );
};

export default AdminSchemes;