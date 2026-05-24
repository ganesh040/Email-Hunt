import { useState } from 'react'

const CONFIDENCE_MAP = {
  'firstname.lastname': 90,
  'firstnamelastname': 82,
  'flastname': 78,
  'f.lastname': 75,
  'firstname': 60,
  'lastname.firstname': 55,
  'lastname': 45,
  'firstname.l': 40,
}

const SOURCE_LABELS = {
  website: 'Website',
  github_org: 'GitHub Org',
  github_commits: 'GitHub Commits',
  whois: 'WHOIS',
}

const SOURCE_ICONS = {
  website: '🌐',
  github_org: '🐙',
  github_commits: '💻',
  whois: '📋',
}

const SMTP_BADGE = {
  valid: { label: 'Verified', color: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20' },
  invalid: { label: 'Invalid', color: 'text-red-400 bg-red-400/10 border-red-400/20' },
  unknown: { label: 'Unverified', color: 'text-amber-400 bg-amber-400/10 border-amber-400/20' },
  no_mx_record: { label: 'No MX', color: 'text-gray-400 bg-gray-400/10 border-gray-400/20' },
}

function ConfidenceBar({ pattern }) {
  const score = CONFIDENCE_MAP[pattern] || 40
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1 bg-white/10 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{
            width: `${score}%`,
            background: score >= 80
              ? 'linear-gradient(90deg, #34d399, #10b981)'
              : score >= 60
              ? 'linear-gradient(90deg, #fbbf24, #f59e0b)'
              : 'linear-gradient(90deg, #f87171, #ef4444)'
          }}
        />
      </div>
      <span className="text-xs font-mono text-white/40">{score}%</span>
    </div>
  )
}

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false)
  const handleCopy = () => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  return (
    <button
      onClick={handleCopy}
      className="text-xs px-2 py-1 rounded-md border border-white/10 text-white/40 hover:text-white hover:border-white/30 transition-all"
    >
      {copied ? '✓ copied' : 'copy'}
    </button>
  )
}

