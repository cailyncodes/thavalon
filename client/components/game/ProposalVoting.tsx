import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Person, Proposal, ProposalVote } from "../../types";

interface ProposalVotingProps {
  person: Person;
  missionNumber: number; // Current mission number
  proposalNumber: number;
  proposals: Proposal[]; // List of proposals made so far
  totalPlayers: number; // Total number of players eligible to vote
  submitVote: (vote: string) => void; // Function to submit a player's vote
}

const ProposalVoting: React.FC<ProposalVotingProps> = ({
  person,
  missionNumber,
  proposalNumber,
  proposals,
  totalPlayers,
  submitVote,
}) => {
  const isFirstProposal = missionNumber === 1;
  const firstRoundProposals = proposals.filter((proposal) => proposal.round_number === 1);
  const mostRecentProposal = proposals[proposals.length - 1];
  const votesForFirstRound = firstRoundProposals[0]?.votes;
  const votesForMostRecent = mostRecentProposal?.votes;
  const votesForThisRound = isFirstProposal ? votesForFirstRound : votesForMostRecent;
  const vote = votesForThisRound && votesForThisRound[person.name];
  const [selectedVote, setSelectedVote] = useState<ProposalVote | null>(vote);

  const handleVote = (vote: ProposalVote) => {
    setSelectedVote(vote);
    submitVote(vote);
  };

  const voteOutcome = (() => {
    if (votesForThisRound && Object.keys(votesForThisRound).length === totalPlayers) {
      let option1Votes = 0;
      let option2Votes = 0;
      let yesVotes = 0;
      let noVotes = 0;

      Object.values(votesForThisRound).forEach((vote) => {
        if (isFirstProposal) {
          if (vote === "Option 1") {
            option1Votes += 1;
          } else {
            option2Votes += 1;
          }
        } else {
          if (vote === "Yes") {
            yesVotes += 1;
          } else {
            noVotes += 1;
          }
        }
      });

      if (isFirstProposal) {
        return option1Votes > option2Votes
            ? "Option 1 Approved"
            : "Option 2 Approved"
      } else {
        return yesVotes > noVotes
            ? "Proposal Accepted"
            : "Proposal Rejected"
      }
    }
  })();

  return (
    <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold text-indigo-300 mb-4">Proposal Voting</h2>

      {isFirstProposal && firstRoundProposals ? (
        <>
          {firstRoundProposals.map((proposal, index) => {
            const key = `proposal-${index}`;
            const value = proposal.team;
            return (
              <div key={key} className="mb-6">
                <h3 className="text-lg font-bold text-gray-200 mb-2">
                  Proposal {index + 1} {`(by ${proposal.proposer.name})`}:
                </h3>
                <ul className="list-disc list-inside text-gray-300">
                  {value.map((person) => (
                    <li key={person.name} className="font-bold text-indigo-400">
                      {person.name}
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
          <div className="flex flex-wrap gap-4 mt-4">
            <div className="flex items-center space-x-2">
              <motion.button
                whileHover={{
                  scale: selectedVote ? 1 : 1.05,
                }}
                whileTap={{
                  scale: selectedVote ? 1 :0.95,
                }}
                onClick={() => handleVote("Option 1")}
                className={`px-4 py-2 rounded-lg font-bold text-white ${
                  selectedVote === "Option 1"
                    ? "bg-green-500"
                    : "bg-gray-600"
                } ${!selectedVote ? "hover:bg-green-400" : ""}`}
                disabled={!!selectedVote}
              >
                Option 1
              </motion.button>
              <motion.button
                whileHover={{
                  scale: selectedVote ? 1 : 1.05,
                }}
                whileTap={{
                  scale: selectedVote ? 1 :0.95,
                }}
                onClick={() => handleVote("Option 2")}
                className={`px-4 py-2 rounded-lg font-bold text-white ${
                  selectedVote === "Option 2"
                    ? "bg-green-500"
                    : "bg-gray-600"
                } ${!selectedVote ? "hover:bg-green-400" : ""}`}
                disabled={!!selectedVote}
              >
                Option 2
              </motion.button>
            </div>
          </div>
        </>
      ) : (
        mostRecentProposal && (
          <>
              <div className="mb-6">
                <h3 className="text-lg font-bold text-gray-200 mb-2">
                  Proposal {proposalNumber} {`(by ${mostRecentProposal.proposer.name})`}:
                </h3>
                <ul className="list-disc list-inside text-gray-300">
                  {mostRecentProposal.team.map((person) => (
                    <li key={person.name} className="font-bold text-indigo-400">
                      {person.name}
                    </li>
                  ))}
                </ul>
                <div className="flex flex-wrap gap-4 mt-4">
                  <div className="flex items-center space-x-2">
                    <motion.button
                      whileHover={{
                        scale: selectedVote ? 1 : 1.05,
                      }}
                      whileTap={{
                        scale: selectedVote ? 1 :0.95,
                      }}
                      onClick={() => handleVote("Yes")}
                      className={`px-4 py-2 rounded-lg font-bold text-white ${
                        selectedVote === "Yes"
                          ? "bg-green-500"
                          : "bg-gray-600"
                      } ${!selectedVote ? "hover:bg-green-400" : ""}`}
                      disabled={!!selectedVote}
                    >
                      Yes
                    </motion.button>
                    <motion.button
                      whileHover={{
                        scale: selectedVote ? 1 : 1.05,
                      }}
                      whileTap={{
                        scale: selectedVote ? 1 :0.95,
                      }}
                      onClick={() => handleVote("No")}
                      className={`px-4 py-2 rounded-lg font-bold text-white ${
                        selectedVote === "No"
                          ? "bg-red-500"
                          : "bg-gray-600"
                      } ${!selectedVote ? "hover:bg-red-400" : ""}`}
                      disabled={!!selectedVote}
                    >
                      No
                      </motion.button>
                  </div>
                </div>
              </div>
          </>
        )
      )}

      {voteOutcome && (
        <div className="mt-6 p-4 bg-indigo-700 text-white rounded-lg">
          <h3 className="text-xl font-bold">Outcome: {voteOutcome}</h3>
          <ul className="list-disc list-inside text-gray-300">
            {Object.entries(mostRecentProposal.votes).map(([person, vote]) => (
              <li key={person} className="font-bold text-gray-100">
                {person} cast a {vote} vote
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ProposalVoting;
