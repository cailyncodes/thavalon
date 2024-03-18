"use client"
import React from 'react'
import { Game, MissionVote, createGame, createGameCode, getGame, getGameId, updateGameState, startMission, voteOnMission, stopMission } from '../../index';

interface Props {
    gameId: string;
  }

export const GameStateManager = ({gameId}: Props) => {
  const [username, setUsername] = React.useState<string>();
  const [game, setGame] = React.useState<Game>();
  const [isLoading, setIsLoading] = React.useState(false);
  const [missionVote, setMissionVote] = React.useState<MissionVote>("REVERSE");

  React.useEffect(() => {
    const name = window.localStorage.getItem("username");
    if (name) {
      setUsername(name);
    }
  }, []);

  const fetchGame = async () => {
    const game = await getGame(gameId);
    setGame(game);
    setIsLoading(false);
    // here we check if we are in the mission voting state and all players have voted
    if (game.gameState === "MISSION_VOTING" && game.missionToVotes?.[game.missionIndex]) {
      const numVoted = Object.keys(game.missionToVotes[game.missionIndex]).length;
      if (numVoted === game.missionToPeople[game.missionIndex].length) {
        stopMission(gameId, game.missionIndex);
      }
    }
  }

  const submitStartMission = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!game || !username) {
        return;
    }
    // for each player in the form, check if they are on the mission
    const missionPlayers = [];
    for (let player of game.players) {
        if (e.currentTarget[player].checked) {
            missionPlayers.push(player);
        }
    }
    
    startMission(gameId, game.missionIndex, missionPlayers);
    setIsLoading(true);
  }

  const submitStopMission = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!game || !username) {

        return;
    }
    updateGameState(gameId, "PROPOSING");
    setIsLoading(true);
  }

  const submitMissionVote = async (_: FormData) => {
    if (!game || !username) {
        return;
    }

    if (window.confirm(`Are you sure you want to vote ${missionVote}?\n\nYou cannot change your vote after submitting. Cancel to close.`)) {
        voteOnMission(gameId, game.missionIndex, username, missionVote);
        setIsLoading(true);
      }
  }

  React.useEffect(() => {
    const interval = setInterval(fetchGame, 3000);
    return () => clearInterval(interval);
  }
    , [fetchGame]);

  if (!game || !username || isLoading) {
    return <div className="w-full flex flex-col items-center justify-between">
    <p className='text-md font-bold'>Loading...</p>
  </div>;
  }

  const isOnMission = game.missionToPeople[game.missionIndex]?.includes(username) ?? false;
  const hasVoted = game.missionToVotes[game.missionIndex] && game.missionToVotes[game.missionIndex][username];

  
  return (<>
  <div className="w-full flex flex-col items-center justify-between">
     <p className='text-md font-bold'>Mission: {game.missionIndex}</p>
   </div>
   <div className="w-full flex flex-col items-center justify-between">
   <p className='text-md font-bold'>{game.gameState}</p>
    {game.gameState === "PROPOSING" ? <>
    {game.missionIndex > 1 && (
            <div>
                Previous mission votes: 
                {Object.values(game.missionToVotes[game.missionIndex - 1]).map((vote, index) => {
            return <div key={index}>{vote}</div>
        })}
            </div>)}
    { game.host === username ?
     (<>
        <form className="w-full max-w-lg flex justify-center items-center m-2" onSubmit={submitStartMission}>
            {game.players.map((player, index) => {
                // radio button for each player
                return <div key={index}>
                    <input type="checkbox" id={player} name={player} value="yes" />
                    <label htmlFor={player}>{player}</label>
                </div>
            })
            }
            <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" type="submit">
                Start Mission
            </button>
        </form>
     </>) : <div>Waiting for host to start mission</div>
         } </> :
     game.gameState === "MISSION_VOTING" ?
    <>
        <div>On the mission: {game.missionToPeople[game.missionIndex].join(", ")}</div>
        {isOnMission && hasVoted ? (
            <div>Your vote: {game.missionToVotes[game.missionIndex][username]}</div> 
        ) : isOnMission ? (<>
        <form className="w-full max-w-lg flex justify-center items-center m-2" action={submitMissionVote}>
            <select className="border-2 border-gray-300 p-2 rounded m-2 text-gray-700 bg-white w-2/5" name="mission-vote" value={missionVote} onChange={e => setMissionVote(e.target.value as MissionVote)}>
                <option value="FAIL">Fail</option>
                <option value="REVERSE">Reverse</option>
                <option value="SUCCESS">Success</option>
            </select>
            <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" type="submit">
                Vote
            </button>
        </form>
    </>) : <div>Waiting for mission to complete</div>}
        <form className="w-full max-w-lg flex justify-center items-center m-2" onSubmit={submitStopMission}>
            <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" type="submit">
                Stop Mission
            </button>
        </form>
      </>
     : <div>Invalid Game State</div>}
     </div>
    </>
  )
}