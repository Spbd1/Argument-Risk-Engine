export function EvidenceHighlight({ text, start, end }: { text: string; start: number; end: number }) {
  if (start < 0 || end <= start || end > text.length) return <span>{text}</span>
  return <span>{text.slice(0, start)}<mark>{text.slice(start, end)}</mark>{text.slice(end)}</span>
}
