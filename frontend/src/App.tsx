import { AnalyzePage } from './components/analyze/AnalyzePage'
import { AppShell } from './components/layout/AppShell'
import { EvaluationPage } from './components/evaluation/EvaluationPage'
import { ReportsPage } from './components/reports/ReportsPage'
import { ReviewPage } from './components/review/ReviewPage'
import { ModelSettingsPage } from './components/settings/ModelSettingsPage'
import { TaxonomyPage } from './components/taxonomy/TaxonomyPage'
import { TaxonomyWorkbenchPage } from './components/taxonomy_workbench/TaxonomyWorkbenchPage'

export default function App() {
  return <AppShell><div className="grid"><AnalyzePage /><TaxonomyPage /><TaxonomyWorkbenchPage /><ModelSettingsPage /><ReviewPage /><EvaluationPage /><ReportsPage /></div></AppShell>
}
