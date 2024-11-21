"use client";

import React, { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

type CommunicationChannel = "http";

function getDomain(env?: string) {
  env = env || "development";

  if (env.startsWith("thavalon-")) {
    return `api-${env}.up.railway.app`;
  }
  switch (env) {
    case "development":
      return "localhost:6464";
    case "next":
      return "next-api.thavalon.quest";
    case "production":
      return "api.thavalon.quest";
    default:
      throw new Error("Unknown environment");
  }
}

function getUrl(env: string | undefined, channel: CommunicationChannel) {
  const origin = getDomain(env);
  return origin.includes("localhost")
    ? `${channel}://${origin}`
    : `${channel}s://${origin}`;
}

interface Person {
  id: string;
  name: string;
}

interface Role {
  id: string;
  name: string;
}

interface Player {
  person: Person;
  role: Role;
}

interface GameData {
  id: string;
  players: Player[];
  starting_person: Player;
}

const GameViewPage: React.FC = () => {
  const pathname = usePathname();
  const gameId = pathname.split("/")[2]; // Extract game_id from URL
  const API_URL = getUrl(process.env.NEXT_PUBLIC_ENVIRONMENT, "http");

  const [gameData, setGameData] = useState<GameData | null>(null);
  const [loading, setLoading] = useState(true);
  const [username, setUsername] = useState<string>("");
  const [showOwnRole, setShowOwnRole] = useState<boolean>(false);
  const [showFullGameState, setShowFullGameState] = useState<boolean>(false);

  useEffect(() => {
    const storedUsername = localStorage.getItem("username") || "";
    setUsername(storedUsername);

    const fetchGameData = async () => {
      try {
        const response = await fetch(`${API_URL}/api/game/${gameId}`);
        if (response.ok) {
          const data: GameData = await response.json();
          setGameData(data);
        } else {
          console.error("Failed to fetch game data.");
        }
      } catch (error) {
        console.error("Error fetching game data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchGameData();
  }, [gameId, API_URL]);

  const closeGame = async () => {
    try {
      const response = await fetch(`${API_URL}/api/game/${gameId}/close`, {
        method: "POST",
      });
      if (response.ok) {
        toast.success("Game closed successfully!");
      } else {
        toast.error("Failed to close game.");
      }
    } catch (error) {
      console.error("Error closing game:", error);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <p className="text-gray-400">Loading game data...</p>
      </div>
    );
  }

  if (!gameData) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <p className="text-gray-400">No game data available.</p>
      </div>
    );
  }

  const currentPlayer = gameData.players.find(
    (player) => player.person.name === username
  );

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <ToastContainer />
      <motion.section
        className="text-center mb-12"
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <h1 className="text-4xl font-bold text-indigo-400">Game Overview</h1>
        <p className="text-lg text-gray-300 mt-2">Viewing game ID: {gameId}</p>
        <div className="mt-4 flex justify-center items-center space-x-4">
          <button
            onClick={() => {
              const fullUrl = `${window.location.origin}/game/${gameId}/view`;
              navigator.clipboard.writeText(fullUrl);
              toast.success("Link copied to clipboard!");
            }}
            className="bg-blue-500 hover:bg-blue-400 text-white font-bold py-2 px-4 rounded-lg shadow-md flex items-center space-x-2"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M9 2H15C15.5523 2 16 2.44772 16 3V7H20C20.5523 7 21 7.44772 21 8V20C21 20.5523 20.5523 21 20 21H4C3.44772 21 3 20.5523 3 20V8C3 7.44772 3.44772 7 4 7H8V3C8 2.44772 8.44772 2 9 2ZM10 3V7H14V3H10ZM5 9V19H19V9H5Z"
              />
            </svg>
            <span>Copy Link</span>
          </button>
        </div>
      </motion.section>



      <div className="space-y-8">
        <motion.div
          className="bg-gray-800 p-6 rounded-lg shadow-lg"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h2 className="text-2xl font-bold text-indigo-300">
            Starting Player
          </h2>
          <p className="mt-2 text-gray-200">
            {gameData.starting_person.name}
          </p>
        </motion.div>

        {currentPlayer && (
          <motion.div
            className="bg-gray-800 p-6 rounded-lg shadow-lg"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-2xl font-bold text-indigo-300">
              Your Information
            </h2>
            <button
              onClick={() => setShowOwnRole(!showOwnRole)}
              className="mt-4 bg-blue-500 hover:bg-blue-400 text-white font-bold py-2 px-4 rounded-lg shadow-md"
            >
              {showOwnRole ? "Hide Your Role" : "Show Your Role"}
            </button>
            {showOwnRole && (
              <>
                <p className="mt-4 text-lg text-indigo-400">
                  Your Role: {currentPlayer.role.name}
                </p>
                <p className="mt-4 text-lg text-indigo-400">
                  {currentPlayer.role.description}
                </p>
                <p className="mt-4 text-lg text-indigo-400">
                  {currentPlayer.role.information.map((info, index) => (
                    <span key={index}>
                      {info}
                      <br />
                    </span>
                  ))}
                </p>
              </>
            )}
          </motion.div>
        )}

        <motion.div
          className="bg-red-800 p-6 rounded-lg shadow-lg"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h2 className="text-2xl font-bold text-red-300">Danger Zone</h2>
          <p className="mt-2 text-red-200">
            The following button will reveal the full game state.
          </p>
          <button
            onClick={() => setShowFullGameState(!showFullGameState)}
            className="mt-4 bg-red-600 hover:bg-red-500 text-white font-bold py-2 px-4 rounded-lg shadow-md"
          >
            {showFullGameState ? "Hide Full Game State" : "Show Full Game State"}
          </button>
          <button
            onClick={() => closeGame()}
            className="mt-4 ml-4 bg-orange-600 hover:bg-orange-500 text-white font-bold py-2 px-4 rounded-lg shadow-md"
          >
            Terminate Game
          </button>
          {showFullGameState && (
            <div className="mt-6 space-y-4">
              {gameData.players.map((player, index) => (
                <div
                  key={index}
                  className="p-4 bg-red-700 rounded-lg shadow-md flex flex-col space-y-2"
                >
                  <p className="text-xl text-white font-semibold">
                    {player.person.name}
                  </p>
                  <p className="text-red-200">
                    Role:{" "}
                    <span className="text-red-100 font-medium">
                      {player.role.name}
                    </span>
                  </p>
                </div>
              ))}
            </div>
          )}
        </motion.div>

        <motion.div
          className="bg-gray-800 p-6 rounded-lg shadow-lg"
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h2 className="text-2xl font-bold text-indigo-300">Players</h2>
          <ul className="mt-4 space-y-4">
            {gameData.players.map((player, index) => (
              <li
                key={index}
                className="p-4 bg-gray-700 rounded-lg shadow-md flex flex-col space-y-2"
              >
                <p className="text-xl text-white font-semibold">
                  {player.person.name}
                </p>
              </li>
            ))}
          </ul>
        </motion.div>
      </div>
    </div>
  );
};

export default GameViewPage;
