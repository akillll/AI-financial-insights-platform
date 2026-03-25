import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import UploadPage from "./pages/UploadPage";
import HouseholdsPage from "./pages/HouseholdsPage";
import InsightsPage from "./pages/InsightsPage";
import HouseholdDetailsPage from "./pages/HouseholdDetailsPage";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/households" element={<HouseholdsPage />} />
        <Route path="/household/:id" element={<HouseholdDetailsPage />} />
        <Route path="/insights/:id" element={<InsightsPage />} />
      </Routes>
    </Router>
  );
}