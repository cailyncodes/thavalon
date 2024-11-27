"use client";

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { Game } from "./types";

interface HomeProps {
  url: string;
}

const Home = ({ url }: HomeProps) => {
  const [isLoading, setIsLoading] = useState(false);
  const [username, setUsername] = useState<string | null>(null);
  const [variant, setVariant] = useState<string | null>(null);
  const [openGames, setOpenGames] = useState<Game[]>([]);
  const [inProgressGames, setInProgressGames] = useState<Game[]>([]);
  const [closedGames, setClosedGames] = useState<Game[]>([]);
  const games = {
    open: openGames,
    inProgress: inProgressGames,
    closed: closedGames
  }
  const [activeGame, setActiveGame] = useState<Game | null>(null);
  const [activeGameStatus, setActiveGameStatus] = useState<string | null>(null);

  // Load username from LocalStorage
  useEffect(() => {
    const storedUsername = localStorage.getItem("username");
    if (storedUsername) {
      setUsername(storedUsername);
    }
    fetchGames();
  }, []);

  // Save username to LocalStorage
  const saveUsername = (name: string) => {
    localStorage.setItem("username", name);
    setUsername(name);
  };

  const login = () => {
    const name = prompt("Please enter your name:");
    if (name) {
      saveUsername(name);
    }
  };

  // Fetch all games by status
  const fetchGames = async () => {
    try {
      const response = await fetch(`${url}/api/game/status`);

      if (response.ok) {
        const games = await response.json();
        setOpenGames(games.open || []);
        setInProgressGames(games["in-progress"] || []);
        setClosedGames(games.closed || []);
        const activeGame = getActiveGame(games)
        if (activeGame) {
          setActiveGame(activeGame);
        }
      } else {
        console.error("Failed to fetch games");
      }
    } catch (error) {
      console.error("Error fetching games:", error);
    }
  };

  const getActiveGame = (games: Record<string, Game[]>) => {
    return Object.values(games).flat().find((game) =>
      game.persons?.some((person: { name: string }) => person.name === username) && game.status !== "closed"
    );
  }

  useEffect(() => {
    if (activeGame) {
      setActiveGameStatus(activeGame.status);
    }
  }, [activeGame]);

  useEffect(() => {
    const interval = setInterval(() => {
      fetchGames();
    }, 750);

    return () => clearInterval(interval); // Cleanup on unmount
  }, [username]);

  // Create a new game
  const createNewGame = async () => {
    if (!username) {
      toast.error("Please set your name first!");
      return;
    }
    if (getActiveGame(games)) {
      toast.error("You are already in a game. Leave or finish it to create a new one.");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`${url}/api/game/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          persons: [{ name: username }],
        }),
      });

      if (!response.ok) {
        toast.error("Failed to create game.");
        return;
      }

      const data = await response.json();
      toast.success(`Game "${data.name}" created successfully!`);
      fetchGames(); // Refresh games after creating one
    } catch (error) {
      console.error("Error creating game:", error);
      toast.error("An error occurred while creating the game.");
    } finally {
      setIsLoading(false);
    }
  };

  const assignRolesAndStartGame = async (gameId: string) => {
    try {
      const response = await fetch(`${url}/api/game/${gameId}/assign_roles_and_start`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          variant,
        }),
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

  const isStartGameEnabled = (game: any) => {
    return (
      game.persons[0]?.name === username && // The user is the first player in the game
      game.persons.length >= 5 && // Minimum 5 players
      game.persons.length <= 10 && // Maximum 10 players
      !isLoading // Not currently loading
    );
  };

  // Join a game
  const joinGame = async (gameId: string) => {
    if (!username) {
      toast.error("Please set your name first!");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`${url}/api/game/${gameId}/join`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          person: { name: username },
        }),
      });

      if (!response.ok) {
        toast.error("Failed to join the game.");
        return;
      }

      const data = await response.json();
      toast.success(`Joined game "${data.name}" successfully!`);
      fetchGames(); // Refresh the games list
    } catch (error) {
      console.error("Error joining game:", error);
      toast.error("An error occurred while joining the game.");
    } finally {
      setIsLoading(false);
    }
  };

  // Close a game
  const closeGame = async (gameId: string) => {
    try {
      const response = await fetch(`${url}/api/game/${gameId}/close`, {
        method: "POST",
      });

      if (response.ok) {
        toast.success("Game closed successfully!");
        fetchGames(); // Refresh the games list
      } else {
        toast.error("Failed to close the game.");
      }
    } catch (error) {
      console.error("Error closing game:", error);
      toast.error("An error occurred while closing the game.");
    }
  };

  const handleVariantChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setVariant(event.target.value);
  };

  React.useEffect(() => {
    if (activeGame && activeGameStatus === "in-progress") {
      window.location.assign(`/game/${activeGame.id}/view`);
    }
  }, [activeGame, activeGameStatus]);

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
          {/* Create Game Section */}
          <motion.div
            className="col-span-2 md:col-span-1 bg-gray-800 p-6 rounded-lg shadow-lg"
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
                <motion.button
                  onClick={createNewGame}
                  className={`bg-indigo-500 hover:bg-indigo-400 text-white font-bold py-3 px-6 rounded-lg shadow-md ${isLoading ? "opacity-50 cursor-not-allowed" : ""
                    } w-full`}
                  disabled={isLoading}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  {isLoading ? "Creating Game..." : "Create New Game"}
                </motion.button>
              </>
            )}
          </motion.div>

          {/* Available Games Section */}
          <motion.div
            className="col-span-2 bg-gray-700 p-8 rounded-lg shadow-lg"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-2xl font-bold text-indigo-300 mb-6 text-center">
              Available Games
            </h2>
            <div className="space-y-6">
              {games.open.length > 0 ? (
                games.open.map((game) => (
                  <motion.div
                    key={game.id}
                    className="p-6 bg-gray-800 rounded-lg shadow-md flex flex-col justify-between items-start border-l-4 border-indigo-500"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div>
                      <p className="text-xl font-semibold text-gray-100">{game.name}</p>
                      <p className="text-sm text-gray-400">
                          {game.persons.length} / 10 players
                        </p>
                      <ul className="text-gray-300 list-disc list-inside">
                        {game.persons?.map((person: { name: string }) => (
                          <li key={person.name}>
                            {person.name}{" "}
                            {person.name === username ? (
                              <span className="text-indigo-300 font-bold">(You)</span>
                            ) : null}
                          </li>
                        )) || <p className="text-gray-400">No players yet</p>}
                      </ul>
                    </div>
                    {game.persons[0]?.name === username && (
                      <div className="flex flex-col sm:flex-row gap-4 mt-4 w-full">
                        <motion.select
                          value={variant ?? "thavalon"}
                          onChange={handleVariantChange}
                          className="w-full sm:w-auto appearance-none bg-white border border-gray-300 text-gray-700 py-2 px-4 pr-10 rounded-lg shadow-sm"
                          style={{
                            appearance: 'none', // Remove default arrow in some browsers
                            backgroundColor: '#fff',
                            backgroundImage: 'url("data:image/svg+xml;charset=US-ASCII,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'10\' height=\'5\' viewBox=\'0 0 10 5\'><path fill=\'%23000\' d=\'M0 0l5 5 5-5z\'/></svg>")',
                            backgroundRepeat: 'no-repeat',
                            backgroundPosition: 'right 15px center',
                            backgroundSize: '10px 5px',
                          }}
                          aria-label="Select Variant"
                        >
                          <motion.option value="thavalon">Thavalon</motion.option>
                          <motion.option value="jealousy">Jealousy</motion.option>
                          <motion.option value="esoteric">Esoteric</motion.option>
                        </motion.select>
                        <motion.button
                          onClick={() => assignRolesAndStartGame(game.id)}
                          className={`w-full sm:w-auto text-white font-semibold py-2 px-4 rounded-lg shadow-md ${
                            isStartGameEnabled(game)
                              ? "bg-green-500 hover:bg-green-400"
                              : "bg-gray-500 cursor-not-allowed"
                          } focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-opacity-50 transition duration-200`}
                          whileHover={{
                            scale: isStartGameEnabled(game) ? 1.05 : 1,
                          }}
                          whileTap={{
                            scale: isStartGameEnabled(game) ? 0.95 : 1,
                          }}
                          disabled={!isStartGameEnabled(game)}
                          aria-label="Start Game"
                        >
                          Start Game
                        </motion.button>

                        {/* Close Game Button */}
                        <motion.button
                          onClick={() => closeGame(game.id)}
                          className="w-full sm:w-auto text-white font-semibold py-2 px-4 rounded-lg shadow-md bg-yellow-500 hover:bg-yellow-400 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:ring-opacity-50 transition duration-200"
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          aria-label="Close Game"
                        >
                          Close Game
                        </motion.button>
                      </div>
                    )}
                    {!game.persons.some((person: { name: string }) => person.name === username) && (
                      <motion.button
                        onClick={() => joinGame(game.id)}
                        className={`mt-4 bg-blue-500 hover:bg-blue-400 text-white font-bold py-2 px-4 rounded-lg shadow-md ${isLoading ? "opacity-50 cursor-not-allowed" : ""
                          }`}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        disabled={isLoading}
                      >
                        Join Game
                      </motion.button>
                    )}
                  </motion.div>
                ))
              ) : (
                <p className="text-gray-400 text-center">
                  No active games found.
                </p>
              )}
            </div>
          </motion.div>
        </div>

        {/* In-Progress Games Section */}
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
            {games.inProgress.length > 0 ? (
              games.inProgress.map((game) => (
                <div key={game.id} className="p-6 bg-gray-800 rounded-lg shadow-md">
                  <p className="text-xl text-gray-100 mb-3">{game.name}</p>
                  <p className="text-sm text-gray-300">
                    {game.persons?.map((person: { name: string }, index) => (
                      <span key={person.name}>
                        {person.name}
                        {person.name === username ? (
                          <span className="text-indigo-300 font-bold">{" "}(You)</span>
                        ) : null}
                        {index === game.persons.length - 1 ? "" : ", "}
                      </span>
                    ))}
                  </p>
                  <a
                    href={`/game/${game.id}/view`}
                    className="mt-4 inline-block text-indigo-400 hover:underline"
                  >
                    Spectate Game
                  </a>
                </div>
              ))
            ) : (
              <p className="text-gray-400 text-center">
                No in-progress games found.
              </p>
            )}
          </div>
        </motion.div>

        {/* Completed Games Section */}
        <motion.div
          className="bg-gray-700 p-8 rounded-lg shadow-lg"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h2 className="text-2xl font-bold text-indigo-300 mb-6 text-center">
            Completed Games
          </h2>
          <div className="space-y-6">
            {games.closed.length > 0 ? (
              games.closed.map((game) => (
                <div key={game.id} className="p-6 bg-gray-800 rounded-lg shadow-md">
                  <p className="text-xl text-gray-100 mb-3">{game.name}</p>
                  <p className="text-sm text-gray-300">
                    {game.persons?.map((person: { name: string }, index) => (
                      <span key={person.name}>
                        {person.name}
                        {person.name === username ? (
                          <span className="text-indigo-300 font-bold">{" "}(You)</span>
                        ) : null}
                        {index === game.persons.length - 1 ? "" : ", "}
                      </span>
                    ))}
                  </p>
                  <a
                    href={`/game/${game.id}/view`}
                    className="mt-4 inline-block text-indigo-400 hover:underline"
                  >
                    View Game
                  </a>
                </div>
              ))
            ) : (
              <p className="text-gray-400 text-center">
                No completed games found.
              </p>
            )}
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

export default Home;
