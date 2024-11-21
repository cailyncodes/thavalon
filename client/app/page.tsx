import React from "react";
import Lobby from "./Lobby";


type CommunicationChannel = "http";

function getDomain(env?: string) {
  env = env || "development";

  if (env.startsWith("thavalon-")) {
    return `api-${env}.up.railway.app`;
  }
  switch (env) {
    case "development":
      return "localhost:6464";
    case "next":
      return "next-api.thavalon.quest";
    case "production":
      return "api.thavalon.quest";
    default:
      throw new Error("Unknown environment");
  }
}

function getUrl(env: string | undefined, channel: CommunicationChannel) {
  const origin = getDomain(env);
  return origin.includes("localhost")
    ? `${channel}://${origin}`
    : `${channel}s://${origin}`;
}


export default function Home() {
  const url = getUrl(process.env.RAILWAY_ENVIRONMENT_NAME, "http");

  return (
    <main className="flex min-h-screen flex-col items-stretch bg-gray-900 text-gray-200">
      <Lobby url={url} />
    </main>
  );
}
