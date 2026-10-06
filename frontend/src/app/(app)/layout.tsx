import type { ReactNode } from "react";
import { ProtectedApp } from "@/features/auth/protected-dashboard";

export default function AppLayout({ children }: { children: ReactNode }) {
  return <ProtectedApp>{children}</ProtectedApp>;
}
