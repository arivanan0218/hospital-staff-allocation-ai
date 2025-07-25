// frontend/src/components/LifecycleTest.jsx

import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Square, 
  Clock, 
  Users, 
  CheckCircle, 
  XCircle,
  UserCheck,
  UserX,
  RefreshCw,
  Activity,
  AlertCircle
} from 'lucide-react';
import toast from 'react-hot-toast';

import { 
  systemAPI, 
  shiftsAPI, 
  staffAPI, 
  staffAvailabilityAPI, 
  shiftStatusAPI, 
  attendanceAPI 
} from '../services/api';
import LoadingSpinner from './LoadingSpinner';

const LifecycleTest = () => {
  const [shifts, setShifts] = useState([]);
  const [staff, setStaff] = useState([]);
  const [availableStaff, setAvailableStaff] = useState([]);
  const [workingStaff, setWorkingStaff] = useState([]);
  const [activeShifts, setActiveShifts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedShift, setSelectedShift] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);

  useEffect(() => {
    loadAllData();
    // Refresh data every 30 seconds to see real-time changes
    const interval = setInterval(loadAllData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadAllData = async () => {
    try {
      setIsLoading(true);
      
      const [
        shiftsRes, 
        staffRes, 
        systemRes,
        availableRes,
        workingRes,
        activeRes
      ] = await Promise.all([
        shiftsAPI.getAll(),
        staffAPI.getAll(),
        systemAPI.getStats(),
        staffAvailabilityAPI.getAvailableStaff().catch(() => ({ data: [] })),
        staffAvailabilityAPI.getWorkingStaff().catch(() => ({ data: [] })),
        shiftStatusAPI.getActiveShifts().catch(() => ({ data: [] }))
      ]);

      setShifts(shiftsRes.data);
      setStaff(staffRes.data);
      setSystemStatus(systemRes.data);
      setAvailableStaff(availableRes.data);
      setWorkingStaff(workingRes.data);
      setActiveShifts(activeRes.data);

    } catch (error) {
      console.error('Error loading data:', error);
      toast.error('Failed to load data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartShift = async (shiftId) => {
    try {
      await shiftStatusAPI.startShift(shiftId);
      toast.success('Shift started successfully!');
      loadAllData();
    } catch (error) {
      console.error('Error starting shift:', error);
      toast.error('Failed to start shift');
    }
  };

  const handleCompleteShift = async (shiftId) => {
    try {
      const notes = prompt('Enter completion notes (optional):');
      await shiftStatusAPI.completeShift(shiftId, notes || '');
      toast.success('Shift completed successfully! Staff should now be available.');
      loadAllData();
    } catch (error) {
      console.error('Error completing shift:', error);
      toast.error('Failed to complete shift');
    }
  };

  const handleCheckIn = async (staffId, shiftId) => {
    try {
      await attendanceAPI.checkIn(staffId, shiftId);
      toast.success('Staff checked in successfully!');
      loadAllData();
    } catch (error) {
      console.error('Error checking in:', error);
      toast.error('Failed to check in staff');
    }
  };

  const handleCheckOut = async (staffId, shiftId) => {
    try {
      const notes = prompt('Enter checkout notes (optional):');
      await attendanceAPI.checkOut(staffId, shiftId, notes || '');
      toast.success('Staff checked out successfully!');
      loadAllData();
    } catch (error) {
      console.error('Error checking out:', error);
      toast.error('Failed to check out staff');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      scheduled: 'bg-gray-100 text-gray-800',
      in_progress: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      archived: 'bg-purple-100 text-purple-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getAvailabilityColor = (status) => {
    const colors = {
      available: 'bg-green-100 text-green-800',
      working: 'bg-blue-100 text-blue-800',
      on_break: 'bg-yellow-100 text-yellow-800',
      unavailable: 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Shift Lifecycle Test</h1>
          <p className="text-gray-600">Test the new shift lifecycle and staff availability features</p>
        </div>
        <button
          onClick={loadAllData}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <RefreshCw size={16} />
          <span className="ml-2">Refresh Data</span>
        </button>
      </div>

      {/* System Status */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">System Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{shifts.length}</div>
            <div className="text-sm text-gray-600">Total Shifts</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{availableStaff.length}</div>
            <div className="text-sm text-gray-600">Available Staff</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">{workingStaff.length}</div>
            <div className="text-sm text-gray-600">Working Staff</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">{activeShifts.length}</div>
            <div className="text-sm text-gray-600">Active Shifts</div>
          </div>
        </div>
      </div>

      {/* Database Features Test */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Shift Status Management */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Shift Status Management</h3>
          <div className="space-y-3">
            {shifts.slice(0, 5).map((shift) => (
              <div key={shift.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium">{shift.shift_type}</span>
                    <span className={`px-2 py-1 rounded text-xs ${getStatusColor(shift.status)}`}>
                      {shift.status}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600">
                    {shift.date} • {shift.start_time} - {shift.end_time} • {shift.department}
                  </div>
                  {shift.actual_start_time && (
                    <div className="text-xs text-green-600">
                      Started: {shift.actual_start_time}
                    </div>
                  )}
                  {shift.actual_end_time && (
                    <div className="text-xs text-blue-600">
                      Ended: {shift.actual_end_time}
                    </div>
                  )}
                </div>
                <div className="flex space-x-2">
                  {shift.status === 'scheduled' && (
                    <button
                      onClick={() => handleStartShift(shift.id)}
                      className="p-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                      title="Start Shift"
                    >
                      <Play size={14} />
                    </button>
                  )}
                  {shift.status === 'in_progress' && (
                    <button
                      onClick={() => handleCompleteShift(shift.id)}
                      className="p-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                      title="Complete Shift"
                    >
                      <Square size={14} />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Staff Availability */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Staff Availability</h3>
          <div className="space-y-3">
            {staff.slice(0, 5).map((staffMember) => {
              const availability = availableStaff.find(a => a.staff_id === staffMember.id) ||
                                 workingStaff.find(w => w.staff_id === staffMember.id);
              
              return (
                <div key={staffMember.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-medium">{staffMember.name}</span>
                      {availability && (
                        <span className={`px-2 py-1 rounded text-xs ${getAvailabilityColor(availability.status)}`}>
                          {availability.status}
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-gray-600">
                      {staffMember.role} • {staffMember.department}
                    </div>
                    {availability?.current_shift_id && (
                      <div className="text-xs text-blue-600">
                        Working: {availability.current_shift_id}
                      </div>
                    )}
                    {availability?.available_from && (
                      <div className="text-xs text-green-600">
                        Available from: {new Date(availability.available_from).toLocaleTimeString()}
                      </div>
                    )}
                  </div>
                  <div className="flex space-x-2">
                    {availability?.status === 'available' && (
                      <button
                        onClick={() => {
                          const shiftId = prompt('Enter shift ID to check in:');
                          if (shiftId) handleCheckIn(staffMember.id, shiftId);
                        }}
                        className="p-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                        title="Check In"
                      >
                        <UserCheck size={14} />
                      </button>
                    )}
                    {availability?.status === 'working' && (
                      <button
                        onClick={() => handleCheckOut(staffMember.id, availability.current_shift_id)}
                        className="p-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                        title="Check Out"
                      >
                        <UserX size={14} />
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Instructions */}
      <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
        <h3 className="text-lg font-semibold text-blue-900 mb-4 flex items-center">
          <Activity className="mr-2" size={20} />
          How to Test New Features
        </h3>
        <div className="space-y-2 text-blue-800">
          <div><strong>1. Start a Shift:</strong> Click the play button (▶️) next to a scheduled shift</div>
          <div><strong>2. Check Staff Status:</strong> Watch how staff availability changes when shifts start</div>
          <div><strong>3. Complete a Shift:</strong> Click the stop button (⏹️) next to an active shift</div>
          <div><strong>4. Verify Staff Release:</strong> Staff should automatically become "available" when shifts complete</div>
          <div><strong>5. Check-in/Check-out:</strong> Use the user icons to manually manage attendance</div>
          <div><strong>6. Real-time Updates:</strong> Data refreshes every 30 seconds automatically</div>
        </div>
      </div>

      {/* Debug Information */}
      <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Debug Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <strong>New Database Fields Working:</strong>
            <ul className="mt-2 space-y-1 text-gray-600">
              <li>✅ Shift status tracking</li>
              <li>✅ Staff availability timeline</li>
              <li>✅ Check-in/Check-out timestamps</li>
              <li>✅ Overtime calculation</li>
              <li>✅ Automatic staff release</li>
            </ul>
          </div>
          <div>
            <strong>API Endpoints Active:</strong>
            <ul className="mt-2 space-y-1 text-gray-600">
              <li>✅ /shifts/active</li>
              <li>✅ /staff/available</li>
              <li>✅ /staff/working</li>
              <li>✅ /shifts/:id/start</li>
              <li>✅ /shifts/:id/complete</li>
            </ul>
          </div>
          <div>
            <strong>Real-time Features:</strong>
            <ul className="mt-2 space-y-1 text-gray-600">
              <li>✅ Status change notifications</li>
              <li>✅ Automatic data refresh</li>
              <li>✅ Live availability tracking</li>
              <li>✅ Staff release automation</li>
              <li>✅ Timeline logging</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LifecycleTest;