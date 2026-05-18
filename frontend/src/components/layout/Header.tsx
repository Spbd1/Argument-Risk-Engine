import { API_BASE } from '../../api/client'
import type { PageId } from '../../App'

const titles: Record<PageId, string> = {
  analyze: 'Analyze Text',
  taxonomy: 'Taxonomy Browser',
  workbench: 'Taxonomy Workbench',
  settings: 'Model Settings',
  review: 'Review Outputs',
  evaluation: 'Evaluation',
  reports: 'Reports',
  about: 'About',
}

export function Header({ activePage }: { activePage: PageId }) {
  return <header className="header">
    <div>
      <p className="eyebrow">Argument-Risk-Engine Dashboard</p>
      <h1>{titles[activePage]}</h1>
      <p>Taxonomy-grounded argument risk signals for human analysts.</p>
    </div>
    <div className="api-pill"><span className="status-dot" />Backend: {API_BASE}</div>
  </header>
}
