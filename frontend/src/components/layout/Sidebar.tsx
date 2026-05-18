const items = ['Analyze', 'Taxonomy', 'Workbench', 'Settings', 'Review', 'Evaluation', 'Reports']
export function Sidebar() { return <aside className="sidebar"><h2>ARE</h2>{items.map(item => <a key={item} href={`#${item.toLowerCase()}`}>{item}</a>)}</aside> }
