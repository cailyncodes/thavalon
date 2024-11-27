import { useState } from "react";
import { motion } from "framer-motion"
import { Game } from "../../types";

interface DangerZoneProps {
  game: Game;
  closeGame: () => void;
}

const DangerZone = ({ game, closeGame }: DangerZoneProps) => {
  const [showFullGameState, setShowFullGameState] = useState(false);

  return (
    <motion.div
    className="bg-red-800 p-6 rounded-lg shadow-lg flex flex-col"
    initial={{ opacity: 0, y: 50 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.8 }}
  >
    <div className="sm:w-full flex-grow">
      <h2 className="text-2xl font-bold text-red-300">Danger Zone</h2>
      <p className="mt-2 text-red-200">
        The following button will reveal the full game state.
      </p>
    </div>
    <div className="flex flex-col sm:flex-row">
      <button
        onClick={() => setShowFullGameState(!showFullGameState)}
        className="w-full sm:max-w-fit sm mt-4 bg-red-600 hover:bg-red-500 text-white font-bold py-2 px-4 rounded-lg shadow-md"
      >
        {showFullGameState ? "Hide Full Game State" : "Show Full Game State"}
      </button>
      {game.status !== "closed" && (
        <button
          onClick={() => closeGame()}
          className="w-full sm:max-w-fit mt-4 sm:ml-4 bg-orange-600 hover:bg-orange-500 text-white font-bold py-2 px-4 rounded-lg shadow-md"
        >
          Terminate Game
        </button>
      )}
    </div>
    {showFullGameState && (
      <div className="mt-6 space-y-4">
        {game.players.map((player, index) => (
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
  )
};

export default DangerZone;
