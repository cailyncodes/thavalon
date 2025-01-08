// src/types.ts

export interface Role {
  name: string; // Name of the role
  description: string; // Description of the role
  information: string[]; // Array of additional information
}

export interface Person {
  name: string; // Name of the person
}

export interface Player {
  person: Person;
  role: Role;
}

export type ProposalVote = "Yes" | "No";

export type MissionVote = "Success" | "Fail" | "Reverse" | "Cancel";

export interface Proposal {
  proposal_number: number; // Proposal number
  round_number: number; // Proposal round number
  proposer: Person; // Player who made the proposal
  team: Person[]; // Team members proposed for the mission
  votes: Record<string, ProposalVote>; // Object of votes cast for this proposal
  passed: boolean | null; // Proposal result after finalization
}

export interface Mission {
  round_number: number; // Mission round number
  required_team_size: number; // Number of players required for the mission
  team: Person[]; // Assigned team members for the mission
  votes: Record<string, MissionVote>; // Object of cards played for this mission
  result: boolean | null; // Mission result after finalization
}

export interface Game {
  id: string; // Unique game identifier
  name: string; // Name of the game
  persons: Person[]; // Array of persons in the game
  players: Player[]; // Array of players in the game
  starting_person: Person; // Starting person for the game
  num_players: number; // Total number of players
  max_proposals: number; // Maximum number of proposals allowed
  mission_sizes: number[]; // Sizes of teams for the missions
  proposal_round: number; // Current proposal round
  mission_number: number; // Current mission number
  proposals: Proposal[]; // Array of proposals
  missions: Mission[]; // Array of missions
  status: "open" | "in-progress" | "closed"; // Status of the game
  variant: string; // Variant of the game (e.g., "thavalon")
}
