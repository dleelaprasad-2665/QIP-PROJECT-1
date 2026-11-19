import React, { useState } from 'react';
import { AuthProvider } from './context/AuthContext';
import { Sidebar, NavigationTab } from './components/layout/Sidebar';
import { Navbar } from './components/layout/Navbar';
import { DashboardPage } from './pages/DashboardPage';
import { MaterialInspectionPage } from './pages/MaterialInspectionPage';
import { DefectDetectionPage } from './pages/DefectDetectionPage';
import { MaterialInventoryPage } from './pages/MaterialInventoryPage';
import { InspectionHistoryPage } from './pages/InspectionHistoryPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { ReportsPage } from './pages/ReportsPage';
import { ModelEvaluationPage } from './pages/ModelEvaluationPage';
import { SettingsPage } from './pages/SettingsPage';
import { AuthModal } from './components/auth/AuthModal';

const AppContent: React.FC = () => {
  const [activeTab, setActiveTab] = useState<NavigationTab>('dashboard');
  const [currentSite, setCurrentSite] = useState<string>('All');
  const [isAuthOpen, setIsAuthOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-slate-50 text-gray-900 font-sans antialiased selection:bg-blue-600 selection:text-white">
      {/* Sidebar Navigation */}
      <Sidebar activeTab={activeTab} onSelectTab={setActiveTab} />

      {/* Main Workspace */}
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar
          currentSite={currentSite}
          onSiteChange={setCurrentSite}
          onOpenAuth={() => setIsAuthOpen(true)}
        />

        <main className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto overflow-y-auto">
          {activeTab === 'dashboard' && (
            <DashboardPage
              onNavigate={(tab) => setActiveTab(tab)}
            />
          )}

          {activeTab === 'inspection' && (
            <MaterialInspectionPage
              onSavedToInventory={() => setActiveTab('inventory')}
            />
          )}

          {activeTab === 'defect-detection' && (
            <DefectDetectionPage
              onNavigateToInspection={() => setActiveTab('inspection')}
            />
          )}

          {activeTab === 'inventory' && (
            <MaterialInventoryPage
              onStartNewInspection={() => setActiveTab('inspection')}
            />
          )}

          {activeTab === 'history' && (
            <InspectionHistoryPage
              onNavigateToInspection={() => setActiveTab('inspection')}
            />
          )}

          {activeTab === 'analytics' && (
            <AnalyticsPage
              onNavigateToInspection={() => setActiveTab('inspection')}
            />
          )}

          {activeTab === 'reports' && (
            <ReportsPage
              onNavigateToInspection={() => setActiveTab('inspection')}
            />
          )}

          {activeTab === 'evaluation' && (
            <ModelEvaluationPage />
          )}

          {activeTab === 'settings' && (
            <SettingsPage />
          )}
        </main>
      </div>

      {/* Auth Modal */}
      <AuthModal isOpen={isAuthOpen} onClose={() => setIsAuthOpen(false)} />
    </div>
  );
};

export function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
