import React, { useState } from "react";
import { Person } from "../../types";

const HAMMER_COUNTS = {
  5: 3,
  6: 3,
  7: 4,
  8: 4,
  9: 4,
  10: 5
}

interface MissionProposalManagerProps {
  persons: Person[];
  missionNumber: number;
  proposalCount: number;
  requiredSize: number;
  submitProposal: (selectedPersons: Person[]) => void;
}

const MissionProposalManager: React.FC<MissionProposalManagerProps> = ({
  persons,
  missionNumber,
  proposalCount,
  requiredSize,
  submitProposal,
}) => {
  const [selectedPersons, setSelectedPersons] = useState<Person[]>([]);

  const togglePlayerSelection = (person: Person) => {
    if (selectedPersons.includes(person)) {
      setSelectedPersons(selectedPersons.filter((p) => p.name !== person.name));
    } else {
      setSelectedPersons([...selectedPersons, person]);
    }
  };

  const handleSubmitProposal = () => {
    if (selectedPersons.length === 0) {
      alert("Select at least one person to propose for the mission.");
      return;
    }

    submitProposal(selectedPersons);
    setSelectedPersons([]);
  };

  return (
    <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold text-indigo-300 mb-4">Mission Proposal {`(Round ${missionNumber})`}</h2>

      <p className="text-gray-300 mb-2">
        {missionNumber > 1 ?
        `Proposal: ${proposalCount} / ${HAMMER_COUNTS[persons.length as keyof typeof HAMMER_COUNTS]}`
        : null
        }
      </p>

      <div className="mb-6">
        <h3 className="text-lg font-bold text-gray-200 mb-2">Select players {`(${requiredSize})`} for the mission:</h3>
        <div className="flex flex-wrap gap-2">
          {persons.map((person) => (
            <button
              key={person.name}
              onClick={() => togglePlayerSelection(person)}
              className={`px-4 py-2 rounded-lg font-bold text-white ${
                selectedPersons.includes(person) ? "bg-green-500" : "bg-gray-600"
              }`}
            >
              {person.name}
            </button>
          ))}
        </div>
      </div>

      <button
        onClick={handleSubmitProposal}
        className="bg-blue-500 hover:bg-blue-400 text-white font-bold py-2 px-4 rounded-lg shadow-md"
      >
        Submit Proposal
      </button>
    </div>
  );
};

export default MissionProposalManager;
