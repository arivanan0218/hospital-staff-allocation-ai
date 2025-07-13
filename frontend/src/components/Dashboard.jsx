// frontend/src/components/Dashboard.jsx

import React, { useState, useEffect } from 'react';
import { 
  Users, 
  Calendar, 
  Clock, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle,
  Brain,
  BarChart3,
  Zap
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import toast from 'react-hot-toast';

import { systemAPI, allocationsAPI, staffAPI, shiftsAPI } from '../services/api';
import LoadingSpinner from './LoadingSpinner';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [utilization, setUtilization] = useState(null);
  const [recentAllocations, setRecentAllocations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Load dashboard data
  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      
      // Load system stats
      const [statsResponse, utilizationResponse, allocationsResponse] = await Promise.all([
        systemAPI.getStats(),
        allocationsAPI.getUtilizationAnalytics(),
        allocationsAPI.getAll()
      ]);

      setStats(statsResponse.data);
      setUtilization(utilizationResponse.data);
      
      // Get recent allocations (last 10)
      const allAllocations = allocationsResponse.data;
      setRecentAllocations(allAllocations.slice(-10).reverse());

    } catch (error) {
      console.error('Error loading dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadDashboardData();
    setIsRefreshing(false);
    toast.success('Dashboard refreshed!');
  };

  const handleAutoAllocate = async () => {
    try {
      // Get upcoming shifts that need allocation
      const today = new Date().toISOString().split('T')[0];
      const shiftsResponse = await shiftsAPI.getByDate(today);
      const shifts = shiftsResponse.data;
      
      if (shifts.length === 0) {
        toast.error('No shifts found for today');
        return;
      }

      const shiftIds = shifts.map(shift => shift.id);
      
      toast.loading('AI is allocating staff...', { id: 'auto-allocate' });
      
      const result = await allocationsAPI.autoAllocate({
        shift_ids: shiftIds,
        preferences: { optimize_for: 'balance' },
        constraints: {}
      });

      if (result.data.success) {
        toast.success(`Successfully allocated ${result.data.allocations.length} shifts!`, { id: 'auto-allocate' });
        loadDashboardData(); // Refresh data
      } else {
        toast.error(result.data.message, { id: 'auto-allocate' });
      }
    } catch (error) {
      console.error('Auto-allocation error:', error);
      toast.error('Auto-allocation failed', { id: 'auto-allocate' });
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  // Prepare chart data
  const departmentData = stats?.staff_by_department ? 
    Object.entries(stats.staff_by_department).map(([dept, data]) => ({
      name: dept.charAt(0).toUpperCase() + dept.slice(1),
      count: data.count,
      avgSkill: data.avg_skill
    })) : [];

  const roleData = stats?.staff_by_role ? 
    Object.entries(stats.staff_by_role).map(([role, data]) => ({
      name: role.charAt(0).toUpperCase() + role.slice(1),
      count: data.count,
      avgExperience: data.avg_experience
    })) : [];

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Hospital staff allocation overview</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50"
          >
            {isRefreshing ? <LoadingSpinner size="small" /> : <TrendingUp size={16} />}
            <span className="ml-2">Refresh</span>
          </button>
          <button
            onClick={handleAutoAllocate}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Brain size={16} />
            <span className="ml-2">AI Auto-Allocate</span>
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Total Staff</h3>
              <p className="text-2xl font-bold text-gray-900">{stats?.overview?.total_staff || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <Calendar className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Total Shifts</h3>
              <p className="text-2xl font-bold text-gray-900">{stats?.overview?.total_shifts || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Clock className="w-6 h-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Staff Utilization</h3>
              <p className="text-2xl font-bold text-gray-900">
                {Math.round((stats?.overview?.staff_utilization_rate || 0) * 100)}%
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <BarChart3 className="w-6 h-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Shift Coverage</h3>
              <p className="text-2xl font-bold text-gray-900">
                {Math.round((stats?.overview?.shift_coverage_rate || 0) * 100)}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Department Distribution */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Staff by Department</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={departmentData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Role Distribution */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Staff by Role</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={roleData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, count }) => `${name}: ${count}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="count"
              >
                {roleData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Activity & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Allocations */}
        <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Allocations</h3>
          <div className="space-y-3">
            {recentAllocations.length > 0 ? recentAllocations.map((allocation) => (
              <div key={allocation.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${
                    allocation.status === 'confirmed' ? 'bg-green-500' : 
                    allocation.status === 'pending' ? 'bg-yellow-500' : 'bg-red-500'
                  }`}></div>
                  <div>
                    <p className="font-medium text-gray-900">Staff {allocation.staff_id}</p>
                    <p className="text-sm text-gray-600">Shift {allocation.shift_id}</p>
                  </div>
                </div>
                <div className="text-right">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    allocation.status === 'confirmed' ? 'bg-green-100 text-green-800' : 
                    allocation.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {allocation.status}
                  </span>
                  <p className="text-xs text-gray-500 mt-1">
                    {Math.round(allocation.confidence_score * 100)}% confidence
                  </p>
                </div>
              </div>
            )) : (
              <div className="text-center py-8 text-gray-500">
                <Calendar className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p>No recent allocations</p>
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <button 
              onClick={handleAutoAllocate}
              className="w-full flex items-center justify-center px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Brain className="w-5 h-5 mr-2" />
              Auto-Allocate Today
            </button>
            
            <button className="w-full flex items-center justify-center px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
              <CheckCircle className="w-5 h-5 mr-2" />
              Approve Pending
            </button>
            
            <button className="w-full flex items-center justify-center px-4 py-3 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors">
              <AlertTriangle className="w-5 h-5 mr-2" />
              Review Conflicts
            </button>
            
            <button className="w-full flex items-center justify-center px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
              <Zap className="w-5 h-5 mr-2" />
              Optimize Schedule
            </button>
          </div>
        </div>
      </div>

      {/* System Health */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">System Health</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center space-x-3">
            <div className="w-4 h-4 bg-green-500 rounded-full"></div>
            <div>
              <p className="font-medium text-gray-900">Database</p>
              <p className="text-sm text-gray-600">{stats?.system_health?.database_status || 'Operational'}</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-4 h-4 bg-green-500 rounded-full"></div>
            <div>
              <p className="font-medium text-gray-900">AI Agents</p>
              <p className="text-sm text-gray-600">{stats?.system_health?.ai_agents_status || 'Operational'}</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-4 h-4 bg-green-500 rounded-full"></div>
            <div>
              <p className="font-medium text-gray-900">LLM Service</p>
              <p className="text-sm text-gray-600">{stats?.system_health?.llm_service_status || 'Operational'}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;