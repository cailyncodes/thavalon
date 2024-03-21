import React from "react";
import { GameManager } from "./GameManager";

export default function GameHome({
  params,
  searchParams,
}: {
  params: { gameId: string };
  searchParams: { [key: string]: string | string[] | undefined }
}) {
  const initialPlayersParam = searchParams['initial_players[]']
  const gameCodeParam = searchParams['gameCode']

  let initialPlayers: string[] = []
  if (Array.isArray(initialPlayersParam)) {
    initialPlayers = initialPlayersParam
  }

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
    />
  )
}