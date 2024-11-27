import { motion } from "framer-motion";
import { toast } from "react-toastify";
import { Game } from "../../types";

interface GameHeaderProps {
  game: Game;
}

const GameHeader = ({ game }: GameHeaderProps) => (
  <motion.section
    className="text-center"
    initial={{ opacity: 0, y: -50 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.8 }}
  >
    <h1 className="text-4xl font-bold text-indigo-400">Game Overview</h1>
    <p className="text-lg text-gray-300 mt-2">Viewing game: {game.name}</p>
    <div className="mt-4 flex justify-center items-center space-x-4">
      <button
        onClick={() => {
          const fullUrl = `${window.location.origin}/game/${game.id}/view`;
          navigator.clipboard.writeText(fullUrl);
          toast.success("Link copied to clipboard!");
        }}
        className="bg-blue-500 hover:bg-blue-400 text-white font-bold py-2 px-4 rounded-lg shadow-md flex items-center space-x-2"
      >
        {/* SVG Icon */}
        <span>Copy Link</span>
      </button>
      <button
        onClick={() => window.location.assign("/")}
        className="bg-purple-700 hover:bg-purple-600 text-white font-bold py-2 px-4 rounded-lg shadow-md"
      >
        Return to main page
      </button>
    </div>
  </motion.section>
);

export default GameHeader;
