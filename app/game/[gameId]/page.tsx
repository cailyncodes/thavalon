import React from "react";
import { GameManager } from "./GameManager";

export default function GameHome({
  params,
  searchParams,
}: {
  params: { gameId: string};
  searchParams: { [key: string]: string | string[] | undefined }
}) {
  const initialPlayersParam = searchParams['initial_players[]']
  let initialPlayers: string[] = []
  if (Array.isArray(initialPlayersParam)) {
    initialPlayers = initialPlayersParam
  }

  return (
    <GameManager gameId={params.gameId} initialPlayers={initialPlayers} />
  )
}