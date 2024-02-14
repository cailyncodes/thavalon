"use client"
import React from 'react'
import { createGameCode, startGame } from '../index'

export const GameManager = (props: { gameId: string }) => {
  const [players, setPlayers] = React.useState<string[]>([]);

  const addPlayer = (e: React.FormEvent) => {
    e.preventDefault();
    setPlayers(players.concat(""));
  }

  const removePlayer = (e: React.FormEvent, index: number) => {
    e.preventDefault();
    const newPlayers = players.slice();
    newPlayers.splice(index, 1);
    setPlayers(newPlayers);
  }

  const startNewGame = async (_: FormData) => {
    await startGame({ gameId: props.gameId, players });
    const gameCode = await createGameCode(props.gameId);
    window.location.assign(`/game/${props.gameId}/view?gameCode=${gameCode}`);
  }

  return (
    <main className="min-h-screen h-full flex flex-col items-center justify-center p-24">
        <div className="max-w-5xl w-full font-mono text-sm flex flex-col">
          <div className="mb-12"><h1 className='text-lg'>Players</h1></div>
          <form className="max-w-lg w-full h-full flex flex-col self-center items-center justify-center" action={startNewGame}>
            <div className='flex flex-col justify-center items-center w-full mb-6 lg:mb-12'>
            {players.map((player, index) => (
              <div key={index} className='flex flex-row justify-center items-center w-full'>
                <label className='mr-3'>Player {index + 1}</label>
                <input type="text" placeholder='Name' value={player} onChange={(event) => {
                  const newPlayers = players.slice()
                  newPlayers[index] = event.target.value
                  setPlayers(newPlayers)
                }} className="border-2 border-gray-300 p-2 rounded m-2 text-gray-700" />
                <div className='ml-2'>
                <button onClick={e => removePlayer(e, index)} className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded">Remove player</button>
              </div>
              </div>
            ))}
            </div>
            <div className='w-full flex flex-col justify-center items-center lg:flex-row'>
              <button onClick={addPlayer} className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mb-6 lg:mb-0 lg:mr-6">Add player</button>
              <button className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded" type="submit">
                Start
              </button>
            </div>
          </form>
        </div>
      </main>
  )
}