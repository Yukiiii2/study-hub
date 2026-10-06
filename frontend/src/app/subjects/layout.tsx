import type { ReactNode } from "react";
import { ProtectedApp } from "@/features/auth/protected-dashboard";

export default function SubjectsLayout({ children }: { children: ReactNode }) {
  return <ProtectedApp>{children}</ProtectedApp>;
}
