"use server"
import { put } from "@vercel/blob"
import { randomUUID } from "crypto";

export async function createGame() {
  const gameId = randomUUID();

  const file = new Blob([JSON.stringify({ gameId })], { type: "application/json" });
  await put(gameId, file, {
    access: 'public',
    addRandomSuffix: false,
    contentType: 'application/json',
    token: process.env.DB_READ_WRITE_TOKEN
  })

  console.log("Game started with id: ", gameId);

  return gameId
}

export async function startGame(data: { gameId: string, players: string[] }) {
  const game = {
    gameId: data.gameId,
    players: data.players,
  }

  const file = new Blob([JSON.stringify(game)], { type: "application/json" });
  await put(data.gameId, file, {
    access: 'public',
    addRandomSuffix: false,
    contentType: 'application/json',
    token: process.env.DB_READ_WRITE_TOKEN
  })
}

export async function getGame(gameId: string) {
  const response = await fetch(
    "https://kslx3eprjeoij69w.public.blob.vercel-storage.com/" + gameId,
    {
      headers: {
        "content-type": "application/json",
      },
    }
  )
  const gameData = await response.json()
  return gameData
}
