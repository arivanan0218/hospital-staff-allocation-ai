// frontend/src/components/StatusWidget.jsx

import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Users, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  RefreshCw
} from 'lucide-react';
import { staffAvailabilityAPI, shiftStatusAPI } from '../services/api';

const StatusWidget = () => {
  const [statusData, setStatusData] = useState({
    availableStaff: 0,
    workingStaff: 0,
    activeShifts: 0,
    endingSoonShifts: 0
  });
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    loadStatusData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadStatusData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadStatusData = async () => {
    try {
      const [availableRes, workingRes, activeRes, endingRes] = await Promise.all([
        staffAvailabilityAPI.getAvailableStaff().catch(() => ({ data: [] })),
        staffAvailabilityAPI.getWorkingStaff().catch(() => ({ data: [] })),
        shiftStatusAPI.getActiveShifts().catch(() => ({ data: [] })),
        shiftStatusAPI.getEndingSoon().catch(() => ({ data: [] }))
      ]);

      setStatusData({
        availableStaff: availableRes.data.length,
        workingStaff: workingRes.data.length,
        activeShifts: activeRes.data.length,
        endingSoonShifts: endingRes.data.length
      });

      setLastUpdated(new Date().toLocaleTimeString());
    } catch (error) {
      console.error('Error loading status data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <Activity className="mr-2" size={20} />
          Live Status
        </h3>
        <div className="flex items-center space-x-2">
          <button
            onClick={loadStatusData}
            className="p-1 hover:bg-gray-100 rounded transition-colors"
            title="Refresh"
          >
            <RefreshCw size={16} className={isLoading ? 'animate-spin' : ''} />
          </button>
          {lastUpdated && (
            <span className="text-xs text-gray-500">
              {lastUpdated}
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="text-center p-3 bg-green-50 rounded-lg">
          <div className="flex justify-center mb-2">
            <Users className="w-6 h-6 text-green-600" />
          </div>
          <div className="text-2xl font-bold text-green-600">
            {statusData.availableStaff}
          </div>
          <div className="text-sm text-green-700">Available</div>
        </div>

        <div className="text-center p-3 bg-blue-50 rounded-lg">
          <div className="flex justify-center mb-2">
            <CheckCircle className="w-6 h-6 text-blue-600" />
          </div>
          <div className="text-2xl font-bold text-blue-600">
            {statusData.workingStaff}
          </div>
          <div className="text-sm text-blue-700">Working</div>
        </div>

        <div className="text-center p-3 bg-purple-50 rounded-lg">
          <div className="flex justify-center mb-2">
            <Activity className="w-6 h-6 text-purple-600" />
          </div>
          <div className="text-2xl font-bold text-purple-600">
            {statusData.activeShifts}
          </div>
          <div className="text-sm text-purple-700">Active Shifts</div>
        </div>

        <div className="text-center p-3 bg-orange-50 rounded-lg">
          <div className="flex justify-center mb-2">
            <Clock className="w-6 h-6 text-orange-600" />
          </div>
          <div className="text-2xl font-bold text-orange-600">
            {statusData.endingSoonShifts}
          </div>
          <div className="text-sm text-orange-700">Ending Soon</div>
        </div>
      </div>

      {/* Status Indicators */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-gray-600">Database Models Active</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
            <span className="text-gray-600">Real-time Updates</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatusWidget;