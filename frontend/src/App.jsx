// // frontend/src/App.jsx

// import React, { useState, useEffect } from 'react';
// import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
// import { Toaster } from 'react-hot-toast';
// import { 
//   Users, 
//   Calendar, 
//   Settings, 
//   BarChart3, 
//   Brain, 
//   Menu, 
//   X,
//   Home
// } from 'lucide-react';

// // Import components
// import Dashboard from './components/Dashboard';
// import StaffList from './components/StaffList';
// import ShiftCalendar from './components/ShiftCalendar';
// import AllocationView from './components/AllocationView';
// import LoadingSpinner from './components/LoadingSpinner';

// // Import API
// import { systemAPI } from './services/api';

// function App() {
//   const [currentView, setCurrentView] = useState('dashboard');
//   const [isSidebarOpen, setIsSidebarOpen] = useState(true);
//   const [isLoading, setIsLoading] = useState(true);
//   const [systemHealth, setSystemHealth] = useState(null);

//   // Navigation items
//   const navigationItems = [
//     { id: 'dashboard', label: 'Dashboard', icon: Home, component: Dashboard },
//     { id: 'staff', label: 'Staff Management', icon: Users, component: StaffList },
//     { id: 'shifts', label: 'Shift Calendar', icon: Calendar, component: ShiftCalendar },
//     { id: 'allocations', label: 'AI Allocation', icon: Brain, component: AllocationView },
//     { id: 'analytics', label: 'Analytics', icon: BarChart3, component: Dashboard }, // Reuse Dashboard for now
//   ];

//   // Check system health on app load
//   useEffect(() => {
//     const checkSystemHealth = async () => {
//       try {
//         const response = await systemAPI.healthCheck();
//         setSystemHealth(response.data);
//       } catch (error) {
//         console.error('System health check failed:', error);
//         setSystemHealth({ status: 'unhealthy', error: error.message });
//       } finally {
//         setIsLoading(false);
//       }
//     };

//     checkSystemHealth();
//   }, []);

//   // Get current component
//   const getCurrentComponent = () => {
//     const navItem = navigationItems.find(item => item.id === currentView);
//     return navItem ? navItem.component : Dashboard;
//   };

//   // Render loading state
//   if (isLoading) {
//     return (
//       <div className="min-h-screen bg-gray-50 flex items-center justify-center">
//         <div className="text-center">
//           <LoadingSpinner size="large" />
//           <p className="mt-4 text-gray-600">Loading Hospital Staff Allocation AI...</p>
//         </div>
//       </div>
//     );
//   }

//   // Render system health error
//   if (systemHealth?.status === 'unhealthy') {
//     return (
//       <div className="min-h-screen bg-red-50 flex items-center justify-center">
//         <div className="text-center p-8 bg-white rounded-lg shadow-lg max-w-md">
//           <div className="text-red-500 text-6xl mb-4">⚠️</div>
//           <h1 className="text-2xl font-bold text-red-800 mb-2">System Error</h1>
//           <p className="text-red-600 mb-4">
//             Unable to connect to the backend server. Please ensure the API is running.
//           </p>
//           <button 
//             onClick={() => window.location.reload()}
//             className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors"
//           >
//             Retry Connection
//           </button>
//         </div>
//       </div>
//     );
//   }

//   const CurrentComponent = getCurrentComponent();

//   return (
//     <div className="min-h-screen bg-gray-50">
//       {/* Toast notifications */}
//       <Toaster 
//         position="top-right"
//         toastOptions={{
//           duration: 4000,
//           style: {
//             background: '#363636',
//             color: '#fff',
//           },
//         }}
//       />

//       {/* Header */}
//       <header className="bg-white shadow-sm border-b border-gray-200">
//         <div className="flex items-center justify-between px-6 py-4">
//           <div className="flex items-center space-x-4">
//             <button
//               onClick={() => setIsSidebarOpen(!isSidebarOpen)}
//               className="text-gray-500 hover:text-gray-700 transition-colors"
//             >
//               {isSidebarOpen ? <X size={24} /> : <Menu size={24} />}
//             </button>
//             <div className="flex items-center space-x-3">
//               <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
//                 <Brain className="w-5 h-5 text-white" />
//               </div>
//               <div>
//                 <h1 className="text-xl font-bold text-gray-900">
//                   Hospital Staff Allocation AI
//                 </h1>
//                 <p className="text-sm text-gray-500">
//                   Intelligent scheduling powered by AI
//                 </p>
//               </div>
//             </div>
//           </div>
          
//           <div className="flex items-center space-x-4">
//             {/* System health indicator removed */}
//           </div>
//         </div>
//       </header>

