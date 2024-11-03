import React from "react";
import { GameManager } from "./GameManager";


type CommunicationChannel = "ws" | "http"

function getDomain(env?: string) {
  env = env || 'development'

  if (env.startsWith("thavalon-")) {
    return `api-${env}.up.railway.app`
  }
  switch (env) {
    case 'development':
      return 'localhost:6464'
    case 'next':
      return 'next-api.thavalon.quest'
    case 'production':
      return "api.thavalon.quest"
    default:
      throw new Error('Unknown environment')
  }
}

function getUrl(env: string | undefined, channel: CommunicationChannel) {
  const origin = getDomain(env);
  return origin?.includes('localhost') ? `${channel}://${origin}` : `${channel}s://${origin}`
}

export default function GameHome({
  params,
  searchParams,
}: {
  params: { gameId: string };
  searchParams: { [key: string]: string | string[] | undefined }
}) {
  const wsUrl = getUrl(process.env.RAILWAY_ENVIRONMENT_NAME, "ws")
  const httpUrl = getUrl(process.env.RAILWAY_ENVIRONMENT_NAME, "http")

  const gameCodeParam = searchParams['gameCode']

  let gameCode: string | undefined = undefined
  if (typeof gameCodeParam === 'string') {
    gameCode = gameCodeParam.toUpperCase()
  } else if (Array.isArray(gameCodeParam)) {
    gameCode = gameCodeParam[0].toUpperCase()
  }

  return (
    <GameManager
      gameId={params.gameId}
      gameCode={gameCode}
      wsUrl={wsUrl}
      httpUrl={httpUrl}
    />
  )
}