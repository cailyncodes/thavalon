"use client";

import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { toast, ToastContainer } from "react-toastify";
import QuestBoard from "../../../../components/game/Board";
import NoGameData from "../../../../components/game/Empty";
import GameHeader from "../../../../components/game/Header";
import LoadingState from "../../../../components/game/Loading";
import PlayerDetails from "../../../../components/game/PlayerDetail";
import VotingSection from "../../../../components/game/Voting";
import { Game, MissionVote, Person, Player } from "../../../types";
import DangerZone from "../../../../components/game/DangerZone";
import PlayerList from "../../../../components/game/PlayerList";
import MissionProposalManager from "../../../../components/game/MissionProposal";
import StartingPlayer from "../../../../components/game/StartingPlayer";
import ProposalVoting from "../../../../components/game/ProposalVoting";

import "react-toastify/dist/ReactToastify.css";
import MostRecentProposalOutcome from "../../../../components/game/MostRecentProposalOutcome";

interface GameViewPageProps {
  url: string;
}

const GameViewPage = ({ url }: GameViewPageProps) => {
  const pathname = usePathname();
  const gameId = pathname.split("/")[2];

  const [username, setUsername] = useState<string>("");
  const [gameData, setGameData] = useState<Game | null>(null);
  const [currentPlayer, setCurrentPlayer] = useState<Player | null>(null);
  const [persons, setPersons] = useState<Person[]>([]);
  const [loading, setLoading] = useState(true);
  const [showOwnRole, setShowOwnRole] = useState(false);
  const [selectedVote, setSelectedVote] = useState<MissionVote | null>(null);

  const isGameOver = ((gameData?.mission_number ?? 0) > 5 && gameData?.missions[4].result !== null) || gameData?.status === "closed";
  const roundProposals = gameData?.proposals.filter((p) => p.round_number === gameData.mission_number && (gameData.mission_number > 1 ? p.proposal_number === gameData.proposal_round : true)) ?? [];
  const isCurrentProposalPending = (gameData && (gameData.mission_number === 1 ? roundProposals.length === 2 : roundProposals.length > 0) && roundProposals[roundProposals.length - 1].passed === null) ?? false;
  const currentMission = gameData ? gameData.missions[gameData.mission_number - 1] : null;
  const isOnMission = currentMission?.team.some((p) => p.name === username) ?? false;
  const isCurrentMissionPending = (roundProposals.length > 0 && currentMission?.result === null && currentMission?.team.length > 0) ?? false

  const fetchGameData = async () => {
    try {
      const response = await fetch(`${url}/api/game/${gameId}`);
      if (response.ok) {
        const data: Game = await response.json();
        setGameData(data);
        return data;
      } else {
        console.error("Failed to fetch game data.");
      }
    } catch (error) {
      console.error("Error fetching game data:", error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch game data on initial load
  useEffect(() => {
    const storedUsername = localStorage.getItem("username") || "";
    setUsername(storedUsername);
    (async () => {
      const data = await fetchGameData();
      if (data) {
        setPersons(data.persons);
      }
    })();
  }, [gameId, url]);

  useEffect(() => {
    const interval = setInterval(() => {
      fetchGameData();
    }, 1500);

    return () => clearInterval(interval); // Cleanup on unmount
  }, [gameId, username]);

  useEffect(() => {
    if (!gameData) return;
    const player = gameData.players.find(
      (p) => p.person.name === username
    );
    setCurrentPlayer(player || null);
  }, [gameData, username]);

  const submitProposal = async (selectedPersons: Person[]) => {
    try {
      const response = await fetch(`${url}/api/game/${gameId}/proposal`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          proposer: username,
          team: selectedPersons,
        }),
      });

      if (response.ok) {
        toast.success("Proposal submitted successfully!");
      } else {
        const errorData = await response.json();
        toast.error(errorData.message || "Failed to submit proposal.");
      }
    } catch (error) {
      console.error("Error submitting proposal:", error);
      toast.error("An error occurred while submitting your proposal.");
    }
  }

  const submitProposalVote = async (vote: string) => {
    try {
      const response = await fetch(`${url}/api/game/${gameId}/proposal/vote`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          voter: username,
          option: vote,
        }),
      });

      if (response.ok) {
        toast.success("Vote submitted successfully!");
      } else {
        const errorData = await response.json();
        toast.error(errorData.message || "Failed to submit vote.");
      }
    } catch (error) {
      console.error("Error submitting vote:", error);
      toast.error("An error occurred while submitting your vote.");
    }
  }

  const submitVote = async (vote: MissionVote) => {
    if (!vote) {
      toast.error("Please select a vote before submitting.");
      return;
    }

    try {
      const response = await fetch(`${url}/api/game/${gameId}/mission/vote`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          voter: username,
          vote: vote,
        }),
      });

      if (response.ok) {
        toast.success("Vote submitted successfully!");
      } else {
        const errorData = await response.json();
        toast.error(errorData.message || "Failed to submit vote.");
      }
    } catch (error) {
      console.error("Error submitting vote:", error);
      toast.error("An error occurred while submitting your vote.");
    }
  };

  const closeGame = async () => {
    try {
      const response = await fetch(`${url}/api/game/${gameId}/close`, {
        method: "POST",
      });
      if (response.ok) {
        toast.success("Game closed successfully!");
      } else {
        toast.error("Failed to close game.");
      }
    } catch (error) {
      console.error("Error closing game:", error);
    }
  };

  if (loading) return <LoadingState />;
  if (!gameData) return <NoGameData />;

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6 flex flex-col gap-10">
      <ToastContainer />
      <GameHeader game={gameData} />
      <StartingPlayer person={gameData.starting_person} />
      <QuestBoard missions={gameData.missions} currentRound={gameData.mission_number} numPlayers={gameData.num_players} />
      {currentPlayer && currentMission && isOnMission ? (
        <VotingSection
          currentMission={currentMission}
          person={currentPlayer.person}
          roundNumber={gameData.mission_number}
          submitVote={submitVote}
        />
      ): null}
      {isCurrentMissionPending || (gameData.mission_number > 1 && gameData.proposal_round > 1 && roundProposals.length > 0 && Object.entries(roundProposals[roundProposals.length - 1].votes).length === gameData.num_players)? 
        <MostRecentProposalOutcome
          missionNumber={gameData.mission_number}
          proposals={gameData.proposals}
        />
      : null}
      {currentPlayer && (isCurrentProposalPending || (!isCurrentProposalPending && gameData.proposal_round === 1 && !isCurrentMissionPending && roundProposals.length > 0)) ?
      // currentPlayer?.person && gameData.proposals.filter((p) => p.round_number == gameData.mission_number).length > 0 && currentMission?.team && currentMission.team.length === 0 ? (
      (
        <ProposalVoting
          person={currentPlayer?.person}
          missionNumber={gameData.mission_number}
          proposalNumber={gameData.proposal_round}
          proposals={gameData.proposals}
          totalPlayers={gameData.players.length}
          submitVote={submitProposalVote}
        />
      ) : null}
      {currentPlayer && !isGameOver && !isCurrentProposalPending && !isCurrentMissionPending ?
      // (roundProposals.length === 0 || (roundProposals[roundProposals.length - 1].passed !== null && currentMission && currentMission.result !== null)) ?
        <MissionProposalManager
          persons={persons}
          missionNumber={gameData.mission_number}
          proposalCount={gameData.proposal_round}
          requiredSize={gameData.missions[gameData.mission_number - 1].required_team_size}
          submitProposal={submitProposal}
        />
        : null}
      {currentPlayer && (
        <PlayerDetails
          currentPlayer={currentPlayer}
          showOwnRole={showOwnRole}
          toggleShowOwnRole={() => setShowOwnRole(!showOwnRole)}
        />
      )}
      <PlayerList currentPlayer={currentPlayer} players={gameData.players} />
      <DangerZone game={gameData} closeGame={closeGame} />
    </div>
  );
};

export default GameViewPage;
