// Empty API origin means same-origin /api requests on Vercel Services.
// Local Uvicorn development sets NEXT_PUBLIC_API_URL=http://localhost:8001.
export const config = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL?.trim().replace(/\/+$/, "") ?? "",
};
