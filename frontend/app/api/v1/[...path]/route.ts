import type { NextRequest } from "next/server";

type RouteContext = {
  params: Promise<{ path: string[] }>;
};

async function proxyRequest(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  const backendUrl = (
    process.env.BACKEND_API_URL ?? "http://localhost:8000"
  ).replace(/\/+$/, "");
  const incomingUrl = new URL(request.url);
  const pathSuffix = path.join("/");
  const trailingSlash = incomingUrl.pathname.endsWith("/") ? "/" : "";
  const targetUrl = `${backendUrl}/api/v1/${pathSuffix}${trailingSlash}${incomingUrl.search}`;
  const headers = new Headers();

  for (const header of ["accept", "authorization", "content-type"]) {
    const value = request.headers.get(header);
    if (value) headers.set(header, value);
  }

  try {
    const upstream = await fetch(targetUrl, {
      method: request.method,
      headers,
      body: ["GET", "HEAD"].includes(request.method)
        ? undefined
        : await request.arrayBuffer(),
      cache: "no-store",
      signal: request.signal,
    });
    const responseHeaders = new Headers();
    const contentType = upstream.headers.get("content-type");
    if (contentType) responseHeaders.set("content-type", contentType);

    return new Response(
      upstream.status === 204 || request.method === "HEAD"
        ? null
        : upstream.body,
      {
        status: upstream.status,
        headers: responseHeaders,
      },
    );
  } catch (error) {
    console.error("DevTalks backend proxy request failed", error);
    return Response.json(
      { detail: "Не удалось связаться с сервером DevTalks. Попробуйте позже." },
      { status: 502 },
    );
  }
}

export const GET = proxyRequest;
export const POST = proxyRequest;
export const PATCH = proxyRequest;
export const PUT = proxyRequest;
export const DELETE = proxyRequest;
