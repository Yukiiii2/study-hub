import { ResourceLibrary } from "@/features/resources/resource-library";

export default async function LibraryPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) { const params = await searchParams; return <ResourceLibrary key={typeof params.subject_id === "string" ? params.subject_id : ""} initialSubject={typeof params.subject_id === "string" ? params.subject_id : ""} />; }
