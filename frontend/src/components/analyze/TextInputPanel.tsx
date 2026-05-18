import { Button } from '../shared/Button'
export function TextInputPanel({ text, setText, onAnalyze }: { text: string; setText: (value: string) => void; onAnalyze: () => void }) {
  return <div className="stack"><textarea value={text} onChange={event => setText(event.target.value)} rows={8} /><Button onClick={onAnalyze}>Analyze text</Button></div>
}
