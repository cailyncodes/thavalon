"use server"
import { put } from "@vercel/blob"
import { kv } from "@vercel/kv";
import { randomUUID } from "crypto";

export type Variant = "thavalon" | "esoteric" | "jealousy";

// Game data before running script to determine start player
interface ProtoGame {
  gameId: string;
  players: string[];
  variant: Variant;
}

// Game data with a specified start player
export interface Game extends ProtoGame {
  // starting player for proposing missions
  start: string;
  // games also have a mapping from player names to their roles
  [player: string]: any;
}

export async function createGame(host: string) {
  const gameId = randomUUID();

  const file = new Blob([JSON.stringify({ gameId, host, players: [host] })], { type: "application/json" });
  await put(`${gameId}.json`, file, {
    access: 'public',
    addRandomSuffix: false,
    contentType: 'application/json',
    token: process.env.DB_READ_WRITE_TOKEN
  })

  return gameId
}

export async function startGame(gameId: string, gameData: unknown) {
  const file = new Blob([JSON.stringify(gameData)], { type: "application/json" });
  // @ts-ignore
  await put(`${gameId}.json`, file, {
    access: 'public',
    addRandomSuffix: false,
    token: process.env.DB_READ_WRITE_TOKEN
  })
}

export async function getGame(gameId: string): Promise<Game> {
  const response = await fetch(
    `https://kslx3eprjeoij69w.public.blob.vercel-storage.com/${gameId}.json?timestamp=${Date.now()}`,
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
  // see https://random-word-api.vercel.app/
  const response = await fetch(
    'https://random-word-api.vercel.app/api?words=1&length=4'
  )
  const gameCode = (await response.json())[0]

  kv.set(gameCode, gameId)

  return gameCode
}

export async function getGameId(gameCode: string) {
  const gameId = await kv.get(gameCode.toUpperCase())

  return gameId
}
