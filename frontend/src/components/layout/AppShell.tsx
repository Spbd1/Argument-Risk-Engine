import type { ReactNode } from 'react'
import type { PageId } from '../../App'
import { Header } from './Header'
import { Sidebar } from './Sidebar'

export function AppShell({ activePage, onNavigate, children }: { activePage: PageId; onNavigate: (page: PageId) => void; children: ReactNode }) {
  return <div className="shell"><Sidebar activePage={activePage} onNavigate={onNavigate} /><main className="main"><Header activePage={activePage} />{children}</main></div>
}
