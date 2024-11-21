
"use client";

import React, { useState, useEffect } from "react";
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

const Lobby = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [username, setUsername] = useState<string | null>(null);
  const [lobbies, setLobbies] = useState<any[]>([]);
  const [lobbyName, setLobbyName] = useState<string>("");
  const [gameStarted, setGameStarted] = useState<boolean>(false);

  const API_URL = getUrl(process.env.RAILWAY_ENVIRONMENT_NAME, "http");

  // Load username from LocalStorage
  useEffect(() => {
    const storedUsername = localStorage.getItem("username");
    if (storedUsername) {
      setUsername(storedUsername);
    }
    fetchLobbies();
  }, []);

  // Save username to LocalStorage
  const saveUsername = (name: string) => {
    localStorage.setItem("username", name);
    setUsername(name);
  };

  // Fetch all active lobbies
  const fetchLobbies = async () => {
    try {
      const response = await fetch(`${API_URL}/api/lobby/`);
      if (response.ok) {
        const data = await response.json();
        // @ts-expect-error
        if (data.lobbies.find((lobby) =>
          lobby.persons?.some((player: { name: string }) => player.name === username)
        )?.status === "in-progress") {
          console.log("Game started");
          setGameStarted(true);
        }
        setLobbies(data.lobbies || []);
      } else {
        console.error("Failed to fetch lobbies");
      }
    } catch (error) {
      console.error("Error fetching lobbies:", error);
    }
  };

  // Poll lobbies every 500ms
  useEffect(() => {
    const interval = setInterval(() => {
      fetchLobbies();
    }, 500);

    return () => clearInterval(interval); // Cleanup on unmount
  }, [username]);

  // Check if the user is already in a lobby
  const isUserInLobby = () => {
    return lobbies.some((lobby) =>
      lobby.persons?.some((player: { name: string }) => player.name === username) && lobby.status !== "closed"
    );
  };

  const getActiveLobby = () => {
    return lobbies.find((lobby) =>
      lobby.persons?.some((player: { name: string }) => player.name === username)
    );
  }

  // Create a new lobby
  const createNewLobby = async () => {
    if (!username) {
      toast.error("Please set your name first!");
      return;
    }
    if (!lobbyName) {
      toast.error("Please provide a lobby name!");
      return;
    }
    if (isUserInLobby()) {
      toast.error("You are already in a lobby. Leave or finish it to create a new one.");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/lobby/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: lobbyName,
          persons: [{ name: username, login: "" }],
        }),
      });

      if (!response.ok) {
        toast.error("Failed to create lobby.");
        return;
      }

      const data = await response.json();
      toast.success(`Lobby "${lobbyName}" created successfully!`);
      setLobbyName(""); // Clear the input after creation
      fetchLobbies(); // Refresh lobbies after creating one
    } catch (error) {
      console.error("Error creating lobby:", error);
      toast.error("An error occurred while creating the lobby.");
    } finally {
      setIsLoading(false);
    }
  };

  // Prompt to set username
  const login = () => {
    const name = prompt("Enter your name");
    if (name) {
      saveUsername(name);
    }
  };

  const startGame = async (lobbyId: string) => {
    try {
      const response = await fetch(`${API_URL}/api/game`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ lobby_id: lobbyId }),
      });

      if (response.ok) {
        toast.success("Game started successfully!");
      } else {
        toast.error("Failed to start the game.");
      }
    } catch (error) {
      console.error("Error starting game:", error);
      toast.error("An error occurred while starting the game.");
    }
  };

  const isStartGameEnabled = (lobby: any) => {
    return (
      lobby.persons[0]?.name === username && // The user is the first player in the lobby
      lobby.persons.length >= 1 && // Minimum 5 players
      lobby.persons.length <= 10 && // Maximum 10 players
      !isLoading // Not currently loading
    );
  };

  // Join a lobby
  const joinLobby = async (lobbyId: string) => {
    if (!username) {
      toast.error("Please set your name first!");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/lobby/${lobbyId}/join`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          person: { name: username, login: "" },
        }),
      });

      if (!response.ok) {
        toast.error("Failed to join the lobby.");
        return;
      }

      const data = await response.json();
      toast.success(`Joined lobby "${data.name}" successfully!`);
      fetchLobbies(); // Refresh the lobbies list
    } catch (error) {
      console.error("Error joining lobby:", error);
      toast.error("An error occurred while joining the lobby.");
    } finally {
      setIsLoading(false);
    }
  };

  React.useEffect(() => {
    console.log(lobbies, isUserInLobby(), gameStarted);
    // if the user is already in a lobby and it is now closed, redirect to the game page
    if (isUserInLobby() && gameStarted) {
      const activeLobby = getActiveLobby();
      console.log(activeLobby);
      window.location.assign(`/game/${activeLobby.game_id}/view`);
    }
  }, [lobbies, gameStarted]);

  return (
    <div className="flex flex-col min-h-screen">
      <ToastContainer />

      {/* Full-Bleed Hero Section */}
      <motion.section
        className="relative w-full py-20 bg-gradient-to-br from-purple-600 via-indigo-600 to-blue-600 text-center text-white"
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <div className="max-w-5xl mx-auto px-6">
          <h1 className="text-5xl font-bold leading-tight drop-shadow-lg">
            Welcome to Thavalon
          </h1>
          <p className="mt-4 text-lg leading-relaxed text-gray-200">
            A social deception game where strategy, trust, and betrayal come
            together.
          </p>
        </div>
      </motion.section>

      {/* Main Content Section */}
      <div className="flex-grow w-full max-w-6xl mx-auto px-6 py-12 space-y-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Create Lobby Section */}
          <motion.div
            className="col-span-1 bg-gray-800 p-6 rounded-lg shadow-lg"
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
          >
            {!username ? (
              <motion.button
                onClick={login}
                className="bg-indigo-500 hover:bg-indigo-400 text-white font-bold py-3 px-6 rounded-lg shadow-md w-full"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Set Your Name
              </motion.button>
            ) : (
              <>
                <p className="text-lg text-gray-300 mb-4">
                  Welcome,{" "}
                  <span className="font-semibold text-indigo-300">
                    {username}
                  </span>
                  !
                </p>
                <div className="mb-4">
                  <input
                    type="text"
                    value={lobbyName}
                    onChange={(e) => setLobbyName(e.target.value)}
                    placeholder="Enter lobby name"
                    className="w-full p-3 rounded-lg text-gray-800"
                  />
                </div>
                <motion.button
                  onClick={createNewLobby}
                  className={`bg-indigo-500 hover:bg-indigo-400 text-white font-bold py-3 px-6 rounded-lg shadow-md ${isLoading ? "opacity-50 cursor-not-allowed" : ""
                    } w-full`}
                  disabled={isLoading}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  {isLoading ? "Creating Lobby..." : "Create New Lobby"}
                </motion.button>
              </>
            )}
          </motion.div>

          {/* Available Lobbies Section */}
          <motion.div
            className="col-span-2 bg-gray-700 p-8 rounded-lg shadow-lg"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-2xl font-bold text-indigo-300 mb-6 text-center">
              Available Lobbies
            </h2>
            <div className="space-y-6">
              {lobbies.filter((lobby) => lobby.status === "open").length > 0 ? (
                lobbies.filter((lobby) => lobby.status === "open").map((lobby) => (
                  <motion.div
                    key={lobby.lobby_id}
                    className="p-6 bg-gray-800 rounded-lg shadow-md flex flex-col justify-between items-start border-l-4 border-indigo-500"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div>
                      <p className="text-xl font-semibold text-gray-100">{lobby.name}</p>
                      <p className="text-sm text-gray-400">Players:</p>
                      <ul className="text-gray-300 list-disc list-inside">
                        {lobby.persons?.map((player: { name: string }) => (
                          <li key={player.name}>
                            {player.name}{" "}
                            {player.name === username ? (
                              <span className="text-indigo-300 font-bold">(You)</span>
                            ) : null}
                          </li>
                        )) || <p className="text-gray-400">No players yet</p>}
                      </ul>
                    </div>
                    {lobby.persons[0]?.name === username && (
                      <motion.button
                        onClick={() => startGame(lobby.lobby_id)}
                        className={`mt-4 text-white font-bold py-2 px-4 rounded-lg shadow-md ${isStartGameEnabled(lobby)
                          ? "bg-green-500 hover:bg-green-400"
                          : "bg-gray-500 cursor-not-allowed"
                          }`}
                        whileHover={{
                          scale: isStartGameEnabled(lobby) ? 1.05 : 1,
                        }}
                        whileTap={{
                          scale: isStartGameEnabled(lobby) ? 0.95 : 1,
                        }}
                        disabled={!isStartGameEnabled(lobby)}
                      >
                        Start Game
                      </motion.button>
                    )}
                    {!lobby.persons.some((player: { name: string }) => player.name === username) && (
                      <motion.button
                        onClick={() => joinLobby(lobby.lobby_id)}
                        className={`mt-4 bg-blue-500 hover:bg-blue-400 text-white font-bold py-2 px-4 rounded-lg shadow-md ${isLoading ? "opacity-50 cursor-not-allowed" : ""
                          }`}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        disabled={isLoading}
                      >
                        Join Lobby
                      </motion.button>
                    )}
                  </motion.div>
                ))
              ) : (
                <p className="text-gray-400 text-center">
                  No active lobbies found.
                </p>
              )}
            </div>
          </motion.div>

        </div>
        <motion.div
          className="bg-gray-700 p-8 rounded-lg shadow-lg"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h2 className="text-2xl font-bold text-indigo-300 mb-6 text-center">
            In-Progress Games
          </h2>
          <div className="space-y-6">
            {lobbies
              .filter((lobby) => lobby.status === "in-progress")
              .length > 0 ?
              (lobbies
                .filter((lobby) => lobby.status === "in-progress")
                .map((lobby) => (
                  <div key={lobby.lobby_id} className="p-6 bg-gray-800 rounded-lg shadow-md">
                    <p className="text-xl text-gray-100 mb-3">{lobby.name}</p>
                    <p className="text-sm text-gray-300">
                      {/* @ts-expect-error */}
                      {lobby.persons?.map((player: { name: string }, index) => (
                        <span key={player.name}>
                          {player.name}
                          {player.name === username ? (
                            <span className="text-indigo-300 font-bold">{" "}(You)</span>
                          ) : null}
                          {index === lobby.persons.length - 1 ? "" : ", "}
                        </span>
                      ))}
                    </p>
                    <a
                      href={`/game/${lobby.game_id}/view`}
                      className="mt-4 inline-block text-indigo-400 hover:underline"
                    >
                      Spectate Game
                    </a>
                  </div>
                ))) : <p className="text-gray-400 text-center">
                No in progress games found.
              </p>}
          </div>
        </motion.div>
      </div>

      {/* Footer Section */}
      <footer className="w-full py-6 bg-gray-800 text-center text-sm text-gray-400 border-t border-gray-700">
        <motion.div
          className="space-y-2"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.6 }}
        >
          <p>&copy; 2024 Thavalon. All rights reserved.</p>
          <p>
            Built with 💜 by the{" "}
            <a
              href="https://github.com/cailyncodes/thavalon"
              target="_blank"
              rel="noopener noreferrer"
              className="underline hover:text-indigo-300"
            >
              Thavalon Team
            </a>
          </p>
        </motion.div>
      </footer>
    </div>
  );
};

export default Lobby;
