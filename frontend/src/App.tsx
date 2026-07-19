import { Navigate, Route, Routes } from "react-router-dom";
import { useTeam } from "./context/TeamContext";
import Dashboard from "./pages/Dashboard";
import InspectSquad from "./pages/InspectSquad";
import Login from "./pages/Login";
import News from "./pages/News";
import Tactics from "./pages/Tactics";

export default function App() {
  const { activeTeam } = useTeam();
  const fallback = activeTeam ? "/dashboard" : "/login";

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/inspect" element={<InspectSquad />} />
      <Route path="/tactics" element={<Tactics />} />
      <Route path="/news" element={<News />} />
      <Route path="/" element={<Navigate to={fallback} replace />} />
      <Route path="*" element={<Navigate to={fallback} replace />} />
    </Routes>
  );
}
