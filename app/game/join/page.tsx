"use client"

import React from "react";
import { getGameId } from "../index";

export default function JoinGame() {
  const joinGame = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const gameCode = formData.get("gameCode");
    const gameId = await getGameId(gameCode as string);
    window.location.assign(`/game/${gameId}/view?gameCode=${gameCode}`);
  };

  return (
    <main className="min-h-screen h-full flex flex-col items-center justify-center p-24">
      <div className="max-w-5xl w-full font-mono text-sm flex flex-col">
        <div className="mb-12">
          <h1 className="text-lg">Join a game</h1>
        </div>
        <form
          className="max-w-lg w-full h-full flex flex-col self-center items-center justify-center mb-6 text-lg"
          onSubmit={joinGame}
        >
          <input
            className="p-2 mb-4 w-full text-gray-700 border-2 border-gray-300 rounded"
            type="text"
            name="gameCode"
            placeholder="Game code"
          />
          <button
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            type="submit"
          >
            Join
          </button>
        </form>
      </div>
    </main>
  );
}