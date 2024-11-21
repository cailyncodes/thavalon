import React from "react";
import Lobby from "./Lobby";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-stretch bg-gray-900 text-gray-200">
      <Lobby />
    </main>
  );
}
