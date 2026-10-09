import { ResourceDetail } from "@/features/resources/resource-detail";

export default async function ResourcePage({ params }: { params: Promise<{ resourceId: string }> }) {
  const { resourceId } = await params;
  return <ResourceDetail key={resourceId} resourceId={resourceId} />;
}
