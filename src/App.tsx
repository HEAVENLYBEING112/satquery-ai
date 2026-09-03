// frontend/src/App.tsx
import React from 'react';
import { HashRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { LandingPage } from './pages/LandingPage';
import { DashboardPage } from './pages/DashboardPage';
import { WorkspacePage } from './pages/WorkspacePage';
import { SingleImagePage } from './pages/SingleImagePage';
import { ChangeDetectionPage } from './pages/ChangeDetectionPage';
import { OpticalSarPage } from './pages/OpticalSarPage';
import { AgentMonitorPage } from './pages/AgentMonitorPage';
import { HistoryPage } from './pages/HistoryPage';
import { ReportsPage } from './pages/ReportsPage';
import { SettingsPage } from './pages/SettingsPage';

export function App() {
  return (
    <HashRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<LandingPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/workspace" element={<WorkspacePage />} />
          <Route path="/single-image" element={<SingleImagePage />} />
          <Route path="/change-detection" element={<ChangeDetectionPage />} />
          <Route path="/optical-sar" element={<OpticalSarPage />} />
          <Route path="/agent-monitor" element={<AgentMonitorPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </HashRouter>
  );
}

export default App;
