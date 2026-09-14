import React, { useState, useEffect, useCallback } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';
import { authApi, analyticsApi, patientApi, donorApi, emergencyApi, matchingApi, orchestrationApi, adminApi } from './api.js';

// ── Icons (inline SVG) ─────────────────────
const Icon = ({ name, size = 16 }) => {
  const icons = {
    dashboard: <><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></>,
    patients: <><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></>,
    donors: <><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></>,
    emergency: <><polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></>,
    analytics: <><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></>,
    models: <><circle cx="12" cy="12" r="3"/><path d="M12 2v4m0 12v4M4.22 4.22l2.83 2.83m9.9 9.9 2.83 2.83M2 12h4m12 0h4M4.22 19.78l2.83-2.83m9.9-9.9 2.83-2.83"/></>,
    admin: <><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></>,
    demo: <><polygon points="5 3 19 12 5 21 5 3"/></>,
    logout: <><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></>,
    check: <><polyline points="20 6 9 17 4 12"/></>,
    x: <><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></>,
    clock: <><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></>,
    alert: <><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></>,
    info: <><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></>,
    brain: <><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.46 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.46 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"/></>,
    droplet: <><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></>,
    zap: <><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></>,
    plus: <><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></>,
    refresh: <><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></>,
  };
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      {icons[name] || null}
    </svg>
  );
};

// ── Risk Badge ─────────────────────────
const RiskBadge = ({ level }) => {
  const l = (level || '').toLowerCase().replace('_', '-');
  return <span className={`badge badge-${l}`}>{level}</span>;
};

// ── Loading Skeleton ─────────────────────────
const Skeleton = ({ h = '16px', w = '100%' }) => (
  <div className="loading-shimmer" style={{ height: h, width: w, borderRadius: 6, marginBottom: 6 }} />
);

// ── Login Page ─────────────────────────
function LoginPage({ onLogin }) {
  const [email, setEmail] = useState('coordinator@ratham.ai');
  const [password, setPassword] = useState('coord123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true); setError('');
    try {
      const res = await authApi.login(email, password);
      localStorage.setItem('ratham_token', res.access_token);
      localStorage.setItem('ratham_user', JSON.stringify({ name: res.name, role: res.role, id: res.user_id }));
      onLogin(res);
    } catch (err) {
      setError(err.message || 'Login failed. Check credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-logo">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, marginBottom: 8 }}>
            <div style={{ color: '#c0392b' }}><Icon name="droplet" size={28} /></div>
            <h1>RATHAM AI</h1>
          </div>
          <p>Predictive Blood Continuity Intelligence Network</p>
        </div>
        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input className="form-input" type="email" value={email} onChange={e => setEmail(e.target.value)} required autoFocus />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input className="form-input" type="password" value={password} onChange={e => setPassword(e.target.value)} required />
          </div>
          {error && <div className="error-state mb-3">{error}</div>}
          <button type="submit" className="btn btn-primary w-full" disabled={loading} style={{ justifyContent: 'center' }}>
            {loading ? 'Authenticating...' : 'Sign In to Operations'}
          </button>
        </form>
        <div style={{ marginTop: 20, padding: '12px', background: '#f8f9fa', borderRadius: 8, fontSize: 12, color: '#5f6368' }}>
          <strong>System credentials:</strong><br/>
          coordinator@ratham.ai / coord123<br/>
          admin@ratham.ai / admin123
        </div>
      </div>
    </div>
  );
}

// ── Dashboard Page ─────────────────────────
function DashboardPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    analyticsApi.overview().then(setData).catch(e => setError(e.message)).finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="page-body">
      <div className="metrics-grid">{[...Array(6)].map((_, i) => <div key={i} className="metric-card"><Skeleton h="60px" /></div>)}</div>
    </div>
  );
  if (error) return <div className="page-body"><div className="error-state">⚠ Unable to load operations data: {error}</div></div>;
  if (!data) return null;

  const { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } = window.Recharts || {};

  return (
    <div className="page-body">
      <div className="metrics-grid">
        <div className="metric-card"><div className="label">Patients Monitored</div><div className="value">{data.patients_monitored}</div><div className="sublabel">Active in system</div></div>
        <div className="metric-card danger"><div className="label">High Risk Patients</div><div className="value">{data.high_risk_patients}</div><div className="sublabel">Require attention</div></div>
        <div className="metric-card success"><div className="label">Available Donors</div><div className="value">{data.available_donors}</div><div className="sublabel">Ready to respond</div></div>
        <div className="metric-card warning"><div className="label">At-Risk Donors</div><div className="value">{data.at_risk_donors}</div><div className="sublabel">Burnout flag raised</div></div>
        <div className="metric-card critical"><div className="label">Active Emergencies</div><div className="value">{data.active_emergencies}</div><div className="sublabel">In progress</div></div>
        <div className="metric-card"><div className="label">Requests Fulfilled</div><div className="value">{data.requests_fulfilled}</div><div className="sublabel">Avg {data.avg_fulfillment_time_minutes}m</div></div>
      </div>

      <div className="charts-grid">
        <div className="card">
          <div className="card-header"><div className="card-title">7-Day Blood Demand Trend</div></div>
          <div className="card-body">
            <div className="chart-wrap">
              <DailyDemandChart data={data.blood_demand_trend} />
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-header"><div className="card-title">Donor Reachability Distribution</div></div>
          <div className="card-body">
            <ReachabilityChart data={data.reachability_distribution} />
          </div>
        </div>
        <div className="card">
          <div className="card-header"><div className="card-title">Donor Engagement Health</div></div>
          <div className="card-body">
            <BurnoutChart data={data.burnout_distribution} />
          </div>
        </div>
        <div className="card">
          <div className="card-header"><div className="card-title">ML Model Status</div></div>
          <div className="card-body">
            <ModelStatusCard metrics={data.metrics} />
          </div>
        </div>
      </div>
    </div>
  );
}

function DailyDemandChart({ data }) {
  if (!data || !data.length) return <div className="empty-state"><p>No demand trend data</p></div>;
  return (
    <div style={{ width: '100%', height: 220 }}>
      <SimpleBarChart data={data} bars={[
        { key: 'demand', color: '#c0392b', label: 'Demand' },
        { key: 'fulfilled', color: '#27ae60', label: 'Fulfilled' }
      ]} xKey="day" />
    </div>
  );
}

function SimpleBarChart({ data, bars, xKey }) {
  if (!data?.length) return null;
  const max = Math.max(...data.flatMap(d => bars.map(b => d[b.key] || 0)));
  const w = 100 / data.length;
  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', gap: 4, height: 200, paddingBottom: 24, position: 'relative' }}>
      {data.map((d, i) => (
        <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2, height: '100%', justifyContent: 'flex-end' }}>
          <div style={{ display: 'flex', gap: 2, width: '100%', height: '85%', alignItems: 'flex-end' }}>
            {bars.map(b => (
              <div key={b.key} style={{ flex: 1, height: `${Math.max(4, (d[b.key] / max) * 100)}%`, background: b.color, borderRadius: '3px 3px 0 0', minHeight: 3 }} title={`${b.label}: ${d[b.key]}`} />
            ))}
          </div>
          <div style={{ fontSize: 10, color: '#80868b', marginTop: 4 }}>{d[xKey]}</div>
        </div>
      ))}
    </div>
  );
}

