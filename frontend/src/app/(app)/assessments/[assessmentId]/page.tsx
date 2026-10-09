import { AssessmentDetailPage } from "@/features/assessments/assessment-detail";

export default async function AssessmentPage({ params }: { params: Promise<{ assessmentId: string }> }) {
  const { assessmentId } = await params;
  return <AssessmentDetailPage key={assessmentId} id={assessmentId} />;
}
