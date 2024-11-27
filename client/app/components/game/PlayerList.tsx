import { motion } from "framer-motion"
import { Player } from "../../types";

interface PlayerListProps {
  currentPlayer: Player | null;
  players: Player[];
}

const PlayerList = ({ currentPlayer, players }: PlayerListProps) => {
  return (
    <motion.div
      className="bg-gray-800 p-6 rounded-lg shadow-lg"
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.8 }}
    >
      <h2 className="text-2xl font-bold text-indigo-300">Players</h2>
      <ul className="mt-4 space-y-4">
        {players.map((player, index) => (
          <li
            key={index}
            className="p-4 bg-gray-700 rounded-lg shadow-md flex flex-col space-y-2"
          >
            <p className="text-xl text-white font-semibold">
              {player.person.name} {player.person.name == currentPlayer?.person.name ? "(you)" : ""}
            </p>
          </li>
        ))}
      </ul>
    </motion.div>
  );
};

export default PlayerList;
