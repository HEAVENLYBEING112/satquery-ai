// frontend/src/components/layout/AppLayout.tsx
import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { AppHeader } from './AppHeader';
import { AppSidebar } from './AppSidebar';
import { TracePanel } from '../trace/TracePanel';

export const AppLayout: React.FC = () => {
  const location = useLocation();
  const isLandingPage = location.pathname === '/';

  if (isLandingPage) {
    return (
      <div className="min-h-screen bg-[#050811] text-slate-100 flex flex-col selection:bg-cyan-500 selection:text-slate-950">
        <AppHeader />
        <main className="flex-1">
          <Outlet />
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050811] text-slate-100 flex flex-col selection:bg-cyan-500 selection:text-slate-950 overflow-x-hidden">
      <AppHeader />
      <div className="flex-1 flex overflow-hidden">
        <AppSidebar />
        <div className="flex-1 flex flex-col min-w-0">
          <main className="flex-1 flex flex-col overflow-y-auto bg-slate-950/40 relative">
            <div className="flex-1 p-4 sm:p-6 max-w-[1700px] w-full mx-auto">
              <Outlet />
            </div>
          </main>
          {/* Global Collapsible Execution Trace Drawer */}
          <div className="relative z-40">
            <TracePanel />
          </div>
        </div>
      </div>
    </div>
  );
};
