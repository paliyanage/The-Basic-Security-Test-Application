import React, { useState } from 'react';

const API_URL = process.env.REACT_APP_API_URL;

export default function App() {
  const [mode, setMode] = useState('register'); // or 'login'

  // Registration state
  const [regData, setRegData] = useState({
    name: '', email: '', team: '', team_manager: '', Phone_number: ''
  });
  const [regResult, setRegResult] = useState('');
  const [regError, setRegError] = useState('');

  // Login state
  const [auditorCode, setAuditorCode] = useState('');
  const [loginError, setLoginError] = useState('');
  const [auditorInfo, setAuditorInfo] = useState(null);
  const [reports, setReports] = useState([]);

  // Handle registration form submit
  const handleRegister = async e => {
    e.preventDefault();
    setRegError('');
    setRegResult('');
    try {
      const res = await fetch(`${API_URL}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(regData),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || 'Registration failed');
      }
      const { auditor_code } = await res.json();
      setRegResult(auditor_code);
    } catch (err) {
      setRegError(err.message);
    }
  };

  // Handle login form submit
  const handleLogin = async e => {
    e.preventDefault();
    setLoginError('');
    setAuditorInfo(null);
    setReports([]);
    try {
      // Validate auditor exists
      let res = await fetch(`${API_URL}/auditors/${auditorCode}`);
      if (!res.ok) throw new Error('Invalid auditor code');
      const info = await res.json();
      setAuditorInfo(info);

      // Fetch reports list (now includes log_path)
      res = await fetch(`${API_URL}/reports?auditor_code=${auditorCode}`);
      if (!res.ok) throw new Error('Could not fetch reports');
      const list = await res.json();
      setReports(list);
    } catch (err) {
      setLoginError(err.message);
    }
  };

  return ( 
    <>
      {/* Background Video */}
      <video className="video-background" autoPlay muted loop>
        <source src="/AS1.mp4" type="video/mp4" />
      </video>

    <div className="container">
      <div className="tabs">
        <div
          className={`tab ${mode==='register' ? 'active' : ''}`}
          onClick={() => setMode('register')}
        >
          Register
        </div>
        <div
          className={`tab ${mode==='login' ? 'active' : ''}`}
          onClick={() => setMode('login')}
        >
          Login
        </div>
      </div>

      {mode === 'register' && (
        <form onSubmit={handleRegister}>
          {['name','email','team','team_manager'].map(field => (
            <div className="form-group" key={field}>
              <input
                required
                type={field==='email'?'email':'text'}
                placeholder={field.replace('_',' ').toUpperCase()}
                value={regData[field]}
                onChange={e => setRegData({...regData, [field]: e.target.value})}
              />
            </div>
          ))}
          <button type="submit" className="btn btn-register">Register</button>
          {regResult && <div className="success">Your Auditor Code: <strong>{regResult}</strong></div>}
          {regError  && <div className="error">{regError}</div>}
        </form>
      )}

      {mode === 'login' && (
        <form onSubmit={handleLogin}>
          <div className="form-group">
            <input
              required
              placeholder="Auditor Code"
              value={auditorCode}
              onChange={e => setAuditorCode(e.target.value)}
            />
          </div>
          <button type="submit" className="btn btn-login">Login</button>
          {loginError && <div className="error">{loginError}</div>}
        </form>
      )}

      {auditorInfo && (
        <div style={{ marginTop: 20 }}>
          <h2>Welcome, {auditorInfo.name}</h2>
          <h3>Your Reports</h3>
          {reports.length === 0 ? (
            <p>No reports found.</p>
          ) : (
            <ul className="report-list">
              {reports.map(r => (
                <li key={r.report_id} className="report-item">
                  {r.client_company} / {r.it_manager_name} &mdash;{' '}
                  {new Date(r.received_at).toLocaleString()}
                  {' '}
                  <a
                    href={`${API_URL}/reports/${r.report_id}/pdf`}
                    target="_blank" rel="noopener noreferrer"
                  >
                    View PDF
                  </a>
                  {r.log_path && (
                    <>
                      {' | '}
                      <a
                        href={`${API_URL}/reports/${r.report_id}/log`}
                        target="_blank" rel="noopener noreferrer"
                      >
                        Download Log
                      </a>
                    </>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
    </>
  );
}


