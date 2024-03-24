"use client"
import React from 'react'
import { createGame, createGameCode, getGameId } from '../../index';

export const RemakeGame = () => {
  const [username, setUsername] = React.useState<string>();

  React.useEffect(() => {
    const name = window.localStorage.getItem("username");
    if (name) {
      setUsername(name);
    }
  }, []);

  const remakeGame = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!username) {
      alert("Please set your name first");
      return false;
    }
    const gameId = await createGame(username);
    const gameCode = await createGameCode(gameId);
    window.location.assign(`/game/${gameId}?gameCode=${gameCode}`);
    return false;
  }

  const joinGame = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!username) {
      alert("Please set your name first");
      return false;
    }
    const formData = new FormData(e.currentTarget);
    const gameCode = formData.get("gameCode");
    const gameId = await getGameId(gameCode as string);
    window.location.assign(`/game/${gameId}?gameCode=${gameCode}`);
    return false;
  }

  return (
    <div className="w-full flex flex-col items-center justify-between my-4">
      <form className="w-full max-w-lg flex justify-center items-center m-2" onSubmit={remakeGame}>
        <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" type="submit">
          Remake Game
        </button>
      </form>
      <p>or</p>
      <form className="w-full max-w-lg flex flex-col justify-center items-center" onSubmit={joinGame}>
        <input className="border-2 border-gray-300 p-2 rounded m-2 text-gray-700 bg-white w-2/5" type="text" name="gameCode" placeholder="Game Code" />
        <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" type="submit">
          Join Game
        </button>
      </form>
    </div>
  )
}
