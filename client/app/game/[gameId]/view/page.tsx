import { getGame } from '../../index'
import React from 'react'
import { GameView } from './GameView'

export default async function GameHome({
  params,
  searchParams
}: {
  params: { gameId: string },
  searchParams: { [key: string]: string | string[] | undefined }
}) {
  const game = await getGame(params.gameId)
  console.log(game)
  const gameCode = (searchParams['gameCode'] as string).toUpperCase()

  return (
    <main className="min-h-screen h-full flex flex-col items-center justify-center p-24">
      <GameView game={game} gameCode={gameCode} />
    </main>
  )
}