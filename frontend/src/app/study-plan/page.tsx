import { ProtectedApp } from "@/features/auth/protected-dashboard";
import { StudyPlanner } from "@/features/study-plan/study-planner";

export default function StudyPlanPage() {
  return <ProtectedApp><StudyPlanner /></ProtectedApp>;
}
