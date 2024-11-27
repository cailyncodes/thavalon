import { motion } from "framer-motion";
import { Player } from "../../types";

interface PlayerDetailsProps {
  currentPlayer: Player | undefined;
  showOwnRole: boolean;
  toggleShowOwnRole: () => void;
}

const PlayerDetails = ({ currentPlayer, showOwnRole, toggleShowOwnRole }: PlayerDetailsProps) => (
  <motion.div
    className="bg-gray-800 p-6 rounded-lg shadow-lg"
    initial={{ opacity: 0, y: 50 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.8 }}
  >
    <h2 className="text-2xl font-bold text-indigo-300">Your Information</h2>
    <button
      onClick={toggleShowOwnRole}
      className="mt-4 bg-blue-500 hover:bg-blue-400 text-white font-bold py-2 px-4 rounded-lg shadow-md"
    >
      {showOwnRole ? "Hide Your Role" : "Show Your Role"}
    </button>
    {showOwnRole && currentPlayer && (
      <>
        <p className="mt-4 text-lg text-indigo-400">Your Role: {currentPlayer.role.name}</p>
        <p className="mt-4 text-lg text-indigo-400">{currentPlayer.role.description}</p>
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
);

export default PlayerDetails;
