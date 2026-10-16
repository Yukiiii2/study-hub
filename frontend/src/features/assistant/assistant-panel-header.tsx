import Link from "next/link";

export function AssistantPanelHeader({ context, close }: { context: string; close: () => void }) {
  return <header className="windowed-assistant-header"><div><h2 id="windowed-assistant-title" tabIndex={-1}>Study Assistant</h2><p>Page: {context}</p></div><Link className="ghost-button" href="/assistant" aria-label="Expand to full Study Assistant">Expand</Link><button type="button" className="ghost-button" onClick={close} aria-label="Close Study Assistant">Close</button></header>;
}
