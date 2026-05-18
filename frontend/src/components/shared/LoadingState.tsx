export function LoadingState({ label = 'Loading…' }: { label?: string }) { return <div className="state state-loading" aria-live="polite"><span className="spinner" />{label}</div> }
