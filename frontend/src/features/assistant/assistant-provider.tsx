"use client";

import { createContext, useContext, useState, type ReactNode } from "react";
import { useAssistantController } from "./use-assistant-controller";

function useAssistantSession() {
  const [activated, setActivated] = useState(false);
  const [open, setOpen] = useState(false);
  const controller = useAssistantController({}, activated);
  return { controller, open, setOpen, activate: () => setActivated(true) };
}
const AssistantContext = createContext<ReturnType<typeof useAssistantSession> | null>(null);

/** Mounted once per authenticated identity; no storage, second auth listener or hidden chat client. */
export function AssistantProvider({ children }: { children: ReactNode }) {
  return <AssistantContext.Provider value={useAssistantSession()}>{children}</AssistantContext.Provider>;
}
export function useAssistant() {
  const value = useContext(AssistantContext);
  if (!value) throw new Error("Assistant must be inside the authenticated AssistantProvider");
  return value;
}
