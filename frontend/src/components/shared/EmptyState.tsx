export function EmptyState({ title = 'No data yet', message }: { title?: string; message: string }) { return <div className="state state-empty"><strong>{title}</strong><p>{message}</p></div> }
