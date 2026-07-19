import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { TeamProvider } from "./context/TeamContext";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <TeamProvider>
        <App />
      </TeamProvider>
    </BrowserRouter>
  </React.StrictMode>,
);