//       <div className="flex">
//         {/* Sidebar */}
//         <aside className={`bg-white shadow-sm border-r border-gray-200 transition-all duration-300 ${
//           isSidebarOpen ? 'w-64' : 'w-0 overflow-hidden'
//         }`}>
//           <nav className="p-4 space-y-2">
//             {navigationItems.map((item) => (
//               <button
//                 key={item.id}
//                 onClick={() => setCurrentView(item.id)}
//                 className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors ${
//                   currentView === item.id
//                     ? 'bg-blue-50 text-blue-700 border border-blue-200'
//                     : 'text-gray-700 hover:bg-gray-100'
//                 }`}
//               >
//                 <item.icon size={20} />
//                 <span className="font-medium">{item.label}</span>
//               </button>
//             ))}
//           </nav>

//           {/* System info removed */}
//         </aside>

//         {/* Main content */}
//         <main className="flex-1 p-6">
//           <div className="max-w-7xl mx-auto">
//             <CurrentComponent />
//           </div>
//         </main>
//       </div>
//     </div>
//   );
// }

// export default App;

// frontend/src/App.jsx

import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { 
  Users, 
  Calendar, 
  Settings, 
  BarChart3, 
  Brain, 
  Menu, 
  X,
  Home
} from 'lucide-react';

// Import components
import Dashboard from './components/Dashboard';
import StaffList from './components/StaffList';
import ShiftCalendar from './components/ShiftCalendar';
import AllocationView from './components/AllocationView';
import LifecycleTest from './components/LifecycleTest';
import LoadingSpinner from './components/LoadingSpinner';

// Import API
import { systemAPI } from './services/api';

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [systemHealth, setSystemHealth] = useState(null);

  // Navigation items
  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home, component: Dashboard },
    { id: 'staff', label: 'Staff Management', icon: Users, component: StaffList },
    { id: 'shifts', label: 'Shift Calendar', icon: Calendar, component: ShiftCalendar },
    { id: 'allocations', label: 'AI Allocation', icon: Brain, component: AllocationView },
    { id: 'lifecycle', label: 'Lifecycle Test', icon: Settings, component: LifecycleTest },
    { id: 'analytics', label: 'Analytics', icon: BarChart3, component: Dashboard }, // Reuse Dashboard for now
  ];

  // Check system health on app load
  useEffect(() => {
    const checkSystemHealth = async () => {
      try {
        const response = await systemAPI.healthCheck();
        setSystemHealth(response.data);
      } catch (error) {
        console.error('System health check failed:', error);
        setSystemHealth({ status: 'unhealthy', error: error.message });
      } finally {
        setIsLoading(false);
      }
    };

    checkSystemHealth();
  }, []);

  // Get current component
  const getCurrentComponent = () => {
    const navItem = navigationItems.find(item => item.id === currentView);
    return navItem ? navItem.component : Dashboard;
  };

  // Render loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="large" />
          <p className="mt-4 text-gray-600">Loading Hospital Staff Allocation AI...</p>
        </div>
      </div>
    );
  }

  // Render system health error
  if (systemHealth?.status === 'unhealthy') {
    return (
      <div className="min-h-screen bg-red-50 flex items-center justify-center">
        <div className="text-center p-8 bg-white rounded-lg shadow-lg max-w-md">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-red-800 mb-2">System Error</h1>
          <p className="text-red-600 mb-4">
            Unable to connect to the backend server. Please ensure the API is running.
          </p>
          <button 
            onClick={() => window.location.reload()}
            className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  const CurrentComponent = getCurrentComponent();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Toast notifications */}
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />

      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="text-gray-500 hover:text-gray-700 transition-colors"
            >
              {isSidebarOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  Hospital Staff Allocation AI
                </h1>
                <p className="text-sm text-gray-500">
                  Intelligent scheduling powered by AI
                </p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* System health indicator */}
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                systemHealth?.status === 'healthy' ? 'bg-green-500' : 'bg-yellow-500'
              }`}></div>
              <span className="text-sm text-gray-600">
                {systemHealth?.status === 'healthy' ? 'System Healthy' : 'System Check'}
              </span>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className={`bg-white shadow-sm border-r border-gray-200 transition-all duration-300 ${
          isSidebarOpen ? 'w-64' : 'w-0 overflow-hidden'
        }`}>
          <nav className="p-4 space-y-2">
            {navigationItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setCurrentView(item.id)}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors ${
                  currentView === item.id
                    ? 'bg-blue-50 text-blue-700 border border-blue-200'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <item.icon size={20} />
                <span className="font-medium">{item.label}</span>
              </button>
            ))}
          </nav>

          {/* System info */}
          <div className="absolute bottom-4 left-4 right-4">
            {/* <div className="bg-gray-50 rounded-lg p-3 text-sm">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-gray-700">System Status</span>
                <span className={`px-2 py-1 rounded text-xs ${
                  systemHealth?.status === 'healthy' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {systemHealth?.status || 'Unknown'}
                </span>
              </div>
              <div className="space-y-1 text-xs text-gray-600">
                <div>LLM: {systemHealth?.services?.llm_service?.status || 'Unknown'}</div>
                <div>DB: {systemHealth?.services?.database?.status || 'Unknown'}</div>
              </div>
            </div> */}
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 p-6">
          <div className="max-w-7xl mx-auto">
            <CurrentComponent />
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;