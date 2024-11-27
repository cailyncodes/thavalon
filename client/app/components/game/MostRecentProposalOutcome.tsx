import React from "react";
import { Person, Proposal } from "../../types";

interface ProposalVotingProps {
  missionNumber: number; // Current mission number
  proposals: Proposal[]; // List of proposals made so far
}

const MostRecentProposalOutcome: React.FC<ProposalVotingProps> = ({
  missionNumber,
  proposals,
}) => {
  const isFirstProposal = missionNumber === 1;
  const firstRoundProposals = proposals.filter((proposal) => proposal.round_number === 1);
  const mostRecentProposal = proposals[proposals.length - 1];
  const voteOutcome = (() => {
    if (isFirstProposal) {
      if (firstRoundProposals[0].passed === true) {
        return "Option 1"
      }
      if (firstRoundProposals[1].passed === true) {
        return "Option 2"
      }
    } else {
      return mostRecentProposal.passed === true ? "Passed" : "Failed"
    }

    return null;
  })()

  return (
    <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold text-indigo-300 mb-4">Last Proposal</h2>

      {isFirstProposal && firstRoundProposals ? (
        <>
          {firstRoundProposals.map((proposal, index) => {
            const key = `proposal-${index}`;
            const value = proposal.team;
            return (
              <div key={key} className="mb-6">
                <p className="text-lg font-bold text-gray-200 mb-2">
                  {`Option ${index + 1} (${proposal.passed ? "Approved" : "Rejected"})`}
                </p>
                <p className="text-gray-300 mb-2">
                  Proposed by: {proposal.proposer.name}
                </p>
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
        </>
      ) : (
        mostRecentProposal && (
          <>
              <div className="mb-6">
                <p className="text-lg font-bold text-gray-200 mb-2">
                  Proposed by: {mostRecentProposal.proposer.name}
                </p>
                <ul className="list-disc list-inside text-gray-300">
                  {mostRecentProposal.team.map((person) => (
                    <li key={person.name} className="font-bold text-indigo-400">
                      {person.name}
                    </li>
                  ))}
                </ul>
              </div>
          </>
        )
      )}

      {voteOutcome && (
        <div className="mt-6 p-4 bg-indigo-700 text-white rounded-lg">
        <h3 className="text-xl font-bold">Votes</h3>
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

export default MostRecentProposalOutcome;
