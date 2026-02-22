export default function MetricCard({ title, value, trend, caption }) {
  return (
    <div className="card">
      <div className="muted">{title}</div>
      <div style={{ fontSize: '1.8rem', fontWeight: 700, marginTop: '0.4rem' }}>{value}</div>
      <div style={{ marginTop: '0.35rem', color: '#334155', fontWeight: 600 }}>{trend}</div>
      <div className="muted" style={{ marginTop: '0.25rem' }}>{caption}</div>
    </div>
  )
}
