import { useEffect, useState } from 'react'
import { downloadReport, fetchDemoReport, listReports, saveGeneratedReport } from '../../api/client'
import type { GeneratedReport, ReportFormat } from '../../api/types'
import { Button } from '../shared/Button'
import { Card } from '../shared/Card'
import { EmptyState } from '../shared/EmptyState'
import { ReportPreview } from './ReportPreview'

export function ReportsPage() {
  const [reports, setReports] = useState<GeneratedReport[]>([])
  const [selectedId, setSelectedId] = useState('')
  const [format, setFormat] = useState<ReportFormat>('markdown')
  const selected = reports.find(report => report.id === selectedId) ?? reports[0]
  const reload = () => { const items = listReports(); setReports(items); setSelectedId(current => current || items[0]?.id || '') }
  useEffect(reload, [])
  async function loadDemo() { const markdown = await fetchDemoReport(); saveGeneratedReport({ id: `demo-${Date.now()}`, title: 'Demo backend report', created_at: new Date().toISOString(), formats: ['markdown'], markdown }); reload() }
  return <div className="page-grid two-column"><Card className="stack"><div className="section-header"><div><h2>Reports</h2><p className="muted">List generated reports, preview content, and download JSON, Markdown, or HTML when available.</p></div><Button variant="secondary" onClick={loadDemo}>Load demo report</Button></div>{reports.length ? <div className="report-list">{reports.map(report => <button key={report.id} className={selected?.id === report.id ? 'list-button active' : 'list-button'} onClick={() => setSelectedId(report.id)}><strong>{report.title}</strong><span>{new Date(report.created_at).toLocaleString()}</span></button>)}</div> : <EmptyState title="No generated reports" message="Save a report from the Analyze page or load the backend demo report." />}</Card><Card className="stack"><div className="button-row"><select value={format} onChange={event => setFormat(event.target.value as ReportFormat)}><option value="markdown">Markdown</option><option value="html">HTML</option><option value="json">JSON</option></select>{selected ? selected.formats.map(item => <Button key={item} variant="secondary" onClick={() => downloadReport(selected, item)}>Download {item}</Button>) : null}</div><ReportPreview report={selected} format={format} /></Card></div>
}
