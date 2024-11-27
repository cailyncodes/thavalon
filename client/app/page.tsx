import React from "react";
import Home from "./Home";
import { getUrl } from "./url";

export default function HomePage() {
  const url = getUrl(process.env.RAILWAY_ENVIRONMENT_NAME, "http");

  return (
    <main className="flex min-h-screen flex-col items-stretch bg-gray-900 text-gray-200">
      <Home url={url} />
    </main>
  );
}
