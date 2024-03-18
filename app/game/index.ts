"use server"
import { put } from "@vercel/blob"
import { kv } from "@vercel/kv";
import { randomUUID } from "crypto";

export type Variant = "thavalon" | "avalon" | "jealousy";



// Game data with a specified host
interface HostedGame {
  host: string;
  gameId: string;
  players: string[];
}

// Game data before running script to determine start player
interface ProtoGame extends HostedGame {
  variant: Variant;
  // current mission number tracks the current quest, 1-5
  missionIndex: number;
  // map mission index to people on the mission
  missionToPeople: Record<number, string[]>;
  // map mission index to votes
  missionToVotes: MissionToVotes;
  // game state
  gameState: GameState;
}

// TODO - where should I define these const? Vercel doesn't let useServer export consts
export type MissionVote = "SUCCESS" | "FAIL" | "REVERSE";

interface MissionToVotes {
  [index: number]: Record<string, MissionVote>;
}

// define a type of game state
export type GameState = "PROPOSING" | "MISSION_VOTING";

// Game data with a specified start player
export interface Game extends ProtoGame {
  // overall game state as a string
  doNotOpen: string;
  // starting player for proposing missions
  start: string;
  // games also have a mapping from player names to their roles
  [player: string]: any;
}

export async function createGame(host: string) {
  const gameId = randomUUID();

  const game: HostedGame = { gameId, host, players: [host] }
  putGame(game)

  return gameId
}

export async function startGame(data: { gameId: string, host: string, players: string[], variant: Variant }) {
  const game: ProtoGame = {
    gameId: data.gameId,
    gameState: "PROPOSING",
    host: data.host,
    missionIndex: 1,
    missionToPeople: {},
    missionToVotes: {},
    players: data.players,
    variant: data.variant,
  }

  const env = process.env.VERCEL_ENV || 'development'

  const origin = typeof window !== 'undefined' ? window.location.origin : (() => {
    switch (env) {
      case 'development':
        return 'localhost:3000'
      case 'preview':
        return process.env.VERCEL_BRANCH_URL
      case 'production':
        return "thavalon-five.vercel.app"
      default:
        throw new Error('Unknown environment')
    }
  })()

  const url = origin?.includes('localhost') ? `http://${origin}` : `https://${origin}`

  const response = await fetch(
    `${url}/api/game`,
    {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify(game),
    }
  )

  const gameData = await response.json()
  putGame(gameData)
}

export async function getGame(gameId: string): Promise<Game> {
  const response = await fetch(
    `https://spwamd4ap0dqqd0y.public.blob.vercel-storage.com/${gameId}.json?timestamp=${Date.now()}`,
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
  const gameId = await kv.get(gameCode.toUpperCase())

  return gameId
}

export async function putGame(game: HostedGame | Game) {
  const file = new Blob([JSON.stringify(game)], { type: "application/json" });
  const response = await put(`${game.gameId}.json`, file, {
    access: 'public',
    addRandomSuffix: false,
    token: process.env.DB_READ_WRITE_TOKEN,
  })
}

export async function addPlayer(gameId: string, player: string) {
  const game = await getGame(gameId)
  const players = game.players || []

  if (players.includes(player)) {
    return
  }

  players.push(player)
  game.players = players

  putGame(game)
}

export async function updateGameState(gameId: string, gameState: GameState) {
  const game = await getGame(gameId)
  if (game.gameState === gameState) {
    return
  }
  game.gameState = gameState

  putGame(game)
}

export async function startMission(gameId: string, missionIndex: number, players: string[]) {
  const game = await getGame(gameId)
  if (game.gameState !== "PROPOSING" || game.missionIndex !== missionIndex) {
    return
  }
  const missionToPeople = game.missionToPeople || {}
  missionToPeople[missionIndex] = players
  game.missionToProposals = missionToPeople
  game.gameState = "MISSION_VOTING"

  putGame(game)
}

export async function stopMission(gameId: string, missionIndex: number) {
  const game = await getGame(gameId)
  if (game.gameState !== "MISSION_VOTING" || game.missionIndex !== missionIndex) {
    return
  }
  game.gameState = "PROPOSING"
  game.missionIndex = missionIndex + 1

  putGame(game)
}

export async function voteOnMission(gameId: string, missionIndex: number, player: string, vote: MissionVote) {
  const game = await getGame(gameId)
  if (game.gameState !== "MISSION_VOTING" || game.missionIndex !== missionIndex) {
    return
  }
  const missionToVotes = game.missionToVotes || {}
  missionToVotes[missionIndex] = missionToVotes[missionIndex] || {}
  missionToVotes[missionIndex][player] = vote
  game.missionToVotes = missionToVotes

  putGame(game)
}