function ReachabilityChart({ data }) {
  if (!data?.length) return <div className="empty-state"><p>No data</p></div>;
  return (
    <div>
      {data.map((d, i) => {
        const colors = ['#c0392b', '#e67e22', '#27ae60', '#1a5f7a'];
        const total = data.reduce((a, b) => a + b.count, 0) || 1;
        return (
          <div key={i} style={{ marginBottom: 10 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
              <span style={{ fontSize: 12, color: '#5f6368' }}>{d.range}</span>
              <span style={{ fontSize: 12, fontWeight: 600 }}>{d.count}</span>
            </div>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${(d.count / total) * 100}%`, background: colors[i] }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}

function BurnoutChart({ data }) {
  if (!data?.length) return null;
  const colors = { HEALTHY: '#27ae60', WATCH: '#e67e22', HIGH_RISK: '#c0392b' };
  const total = data.reduce((a, b) => a + b.count, 0) || 1;
  return (
    <div>
      {data.map((d, i) => (
        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 14 }}>
          <div style={{ width: 10, height: 10, borderRadius: '50%', background: colors[d.status] || '#ccc', flexShrink: 0 }} />
          <span style={{ flex: 1, fontSize: 13 }}>{d.status}</span>
          <span style={{ fontSize: 13, fontWeight: 600 }}>{d.count}</span>
          <div style={{ width: 80 }}>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${(d.count / total) * 100}%`, background: colors[d.status] || '#ccc' }} />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function ModelStatusCard({ metrics }) {
  if (!metrics) return <div className="empty-state"><p>No metrics available</p></div>;
  return (
    <div>
      {Object.entries(metrics).map(([model, m]) => (
        <div key={model} style={{ marginBottom: 16, paddingBottom: 16, borderBottom: '1px solid #e8eaed' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
            <span style={{ fontSize: 13, fontWeight: 600 }}>{model.replace('_', ' ').replace('model', '').trim()}</span>
            <span className="badge badge-success">ACTIVE</span>
          </div>
          <div style={{ display: 'flex', gap: 16 }}>
            <span style={{ fontSize: 11, color: '#5f6368' }}>F1: <strong>{m?.f1 || '—'}</strong></span>
            <span style={{ fontSize: 11, color: '#5f6368' }}>AUC: <strong>{m?.roc_auc || '—'}</strong></span>
            <span style={{ fontSize: 11, color: '#5f6368' }}>n={m?.rows?.toLocaleString() || '—'}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

// ── Patients Page ─────────────────────────
function PatientsPage({ onNavigate }) {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [riskFilter, setRiskFilter] = useState('');
  const [selected, setSelected] = useState(null);
  const [predResult, setPredResult] = useState(null);
  const [timeline, setTimeline] = useState(null);

  useEffect(() => {
    let params = '?limit=50';
    if (search) params += `&search=${encodeURIComponent(search)}`;
    if (riskFilter) params += `&risk=${riskFilter}`;
    patientApi.list(params).then(setPatients).catch(console.error).finally(() => setLoading(false));
  }, [search, riskFilter]);

  const selectPatient = async (p) => {
    setSelected(p); setPredResult(null); setTimeline(null);
    const [pred, tl] = await Promise.all([
      patientApi.predictions(p.id).catch(() => null),
      patientApi.timeline(p.id).catch(() => null)
    ]);
    setPredResult(pred); setTimeline(tl);
  };

  return (
    <div className="page-body" style={{ display: 'flex', gap: 20 }}>
      <div style={{ flex: 1 }}>
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 11, color: '#80868b', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 12, fontWeight: 600 }}>PATIENT MONITORING</div>
          <div className="search-bar">
            <input className="search-input" placeholder="Search patients..." value={search} onChange={e => setSearch(e.target.value)} />
            <select className="filter-select" value={riskFilter} onChange={e => setRiskFilter(e.target.value)}>
              <option value="">All Risk Levels</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>
        </div>
        <div className="card">
          {loading ? (
            <div className="card-body">{[...Array(4)].map((_, i) => <Skeleton key={i} h="40px" />)}</div>
          ) : patients.length === 0 ? (
            <div className="empty-state"><h3>No patients found</h3><p>Adjust filters or add a patient</p></div>
          ) : (
            <table className="data-table">
              <thead>
                <tr><th>Code</th><th>Name</th><th>Blood Group</th><th>Hospital</th><th>Risk Level</th><th>Need %</th><th>Status</th></tr>
              </thead>
              <tbody>
                {patients.map(p => (
                  <tr key={p.id} onClick={() => selectPatient(p)} style={{ cursor: 'pointer', background: selected?.id === p.id ? '#eaf4f8' : '' }}>
                    <td><code style={{ fontSize: 12, color: '#1a5f7a' }}>{p.patient_code}</code></td>
                    <td><strong>{p.name}</strong></td>
                    <td><span className="tag">{p.blood_group}</span></td>
                    <td style={{ fontSize: 12, color: '#5f6368' }}>{p.hospital_name}</td>
                    <td><RiskBadge level={p.risk_level} /></td>
                    <td><strong>{(p.need_probability * 100).toFixed(0)}%</strong></td>
                    <td><span className={`badge badge-${p.status === 'URGENT' ? 'danger' : 'info'}`}>{p.status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {selected && (
        <div style={{ width: 340, flexShrink: 0 }}>
          <div className="card mb-4">
            <div className="card-header">
              <div>
                <div className="card-title">{selected.name}</div>
                <div style={{ fontSize: 11, color: '#80868b', marginTop: 2 }}>{selected.patient_code}</div>
              </div>
              <span className="tag">{selected.blood_group}</span>
            </div>
            <div className="card-body">
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 14 }}>
                <div><div style={{ fontSize: 11, color: '#80868b' }}>Hospital</div><div style={{ fontSize: 13, fontWeight: 600 }}>{selected.hospital_name}</div></div>
                <div><div style={{ fontSize: 11, color: '#80868b' }}>City</div><div style={{ fontSize: 13, fontWeight: 600 }}>{selected.city}</div></div>
                <div><div style={{ fontSize: 11, color: '#80868b' }}>Hb Level</div><div style={{ fontSize: 13, fontWeight: 600 }}>{selected.hb_level} g/dL</div></div>
                <div><div style={{ fontSize: 11, color: '#80868b' }}>Fatigue Score</div><div style={{ fontSize: 13, fontWeight: 600 }}>{selected.fatigue_score}/10</div></div>
                <div><div style={{ fontSize: 11, color: '#80868b' }}>Risk Level</div><div><RiskBadge level={selected.risk_level} /></div></div>
                <div><div style={{ fontSize: 11, color: '#80868b' }}>Need Prob.</div><div style={{ fontSize: 20, fontWeight: 700, color: selected.need_probability >= 0.6 ? '#c0392b' : '#1a5f7a' }}>{(selected.need_probability * 100).toFixed(0)}%</div></div>
              </div>
              <button className="btn btn-primary btn-sm w-full" style={{ justifyContent: 'center' }} onClick={() => onNavigate('emergency', { patient: selected })}>
                <Icon name="emergency" size={13} /> Create Emergency Request
              </button>
            </div>
          </div>

          {predResult && (
            <div className="explanation-card mb-4">
              <div className="explanation-title"><Icon name="brain" size={14} /> Why is this patient flagged?</div>
              <div style={{ fontSize: 13, fontWeight: 600, color: predResult.risk_level === 'CRITICAL' || predResult.risk_level === 'HIGH' ? '#c0392b' : '#1a5f7a', marginBottom: 8 }}>
                {predResult.risk_level} RISK — {(predResult.need_probability * 100).toFixed(0)}%
              </div>
              {predResult.top_factors?.map((f, i) => (
                <div key={i} className="factor-row">
                  <div className="factor-icon" style={{ color: f.direction?.includes('increased') ? '#c0392b' : '#27ae60' }}>
                    <Icon name={f.direction?.includes('increased') ? 'alert' : 'check'} size={16} />
                  </div>
                  <div className="factor-text">{f.description}</div>
                </div>
              ))}
              <div style={{ marginTop: 12, fontSize: 12, color: '#5f6368', borderTop: '1px solid rgba(26,95,122,0.15)', paddingTop: 10 }}>
                <strong>Recommendation:</strong> {predResult.recommendation}
              </div>
            </div>
          )}

          {timeline && (
            <div className="card">
              <div className="card-header"><div className="card-title">Transfusion Timeline</div></div>
              <div className="card-body">
                <div className="timeline">
                  {timeline.timeline?.map((t, i) => (
                    <div key={i} className="timeline-item">
                      <div className="timeline-date">{t.date}</div>
                      <div className="timeline-event">{t.event}</div>
                      <div className="timeline-detail">{t.details || t.location}{t.units ? ` · ${t.units} unit(s)` : ''}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ── Donors Page ─────────────────────────
function DonorsPage() {
  const [donors, setDonors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [availFilter, setAvailFilter] = useState('');
  const [selected, setSelected] = useState(null);
  const [riskData, setRiskData] = useState(null);

  const load = useCallback(() => {
    let params = '?limit=50';
    if (search) params += `&search=${encodeURIComponent(search)}`;
    if (availFilter) params += `&availability=${availFilter}`;
    donorApi.list(params).then(setDonors).catch(console.error).finally(() => setLoading(false));
  }, [search, availFilter]);

  useEffect(() => { load(); }, [load]);

  const selectDonor = async (d) => {
    setSelected(d); setRiskData(null);
    const r = await donorApi.risk(d.id).catch(() => null);
    setRiskData(r);
  };

  const toggleAvailability = async (donor, newStatus) => {
    await donorApi.updateAvailability(donor.id, newStatus);
    load();
    if (selected?.id === donor.id) setSelected({ ...donor, availability_status: newStatus });
  };

  const avail_colors = { AVAILABLE: '#27ae60', UNAVAILABLE: '#80868b', ON_COOLDOWN: '#e67e22', CONTACTED: '#1a5f7a' };

  return (
    <div className="page-body" style={{ display: 'flex', gap: 20 }}>
      <div style={{ flex: 1 }}>
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 11, color: '#80868b', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 12, fontWeight: 600 }}>DONOR INTELLIGENCE</div>
          <div className="search-bar">
            <input className="search-input" placeholder="Search donors..." value={search} onChange={e => setSearch(e.target.value)} />
            <select className="filter-select" value={availFilter} onChange={e => setAvailFilter(e.target.value)}>
              <option value="">All Status</option>
              <option value="AVAILABLE">Available</option>
              <option value="UNAVAILABLE">Unavailable</option>
              <option value="ON_COOLDOWN">On Cooldown</option>
            </select>
          </div>
        </div>
        <div className="card">
          {loading ? (
            <div className="card-body">{[...Array(4)].map((_, i) => <Skeleton key={i} h="40px" />)}</div>
          ) : donors.length === 0 ? (
            <div className="empty-state"><h3>No donors found</h3><p>Adjust filters or add a donor</p></div>
          ) : (
            <table className="data-table">
              <thead>
                <tr><th>Code</th><th>Name</th><th>Blood Grp</th><th>City</th><th>Reachability</th><th>Burnout Risk</th><th>Status</th></tr>
              </thead>
              <tbody>
                {donors.map(d => (
                  <tr key={d.id} onClick={() => selectDonor(d)} style={{ cursor: 'pointer', background: selected?.id === d.id ? '#eaf4f8' : '' }}>
                    <td><code style={{ fontSize: 12, color: '#1a5f7a' }}>{d.donor_code}</code></td>
                    <td><strong>{d.name}</strong></td>
                    <td><span className="tag">{d.blood_group}</span></td>
                    <td style={{ fontSize: 12, color: '#5f6368' }}>{d.city}</td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <div className="progress-bar" style={{ width: 60 }}>
                          <div className="progress-fill" style={{ width: `${d.reachability_probability * 100}%`, background: d.reachability_probability >= 0.7 ? '#27ae60' : d.reachability_probability >= 0.4 ? '#e67e22' : '#c0392b' }} />
                        </div>
                        <span style={{ fontSize: 12 }}>{(d.reachability_probability * 100).toFixed(0)}%</span>
                      </div>
                    </td>
                    <td><RiskBadge level={d.burnout_risk_level} /></td>
                    <td>
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontSize: 12, fontWeight: 600, color: avail_colors[d.availability_status] || '#80868b' }}>
                        <span className="status-dot" style={{ background: avail_colors[d.availability_status] || '#ccc' }} />
                        {d.availability_status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {selected && (
        <div style={{ width: 340, flexShrink: 0 }}>
          <div className="card mb-4">
            <div className="card-header">
              <div>
                <div className="card-title">{selected.name}</div>
                <div style={{ fontSize: 11, color: '#80868b', marginTop: 2 }}>{selected.donor_code}</div>
              </div>
              <span className="tag">{selected.blood_group}</span>
            </div>
            <div className="card-body">
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
                <div><div style={{ fontSize: 11, color: '#80868b' }}>Response Rate</div><div style={{ fontSize: 20, fontWeight: 700, color: '#1a5f7a' }}>{(selected.response_rate_90d * 100).toFixed(0)}%</div></div>
                <div><div style={{ fontSize: 11, color: '#80868b' }}>Avg Response</div><div style={{ fontSize: 20, fontWeight: 700 }}>{(selected.avg_response_hours * 60).toFixed(0)} min</div></div>
                <div><div style={{ fontSize: 11, color: '#80868b' }}>Reachability</div><div style={{ fontSize: 18, fontWeight: 700, color: selected.reachability_probability >= 0.7 ? '#27ae60' : '#e67e22' }}>{(selected.reachability_probability * 100).toFixed(0)}%</div></div>
                <div><div style={{ fontSize: 11, color: '#80868b' }}>Burnout Risk</div><div><RiskBadge level={selected.burnout_risk_level} /></div></div>
                <div><div style={{ fontSize: 11, color: '#80868b' }}>Contacts (14d)</div><div style={{ fontSize: 14, fontWeight: 600 }}>{selected.contacts_last_14d}</div></div>
                <div><div style={{ fontSize: 11, color: '#80868b' }}>Distance</div><div style={{ fontSize: 14, fontWeight: 600 }}>{selected.distance_km?.toFixed(1)} km</div></div>
              </div>
              <div style={{ marginBottom: 12 }}>
                <div style={{ fontSize: 11, color: '#80868b', fontWeight: 600, marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.4px' }}>Update Availability</div>
                <div style={{ display: 'flex', gap: 6 }}>
                  <button className="btn btn-success btn-sm" onClick={() => toggleAvailability(selected, 'AVAILABLE')}>Available</button>
                  <button className="btn btn-outline btn-sm" onClick={() => toggleAvailability(selected, 'UNAVAILABLE')}>Unavailable</button>
                  <button className="btn btn-outline btn-sm" style={{ color: '#e67e22' }} onClick={() => toggleAvailability(selected, 'ON_COOLDOWN')}>Cooldown</button>
                </div>
              </div>
            </div>
          </div>

          {riskData && (
            <div className="explanation-card">
              <div className="explanation-title"><Icon name="brain" size={14} /> Engagement Health Analysis</div>
              <div style={{ marginBottom: 8 }}>
                <div style={{ fontSize: 12, color: '#5f6368', marginBottom: 4 }}>Reachability: <strong style={{ color: riskData.reachable ? '#27ae60' : '#c0392b' }}>{(riskData.reachability_probability * 100).toFixed(0)}%</strong></div>
                <div style={{ fontSize: 12, color: '#5f6368', marginBottom: 4 }}>Expected Response: <strong>{riskData.expected_response_minutes} min</strong></div>
                <div style={{ fontSize: 12, color: '#5f6368', marginBottom: 8 }}>Burnout Risk: <strong style={{ color: riskData.high_burnout_risk ? '#c0392b' : '#27ae60' }}>{(riskData.burnout_probability * 100).toFixed(0)}%</strong></div>
              </div>
              {riskData.top_factors?.slice(0, 3).map((f, i) => (
                <div key={i} className="factor-row">
                  <div className="factor-icon" style={{ color: f.direction?.includes('decreased') || f.direction?.includes('healthy') ? '#27ae60' : '#c0392b' }}>
                    <Icon name={f.direction?.includes('decreased') ? 'check' : 'alert'} size={15} />
                  </div>
                  <div className="factor-text">{f.description}</div>
                </div>
              ))}
              {riskData.recommended_cooldown_days > 0 && (
                <div style={{ marginTop: 10, padding: '8px 12px', background: '#fef3e7', borderRadius: 6, fontSize: 12, color: '#d35400' }}>
                  ⚠ Suggested cooldown: {riskData.recommended_cooldown_days} days to prevent disengagement.
                </div>
              )}
              <p style={{ fontSize: 10, color: '#80868b', marginTop: 10 }}>This is an operational engagement signal — not a medical assessment.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ── Emergency Control Center ─────────────────────────
function EmergencyPage({ initialPatient }) {
  const [emergencies, setEmergencies] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [showCreate, setShowCreate] = useState(!!initialPatient);
  const [newEmForm, setNewEmForm] = useState({
    patient_id: initialPatient?.id || '',
    blood_group: initialPatient?.blood_group || 'O+',
    units_required: 2,
    hospital_name: initialPatient?.hospital_name || '',
    priority: 'CRITICAL',
    notes: ''
  });
  const [createError, setCreateError] = useState('');

  const load = useCallback(() => {
    emergencyApi.list('?limit=20').then(data => {
      setEmergencies(data);
      if (data.length && !selected) setSelected(data[0]);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  useEffect(() => { load(); }, [load]);

  const selectAndLoad = async (em) => {
    setSelected(null);
    const full = await emergencyApi.get(em.id).catch(() => em);
    setSelected(full);
  };

  const doAction = async (action, extraData) => {
    if (!selected) return;
    setActionLoading(true);
    try {
      if (action === 'decline') await emergencyApi.decline(selected.id);
      else if (action === 'confirm') await emergencyApi.confirm(selected.id, extraData?.donor_id);
      const updated = await emergencyApi.get(selected.id);
      setSelected(updated);
      load();
    } catch (e) { console.error(e); }
    setActionLoading(false);
  };

  const createEmergency = async () => {
    setCreateError('');
    setActionLoading(true);
    try {
      const em = await emergencyApi.create({ ...newEmForm, units_required: parseInt(newEmForm.units_required), patient_id: parseInt(newEmForm.patient_id) });
      setShowCreate(false);
      const full = await emergencyApi.get(em.id);
      setSelected(full);
      load();
    } catch (e) { setCreateError(e.message); }
    setActionLoading(false);
  };

  const statusColors = { CREATED: '#80868b', SEARCHING: '#1a5f7a', PRIMARY_CONTACTED: '#e67e22', PRIMARY_DECLINED: '#c0392b', BACKUP_SEARCH: '#d35400', BACKUP_CONTACTED: '#e67e22', DONOR_CONFIRMED: '#27ae60', FULFILLED: '#1a7a4a', ESCALATED: '#7b1fa2', CANCELLED: '#80868b' };

  return (
    <div className="page-body" style={{ display: 'flex', gap: 20 }}>
      <div style={{ width: 300, flexShrink: 0 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <div style={{ fontSize: 11, color: '#80868b', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>EMERGENCY QUEUE</div>
          <button className="btn btn-danger btn-sm" onClick={() => setShowCreate(true)}><Icon name="plus" size={13} /> New</button>
        </div>
        <div className="card">
          {loading ? <div className="card-body"><Skeleton h="40px" /><Skeleton h="40px" /></div> :
           emergencies.length === 0 ? <div className="empty-state"><p>No active emergencies</p></div> :
           emergencies.map(em => (
            <div key={em.id} onClick={() => selectAndLoad(em)} style={{ padding: '12px 16px', borderBottom: '1px solid #f1f3f4', cursor: 'pointer', background: selected?.id === em.id ? '#eaf4f8' : '#fff' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                <code style={{ fontSize: 12, color: '#1a5f7a', fontWeight: 700 }}>{em.request_code}</code>
                <span className="tag">{em.blood_group}</span>
              </div>
              <div style={{ fontSize: 12, color: '#5f6368' }}>{em.hospital_name?.slice(0, 28)}</div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 4 }}>
                <span style={{ fontSize: 11, fontWeight: 700, color: statusColors[em.status] || '#80868b' }}>{em.status}</span>
                <span className={`badge badge-${em.priority === 'CRITICAL' ? 'danger' : em.priority === 'HIGH' ? 'warning' : 'info'}`}>{em.priority}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ flex: 1 }}>
        {showCreate && (
          <div className="card mb-4">
            <div className="card-header"><div className="card-title">Create Emergency Request</div><button className="btn btn-ghost btn-sm" onClick={() => setShowCreate(false)}>Cancel</button></div>
            <div className="card-body">
              <div className="grid-2">
                <div className="form-group">
                  <label className="form-label">Patient ID</label>
                  <input className="form-input" value={newEmForm.patient_id} onChange={e => setNewEmForm(f => ({ ...f, patient_id: e.target.value }))} placeholder="Patient ID" />
                </div>
                <div className="form-group">
                  <label className="form-label">Blood Group</label>
                  <select className="form-select" value={newEmForm.blood_group} onChange={e => setNewEmForm(f => ({ ...f, blood_group: e.target.value }))}>
                    {['O+','O-','A+','A-','B+','B-','AB+','AB-'].map(g => <option key={g}>{g}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Hospital</label>
                  <input className="form-input" value={newEmForm.hospital_name} onChange={e => setNewEmForm(f => ({ ...f, hospital_name: e.target.value }))} placeholder="Hospital name" />
                </div>
                <div className="form-group">
                  <label className="form-label">Priority</label>
                  <select className="form-select" value={newEmForm.priority} onChange={e => setNewEmForm(f => ({ ...f, priority: e.target.value }))}>
                    <option>CRITICAL</option><option>HIGH</option><option>MEDIUM</option><option>LOW</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Units Required</label>
                  <input className="form-input" type="number" min="1" max="10" value={newEmForm.units_required} onChange={e => setNewEmForm(f => ({ ...f, units_required: e.target.value }))} />
                </div>
                <div className="form-group">
                  <label className="form-label">Notes</label>
                  <input className="form-input" value={newEmForm.notes} onChange={e => setNewEmForm(f => ({ ...f, notes: e.target.value }))} placeholder="Clinical notes..." />
                </div>
              </div>
              {createError && <div className="error-state mb-3">{createError}</div>}
              <button className="btn btn-danger" onClick={createEmergency} disabled={actionLoading}><Icon name="zap" size={14} /> {actionLoading ? 'Creating...' : 'Activate Emergency'}</button>
            </div>
          </div>
        )}

        {selected ? (
          <>
            <div className="emergency-banner">
              <div style={{ color: 'rgba(255,255,255,0.75)' }}><Icon name="emergency" size={28} /></div>
              <div className="info">
                <div className="code">EMERGENCY REQUEST #{selected.request_code}</div>
                <div className="meta">Blood Group: <strong>{selected.blood_group}</strong> · Units: {selected.units_required} · Priority: {selected.priority}</div>
                <div className="meta" style={{ marginTop: 4 }}>{selected.hospital_name}</div>
              </div>
              <div>
                <div style={{ fontSize: 12, opacity: 0.8, marginBottom: 4 }}>STATUS</div>
                <div style={{ fontSize: 14, fontWeight: 700 }}>{selected.status}</div>
              </div>
            </div>

            <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
              {['PRIMARY_CONTACTED', 'BACKUP_SEARCH', 'BACKUP_CONTACTED'].includes(selected.status) && (
                <button className="btn btn-danger" onClick={() => doAction('decline')} disabled={actionLoading}><Icon name="x" size={14} /> Process Primary Decline → Activate Swarm</button>
              )}
              {['BACKUP_CONTACTED', 'PRIMARY_CONTACTED', 'ESCALATED'].includes(selected.status) && selected.ranked_candidates?.length > 0 && (
                <button className="btn btn-success" onClick={() => doAction('confirm', { donor_id: selected.ranked_candidates[0]?.donor_id })} disabled={actionLoading}><Icon name="check" size={14} /> Confirm Donor Accepted</button>
              )}
            </div>

            <div className="card">
              <div className="card-header">
                <div className="card-title">Ranked Donor Candidates — Wave {selected.current_wave}</div>
                <span style={{ fontSize: 12, color: '#80868b' }}>{selected.ranked_candidates?.length || 0} candidates</span>
              </div>
              {!selected.ranked_candidates?.length ? (
                <div className="empty-state"><h3>Ranking donors...</h3><p>RATHAM AI is identifying compatible candidates.</p></div>
              ) : (
                selected.ranked_candidates.map((c, i) => (
                  <div key={i} className="donor-card">
                    <div className="donor-rank">{c.rank}</div>
                    <div className="donor-info">
                      <div className="donor-name">{c.name} <span className="tag" style={{ marginLeft: 4 }}>{c.blood_group}</span></div>
                      <div className="donor-meta">{c.donor_code} · {c.distance_km} km</div>
                      <div style={{ marginTop: 6, display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                        {c.why_recommended?.slice(0, 2).map((r, j) => <span key={j} style={{ fontSize: 11, color: '#5f6368' }}>✓ {r}</span>)}
                      </div>
                    </div>
                    <div className="donor-scores">
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: 16, fontWeight: 700, color: c.reachability_probability >= 0.7 ? '#27ae60' : c.reachability_probability >= 0.4 ? '#e67e22' : '#c0392b' }}>{(c.reachability_probability * 100).toFixed(0)}%</div>
                        <div style={{ fontSize: 10, color: '#80868b' }}>Reach</div>
                      </div>
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: 16, fontWeight: 700, color: '#1a5f7a' }}>{(c.match_score * 100).toFixed(0)}</div>
                        <div style={{ fontSize: 10, color: '#80868b' }}>Score</div>
                      </div>
                      {c.burnout_penalty_applied && <span style={{ fontSize: 11, color: '#c0392b', background: '#fdecea', padding: '2px 6px', borderRadius: 4 }}>Burnout ⚠</span>}
                    </div>
                  </div>
                ))
              )}
            </div>
          </>
        ) : (
          <div className="empty-state" style={{ marginTop: 60 }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>🚨</div>
            <h3>Emergency Control Center</h3>
            <p style={{ maxWidth: 340, margin: '8px auto 20px' }}>Select an active emergency from the queue, or create a new request to begin the RATHAM AI donor orchestration workflow.</p>
            <button className="btn btn-danger" onClick={() => setShowCreate(true)}><Icon name="plus" size={14} /> Create Emergency Request</button>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Analytics Page ─────────────────────────
function AnalyticsPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analyticsApi.overview().then(setData).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="page-body"><Skeleton h="400px" /></div>;
  if (!data) return null;

  return (
    <div className="page-body">
      <div className="metrics-grid" style={{ marginBottom: 24 }}>
        <div className="metric-card"><div className="label">Donor Response Rate</div><div className="value">{(data.donor_response_rate * 100).toFixed(0)}%</div></div>
        <div className="metric-card"><div className="label">Avg Fulfillment Time</div><div className="value">{data.avg_fulfillment_time_minutes}m</div></div>
        <div className="metric-card success"><div className="label">Requests Fulfilled</div><div className="value">{data.requests_fulfilled}</div></div>
        <div className="metric-card danger"><div className="label">High Risk Patients</div><div className="value">{data.high_risk_patients}</div></div>
      </div>

      <div className="charts-grid">
        <div className="card">
          <div className="card-header"><div className="card-title">Blood Demand (7 Days)</div></div>
          <div className="card-body"><DailyDemandChart data={data.blood_demand_trend} /></div>
        </div>
        <div className="card">
          <div className="card-header"><div className="card-title">Reachability Distribution</div></div>
          <div className="card-body"><ReachabilityChart data={data.reachability_distribution} /></div>
        </div>
        <div className="card">
          <div className="card-header"><div className="card-title">Donor Engagement Health</div></div>
          <div className="card-body"><BurnoutChart data={data.burnout_distribution} /></div>
        </div>
        <div className="card">
          <div className="card-header"><div className="card-title">Blood Group Distribution (Demand)</div></div>
          <div className="card-body">
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {[['O+', 32], ['A+', 22], ['B+', 18], ['AB+', 10], ['O-', 8], ['A-', 5], ['B-', 4], ['AB-', 1]].map(([grp, pct]) => (
                <div key={grp} style={{ flex: '1 1 80px', textAlign: 'center', padding: '12px 8px', background: '#f8f9fa', borderRadius: 8 }}>
                  <div style={{ fontSize: 18, fontWeight: 700, color: '#1a5f7a' }}>{grp}</div>
                  <div style={{ fontSize: 13, fontWeight: 600 }}>{pct}%</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Model Intelligence Page ─────────────────────────
function ModelsPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminApi.models().then(setData).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="page-body"><Skeleton h="300px" /></div>;
  if (!data) return null;

  const modelDefs = [
    { key: 'need_model', label: '01 — Transfusion Need Forecast', desc: 'Predicts 7-day transfusion need for each monitored patient using Hb levels, historical intervals, fatigue and infection indicators.', features: ['days_since_transfusion', 'usual_interval_days', 'hb_level', 'recent_hb_drop', 'fatigue_score', 'prior_delay_count', 'infection_flag', 'appointment_adherence'], output: ['need_probability', 'risk_level (LOW/MEDIUM/HIGH/CRITICAL)', 'urgency_score'] },
    { key: 'reachability_model', label: '02 — Donor Reachability', desc: 'Estimates the probability that a donor will respond positively to a blood request, accounting for historical response behaviour, contact load and distance.', features: ['response_rate_90d', 'contacts_last_30d', 'avg_response_hours', 'distance_km', 'availability_rate_90d', 'weekday_availability', 'opt_in_active'], output: ['reachability_probability', 'expected_response_minutes', 'reachability_risk_level'] },
    { key: 'burnout_model', label: '03 — Donor Burnout / Disengagement', desc: 'Detects donor engagement fatigue using contact frequency trends, decline rate, opt-out behaviour, and donation frequency metrics.', features: ['contacts_last_14d', 'decline_rate_30d', 'engagement_drop_pct', 'voluntary_opt_outs', 'response_rate_30d'], output: ['burnout_probability', 'burnout_risk_level (HEALTHY/WATCH/HIGH_RISK)', 'recommended_cooldown_days'] },
  ];

  return (
    <div className="page-body">
      <div style={{ marginBottom: 20, padding: '16px 20px', background: '#f8f9fa', borderRadius: 10, border: '1px solid #e8eaed' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
          <Icon name="brain" size={16} />
          <strong style={{ fontSize: 14 }}>RATHAM AI — Custom-Trained XGBoost ML Models</strong>
          <span className={`badge badge-${data.models_loaded ? 'success' : 'danger'}`}>{data.models_loaded ? '3/3 ACTIVE' : 'DEGRADED'}</span>
        </div>
        <p style={{ fontSize: 13, color: '#5f6368', maxWidth: 700 }}>
          Three custom XGBoost classifiers trained on production-grade operational datasets. All outputs are <strong>decision-support signals</strong> — human coordinators retain full operational authority.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
        {modelDefs.map(m => {
          const metrics = data.metrics?.[m.key] || {};
          return (
            <div key={m.key} className="card">
              <div className="card-header">
                <div>
                  <div className="card-title" style={{ fontFamily: 'Outfit', fontSize: 16 }}>{m.label}</div>
                  <div style={{ fontSize: 12, color: '#5f6368', marginTop: 4, maxWidth: 600 }}>{m.desc}</div>
                </div>
                <span className="badge badge-success">ACTIVE</span>
              </div>
              <div className="card-body">
                <div className="grid-3" style={{ marginBottom: 16 }}>
                  <div style={{ padding: 16, background: '#f8f9fa', borderRadius: 8, textAlign: 'center' }}>
                    <div style={{ fontSize: 24, fontWeight: 700, color: '#1a5f7a' }}>{metrics.roc_auc || '—'}</div>
                    <div style={{ fontSize: 11, color: '#80868b', textTransform: 'uppercase' }}>ROC-AUC</div>
                  </div>
                  <div style={{ padding: 16, background: '#f8f9fa', borderRadius: 8, textAlign: 'center' }}>
                    <div style={{ fontSize: 24, fontWeight: 700, color: '#1a5f7a' }}>{metrics.f1 || '—'}</div>
                    <div style={{ fontSize: 11, color: '#80868b', textTransform: 'uppercase' }}>F1 Score</div>
                  </div>
                  <div style={{ padding: 16, background: '#f8f9fa', borderRadius: 8, textAlign: 'center' }}>
                    <div style={{ fontSize: 24, fontWeight: 700, color: '#1a5f7a' }}>{metrics.accuracy || '—'}</div>
                    <div style={{ fontSize: 11, color: '#80868b', textTransform: 'uppercase' }}>Accuracy</div>
                  </div>
                </div>
                <div className="grid-2">
                  <div>
                    <div style={{ fontSize: 11, fontWeight: 700, color: '#5f6368', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 8 }}>Input Features</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                      {(metrics.features || m.features).map(f => <span key={f} className="tag" style={{ fontSize: 11 }}>{f}</span>)}
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: 11, fontWeight: 700, color: '#5f6368', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 8 }}>Model Outputs</div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                      {m.output.map(o => <div key={o} style={{ fontSize: 12, color: '#202124' }}>→ {o}</div>)}
                    </div>
                  </div>
                </div>
                {metrics.rows && (
                  <div style={{ marginTop: 14, fontSize: 12, color: '#80868b' }}>
                    Training dataset: <strong>{metrics.rows?.toLocaleString()} rows</strong> · Precision: {metrics.precision} · Recall: {metrics.recall} · Framework: XGBoost
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ── Scenario Control Center ─────────────────────────
function ScenarioPage() {
  const [emergencies, setEmergencies] = useState([]);
  const [activeEm, setActiveEm] = useState(null);
  const [log, setLog] = useState([]);
  const [loading, setLoading] = useState(false);
  const [patients, setPatients] = useState([]);

  useEffect(() => {
    patientApi.list('?limit=10').then(setPatients).catch(console.error);
    emergencyApi.list().then(data => { setEmergencies(data); if (data.length) setActiveEm(data[0]); }).catch(console.error);
  }, []);

  const addLog = (msg, type = 'info') => setLog(l => [{ msg, type, time: new Date().toLocaleTimeString() }, ...l]);

  const createScenario = async () => {
    setLoading(true);
    const p = patients[0];
    if (!p) { addLog('No patients active. Please add patients.', 'error'); setLoading(false); return; }
    try {
      addLog(`Creating CRITICAL emergency for ${p.name} (${p.blood_group})...`);
      const em = await emergencyApi.create({ patient_id: p.id, blood_group: p.blood_group, units_required: 2, hospital_name: p.hospital_name, priority: 'CRITICAL', notes: 'Emergency scenario request' });
      const full = await emergencyApi.get(em.id);
      setActiveEm(full);
      addLog(`Emergency ${full.request_code} created → Primary donor contacted.`, 'success');
    } catch (e) { addLog(`Error: ${e.message}`, 'error'); }
    setLoading(false);
  };

  const processDecline = async () => {
    if (!activeEm) return;
    setLoading(true);
    try {
      addLog(`Primary donor declined. Activating Emergency Swarm (Wave 2)...`, 'warning');
      await orchestrationApi.processDecline(activeEm.id);
      const full = await emergencyApi.get(activeEm.id);
      setActiveEm(full);
      addLog(`Wave 2 dispatched to ${full.ranked_candidates?.length || 0} backup candidates.`, 'success');
    } catch (e) { addLog(`Error: ${e.message}`, 'error'); }
    setLoading(false);
  };

  const processConfirm = async () => {
    if (!activeEm) return;
    setLoading(true);
    try {
      addLog(`Backup donor accepted! Confirming and marking FULFILLED...`);
      await orchestrationApi.processConfirm(activeEm.id);
      const full = await emergencyApi.get(activeEm.id);
      setActiveEm(full);
      addLog(`Emergency ${full.request_code} → FULFILLED ✓`, 'success');
    } catch (e) { addLog(`Error: ${e.message}`, 'error'); }
    setLoading(false);
  };

  const resetScenario = async () => {
    setLoading(true);
    try {
      await orchestrationApi.reset();
      setActiveEm(null); setLog([]);
      addLog('Scenario state reset. All emergency records cleared.', 'info');
    } catch (e) { addLog(`Error: ${e.message}`, 'error'); }
    setLoading(false);
  };

  return (
    <div className="page-body">
      <div style={{ padding: '16px 20px', background: '#f8f9fa', borderRadius: 10, border: '1px solid #e8eaed', marginBottom: 20, fontSize: 13 }}>
        <strong>⚡ Emergency Scenario Control Center</strong> — Operations management interface for real-time emergency dispatch and swarm orchestration using the live ML inference engine.
      </div>

      <div className="grid-2" style={{ marginBottom: 20 }}>
        <div className="card">
          <div className="card-header"><div className="card-title">Orchestration Controls</div></div>
          <div className="card-body">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <button id="btn-create-emergency" className="btn btn-danger" onClick={createScenario} disabled={loading}>
                <Icon name="zap" size={14} /> 1. Create Critical Emergency + Contact Primary Donor
              </button>
              <button id="btn-simulate-decline" className="btn btn-outline" onClick={processDecline} disabled={loading || !activeEm}>
                <Icon name="x" size={14} /> 2. Process Primary Decline → Activate Swarm (Wave 2)
              </button>
              <button id="btn-simulate-confirm" className="btn btn-success" onClick={processConfirm} disabled={loading || !activeEm}>
                <Icon name="check" size={14} /> 3. Confirm Backup Acceptance → Mark Fulfilled
              </button>
              <hr className="divider" />
              <button id="btn-reset-demo" className="btn btn-ghost" onClick={resetScenario} disabled={loading}>
                <Icon name="refresh" size={14} /> Reset Scenario State
              </button>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header"><div className="card-title">Live Operation Log</div></div>
          <div className="card-body" style={{ fontFamily: 'monospace', fontSize: 12, maxHeight: 280, overflowY: 'auto' }}>
            {log.length === 0 ? <div style={{ color: '#80868b' }}>Click a control button to execute workflow step...</div> :
              log.map((l, i) => (
                <div key={i} style={{ marginBottom: 6, color: l.type === 'error' ? '#c0392b' : l.type === 'success' ? '#27ae60' : l.type === 'warning' ? '#e67e22' : '#202124' }}>
                  <span style={{ color: '#80868b', marginRight: 8 }}>{l.time}</span>{l.msg}
                </div>
              ))
            }
          </div>
        </div>
      </div>

      {activeEm && (
        <div className="card">
          <div className="card-header">
            <div className="card-title">Active Emergency — {activeEm.request_code}</div>
            <span style={{ fontWeight: 700, color: activeEm.status === 'FULFILLED' ? '#27ae60' : '#c0392b' }}>{activeEm.status}</span>
          </div>
          <div className="card-body">
            <div className="grid-3" style={{ marginBottom: 16 }}>
              <div><div style={{ fontSize: 11, color: '#80868b' }}>Blood Group</div><div style={{ fontSize: 18, fontWeight: 700 }}>{activeEm.blood_group}</div></div>
              <div><div style={{ fontSize: 11, color: '#80868b' }}>Priority</div><RiskBadge level={activeEm.priority} /></div>
              <div><div style={{ fontSize: 11, color: '#80868b' }}>Wave</div><div style={{ fontSize: 18, fontWeight: 700 }}>Wave {activeEm.current_wave}</div></div>
            </div>
            {activeEm.ranked_candidates?.length > 0 && (
              <div>
                <div style={{ fontSize: 12, fontWeight: 700, color: '#5f6368', textTransform: 'uppercase', marginBottom: 10 }}>Top Ranked Candidates</div>
                {activeEm.ranked_candidates.slice(0, 3).map((c, i) => (
                  <div key={i} className="donor-card">
                    <div className="donor-rank">{c.rank}</div>
                    <div className="donor-info">
                      <div className="donor-name">{c.name} <span className="tag">{c.blood_group}</span></div>
                      <div className="donor-meta">{c.distance_km}km · Reachability: {(c.reachability_probability * 100).toFixed(0)}% · Score: {(c.match_score * 100).toFixed(0)}</div>
                    </div>
                    {c.burnout_penalty_applied && <span style={{ fontSize: 11, color: '#c0392b', background: '#fdecea', padding: '3px 7px', borderRadius: 4 }}>Burnout ⚠</span>}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// ── Admin / Audit Page ─────────────────────────
function AdminPage() {
  const [audits, setAudits] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminApi.audits().then(setAudits).catch(console.error).finally(() => setLoading(false));
  }, []);

  return (
    <div className="page-body">
      <div style={{ fontSize: 11, color: '#80868b', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 16, fontWeight: 600 }}>AUDIT TRAIL — SYSTEM EVENTS</div>
      <div className="card">
        {loading ? <div className="card-body"><Skeleton h="200px" /></div> :
         audits.length === 0 ? <div className="empty-state"><h3>No audit events</h3></div> : (
          <table className="data-table">
            <thead><tr><th>Timestamp</th><th>Actor</th><th>Action</th><th>Entity</th><th>Details</th></tr></thead>
            <tbody>
              {audits.map(a => (
                <tr key={a.id}>
                  <td style={{ fontSize: 11, color: '#80868b', whiteSpace: 'nowrap' }}>{new Date(a.timestamp).toLocaleString()}</td>
                  <td style={{ fontSize: 12 }}>{a.actor_id}</td>
                  <td><code style={{ fontSize: 11, color: '#1a5f7a', background: '#eaf4f8', padding: '2px 6px', borderRadius: 4 }}>{a.action}</code></td>
                  <td style={{ fontSize: 12 }}>{a.entity_type} / {a.entity_id}</td>
                  <td style={{ fontSize: 11, color: '#5f6368', maxWidth: 200 }}>{a.details ? JSON.stringify(a.details).slice(0, 60) : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

// ── Sidebar ─────────────────────────
function Sidebar({ page, setPage, user, onLogout }) {
  const isSuperAdmin = user?.role === 'SUPER_ADMIN';
  const isCoordinator = user?.role === 'COORDINATOR';

  const nav = isSuperAdmin ? [
    { id: 'dashboard', icon: 'dashboard', label: 'Platform Overview', section: 'ADMINISTRATION' },
    { id: 'admin', icon: 'admin', label: 'Audit Trail & Logs', section: null },
    { id: 'models', icon: 'models', label: 'ML Model Governance', section: null },
    { id: 'analytics', icon: 'analytics', label: 'System Analytics', section: 'INSIGHTS' },
  ] : [
    { id: 'dashboard', icon: 'dashboard', label: 'Operations Dashboard', section: 'OPERATIONS' },
    { id: 'emergency', icon: 'emergency', label: 'Emergency Control Center', section: null },
    { id: 'patients', icon: 'patients', label: 'Patient Intelligence', section: null },
    { id: 'donors', icon: 'donors', label: 'Donor Intelligence', section: null },
    { id: 'analytics', icon: 'analytics', label: 'Operations Analytics', section: 'INSIGHTS' },
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-logo">
        <div className="wordmark"><span style={{ color: '#e74c3c' }}>⬤</span> RATHAM <span>AI</span></div>
        <div className="tagline">Blood Continuity Network</div>
      </div>
      <div className="sidebar-nav">
        {nav.map(n => (
          <React.Fragment key={n.id}>
            {n.section && <div className="nav-section-label">{n.section}</div>}
            <button className={`nav-item ${page === n.id ? 'active' : ''}`} onClick={() => setPage(n.id)}>
              <Icon name={n.icon} size={16} />{n.label}
            </button>
          </React.Fragment>
        ))}
      </div>
      <div className="sidebar-footer">
        <div style={{ marginBottom: 4, color: '#fff', fontWeight: 600, fontSize: 13 }}>{user?.name}</div>
        <div style={{ color: isSuperAdmin ? '#f39c12' : '#3498db', fontSize: 11, fontWeight: 700, letterSpacing: '0.5px' }}>
          {isSuperAdmin ? '⚡ SUPER ADMIN' : isCoordinator ? '🛡 CITY COORDINATOR' : user?.role}
        </div>
        <button className="nav-item" style={{ marginTop: 10, padding: '6px 0', color: 'rgba(255,255,255,0.6)' }} onClick={onLogout}>
          <Icon name="logout" size={14} /> Sign out
        </button>
      </div>
    </div>
  );
}

// ── Page titles ─────────────────────────
const PAGE_TITLES = {
  dashboard: { title: 'Operations Dashboard', subtitle: 'RATHAM AI — Predictive Blood Continuity Intelligence Network' },
  patients: { title: 'Patient Intelligence', subtitle: 'Transfusion need prediction and timeline monitoring' },
  donors: { title: 'Donor Intelligence', subtitle: 'Reachability, engagement health and availability management' },
  emergency: { title: 'Emergency Control Center', subtitle: 'Real-time donor orchestration and swarm dispatch' },
  analytics: { title: 'Operations Analytics', subtitle: 'Operational performance and demand analysis' },
  models: { title: 'ML Model Governance', subtitle: 'Custom-trained XGBoost model metrics and health status' },
  admin: { title: 'Audit Trail & Administration', subtitle: 'System event audit logs and security monitoring' },
};

// ── App Root ─────────────────────────
function App() {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('ratham_user')); } catch { return null; }
  });
  const [page, setPage] = useState('dashboard');
  const [navData, setNavData] = useState(null);

  const handleLogin = (res) => {
    const u = { name: res.name, role: res.role, id: res.user_id };
    setUser(u);
    setPage('dashboard');
  };

  const handleLogout = () => {
    localStorage.removeItem('ratham_token');
    localStorage.removeItem('ratham_user');
    setUser(null);
  };

  const navigateTo = (p, data) => { setPage(p); setNavData(data); };

  if (!user) return <LoginPage onLogin={handleLogin} />;

  const isSuperAdmin = user?.role === 'SUPER_ADMIN';
  const isCoordinator = user?.role === 'COORDINATOR';

  const { title, subtitle } = PAGE_TITLES[page] || PAGE_TITLES.dashboard;
  const renderPage = () => {
    switch (page) {
      case 'dashboard': return <DashboardPage />;
      case 'patients': return <PatientsPage onNavigate={navigateTo} />;
      case 'donors': return <DonorsPage />;
      case 'emergency': return <EmergencyPage initialPatient={navData?.patient} key={navData?.patient?.id} />;
      case 'analytics': return <AnalyticsPage />;
      case 'models': return <ModelsPage />;
      case 'admin': return <AdminPage />;
      default: return <DashboardPage />;
    }
  };

  return (
    <div className="layout">
      <Sidebar page={page} setPage={setPage} user={user} onLogout={handleLogout} />
      <div className="main-content">
        <div className="topbar">
          <div>
            <div className="topbar-title">{title}</div>
            <div className="topbar-subtitle">{subtitle}</div>
          </div>
          <div className="topbar-actions">
            <span style={{ 
              fontSize: 11, 
              fontWeight: 700, 
              padding: '4px 10px', 
              borderRadius: 12, 
              background: isSuperAdmin ? 'rgba(231,76,60,0.12)' : 'rgba(26,95,122,0.12)', 
              color: isSuperAdmin ? '#c0392b' : '#1a5f7a',
              border: `1px solid ${isSuperAdmin ? 'rgba(192,57,43,0.3)' : 'rgba(26,95,122,0.3)'}` 
            }}>
              {isSuperAdmin ? '⚡ SUPER ADMIN COMMAND CENTER' : isCoordinator ? '🛡 CITY COORDINATOR CONSOLE' : `${user?.role} PORTAL`}
            </span>
            <button className="btn btn-outline btn-sm" onClick={() => { setPage('dashboard'); }}>
              <Icon name="refresh" size={13} /> Refresh
            </button>
          </div>
        </div>
        {renderPage()}
      </div>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
