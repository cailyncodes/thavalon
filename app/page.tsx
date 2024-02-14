"use client"
import React from "react";
import { FormData } from "next";
import { createGame } from "./game/index";

export default function Home() {
  const createNewGame = async (_: FormData) => {
    const gameId = await createGame();
    window.location.assign(`/game/${gameId}`);
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex mb-12">
        <div className="w-full flex flex-col items-center justify-between">
          <h1 className="text-4xl font-bold">THAvalon</h1>
          <p className="text-xl">Online implementation of THAvalon to speed up games</p>
        </div>
      </div>
      <div className="w-full flex flex-col items-center justify-between">
        <form className="w-full max-w-lg" action={createNewGame}>
          <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" type="submit">
            Start
          </button>
          </form>
        </div>
    </main>
  );
}
