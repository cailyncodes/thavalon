"use client"

import React from "react"
import { Game } from "../../index"
import { RemakeGame } from "./RemakeGame"

interface Props {
  game: Game
  gameCode: string
}

export const GameView = ({ game, gameCode }: Props) => {
  const [username, setUsername] = React.useState<string>();
  const [shouldShowRole, setShouldShowRole] = React.useState<boolean>(false);
  const [shouldShowDoNotOpen, setShouldShowDoNotOpen] = React.useState<boolean>(false);

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
            <div className="flex flex-col justify-center items-center w-full mb-6">
              <div className="flex flex-row justify-center items-center w-full">
                <div className="max-w-3xl w-fit font-mono text-sm flex flex-col justify-center">
                  {shouldShowRole ? (
                    <>
                      <pre className="whitespace-pre-line">
                        {game[username]}
                      </pre>
                      <button
                        className="bg-blue-500 hover:bg-blue-700 w-full text-white font-bold py-2 px-4 rounded w-2/5"
                        onClick={() => setShouldShowRole(false)}
                      >
                        Hide Role
                      </button>
                    </>
                  ) : (
                    <button
                      className="bg-blue-500 hover:bg-blue-700 w-full text-white font-bold py-2 px-4 rounded w-2/5"
                      onClick={() => setShouldShowRole(true)}
                    >
                      Show Role
                    </button>
                  )}
                </div>
              </div>
            </div>
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
          )}
          <hr className="h-px my-2 bg-gray-200 border-0 dark:bg-gray-700"></hr>
          <RemakeGame />
        </div>
      }
    </>
  )
}
