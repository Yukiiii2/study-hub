import { SubjectVideosPage } from "@/features/videos/subject-videos";

export default async function VideosPage({ params }: { params: Promise<{ subjectId: string }> }) {
  const { subjectId } = await params;
  return <SubjectVideosPage subjectId={subjectId} />;
}
