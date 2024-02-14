// component for displaying the data for a player in a game

export default async function PlayerHome({
  params,
}: {
  params: { gameId: string, name: string }
}) {
  return (
    <div>
      <h1>Player: {params.name}</h1>
    </div>
  )
}
