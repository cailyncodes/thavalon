"use client"

import React from "react"
import { Game } from "../../index"
import { RemakeGame } from "./RemakeGame"
import { GameStateManager } from "./GameStateManager"

interface Props {
  game: Game
  gameCode: string
}

export const GameView = ({ game, gameCode }: Props) => {
  const [username, setUsername] = React.useState<string>();
  const [shouldShowDoNotOpen, setShouldShowDoNotOpen] = React.useState<boolean>(false);
  const [showSecretRole, setShowSecretRole] = React.useState<boolean>(false);

  React.useEffect(() => {
    const name = window.localStorage.getItem("username");
    if (name) {
      setUsername(name);
    }
  }, []);

  if (!username) {
    return null
  }

  return (
    <>
      {game &&
        <div className="max-w-5xl w-full font-mono text-sm flex flex-col">
          <div className="max-w-lg w-full h-full flex flex-col self-center items-center justify-center mb-6 text-lg">
            <h2>Game Code: {gameCode}</h2>
          </div>
          <div className="max-w-lg w-full h-full flex flex-col self-center items-center justify-center">
            <div className="flex flex-row justify-center items-center w-full mb-6">
              <p className='text-md font-bold'>{game.start}</p>
            </div>
            <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" 
              onClick={() => {
                setShowSecretRole(prev => !prev)
              }}>
              {showSecretRole ? "Hide Role Info" : "Show Role Info"}
            </button>
            {showSecretRole && <div className="flex flex-col justify-center items-center w-full mb-6">
              <div className="flex flex-row justify-center items-center w-full mb-4">
                <div className="max-w-3xl w-full font-mono text-sm flex flex-col">
                  <pre className="whitespace-pre-line">
                    {game[username]}
                  </pre>
                </div>
              </div>
            </div>}
          </div>
          {shouldShowDoNotOpen ? (
            <div className="max-w-lg w-full h-full flex flex-col self-center items-center justify-center mb-6">
              <div className="flex flex-row justify-center items-center w-full mb-4">
                <div className="max-w-3xl w-full font-mono text-sm flex flex-col">
                  <pre className="whitespace-pre-line">
                    {game["doNotOpen"]}
                  </pre>
                </div>
              </div>
            </div>
          ) : (
            <div className="max-w-lg w-full h-full flex flex-col self-center items-center justify-center mb-6">
              <button
                className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded w-2/5"
                onClick={() => {
                  if (window.confirm("Are you sure? Cancel to close.")) {
                    setShouldShowDoNotOpen(true)
                  }
                }}
              >
                Show Do Not Open
              </button>
            </div>
          )
          }
          <GameStateManager  gameId={game.gameId}/>
          <RemakeGame />
        </div>
      }
    </>
  )
}
