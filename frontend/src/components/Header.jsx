import { Leaf, Github } from 'lucide-react'

export default function Header() {
  return (
    <header style={{
      borderBottom: '1px solid var(--border)',
      background:   'rgba(10,15,10,0.85)',
      backdropFilter: 'blur(12px)',
      position:     'sticky',
      top:          0,
      zIndex:       100,
    }}>
      <div style={{
        maxWidth:   '1200px',
        margin:     '0 auto',
        padding:    '0 24px',
        height:     '60px',
        display:    'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width:        34,
            height:       34,
            borderRadius: 10,
            background:   'linear-gradient(135deg, #166116, #0a3d0a)',
            border:       '1px solid var(--green-700)',
            display:      'flex',
            alignItems:   'center',
            justifyContent: 'center',
          }}>
            <Leaf size={18} color="var(--green-400)" />
          </div>
          <span style={{
            fontFamily:  'var(--font-display)',
            fontSize:    '1.15rem',
            fontWeight:  800,
            color:       'var(--text-primary)',
            letterSpacing: '-0.01em',
          }}>
            GreenDev<span style={{ color: 'var(--green-400)' }}> AI</span>
          </span>
        </div>

        {/* Nav */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
          <span className="pill pill-green">
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--green-400)', display: 'inline-block' }} />
            Multi-Agent Pipeline
          </span>
          <a
            href="https://github.com"
            target="_blank"
            rel="noreferrer"
            style={{ color: 'var(--text-secondary)', transition: 'var(--transition)' }}
            onMouseEnter={e => e.target.style.color = 'var(--text-primary)'}
            onMouseLeave={e => e.target.style.color = 'var(--text-secondary)'}
          >
            <Github size={20} />
          </a>
        </div>
      </div>
    </header>
  )
}
