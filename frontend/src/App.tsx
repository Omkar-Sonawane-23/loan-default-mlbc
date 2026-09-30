import { Routes, Route } from "react-router-dom";
import DashboardLayout from "./components/layout/DashboardLayout";
import Dashboard from "./pages/Dashboard";
import Predict from "./pages/Predict";
import Applications from "./pages/Applications";
import ApplicationDetails from "./pages/ApplicationDetails";
import Analytics from "./pages/Analytics";
import ModelAnalytics from "./pages/ModelAnalytics";
import ModelMonitoring from "./pages/ModelMonitoring";
import Loans from "./pages/Loans";
import Blockchain from "./pages/Blockchain";
import Verify from "./pages/Verify";
import Settings from "./pages/Settings";
import NotFound from "./pages/NotFound";

export default function App() {
  return (
    <Routes>
      <Route element={<DashboardLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/predict" element={<Predict />} />
        <Route path="/applications" element={<Applications />} />
        <Route path="/applications/:id" element={<ApplicationDetails />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/model" element={<ModelAnalytics />} />
        <Route path="/model-monitoring" element={<ModelMonitoring />} />
        <Route path="/loans" element={<Loans />} />
        <Route path="/blockchain" element={<Blockchain />} />
        <Route path="/verify" element={<Verify />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}
