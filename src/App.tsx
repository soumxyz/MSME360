import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { MotionConfig } from 'framer-motion';

// Layouts
import CustomerLayout from './layouts/CustomerLayout';
import OfficerLayout from './layouts/OfficerLayout';

// Customer Pages
import LandingPage from './pages/LandingPage';
import Login from './pages/Login';
import BusinessRegistration from './pages/BusinessRegistration';
import CustomerDashboard from './pages/CustomerDashboard';
import BusinessInsights from './pages/BusinessInsights';
import LoanRecommendations from './pages/LoanRecommendations';
import Applications from './pages/Applications';
import ApplicationDetails from './pages/ApplicationDetails';
import ReportView from './pages/ReportView';

// Officer Pages
import OfficerDashboard from './pages/OfficerDashboard';
import OfficerApplications from './pages/OfficerApplications';
import UnderwritingDetails from './pages/UnderwritingDetails';
import BusinessDirectory from './pages/BusinessDirectory';
import RiskQueue from './pages/RiskQueue';
import HealthCards from './pages/HealthCards';
import OfficerReports from './pages/OfficerReports';
import Settings from './pages/Settings';

function App() {
  return (
    <MotionConfig reducedMotion="user">
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<BusinessRegistration />} />

        {/* Customer Routes (MSME view) */}
        <Route path="/customer" element={<CustomerLayout />}>
          <Route index element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<CustomerDashboard />} />
          <Route path="insights" element={<BusinessInsights />} />
          <Route path="loans" element={<LoanRecommendations />} />
          <Route path="applications" element={<Applications />} />
          <Route path="applications/:id" element={<ApplicationDetails />} />
          <Route path="reports" element={<ReportView />} />
          <Route path="settings" element={<Settings />} />
        </Route>

        {/* Officer Routes (Bank Back-Office view) */}
        <Route path="/officer" element={<OfficerLayout />}>
          <Route index element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<OfficerDashboard />} />
          <Route path="applications" element={<OfficerApplications />} />
          <Route path="applications/:id" element={<UnderwritingDetails />} />
          <Route path="businesses" element={<BusinessDirectory />} />
          <Route path="risk-queue" element={<RiskQueue />} />
          <Route path="health-cards" element={<HealthCards />} />
          <Route path="reports" element={<OfficerReports />} />
          <Route path="settings" element={<Settings />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
    </MotionConfig>
  );
}

export default App;
