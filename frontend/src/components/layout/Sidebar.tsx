import type { PageId } from '../../App'

const items: Array<{ id: PageId; label: string }> = [
  { id: 'analyze', label: 'Analyze' },
  { id: 'taxonomy', label: 'Taxonomy Browser' },
  { id: 'workbench', label: 'Taxonomy Workbench' },
  { id: 'settings', label: 'Model Settings' },
  { id: 'review', label: 'Review' },
  { id: 'evaluation', label: 'Evaluation' },
  { id: 'reports', label: 'Reports' },
  { id: 'about', label: 'About' },
]

export function Sidebar({ activePage, onNavigate }: { activePage: PageId; onNavigate: (page: PageId) => void }) {
  return <aside className="sidebar" aria-label="Primary navigation">
    <div className="brand"><span>ARE</span><small>Argument Risk Engine</small></div>
    <nav>
      {items.map(item => <button key={item.id} className={activePage === item.id ? 'nav-item active' : 'nav-item'} onClick={() => onNavigate(item.id)}>{item.label}</button>)}
    </nav>
  </aside>
}
