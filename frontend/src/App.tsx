import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import SystemHealth from "./pages/SystemHealth";
import Passport from "./pages/Passport";
import Compare from "./pages/Compare";
import ExportPage from "./pages/ExportPage";
import Settings from "./pages/Settings";
import FirstRun from "./pages/FirstRun";
import Capture from "./pages/Capture";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/capture" element={<Capture />} />
        <Route path="/welcome" element={<FirstRun />} />
        <Route path="/passport" element={<Passport />} />
        <Route path="/compare" element={<Compare />} />
        <Route path="/export" element={<ExportPage />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/system" element={<SystemHealth />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}
