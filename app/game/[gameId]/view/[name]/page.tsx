// component for displaying the data for a player in a game

import { getGame } from "../../../index"

export default async function PlayerHome({
  params,
}: {
  params: { gameId: string, name: string }
}) {
  const game = await getGame(params.gameId)

  return (
    <div className="min-h-screen h-full flex flex-col items-center justify-center p-6 sm:p-24">
      {game.players.includes(params.name) ? <h1 className="text-xl mb-5">Player: {params.name}</h1> : null}
      <div className="max-w-3xl w-full font-mono text-sm flex flex-col">
        <pre className="whitespace-pre-line">
          {game[params.name]}
        </pre>
      </div>
    </div>
  )
}
