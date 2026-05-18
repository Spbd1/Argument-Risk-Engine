import { useState } from 'react'
import { AnalyzePage } from './components/analyze/AnalyzePage'
import { AppShell } from './components/layout/AppShell'
import { EvaluationPage } from './components/evaluation/EvaluationPage'
import { ReportsPage } from './components/reports/ReportsPage'
import { ReviewPage } from './components/review/ReviewPage'
import { ModelSettingsPage } from './components/settings/ModelSettingsPage'
import { TaxonomyPage } from './components/taxonomy/TaxonomyPage'
import { TaxonomyWorkbenchPage } from './components/taxonomy_workbench/TaxonomyWorkbenchPage'
import { Card } from './components/shared/Card'

export type PageId = 'analyze' | 'taxonomy' | 'workbench' | 'settings' | 'review' | 'evaluation' | 'reports' | 'about'

function AboutPage() {
  return <Card className="stack">
    <h2>About this dashboard</h2>
    <p>The dashboard is a Chrome-friendly operator console for the Argument-Risk-Engine backend. It supports text analysis, taxonomy inspection, Excel taxonomy operations, model-provider configuration, human review, evaluation, and report export.</p>
    <p className="muted">Use <code>npm install</code> and <code>npm run dev</code> from <code>frontend/</code>, or the repository one-command setup, then keep the backend running on the configured API base.</p>
  </Card>
}

export default function App() {
  const [activePage, setActivePage] = useState<PageId>('analyze')
  const page = {
    analyze: <AnalyzePage />,
    taxonomy: <TaxonomyPage />,
    workbench: <TaxonomyWorkbenchPage />,
    settings: <ModelSettingsPage />,
    review: <ReviewPage />,
    evaluation: <EvaluationPage />,
    reports: <ReportsPage />,
    about: <AboutPage />,
  }[activePage]
  return <AppShell activePage={activePage} onNavigate={setActivePage}>{page}</AppShell>
}
