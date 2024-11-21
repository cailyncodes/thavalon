import React, { useState, useEffect } from "react";
import Game from "./Game";

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

export default function GameViewPage() {
  return <Game url={getUrl(process.env.RAILWAY_ENVIRONMENT_NAME, "http")} />;
}
