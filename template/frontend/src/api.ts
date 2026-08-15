/** HTTP client for the FastAPI backend. Do not add database URLs here. */

function apiUrl(path: string): string {
  const base = (import.meta.env.VITE_API_BASE ?? "/api").replace(/\/$/, "");
  return `${base}${path}`;
}

export async function getHealth(): Promise<{ status: string }> {
  const response = await fetch(apiUrl("/health"));
  if (!response.ok) {
    throw new Error(`health ${response.status}`);
  }
  return response.json() as Promise<{ status: string }>;
}

export async function getHello(name = "formwork"): Promise<{ message: string }> {
  const response = await fetch(apiUrl(`/hello?name=${encodeURIComponent(name)}`));
  if (!response.ok) {
    throw new Error(`hello ${response.status}`);
  }
  return response.json() as Promise<{ message: string }>;
}
