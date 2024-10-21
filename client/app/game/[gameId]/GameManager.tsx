"use client"
import React from 'react'
import useWebSocket, { ReadyState } from 'react-use-websocket';
import { startGame, Variant } from '../index'
import { useRouter } from 'next/navigation';

interface GameManagerProps {
  gameId: string;
  gameCode?: string;
}

export const GameManager = ({ gameId, gameCode }: GameManagerProps) => {
  const { sendJsonMessage, lastJsonMessage, readyState } = useWebSocket(
    `ws://localhost:6464/ws/${gameId}`,
    {
      share: true,
      shouldReconnect: () => true,
    }
  )
  const router = useRouter();
  const [player, setPlayer] = React.useState<string>("")
  const [players, setPlayers] = React.useState<string[]>([]);
  const [variant, setVariant] = React.useState<Variant>("thavalon");
  const [isHost, setIsHost] = React.useState(false);
  const [isStarted, setIsStarted] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(false);

  React.useEffect(() => {
    if (readyState === ReadyState.OPEN && !!player) {
      sendJsonMessage({
        type: "connect",
        message: { username: player }
      })
    }
  }, [readyState, player, sendJsonMessage]);

  React.useEffect(() => {
    console.log(lastJsonMessage)
    // @ts-expect-error
    if (lastJsonMessage?.type === "start") {
      setIsStarted(true);
    }
    // @ts-expect-error
    if (lastJsonMessage && lastJsonMessage.players?.length > 0) {
      // @ts-expect-error
      setPlayers(lastJsonMessage.players);
    }
  }, [lastJsonMessage]);

  const startNewGame = React.useCallback(async (_: FormData) => {
    console.debug("Starting new game")
    setIsLoading(true);
    const response = await (async () => {
      const game = {
        gameId: gameId,
        players: players,
        variant: variant
      }

      const env = process.env.RAILWAY_ENVIRONMENT_NAME || 'development'

      const origin = (() => {
        switch (env) {
          case 'development':
            return 'localhost:6464'
          case 'next':
            return 'next-api.thavalon.quest'
          case 'production':
            return "api.thavalon.quest"
          default:
            throw new Error('Unknown environment')
        }
      })()

      const url = origin?.includes('localhost') ? `http://${origin}` : `https://${origin}`

      const fullUrl = `${url}/api/game`
      let response;
      try {
        response = await fetch(
          fullUrl,
          {
            method: "POST",
            headers: {
              "content-type": "application/json",
            },
            body: JSON.stringify(game),
          }
        )
      } catch (e) {
        console.log(e)
      }

      if (!response) return
      return response.json()
    })()

    if (!response) return

    await startGame(gameId, response);
    sendJsonMessage({ type: "start" });
  }, [gameId, players, variant, sendJsonMessage]);

  React.useEffect(() => {
    const username = window.localStorage.getItem("username");
    if (username) {
      setPlayer(username);
    }
  }, []);

  React.useEffect(() => {
    if (isStarted) {
      router.push(`/game/${gameId}/view?gameCode=${gameCode}`);
    }
    if (players[0] === player) {
      setIsHost(true);
    }
  }, [player, players, gameId, gameCode, isStarted, router]);

  return (
    <main className="min-h-screen h-full flex flex-col items-center justify-center p-24">
      <div className="max-w-5xl w-full font-mono text-sm flex flex-col">
        <div className="mb-12"><h1 className='text-lg'>Players</h1></div>
        <div className="max-w-lg w-full h-full flex flex-col self-center items-center justify-center mb-6 text-lg">
          <h2>Game Code: {gameCode}</h2>
        </div>
        {readyState !== ReadyState.OPEN || players.length === 0 && <div className="mb-12"><h1 className='text-lg'>Loading...</h1></div>}
        {readyState === ReadyState.OPEN && players.length > 0 &&
          <form className="max-w-lg w-full h-full flex flex-col self-center items-center justify-center" action={startNewGame}>
            <div className='flex flex-col justify-center items-center w-full mb-6 lg:mb-12'>
              {players.map((player, index) => (
                <div key={index} className='flex flex-row justify-center items-center w-full'>
                  <label className='mr-3'>Player {index + 1}</label>
                  <p className="border-2 border-gray-300 p-2 rounded m-2 text-gray-700 bg-white w-2/5">{player}</p>
                </div>
              ))}
            </div>
            {isHost ?
              <div className='w-full flex flex-col justify-center items-center lg:flex-row'>
                <select className="border-2 border-gray-300 p-2 rounded m-2 text-gray-700 bg-white w-2/5" name="variant" value={variant} onChange={e => setVariant(e.target.value as Variant)}>
                  <option value="thavalon">Thavalon</option>
                  <option value="jealousy">Jealousy</option>
                  <option value="esoteric">Esoteric</option>
                </select>
                <button className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded" type="submit">
                  {!isLoading ? "Start" : "Loading..."}
                </button>
              </div> : null}
          </form>
        }
      </div>
    </main>
  )
}