import React from "react";
import { GameManager } from "./GameManager";

export default function GameHome({
  params,
}: {
  params: { gameId: string };
}) {
  return (
    <GameManager gameId={params.gameId} />
  )
}