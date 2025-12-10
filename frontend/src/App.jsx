import { useCallback, useEffect, useMemo, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

const PRESET_TICKERS = [
  { label: 'Apple', value: 'AAPL' },
  { label: 'Microsoft', value: 'MSFT' },
  { label: 'NVIDIA', value: 'NVDA' },
  { label: 'Tesla', value: 'TSLA' },
]

const DEV_BACKEND_URL = 'https://investment-backend.redcliff-52269089.francecentral.azurecontainerapps.io'
const PROD_BACKEND_URL = 'https://investment-backend.redcliff-52269089.francecentral.azurecontainerapps.io'

const DEFAULT_API_BASE_URL = (() => {
  const configured = import.meta.env.VITE_API_URL?.trim()
  if (configured) {
    return configured.replace(/\/$/, '')
  }
  const fallback = import.meta.env.DEV ? DEV_BACKEND_URL : PROD_BACKEND_URL
  return fallback.replace(/\/$/, '')
})()

const markdownComponents = {
  h1: ({ children, ...props }) => (
    <h1 {...props} className="mt-6 text-2xl font-semibold text-white">
      {children}
    </h1>
  ),
  h2: ({ children, ...props }) => (
    <h2 {...props} className="mt-5 text-xl font-semibold text-white">
      {children}
    </h2>
  ),
  h3: ({ children, ...props }) => (
    <h3 {...props} className="mt-4 text-lg font-semibold text-white">
      {children}
    </h3>
  ),
  p: ({ children, ...props }) => (
    <p {...props} className="mt-3 text-sm leading-relaxed text-slate-200">
      {children}
    </p>
  ),
  ul: ({ children, ...props }) => (
    <ul {...props} className="mt-3 list-disc space-y-2 pl-5 text-sm text-slate-200">
      {children}
    </ul>
  ),
  ol: ({ children, ...props }) => (
    <ol {...props} className="mt-3 list-decimal space-y-2 pl-5 text-sm text-slate-200">
      {children}
    </ol>
  ),
  li: ({ children, ...props }) => (
    <li {...props} className="leading-relaxed text-slate-200">
      {children}
    </li>
  ),
  strong: ({ children, ...props }) => (
    <strong {...props} className="font-semibold text-white">
      {children}
    </strong>
  ),
  em: ({ children, ...props }) => (
    <em {...props} className="italic text-slate-200">
      {children}
    </em>
  ),
  blockquote: ({ children, ...props }) => (
    <blockquote
      {...props}
      className="mt-4 border-l-4 border-emerald-500/60 bg-slate-900/60 px-4 py-2 text-sm italic text-slate-200"
    >
      {children}
    </blockquote>
  ),
  code: ({ inline, children, ...props }) =>
    inline ? (
      <code {...props} className="rounded bg-slate-900/80 px-1.5 py-0.5 text-[13px] text-emerald-200">
        {children}
      </code>
    ) : (
      <pre className="mt-4 overflow-x-auto rounded-lg border border-slate-800/60 bg-slate-950/90 p-4 text-sm text-emerald-200">
        <code {...props}>{children}</code>
      </pre>
    ),
  table: ({ children, ...props }) => (
    <div className="mt-4 overflow-x-auto">
      <table {...props} className="min-w-full border-collapse border border-slate-700/60">
        {children}
      </table>
    </div>
  ),
  th: ({ children, ...props }) => (
    <th
      {...props}
      className="border border-slate-700/60 bg-slate-900 px-3 py-2 text-left text-xs font-semibold text-slate-200"
    >
      {children}
    </th>
  ),
  td: ({ children, ...props }) => (
    <td {...props} className="border border-slate-800/60 px-3 py-2 text-xs text-slate-200">
      {children}
    </td>
  ),
  a: ({ children, ...props }) => (
    <a {...props} className="text-emerald-300 underline decoration-emerald-500/60 hover:text-emerald-200">
      {children}
    </a>
  ),
}

function normalizeReportPayload(data) {
  if (!data || typeof data !== 'object') return null
  const identifier = data.id ?? data.reportId ?? null
  return {
    ...data,
    id: identifier,
  }
}

function formatTimestamp(isoString) {
  if (!isoString) return 'Unknown'
  const date = new Date(isoString)
  if (Number.isNaN(date.getTime())) return 'Unknown'
  return date.toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}

export default function App() {
  const [ticker, setTicker] = useState('')
  const [companyName, setCompanyName] = useState('')
  const [mode, setMode] = useState('team')
  const [saveToFile, setSaveToFile] = useState(true)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState('')
  const [report, setReport] = useState(null)

  const [history, setHistory] = useState([])
  const [historyError, setHistoryError] = useState('')
  const [isLoadingHistory, setIsLoadingHistory] = useState(false)

  const [selectedReportId, setSelectedReportId] = useState('')
  const [selectedReport, setSelectedReport] = useState(null)
  const [selectedReportError, setSelectedReportError] = useState('')
  const [isLoadingReportDetail, setIsLoadingReportDetail] = useState(false)

  const [copied, setCopied] = useState(false)

  const [chatMessages, setChatMessages] = useState([])
  const [chatInput, setChatInput] = useState('')
  const [chatError, setChatError] = useState('')
  const [isChatLoading, setIsChatLoading] = useState(false)

  const apiBaseUrl = useMemo(() => DEFAULT_API_BASE_URL, [])

  const resolveApiUrl = useCallback(
    (path) => {
      if (/^https?:\/\//i.test(path)) {
        return path
      }
      const normalised = path.startsWith('/') ? path : `/${path}`
      return `${apiBaseUrl}${normalised}`
    },
    [apiBaseUrl],
  )

  const loadHistory = useCallback(async () => {
    setIsLoadingHistory(true)
    setHistoryError('')

    try {
      const response = await fetch(resolveApiUrl('/api/reports'))
      if (!response.ok) {
        const { error: message } = await response.json().catch(() => ({ error: '' }))
        throw new Error(message || 'Unable to load saved reports.')
      }

      const payload = await response.json()
      const items = Array.isArray(payload.items) ? payload.items : []
      const normalized = items
        .map((item) => normalizeReportPayload(item))
        .filter(Boolean)
      setHistory(normalized)
    } catch (err) {
      console.error(err)
      setHistoryError(err.message || 'Unable to load saved reports.')
    } finally {
      setIsLoadingHistory(false)
    }
  }, [resolveApiUrl])

  const fetchReportDetail = useCallback(
    async (id) => {
      if (!id) return null
      setIsLoadingReportDetail(true)
      setSelectedReport(null)
      try {
        const response = await fetch(resolveApiUrl(`/api/reports/${id}`))
        const payload = await response.json().catch(() => ({}))
        if (!response.ok) {
          throw new Error(payload.error || 'Unable to load report.')
        }
        return normalizeReportPayload(payload)
      } finally {
        setIsLoadingReportDetail(false)
      }
    },
    [resolveApiUrl],
  )

  useEffect(() => {
    loadHistory()
  }, [loadHistory])

  const handleSubmit = useCallback(
    async (event) => {
      event.preventDefault()
      const trimmedTicker = ticker.trim().toUpperCase()

      if (!trimmedTicker) {
        setError('Please enter a valid stock ticker (e.g., AAPL).')
        return
      }

      setIsGenerating(true)
      setError('')
      setReport(null)

      try {
        const response = await fetch(resolveApiUrl('/api/reports'), {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            ticker: trimmedTicker,
            companyName: companyName.trim() || undefined,
            mode,
            saveToFile,
          }),
        })

        const payload = await response.json().catch(() => ({}))

        if (!response.ok) {
          throw new Error(payload.error || 'Report generation failed. Please try again.')
        }

        const normalized = normalizeReportPayload(payload)
        setReport(normalized)
        setTicker(trimmedTicker)
        setSelectedReportId(normalized?.id ?? '')
        setSelectedReport(normalized)
        setChatMessages([])
        setChatInput('')
        setChatError('')
        await loadHistory()
      } catch (err) {
        console.error(err)
        setError(err.message || 'Report generation failed. Please try again.')
      } finally {
        setIsGenerating(false)
      }
    },
    [ticker, companyName, mode, saveToFile, resolveApiUrl, loadHistory],
  )

  const handleCopyReport = useCallback(async () => {
    if (!report?.reportMarkdown) return
    try {
      await navigator.clipboard.writeText(report.reportMarkdown)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error(err)
      setError('Unable to copy report to clipboard in this browser context.')
    }
  }, [report])

  const handleSelectReport = useCallback(
    async (record) => {
      if (!record?.id) return
      setSelectedReportId(record.id)
      setSelectedReportError('')
      setChatError('')
      setChatMessages([])

      if (report?.id === record.id && report?.reportMarkdown) {
        setSelectedReport(report)
        return
      }

      try {
        const detail = await fetchReportDetail(record.id)
        setSelectedReport(detail)
      } catch (err) {
        console.error(err)
        setSelectedReportError(err.message || 'Unable to load report detail.')
      }
    },
    [fetchReportDetail, report],
  )

  const handleChatSubmit = useCallback(
    async (event) => {
      event.preventDefault()
      const trimmed = chatInput.trim()
      if (!trimmed || !selectedReport?.id) return

      setChatError('')
      setChatInput('')
      setChatMessages((prev) => [...prev, { role: 'user', content: trimmed }])
      setIsChatLoading(true)

      try {
        const response = await fetch(resolveApiUrl('/api/chat'), {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: trimmed,
            reportId: selectedReport.id,
          }),
        })

        const payload = await response.json().catch(() => ({}))
        if (!response.ok) {
          throw new Error(payload.error || 'Chat request failed.')
        }

        setChatMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: payload.reply,
            sources: Array.isArray(payload.sourceChunks) ? payload.sourceChunks : [],
          },
        ])
      } catch (err) {
        console.error(err)
        setChatError(err.message || 'Chat request failed.')
      } finally {
        setIsChatLoading(false)
      }
    },
    [chatInput, resolveApiUrl, selectedReport],
  )

  const disableSubmit = isGenerating || !ticker.trim()
  const disableChatSubmit = isChatLoading || !chatInput.trim() || !selectedReport?.id

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 bg-slate-900/70 backdrop-blur">
        <div className="mx-auto flex max-w-6xl flex-col gap-4 px-6 py-10 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight text-white md:text-4xl">Investment Intelligence Hub</h1>
            <p className="mt-2 max-w-2xl text-sm text-slate-300 md:text-base">
              Run the multi-agent Gemini workflow directly from your browser. Generate polished Markdown and PDF investment
              reports, browse saved insights, and interrogate them with the embedded finance chatbot.
            </p>
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-900 px-4 py-3 text-xs text-slate-300">
            <p className="font-semibold text-slate-100">API Endpoint</p>
            <p className="truncate text-emerald-300">{apiBaseUrl || 'Current origin'}</p>
            <p className="mt-1 text-[11px] text-slate-400">
              Mode: {mode === 'team' ? 'Multi-agent team (Gemini 4 agents)' : 'Single analyst (lightweight)'}
            </p>
          </div>
        </div>
      </header>

      <main className="mx-auto flex max-w-6xl flex-col gap-8 px-6 py-10 lg:flex-row">
        <section className="w-full space-y-6 lg:w-[380px]">
          <form
            onSubmit={handleSubmit}
            className="space-y-6 rounded-2xl border border-slate-800 bg-slate-900/50 p-6 shadow-xl shadow-emerald-500/5"
          >
            <div>
              <label htmlFor="ticker" className="block text-sm font-medium text-slate-300">
                Stock ticker
              </label>
              <div className="mt-2 flex gap-2">
                <input
                  id="ticker"
                  type="text"
                  value={ticker}
                  onChange={(event) => setTicker(event.target.value.toUpperCase())}
                  placeholder="AAPL"
                  className="w-full rounded-lg border border-slate-700 bg-slate-950/70 px-4 py-3 text-sm uppercase tracking-widest text-white outline-none transition focus:border-emerald-400"
                  autoComplete="off"
                  required
                />
              </div>
              <div className="mt-3 flex flex-wrap gap-2">
                {PRESET_TICKERS.map((preset) => (
                  <button
                    key={preset.value}
                    type="button"
                    onClick={() => setTicker(preset.value)}
                    className="rounded-full border border-slate-700 px-3 py-1 text-xs font-semibold text-slate-300 transition hover:border-emerald-400 hover:text-emerald-300"
                  >
                    {preset.label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label htmlFor="companyName" className="block text-sm font-medium text-slate-300">
                Company name (optional)
              </label>
              <input
                id="companyName"
                type="text"
                value={companyName}
                onChange={(event) => setCompanyName(event.target.value)}
                placeholder="Apple Inc."
                className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none transition focus:border-emerald-400"
                autoComplete="organization"
              />
            </div>

            <fieldset className="space-y-3">
              <legend className="text-sm font-medium text-slate-300">Analysis mode</legend>
              <label className="flex cursor-pointer items-center gap-3 rounded-xl border border-slate-800 bg-slate-950/70 p-4 transition hover:border-emerald-400">
                <input
                  type="radio"
                  name="mode"
                  value="team"
                  checked={mode === 'team'}
                  onChange={() => setMode('team')}
                  className="h-4 w-4 text-emerald-400 focus:ring-emerald-500"
                />
                <div className="space-y-1">
                  <p className="text-sm font-semibold text-white">Multi-agent (comprehensive)</p>
                  <p className="text-xs text-slate-400">
                    Deploys the full team of Gemini agents with research, sentiment, analysis, and reporting roles.
                  </p>
                </div>
              </label>
              <label className="flex cursor-pointer items-center gap-3 rounded-xl border border-slate-800 bg-slate-950/70 p-4 transition hover:border-emerald-400">
                <input
                  type="radio"
                  name="mode"
                  value="simple"
                  checked={mode === 'simple'}
                  onChange={() => setMode('simple')}
                  className="h-4 w-4 text-emerald-400 focus:ring-emerald-500"
                />
                <div className="space-y-1">
                  <p className="text-sm font-semibold text-white">Single analyst (fast)</p>
                  <p className="text-xs text-slate-400">
                    Lightweight one-agent workflow optimised for Gemini free tier and quick iterations.
                  </p>
                </div>
              </label>
            </fieldset>

            <label className="flex items-start gap-3 rounded-xl border border-slate-800 bg-slate-950/70 p-4 text-sm text-slate-300 transition hover:border-emerald-400">
              <input
                type="checkbox"
                checked={saveToFile}
                onChange={(event) => setSaveToFile(event.target.checked)}
                className="mt-1 h-4 w-4 text-emerald-400 focus:ring-emerald-500"
              />
              <span>
                Save Markdown + PDF to <code className="font-mono text-xs text-emerald-300">reports/output/</code>
              </span>
            </label>

            {error && (
              <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">{error}</div>
            )}

            <button
              type="submit"
              disabled={disableSubmit}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-500 px-4 py-3 text-sm font-semibold text-emerald-950 transition hover:bg-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-300 disabled:cursor-not-allowed disabled:bg-emerald-700/50"
            >
              {isGenerating ? 'Generating report…' : 'Generate report'}
            </button>
            <p className="text-xs text-slate-500">
              This process calls Gemini APIs and can take up to a minute for the full team workflow.
            </p>
          </form>
        </section>

        <section className="flex-1 space-y-6">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-6">
            <div className="flex items-center justify-between gap-4">
              <h2 className="text-lg font-semibold text-white">Latest report</h2>
              {report?.reportMarkdown && (
                <button
                  onClick={handleCopyReport}
                  className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-semibold text-slate-200 transition hover:border-emerald-400 hover:text-emerald-300"
                >
                  {copied ? 'Copied!' : 'Copy Markdown'}
                </button>
              )}
            </div>

            {!report && !isGenerating && (
              <div className="mt-6 rounded-xl border border-dashed border-slate-700 bg-slate-900/70 p-6 text-sm text-slate-400">
                Submit a ticker to see the generated analysis. Saved reports appear below for quick access.
              </div>
            )}

            {isGenerating && (
              <div className="mt-6 space-y-3 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-6 text-sm text-emerald-100">
                <p className="font-semibold">Crunching market intelligence…</p>
                <p>
                  The agents are collaborating with Gemini. You can continue working elsewhere; we&apos;ll surface the report
                  automatically once it&apos;s ready.
                </p>
              </div>
            )}

            {report?.reportMarkdown && (
              <div className="mt-6 space-y-4">
                <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4 text-xs text-slate-300">
                  <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-slate-400">
                    <span className="font-semibold text-emerald-300">{report.ticker}</span>
                    <span>{report.mode === 'team' ? 'Multi-agent workflow' : 'Single analyst workflow'}</span>
                    <span>{formatTimestamp(report.createdAt || report.timestamp)}</span>
                  </div>
                </div>
                <article className="max-h-[520px] overflow-y-auto rounded-xl border border-slate-800 bg-slate-950/80 p-4 text-left">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={markdownComponents}
                    className="space-y-4 text-sm leading-relaxed text-slate-200"
                  >
                    {report.reportMarkdown}
                  </ReactMarkdown>
                </article>
                {report.downloads?.length > 0 && (
                  <div className="flex flex-wrap gap-3">
                    {report.downloads.map((item) => (
                      <a
                        key={`${item.url}-${item.label}`}
                        href={resolveApiUrl(item.url)}
                        target="_blank"
                        rel="noreferrer"
                        className="rounded-lg border border-emerald-500/40 px-3 py-2 text-xs font-semibold text-emerald-200 transition hover:border-emerald-400 hover:text-emerald-100"
                      >
                        Download {item.label}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-6">
            <div className="flex items-center justify-between gap-4">
              <h2 className="text-lg font-semibold text-white">Saved analyses</h2>
              <button
                onClick={loadHistory}
                className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-semibold text-slate-200 transition hover:border-emerald-400 hover:text-emerald-300"
              >
                Refresh
              </button>
            </div>
            <p className="mt-1 text-xs text-slate-400">
              Generated reports are stored with embeddings for retrieval-augmented chat. Downloads remain protected behind the API.
            </p>

            {historyError && (
              <div className="mt-4 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-xs text-red-200">
                {historyError}
              </div>
            )}

            {isLoadingHistory ? (
              <p className="mt-6 text-sm text-slate-400">Loading saved reports…</p>
            ) : history.length === 0 ? (
              <p className="mt-6 text-sm text-slate-400">No saved reports yet. Generate one to populate this list.</p>
            ) : (
              <ul className="mt-6 space-y-3 text-sm">
                {history.map((item) => {
                  const isActive = item.id && item.id === selectedReportId
                  return (
                    <li
                      key={item.id}
                      className={`rounded-xl border p-4 transition ${
                        isActive ? 'border-emerald-400/60 bg-emerald-500/10' : 'border-slate-800 bg-slate-950/70'
                      }`}
                    >
                      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                        <div>
                          <p className="font-semibold text-white">
                            {item.ticker}{' '}
                            <span className="text-xs font-normal text-slate-400">{item.companyName || 'Company name unavailable'}</span>
                          </p>
                          <p className="text-xs text-slate-400">
                            {item.mode === 'team' ? 'Multi-agent' : 'Single analyst'} • Saved {formatTimestamp(item.createdAt)}
                          </p>
                          <p className="mt-2 text-xs text-slate-400">
                            {item.preview || 'No preview available. Open the report to view its content.'}
                          </p>
                        </div>
                        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
                          <button
                            type="button"
                            onClick={() => handleSelectReport(item)}
                            className="rounded-lg border border-emerald-500/40 px-3 py-2 text-xs font-semibold text-emerald-200 transition hover:border-emerald-400 hover:text-emerald-100"
                          >
                            View &amp; chat
                          </button>
                          {item.downloads?.map((download) => (
                            <a
                              key={`${download.url}-${download.label}`}
                              href={resolveApiUrl(download.url)}
                              target="_blank"
                              rel="noreferrer"
                              className="rounded-lg border border-slate-700 px-3 py-2 text-xs font-semibold text-slate-200 transition hover:border-emerald-400 hover:text-emerald-300"
                            >
                              {download.label}
                            </a>
                          ))}
                        </div>
                      </div>
                    </li>
                  )
                })}
              </ul>
            )}
          </div>

          {(selectedReport || isLoadingReportDetail || selectedReportError) && (
            <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-6">
              <div className="flex items-center justify-between gap-4">
                <h2 className="text-lg font-semibold text-white">Report workspace</h2>
                {selectedReport?.downloads?.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {selectedReport.downloads.map((item) => (
                      <a
                        key={`${item.url}-${item.label}`}
                        href={resolveApiUrl(item.url)}
                        target="_blank"
                        rel="noreferrer"
                        className="rounded-lg border border-emerald-500/40 px-3 py-1.5 text-xs font-semibold text-emerald-200 transition hover:border-emerald-400 hover:text-emerald-100"
                      >
                        {item.label}
                      </a>
                    ))}
                  </div>
                )}
              </div>

              {selectedReportError && (
                <div className="mt-4 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-xs text-red-200">
                  {selectedReportError}
                </div>
              )}

              {isLoadingReportDetail && (
                <p className="mt-6 text-sm text-slate-400">Loading report detail…</p>
              )}

              {selectedReport && (
                <div className="mt-6 space-y-5">
                  <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4 text-xs text-slate-300">
                    <div className="flex flex-wrap items-center gap-3 text-slate-400">
                      <span className="font-semibold text-emerald-300">{selectedReport.ticker}</span>
                      <span>{selectedReport.companyName || 'Company name unavailable'}</span>
                      <span>{selectedReport.mode === 'team' ? 'Multi-agent workflow' : 'Single analyst workflow'}</span>
                      <span>{formatTimestamp(selectedReport.createdAt)}</span>
                    </div>
                  </div>

                  <article className="max-h-[340px] overflow-y-auto rounded-xl border border-slate-800 bg-slate-950/80 p-4 text-left">
                    {selectedReport.reportMarkdown ? (
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={markdownComponents}
                        className="space-y-4 text-sm leading-relaxed text-slate-200"
                      >
                        {selectedReport.reportMarkdown}
                      </ReactMarkdown>
                    ) : (
                      <p className="text-xs text-slate-400">No Markdown content available.</p>
                    )}
                  </article>

                  <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-4">
                    <div className="flex items-center justify-between gap-3">
                      <h3 className="text-sm font-semibold text-white">Chat about this report</h3>
                      {isChatLoading && <span className="text-[11px] text-emerald-300">Thinking…</span>}
                    </div>
                    <p className="mt-1 text-[11px] text-slate-400">
                      Answers are grounded in the stored report excerpts. The assistant cites excerpt numbers when applicable.
                    </p>

                    <div className="mt-4 max-h-64 space-y-3 overflow-y-auto">
                      {chatMessages.length === 0 ? (
                        <p className="text-xs text-slate-400">Ask a question to start the conversation.</p>
                      ) : (
                        chatMessages.map((message, index) => (
                          <div
                            key={`${message.role}-${index}`}
                            className={`rounded-lg border px-4 py-3 text-sm ${
                              message.role === 'assistant'
                                ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-100'
                                : 'border-slate-700 bg-slate-950/80 text-slate-200'
                            }`}
                          >
                            <p className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                              {message.role === 'assistant' ? 'Assistant' : 'You'}
                            </p>
                            <div className="space-y-3 text-xs leading-relaxed text-slate-200">
                              <ReactMarkdown
                                remarkPlugins={[remarkGfm]}
                                components={markdownComponents}
                                className="space-y-3 text-xs leading-relaxed text-slate-200"
                              >
                                {message.content}
                              </ReactMarkdown>
                            </div>
                            {Array.isArray(message.sources) && message.sources.length > 0 && (
                              <div className="mt-3 space-y-1 text-[11px] text-slate-300">
                                <p className="font-semibold text-slate-200">Referenced excerpts</p>
                                {message.sources.map((source, sourceIndex) => (
                                  <div
                                    key={`${source.reportId}-${source.chunkIndex}-${sourceIndex}`}
                                    className="rounded border border-slate-700/60 bg-slate-900/70 px-3 py-2"
                                  >
                                    <span className="font-semibold text-emerald-300">Excerpt {sourceIndex + 1}</span>
                                    <p className="mt-1 whitespace-pre-wrap text-[11px] leading-relaxed text-slate-300">
                                      {source.content.length > 280
                                        ? `${source.content.slice(0, 280)}…`
                                        : source.content}
                                    </p>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        ))
                      )}
                    </div>

                    <form onSubmit={handleChatSubmit} className="mt-4 space-y-3">
                      <textarea
                        value={chatInput}
                        onChange={(event) => setChatInput(event.target.value)}
                        placeholder={selectedReport?.id ? 'What is the bull case scenario from this report?' : 'Select a report first.'}
                        className="h-24 w-full resize-none rounded-lg border border-slate-700 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none transition focus:border-emerald-400"
                        disabled={!selectedReport?.id || isChatLoading}
                      />
                      {chatError && (
                        <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-2 text-xs text-red-200">
                          {chatError}
                        </div>
                      )}
                      <div className="flex items-center justify-between gap-3">
                        <p className="text-[11px] text-slate-500">Press ↵ Enter to add a newline. Use Shift + Enter to continue typing.</p>
                        <button
                          type="submit"
                          disabled={disableChatSubmit}
                          className="rounded-lg bg-emerald-500 px-4 py-2 text-xs font-semibold text-emerald-950 transition hover:bg-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-300 disabled:cursor-not-allowed disabled:bg-emerald-700/40"
                        >
                          Send
                        </button>
                      </div>
                    </form>
                  </div>
                </div>
              )}
            </div>
          )}
        </section>
      </main>

      <footer className="border-t border-slate-800 bg-slate-900/70">
        <div className="mx-auto max-w-6xl px-6 py-6 text-xs text-slate-500">
          <p>
            ⚠️ Investment research generated by AI is for informational purposes only. Validate figures before making financial
            decisions.
          </p>
        </div>
      </footer>
    </div>
  )
}
