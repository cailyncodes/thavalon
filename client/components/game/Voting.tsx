import React, { useState } from "react";
import { motion } from "framer-motion";
import { Mission, MissionVote, Person } from "../../types";

interface VotingSectionProps {
  roundNumber: number;
  person: Person;
  currentMission: Mission;
  submitVote: (vote: MissionVote) => void;
}

const VotingSection = ({
  roundNumber,
  person,
  currentMission,
  submitVote,
}: VotingSectionProps) => {
  const vote = currentMission?.votes[person.name] ?? null;
  const [selectedVote, setSelectedVote] = useState<MissionVote | null>(vote);

  return (
    <motion.div
      className="bg-gray-800 p-6 rounded-lg shadow-lg"
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
    >
      <h2 className="text-2xl font-bold text-indigo-300">Cast Your Vote</h2>
      <p className="mt-2 text-gray-200">
        You are on mission #{roundNumber}. Please cast your vote.
      </p>
      <p className="mt-2 text-gray-200">
        Current Mission: {currentMission?.team.map((person) => person.name).join(", ")}
      </p>
      <div className="mt-4 flex space-x-4">
        {(["Success", "Fail", "Reverse", "Cancel"] as MissionVote[]).map((vote) => (
          <motion.button
            key={vote}
            whileHover={{
              scale: 1.05,
            }}
            whileTap={{
              scale: 0.95,
            }}
            onClick={() => setSelectedVote(vote)}
            className={`px-4 py-2 rounded-lg shadow-md font-bold text-white ${
              selectedVote === vote ? "bg-indigo-600" : "bg-gray-700"
            }`}
          >
            {vote}
          </motion.button>
        ))}
      </div>
      <motion.button
        whileHover={{
          scale: 1.05,
        }}
        whileTap={{
          scale: 0.95,
        }}
        onClick={() => submitVote(selectedVote as MissionVote)}
        className={`mt-4 bg-green-500 hover:bg-green-400 text-white font-bold py-2 px-4 rounded-lg shadow-md ${
          !selectedVote ? "opacity-50 cursor-not-allowed" : ""
        }`}
        disabled={!selectedVote}
      >
        Submit Vote
      </motion.button>
    </motion.div>
  )
}

export default VotingSection;
