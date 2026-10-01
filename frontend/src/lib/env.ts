/**
 * Public API configuration — only NEXT_PUBLIC_* vars belong here.
 * Never import server secrets into client code.
 */

const LOCAL_API_FALLBACK = "http://localhost:8000/api/v1";

function isProductionBuild(): boolean {
  return process.env.NODE_ENV === "production";
}

export function getApiBaseUrl(): string {
  const url = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (url) return url.replace(/\/$/, "");

  if (isProductionBuild()) {
    throw new Error(
      "NEXT_PUBLIC_API_URL is required in production. Set it in Vercel environment variables."
    );
  }

  return LOCAL_API_FALLBACK;
}

export function getApiOrigin(): string {
  return getApiBaseUrl().replace(/\/api\/v1\/?$/, "");
}

export function getPublicApiDisplayUrl(): string {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  return isProductionBuild() ? "Not configured" : LOCAL_API_FALLBACK;
}