export default function App() {
  const [form, setForm] = useState({ first_name: '', last_name: '', domain: '' })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async () => {
    if (!form.first_name || !form.last_name || !form.domain) return
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await fetch('http://127.0.0.1:8000/api/find-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      })
      const data = await res.json()
      setResult(data)
    } catch (e) {
      setError('Could not connect to backend. Make sure FastAPI is running.')
    } finally {
      setLoading(false)
    }
  }

  const topCandidate = result?.candidates?.[0]

  return (
    <div className="min-h-screen bg-[#020817] text-white overflow-x-hidden">

      {/* Background blobs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] rounded-full opacity-20"
          style={{ background: 'radial-gradient(circle, #6366f1 0%, transparent 70%)' }} />
        <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] rounded-full opacity-15"
          style={{ background: 'radial-gradient(circle, #06b6d4 0%, transparent 70%)' }} />
        <div className="absolute top-[40%] left-[50%] w-[400px] h-[400px] rounded-full opacity-10"
          style={{ background: 'radial-gradient(circle, #8b5cf6 0%, transparent 70%)' }} />
      </div>

      <div className="relative z-10 max-w-2xl mx-auto px-6 py-16">

        {/* Header */}
        <div className="mb-12 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-300 text-xs font-mono mb-6">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
            email intelligence
          </div>
          <h1 className="text-5xl font-black tracking-tight mb-3"
            style={{ fontFamily: 'Syne, sans-serif' }}>
            Email<span className="text-transparent bg-clip-text"
              style={{ backgroundImage: 'linear-gradient(135deg, #6366f1, #06b6d4)' }}>Hunt</span>
          </h1>
          <p className="text-white/40 text-sm font-mono">
            find anyone's work email using public data
          </p>
        </div>

        {/* Input Card */}
        <div className="rounded-2xl border border-white/10 p-6 mb-6"
          style={{
            background: 'rgba(255,255,255,0.03)',
            backdropFilter: 'blur(20px)',
            boxShadow: '0 0 0 1px rgba(255,255,255,0.05), 0 20px 40px rgba(0,0,0,0.4)'
          }}>

          <div className="grid grid-cols-2 gap-3 mb-3">
            <div>
              <label className="block text-xs font-mono text-white/40 mb-1.5">First name</label>
              <input
                type="text"
                placeholder="Marzhan"
                value={form.first_name}
                onChange={e => setForm({ ...form, first_name: e.target.value })}
                className="w-full px-3 py-2.5 rounded-xl border border-white/10 bg-white/5 text-white placeholder-white/20 text-sm focus:outline-none focus:border-indigo-500/50 focus:bg-white/8 transition-all"
              />
            </div>
            <div>
              <label className="block text-xs font-mono text-white/40 mb-1.5">Last name</label>
              <input
                type="text"
                placeholder="Anglamas"
                value={form.last_name}
                onChange={e => setForm({ ...form, last_name: e.target.value })}
                className="w-full px-3 py-2.5 rounded-xl border border-white/10 bg-white/5 text-white placeholder-white/20 text-sm focus:outline-none focus:border-indigo-500/50 transition-all"
              />
            </div>
          </div>

          <div className="mb-4">
            <label className="block text-xs font-mono text-white/40 mb-1.5">Company domain</label>
            <input
              type="text"
              placeholder="wise.com"
              value={form.domain}
              onChange={e => setForm({ ...form, domain: e.target.value })}
              className="w-full px-3 py-2.5 rounded-xl border border-white/10 bg-white/5 text-white placeholder-white/20 text-sm focus:outline-none focus:border-indigo-500/50 transition-all"
            />
          </div>

          <button
            onClick={handleSubmit}
            disabled={loading || !form.first_name || !form.last_name || !form.domain}
            className="w-full py-3 rounded-xl font-semibold text-sm transition-all disabled:opacity-40 disabled:cursor-not-allowed"
            style={{
              background: loading ? 'rgba(99,102,241,0.3)' : 'linear-gradient(135deg, #6366f1, #06b6d4)',
              boxShadow: loading ? 'none' : '0 0 30px rgba(99,102,241,0.3)'
            }}
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                </svg>
                Hunting...
              </span>
            ) : 'Find Email'}
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-red-400 text-sm mb-6">
            {error}
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-4">

            {/* Top Guess */}
            {topCandidate && (
              <div className="rounded-2xl border p-5"
                style={{
                  borderColor: 'rgba(99,102,241,0.3)',
                  background: 'rgba(99,102,241,0.06)',
                  backdropFilter: 'blur(20px)',
                  boxShadow: '0 0 40px rgba(99,102,241,0.1)'
                }}>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-mono text-indigo-400">top guess</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full border font-mono ${SMTP_BADGE[topCandidate.smtp_result]?.color}`}>
                    {SMTP_BADGE[topCandidate.smtp_result]?.label}
                  </span>
                </div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xl font-mono font-medium tracking-tight">
                    {topCandidate.email}
                  </span>
                  <CopyButton text={topCandidate.email} />
                </div>
                <ConfidenceBar pattern={topCandidate.pattern} />
                <div className="mt-2 flex items-center gap-2">
                  <span className="text-xs font-mono text-white/30">pattern:</span>
                  <span className="text-xs font-mono text-indigo-300">{topCandidate.pattern}</span>
                  {result.detected_pattern && (
                    <span className="text-xs font-mono text-white/20 ml-auto">
                      detected from {result.found_on_web.length} real email{result.found_on_web.length !== 1 ? 's' : ''}
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* All Pattern Guesses */}
            <div className="rounded-2xl border border-white/10 p-5"
              style={{
                background: 'rgba(255,255,255,0.02)',
                backdropFilter: 'blur(20px)'
              }}>
              <h3 className="text-xs font-mono text-white/40 mb-4">all pattern guesses</h3>
              <div className="space-y-3">
                {result.candidates.map((c, i) => (
                  <div key={i} className={`flex items-center justify-between py-2 px-3 rounded-xl transition-all ${i === 0 ? 'bg-white/5' : ''}`}>
                    <div className="flex-1 min-w-0 mr-3">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-mono text-white/80 truncate">{c.email}</span>
                        {i === 0 && <span className="text-xs text-indigo-400 font-mono shrink-0">★ best</span>}
                      </div>
                      <ConfidenceBar pattern={c.pattern} />
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <span className="text-xs font-mono text-white/30 hidden sm:block">{c.pattern}</span>
                      <CopyButton text={c.email} />
                    </div>
                  </div>
                ))}
              </div>

              {/* All patterns list */}
              <div className="mt-4 pt-4 border-t border-white/5">
                <p className="text-xs font-mono text-white/20 mb-2">all generated variants</p>
                <div className="flex flex-wrap gap-2">
                  {result.all_patterns.map((email, i) => (
                    <span key={i} className="text-xs font-mono px-2 py-1 rounded-lg bg-white/5 text-white/40 border border-white/5">
                      {email}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Sources Breakdown */}
            <div className="rounded-2xl border border-white/10 p-5"
              style={{
                background: 'rgba(255,255,255,0.02)',
                backdropFilter: 'blur(20px)'
              }}>
              <h3 className="text-xs font-mono text-white/40 mb-4">sources breakdown</h3>
              <div className="space-y-3">
                {Object.entries(result.sources).map(([source, emails]) => (
                  <div key={source} className="flex items-start gap-3">
                    <span className="text-base mt-0.5">{SOURCE_ICONS[source]}</span>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-mono text-white/50">{SOURCE_LABELS[source]}</span>
                        <span className="text-xs font-mono text-white/20">
                          {emails.length} found
                        </span>
                      </div>
                      {emails.length > 0 ? (
                        <div className="flex flex-wrap gap-1.5">
                          {emails.map((email, i) => (
                            <div key={i} className="flex items-center gap-1.5 px-2 py-1 rounded-lg border border-emerald-500/20 bg-emerald-500/5">
                              <span className="text-xs font-mono text-emerald-300">{email}</span>
                              <CopyButton text={email} />
                            </div>
                          ))}
                        </div>
                      ) : (
                        <span className="text-xs font-mono text-white/20">nothing found</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        )}
      </div>
    </div>
  )
}
