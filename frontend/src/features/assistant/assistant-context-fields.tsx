"use client";

import { Associations, LoadNotice } from "@/features/quizzes/shared";
import type { AssistantController } from "./use-assistant-controller";

/** One selector presentation reused by both workspaces; source requests live in the controller. */
export function AssistantContextFields({ controller }: { controller: AssistantController }) {
  const { subject, setSubject, topic, setTopic, resource, setResource, snapshot, setSnapshot, offset, setOffset, busy,
    resources, selected, ready, selectedResource, resourceReady, clearPreview, selectResource } = controller;
  return <>
      {snapshot ? <div className="planner-wide"><p className="resource-note">Using the saved completed quiz mistake. The service checks the original answer and source.</p><button type="button" className="secondary-button" onClick={() => { clearPreview(); setSnapshot(null); }}>Choose other study context</button></div> : <>
        <Associations subject={subject} topic={topic} disabled={busy} changeSubject={(id) => { clearPreview(); setSubject(id); setResource(""); setOffset(0); }} changeTopic={(id) => { clearPreview(); setTopic(id); setResource(""); }} />
        <label className="planner-wide">Ready text PDF (optional)<select disabled={resources.loading || !!resources.error} value={resource} onChange={(event) => selectResource(event.target.value)}><option value="">Use subject or topic context</option>{resource && !ready.some((item) => item.id === resource) && <option value={resource}>{selectedResource?.title ?? "Selected resource"}</option>}{ready.map((item) => <option key={item.id} value={item.id}>{item.title}</option>)}</select></label>
        <div className="planner-wide"><LoadNotice layout="control" hasData={resources.data != null} loading={resources.loading} error={resources.error} retry={resources.retry} />{resource && <><LoadNotice layout="control" hasData={selected.data != null} loading={selected.loading} error={selected.error} retry={selected.retry} /><button type="button" className="secondary-button" onClick={() => selectResource("")}>Clear PDF selection</button></>}{resource && !selected.loading && !selected.error && !resourceReady && <p className="auth-error" role="alert">This resource does not have ready PDF text. Choose another source.</p>}
          {resources.data && resources.data.total > 20 && <div className="resource-pagination"><span className="resource-note">Ready PDFs on this source page: {ready.length}</span><button type="button" className="secondary-button" disabled={!offset || resources.loading} onClick={() => setOffset(Math.max(0, offset - 20))}>Previous sources</button><button type="button" className="secondary-button" disabled={offset + 20 >= resources.data.total || resources.loading} onClick={() => setOffset(offset + 20)}>Next sources</button></div>}
        </div></>}
  </>;
}
