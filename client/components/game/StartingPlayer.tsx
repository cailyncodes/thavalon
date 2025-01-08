import { motion } from "framer-motion"
import { Person } from "../../types";

interface StartingPlayerProps {
  person: Person;
}

const StartingPlayer = ({ person }: StartingPlayerProps) => {
  return <div className="space-y-8">
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
      {person.name}
    </p>
  </motion.div>
  </div>
}

export default StartingPlayer;
