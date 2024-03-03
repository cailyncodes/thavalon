"use client"
import React from "react";
import { createGame, getGameId } from "./game/index";

export default function Home() {
  const createNewGame = async (_: FormData) => {
    const gameId = await createGame();
    window.location.assign(`/game/${gameId}`);
  }

  const joinGame = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const gameCode = formData.get("gameCode");
    const gameId = await getGameId(gameCode as string);
    window.location.assign(`/game/${gameId}/view?gameCode=${gameCode}`);
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex mb-12">
        <div className="w-full flex flex-col items-center justify-between">
          <h1 className="text-4xl font-bold">THAvalon</h1>
          <p className="text-xl">Online implementation of THAvalon to speed up games</p>
        </div>
      </div>
      <div className="w-full flex flex-col items-center justify-between">
      <p className="text-xl">Enter a game code to join or start a new game.</p>
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
        <form className="w-full max-w-lg flex justify-center items-center" action={createNewGame}>
          <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" type="submit">
            Start New Game
          </button>
        </form>
      </div>
    </main>
  );
}
