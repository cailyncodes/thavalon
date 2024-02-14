import { getGame } from '../../index'
import React from 'react'

export default async function GameHome({
  params,
}: {
  params: { gameId: string }
}) {
  const game = await getGame(params.gameId)

  return (
    <main className="min-h-screen h-full flex flex-col items-center justify-center p-24">
      <div className="max-w-5xl w-full font-mono text-sm flex flex-col">
        <div className="mb-12">
          <h1 className="text-lg">Players</h1>
        </div>
        <div className="max-w-lg w-full h-full flex flex-col self-center items-center justify-center">
          <div className="flex flex-col justify-center items-center w-full mb-6 lg:mb-12">
            {/* @ts-expect-error */}
            {game.players.map((player, index) => (
              <div key={index} className="flex flex-row justify-center items-center w-full">
                <a href={`/game/${params.gameId}/view/${player}`}>{player}</a>
              </div>
            ))}
          </div>
        </div>
      </div>
    </main>
  )
}