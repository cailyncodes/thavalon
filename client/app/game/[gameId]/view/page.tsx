import React from "react";
import Game from "./Game";
import { getUrl } from "../../../url";

export default function GameViewPage() {
  return <Game url={getUrl(process.env.RAILWAY_ENVIRONMENT_NAME, "http")} />;
}
