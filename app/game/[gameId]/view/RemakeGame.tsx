"use client"
import React from 'react'
import { createGame } from '../../index';

interface RemakeGameProps {
  players: string[];
 }

export const RemakeGame = ({ players }: RemakeGameProps) => {
    const remakeGame = async (_: FormData) => {
        const newGameId = await createGame();
        // add initial_players as an array of strings to the query params
        let params = players.map((player) => 
            `initial_players[]=${encodeURIComponent(player)}`
        ).join('&');
        window.location.assign(`/game/${newGameId}?${params}`);
      }

    return (
    <div className="w-full flex flex-col items-center justify-between">
    <form className="w-full max-w-lg flex justify-center items-center" action={remakeGame}>
      <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" type="submit">
        Remake Game (beta)
      </button>
    </form>
  </div>)
}
