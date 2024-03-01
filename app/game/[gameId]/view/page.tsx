"use client"
import { Game, createGame, getGame } from '../../index'
import React from 'react'

export default function GameHome({
  params,
  searchParams
}: {
  params: { gameId: string },
  searchParams: { [key: string]: string | string[] | undefined }
}) {
  const [game, setGame] = React.useState<Game>()
  const gameCode = (searchParams['gameCode'] as string).toUpperCase()

  React.useEffect(() => {
    const fetchGame = async () => {
      const gameData = await getGame(params.gameId)
      setGame(gameData)
    }
    fetchGame()
  }, []);

  const remakeGame = async (_: FormData) => {
    if (!game) return;
    const newGameId = await createGame();
    // add initial_players as an array of strings to the query params
    let params = game.players.map((player) => 
        `initial_players[]=${encodeURIComponent(player)}`
    ).join('&');
    window.location.assign(`/game/${newGameId}?${params}`);
  }

  return (
    <main className="min-h-screen h-full flex flex-col items-center justify-center p-24">
      {game && 
      <div className="max-w-5xl w-full font-mono text-sm flex flex-col">
        <div className="mb-12">
          <h1 className="text-lg">Players</h1>
        </div>
        <div className="max-w-lg w-full h-full flex flex-col self-center items-center justify-center mb-6 text-lg">
          <h2>Game Code: {gameCode}</h2>
        </div>
        <div className="max-w-lg w-full h-full flex flex-col self-center items-center justify-center">
          <div className="flex flex-row justify-center items-center w-full mb-6">
            <p className='text-md font-bold'>{game.start}</p>
          </div>
          <div className="flex flex-col justify-center items-center w-full mb-6 lg:mb-12">
            {game.players.map((player, index) => (
              <div key={index} className="flex flex-row justify-center items-center w-full mb-4">
                <a href={`/game/${params.gameId}/view/${player}`} className="underline underline-offset-2">{player}</a>
              </div>
            ))}
          </div>
        </div>
        <div className="w-full flex flex-col items-center justify-between">
          <form className="w-full max-w-lg flex justify-center items-center" action={remakeGame}>
            <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" type="submit">
              Remake Game (beta)
            </button>
          </form>
        </div>
      </div>
    }
    </main>
  )
}