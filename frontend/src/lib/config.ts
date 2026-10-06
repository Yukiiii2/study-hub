// Only public browser configuration belongs here.
export const config = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, "") ?? "",
};
