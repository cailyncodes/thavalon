import React from "react";
import Lobby from "./Lobby";

const Home = () => {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex mb-12">
        <div className="w-full flex flex-col items-center justify-between">
          <h1 className="text-4xl font-bold">THAvalon for Name</h1>
        </div>
      </div>
      <div className="w-full flex flex-col items-center justify-between">
        <Lobby />
      </div>
    </main>
  );
}

export default Home