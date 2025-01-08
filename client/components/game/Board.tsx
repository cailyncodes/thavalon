"use client";

import React, { useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Mission, MissionVote } from "../../types";

interface MissionBoardProps {
  numPlayers: number;
  currentRound: number;
  missions: Mission[];
}

function superShuffle<T>(list: T[]): T[] {
  const randomValues = Array.from(crypto.getRandomValues(new Uint32Array(list.length)));

  return list.reduceRight(
      (shuffled, _, i) => {
          const randomIndex = randomValues[i] % (i + 1);
          return shuffled.map((val, idx) =>
              idx === i ? shuffled[randomIndex] :
              idx === randomIndex ? shuffled[i] :
              val
          );
      },
      [...list]
  );
}

const MissionBoard = ({ numPlayers, currentRound, missions }: MissionBoardProps) => {
  const [shuffledVotes, setShuffledVotes] = React.useState<MissionVote[][]>(
    missions.map((m) => superShuffle(Object.values(m.votes)))
  );

  useEffect(() => {
    if (currentRound < 2) return;
    // update only the previous round's votes
    setShuffledVotes((prev) => {
      const newVotes = [...prev];
      newVotes[currentRound - 2] = superShuffle(Object.values(missions[currentRound - 2].votes));
      return newVotes;
    });
  // we only want to update the votes when the currentRound changes,
  // since the missions array will cause the component to re-render
  // even if the votes haven't changed
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentRound]);


  return (
    <div
      className="bg-gray-900 text-white flex flex-col items-center"
    >
      <motion.div
        className="bg-gray-800 p-2 py-6 sm:p-6 rounded-lg shadow-lg w-full"
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <h2 className="text-3xl font-bold text-indigo-300 mb-6 text-center">
          {numPlayers} Players
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 sm:gap-6 justify-items-center">
          {missions.map((mission, questIndex) => {
            const result = mission.result;
            const isSuccess = result === true;
            const isFail = result === false;
            const isPending = result === null && mission.team.length > 0;

            return (
              <div
                key={questIndex}
                className="w-full"
              >
                <motion.div
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={`p-4 rounded-lg shadow-md flex flex-col items-center justify-center text-xl font-bold cursor-pointer transition-colors duration-200 ${
                    isSuccess
                      ? "bg-green-600 text-white"
                      : isFail
                      ? "bg-red-600 text-white"
                      : isPending
                      ? "bg-yellow-600 text-white"
                      : "bg-gray-600 text-white"
                  }`}
                  // Optionally, add click handlers for expanding details
                >
                  <span className="mb-1 text-2xl">
                    {mission.required_team_size}
                    {numPlayers >= 7 && mission.round_number === 4 && (
                      <span className="text-sm absolute">{" (x2)"}</span>
                    )}
                  </span>
                  
                  <span className="text-sm font-medium">
                    {isSuccess
                      ? "Success"
                      : isFail
                      ? "Fail"
                      : isPending
                      ? "In Progress"
                      : "Not Started"}
                  </span>
                </motion.div>

                {/* Mission Details Section */}
                <AnimatePresence>
                  {(isSuccess || isFail || isPending) && (
                    <motion.div
                      key="details"
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={{ duration: 0.3 }}
                      className="mt-2 bg-gray-700 bg-opacity-95 text-white text-sm p-4 rounded-md shadow-lg z-10"
                      id={`mission-details-${questIndex}`}
                      role="region"
                      aria-labelledby={`mission-${questIndex}`}
                    >
                      <div className={`${(isSuccess || isFail) ? "mb-3" : ""}`}>
                        <h3 className="font-semibold">Players on Mission:</h3>
                        {mission.team.length > 0 ? (
                          <ul className="list-disc list-inside">
                            {mission.team.map((person, index) => (
                              <li key={index}>{person.name}</li>
                            ))}
                          </ul>
                        ) : (
                          <p className="text-gray-300">No players assigned.</p>
                        )}
                      </div>
                      {(isSuccess || isFail) ?
                      <div>
                        <h3 className="font-semibold">Votes:</h3>
                        {shuffledVotes[questIndex].length > 0 ? (
                          <ul className="list-disc list-inside">
                            {shuffledVotes[questIndex].map((vote, index) => (
                              <li key={index}>{vote}</li>
                            ))}
                          </ul>
                        ) : null}
                      </div>
                      : isPending ? (
                        <p className="text-gray-300 mt-2">Votes are being collected.</p>
                      ) : null}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            );
          })}
        </div>
      </motion.div>
    </div>
  );
};

export default MissionBoard;
