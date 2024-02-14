"use server"
import { put } from "@vercel/blob"
import { kv } from "@vercel/kv";
import { randomUUID } from "crypto";

export async function createGame() {
  const gameId = randomUUID();

  const file = new Blob([JSON.stringify({ gameId })], { type: "application/json" });
  await put(`${gameId}.json`, file, {
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

  const protocol = process.env.VERCEL_URL?.includes('localhost') ? 'http' : 'https'

  const response = await fetch(
    `${protocol}://${process.env.VERCEL_URL}/api/game`,
    {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify(game),
    }
  )

  const gameData = await response.json()

  const file = new Blob([JSON.stringify(gameData)], { type: "application/json" });
  await put(`${data.gameId}.json`, file, {
    access: 'public',
    addRandomSuffix: false,
    token: process.env.DB_READ_WRITE_TOKEN
  })
}

export async function getGame(gameId: string) {
  const response = await fetch(
    "https://kslx3eprjeoij69w.public.blob.vercel-storage.com/" + gameId + ".json",
    {
      headers: {
        "content-type": "application/json",
      },
    }
  )
  const gameData = await response.json()
  return gameData
}

export async function createGameCode(gameId: string) {
  const code = "ABCDEFGHIJKLMNPQRSTUVWXYZ123456789"
  const gameCode = code.split('').sort(() => Math.random() - 0.5).slice(0, 4).join('')

  kv.set(gameCode, gameId)

  return gameCode
}

export async function getGameId(gameCode: string) {
  const gameId = await kv.get(gameCode)

  return gameId
}