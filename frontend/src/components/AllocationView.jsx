// frontend/src/components/AllocationView.jsx

import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  Zap, 
  Target, 
  Users, 
  Calendar, 
  CheckCircle, 
  AlertTriangle, 
  Clock, 
  TrendingUp,
  Settings,
  RefreshCw,
  Eye,
  ThumbsUp,
  ThumbsDown,
  XCircle,
  BarChart3
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import toast from 'react-hot-toast';

import { allocationsAPI, shiftsAPI, staffAPI } from '../services/api';
import LoadingSpinner from './LoadingSpinner';

const AllocationView = () => {
  const [allocations, setAllocations] = useState([]);
  const [shifts, setShifts] = useState([]);
  const [staff, setStaff] = useState([]);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [selectedShifts, setSelectedShifts] = useState([]);
  const [isAutoAllocating, setIsAutoAllocating] = useState(false);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [allocationResults, setAllocationResults] = useState(null);
  const [optimizationStrategy, setOptimizationStrategy] = useState('balance');
  const [showSettings, setShowSettings] = useState(false);
  const [utilizationData, setUtilizationData] = useState(null);
  const [conflictData, setConflictData] = useState(null);

  // AI Settings
  const [aiSettings, setAiSettings] = useState({
    confidence_threshold: 0.7,
    prefer_experience: true,
    minimize_cost: false,
    respect_preferences: true,
    allow_overtime: false
  });

  const strategies = [
    { value: 'cost', label: 'Cost Optimization', description: 'Minimize staffing costs' },
    { value: 'quality', label: 'Quality Focus', description: 'Maximize care quality' },
    { value: 'balance', label: 'Balanced Approach', description: 'Balance cost and quality' },
    { value: 'satisfaction', label: 'Staff Satisfaction', description: 'Prioritize staff preferences' }
  ];

  useEffect(() => {
    loadData();
  }, [selectedDate]);

  const loadData = async () => {
    try {
      setIsLoading(true);
      const [allocationsRes, shiftsRes, staffRes, utilizationRes] = await Promise.all([
        allocationsAPI.getByDate(selectedDate),
        shiftsAPI.getByDate(selectedDate),
        staffAPI.getAll(),
        allocationsAPI.getUtilizationAnalytics()
      ]);

      setAllocations(allocationsRes.data);
      setShifts(shiftsRes.data);
      setStaff(staffRes.data);
      setUtilizationData(utilizationRes.data);

      // Load conflict data
      loadConflictData();
    } catch (error) {
      console.error('Error loading data:', error);
      toast.error('Failed to load allocation data');
    } finally {
      setIsLoading(false);
    }
  };

  const loadConflictData = async () => {
    try {
      const response = await allocationsAPI.getConflicts(selectedDate);
      setConflictData(response.data);
    } catch (error) {
      console.error('Error loading conflict data:', error);
    }
  };

  const handleAutoAllocate = async () => {
    if (selectedShifts.length === 0) {
      toast.error('Please select shifts to allocate');
      return;
    }

    try {
      setIsAutoAllocating(true);
      toast.loading('AI is analyzing and allocating staff...', { id: 'auto-allocate' });

      const allocationRequest = {
        shift_ids: selectedShifts,
        preferences: {
          optimize_for: optimizationStrategy,
          confidence_threshold: aiSettings.confidence_threshold,
          respect_preferences: aiSettings.respect_preferences,
          minimize_cost: aiSettings.minimize_cost
        },
        constraints: {
          allow_overtime: aiSettings.allow_overtime,
          prefer_experience: aiSettings.prefer_experience
        }
      };

      const response = await allocationsAPI.autoAllocate(allocationRequest);
      const result = response.data;

      setAllocationResults(result);

      if (result.success) {
        toast.success(
          `Successfully allocated ${result.allocations.length} positions! Optimization score: ${Math.round(result.optimization_score * 100)}%`,
          { id: 'auto-allocate' }
        );
        loadData();
      } else {
        toast.error(result.message, { id: 'auto-allocate' });
      }
    } catch (error) {
      console.error('Auto-allocation error:', error);
      toast.error('Auto-allocation failed', { id: 'auto-allocate' });
    } finally {
      setIsAutoAllocating(false);
    }
  };

  const handleOptimizeSchedule = async () => {
    try {
      setIsOptimizing(true);
      toast.loading('AI is optimizing the schedule...', { id: 'optimize' });

      const response = await allocationsAPI.optimize(selectedDate, optimizationStrategy);
      const result = response.data;

      if (result.success) {
        const improvements = result.improvement_metrics;
        let message = 'Schedule optimized! ';
        
        if (improvements.cost_change) {
          message += `Cost savings: $${improvements.cost_change.toFixed(2)} `;
        }
        if (improvements.efficiency_change) {
          message += `Efficiency: +${Math.round(improvements.efficiency_change * 100)}% `;
        }

        toast.success(message, { id: 'optimize' });
        loadData();
      } else {
        toast.error('Optimization failed', { id: 'optimize' });
      }
    } catch (error) {
      console.error('Optimization error:', error);
      toast.error('Optimization failed', { id: 'optimize' });
    } finally {
      setIsOptimizing(false);
    }
  };

  const handleAllocationAction = async (allocationId, action) => {
    try {
      let newStatus;
      switch (action) {
        case 'approve':
          newStatus = 'confirmed';
          break;
        case 'reject':
          newStatus = 'rejected';
          break;
        default:
          return;
      }

      await allocationsAPI.updateStatus(allocationId, newStatus);
      toast.success(`Allocation ${action}d successfully!`);
      loadData();
    } catch (error) {
      console.error(`Error ${action}ing allocation:`, error);
      toast.error(`Failed to ${action} allocation`);
    }
  };

  const toggleShiftSelection = (shiftId) => {
    setSelectedShifts(prev => 
      prev.includes(shiftId) 
        ? prev.filter(id => id !== shiftId)
        : [...prev, shiftId]
    );
  };

  const selectAllShifts = () => {
    const availableShifts = shifts.filter(shift => !getAllocationsForShift(shift.id).some(a => a.status === 'confirmed'));
    setSelectedShifts(availableShifts.map(shift => shift.id));
  };

  const clearSelection = () => {
    setSelectedShifts([]);
  };

  const getAllocationsForShift = (shiftId) => {
    return allocations.filter(alloc => alloc.shift_id === shiftId);
  };

  const getStaffById = (staffId) => {
    return staff.find(s => s.id === staffId);
  };

  const getShiftById = (shiftId) => {
    return shifts.find(s => s.id === shiftId);
  };

  // Prepare chart data
  const allocationStatusData = [
    { name: 'Confirmed', value: allocations.filter(a => a.status === 'confirmed').length, color: '#10b981' },
    { name: 'Pending', value: allocations.filter(a => a.status === 'pending').length, color: '#f59e0b' },
    { name: 'Rejected', value: allocations.filter(a => a.status === 'rejected').length, color: '#ef4444' }
  ];

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
          <h1 className="text-3xl font-bold text-gray-900">AI Staff Allocation</h1>
          <p className="text-gray-600">Intelligent staff allocation powered by AI agents</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <Settings size={16} />
            <span className="ml-2">AI Settings</span>
          </button>
          <button
            onClick={loadData}
            className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <RefreshCw size={16} />
            <span className="ml-2">Refresh</span>
          </button>
        </div>
      </div>

      {/* Date Selection */}
      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <div className="flex items-center space-x-4">
          <label className="text-sm font-medium text-gray-700">Select Date:</label>
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <div className="text-sm text-gray-600">
            {shifts.length} shifts, {allocations.length} allocations
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Brain className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">AI Confidence</h3>
              <p className="text-2xl font-bold text-gray-900">
                {allocations.length > 0 
                  ? Math.round(allocations.reduce((sum, a) => sum + a.confidence_score, 0) / allocations.length * 100)
                  : 0}%
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Confirmed</h3>
              <p className="text-2xl font-bold text-gray-900">
                {allocations.filter(a => a.status === 'confirmed').length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Clock className="w-6 h-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Pending</h3>
              <p className="text-2xl font-bold text-gray-900">
                {allocations.filter(a => a.status === 'pending').length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-red-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Conflicts</h3>
              <p className="text-2xl font-bold text-gray-900">
                {conflictData?.global_conflicts?.length || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* AI Settings Panel */}
      {showSettings && (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Configuration</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Optimization Strategy</label>
              <select
                value={optimizationStrategy}
                onChange={(e) => setOptimizationStrategy(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {strategies.map(strategy => (
                  <option key={strategy.value} value={strategy.value}>
                    {strategy.label} - {strategy.description}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Confidence Threshold: {Math.round(aiSettings.confidence_threshold * 100)}%
              </label>
              <input
                type="range"
                min="0.5"
                max="1"
                step="0.05"
                value={aiSettings.confidence_threshold}
                onChange={(e) => setAiSettings({...aiSettings, confidence_threshold: parseFloat(e.target.value)})}
                className="w-full"
              />
            </div>
            
            <div className="space-y-3">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={aiSettings.respect_preferences}
                  onChange={(e) => setAiSettings({...aiSettings, respect_preferences: e.target.checked})}
                  className="mr-2"
                />
                <span className="text-sm">Respect Staff Preferences</span>
              </label>
              
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={aiSettings.prefer_experience}
                  onChange={(e) => setAiSettings({...aiSettings, prefer_experience: e.target.checked})}
                  className="mr-2"
                />
                <span className="text-sm">Prefer Experienced Staff</span>
              </label>
              
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={aiSettings.minimize_cost}
                  onChange={(e) => setAiSettings({...aiSettings, minimize_cost: e.target.checked})}
                  className="mr-2"
                />
                <span className="text-sm">Minimize Cost</span>
              </label>
            </div>
          </div>
        </div>
      )}

      {/* Control Panel */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Shift Selection & Actions</h3>
          <div className="flex space-x-2">
            <button
              onClick={selectAllShifts}
              className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
            >
              Select All Unallocated
            </button>
            <button
              onClick={clearSelection}
              className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
            >
              Clear Selection
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
          {shifts.map(shift => {
            const shiftAllocations = getAllocationsForShift(shift.id);
            const isSelected = selectedShifts.includes(shift.id);
            const hasConfirmedAllocation = shiftAllocations.some(a => a.status === 'confirmed');

            return (
              <div
                key={shift.id}
                onClick={() => !hasConfirmedAllocation && toggleShiftSelection(shift.id)}
                className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                  isSelected ? 'border-blue-500 bg-blue-50' : 
                  hasConfirmedAllocation ? 'border-green-500 bg-green-50 cursor-not-allowed' :
                  'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium capitalize">{shift.shift_type}</span>
                  <span className={`px-2 py-1 rounded text-xs ${
                    hasConfirmedAllocation ? 'bg-green-100 text-green-800' :
                    shiftAllocations.some(a => a.status === 'pending') ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {hasConfirmedAllocation ? 'Allocated' : 
                     shiftAllocations.some(a => a.status === 'pending') ? 'Pending' : 'Open'}
                  </span>
                </div>
                <div className="text-sm text-gray-600">
                  <div>{shift.department} • {shift.start_time} - {shift.end_time}</div>
                  <div>Required: {Object.entries(shift.required_staff).map(([role, count]) => `${count} ${role}`).join(', ')}</div>
                </div>
              </div>
            );
          })}
        </div>

        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">
            {selectedShifts.length} shifts selected
          </div>
          <div className="flex space-x-3">
            <button
              onClick={handleAutoAllocate}
              disabled={selectedShifts.length === 0 || isAutoAllocating}
              className="flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isAutoAllocating ? <LoadingSpinner size="small" color="white" /> : <Brain size={20} />}
              <span className="ml-2">AI Auto-Allocate</span>
            </button>
            
            <button
              onClick={handleOptimizeSchedule}
              disabled={isOptimizing}
              className="flex items-center px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isOptimizing ? <LoadingSpinner size="small" color="white" /> : <Zap size={20} />}
              <span className="ml-2">Optimize Schedule</span>
            </button>
          </div>
        </div>
      </div>

      {/* Allocation Results */}
      {allocationResults && (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Allocation Results</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{allocationResults.allocations.length}</div>
              <div className="text-sm text-gray-600">Successful Allocations</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{allocationResults.unallocated_shifts.length}</div>
              <div className="text-sm text-gray-600">Unallocated Shifts</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{Math.round(allocationResults.optimization_score * 100)}%</div>
              <div className="text-sm text-gray-600">Optimization Score</div>
            </div>
          </div>
          
          {allocationResults.recommendations.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 mb-2">AI Recommendations:</h4>
              <ul className="space-y-1">
                {allocationResults.recommendations.map((rec, index) => (
                  <li key={index} className="text-sm text-gray-600 flex items-start">
                    <Target size={14} className="mr-2 mt-0.5 text-blue-500" />
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Current Allocations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Allocations List */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Current Allocations</h3>
          </div>
          <div className="max-h-96 overflow-y-auto">
            {allocations.length > 0 ? allocations.map(allocation => {
              const staffMember = getStaffById(allocation.staff_id);
              const shift = getShiftById(allocation.shift_id);
              
              return (
                <div key={allocation.id} className="p-4 border-b border-gray-100 last:border-b-0">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-blue-600 text-sm font-medium">
                          {staffMember?.name.split(' ').map(n => n[0]).join('') || '?'}
                        </span>
                      </div>
                      <div>
                        <div className="font-medium text-gray-900">{staffMember?.name || 'Unknown Staff'}</div>
                        <div className="text-sm text-gray-600">
                          {shift?.shift_type} • {shift?.department}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        allocation.status === 'confirmed' ? 'bg-green-100 text-green-800' :
                        allocation.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {allocation.status}
                      </span>
                      <span className="text-xs text-gray-500">
                        {Math.round(allocation.confidence_score * 100)}%
                      </span>
                    </div>
                  </div>
                  
                  <div className="text-sm text-gray-600 mb-2">
                    {allocation.reasoning}
                  </div>
                  
                  {allocation.status === 'pending' && (
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleAllocationAction(allocation.id, 'approve')}
                        className="flex items-center px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700 transition-colors"
                      >
                        <ThumbsUp size={14} className="mr-1" />
                        Approve
                      </button>
                      <button
                        onClick={() => handleAllocationAction(allocation.id, 'reject')}
                        className="flex items-center px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700 transition-colors"
                      >
                        <ThumbsDown size={14} className="mr-1" />
                        Reject
                      </button>
                    </div>
                  )}
                </div>
              );
            }) : (
              <div className="p-8 text-center text-gray-500">
                <Users className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p>No allocations for this date</p>
              </div>
            )}
          </div>
        </div>

        {/* Analytics */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Allocation Analytics</h3>
          
          {allocationStatusData.some(d => d.value > 0) ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={allocationStatusData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {allocationStatusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-48 text-gray-500">
              <div className="text-center">
                <BarChart3 className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p>No data to display</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AllocationView;