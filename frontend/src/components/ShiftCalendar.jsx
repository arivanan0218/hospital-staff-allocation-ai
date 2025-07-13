// frontend/src/components/ShiftCalendar.jsx

import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  ChevronLeft, 
  ChevronRight, 
  Calendar as CalendarIcon, 
  Clock, 
  Users, 
  MapPin,
  AlertTriangle,
  CheckCircle,
  Edit2,
  Trash2,
  Filter
} from 'lucide-react';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isSameDay, addMonths, subMonths } from 'date-fns';
import toast from 'react-hot-toast';

import { shiftsAPI, allocationsAPI } from '../services/api';
import LoadingSpinner from './LoadingSpinner';

const ShiftCalendar = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [shifts, setShifts] = useState([]);
  const [allocations, setAllocations] = useState([]);
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedShift, setSelectedShift] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingShift, setEditingShift] = useState(null);
  const [coverageAnalytics, setCoverageAnalytics] = useState(null);
  const [filterDepartment, setFilterDepartment] = useState('');

  // Form state for adding/editing shifts
  const [formData, setFormData] = useState({
    date: '',
    shift_type: 'morning',
    department: 'general',
    start_time: '08:00',
    end_time: '16:00',
    required_staff: { doctor: 1, nurse: 2 },
    minimum_skill_level: 5,
    priority: 'medium',
    special_requirements: [],
    max_capacity: 5
  });

  const shiftTypes = [
    { value: 'morning', label: 'Morning', color: 'bg-yellow-100 text-yellow-800' },
    { value: 'afternoon', label: 'Afternoon', color: 'bg-orange-100 text-orange-800' },
    { value: 'evening', label: 'Evening', color: 'bg-purple-100 text-purple-800' },
    { value: 'night', label: 'Night', color: 'bg-blue-100 text-blue-800' },
    { value: 'on_call', label: 'On Call', color: 'bg-red-100 text-red-800' }
  ];

  const departments = [
    { value: 'emergency', label: 'Emergency' },
    { value: 'icu', label: 'ICU' },
    { value: 'surgery', label: 'Surgery' },
    { value: 'pediatrics', label: 'Pediatrics' },
    { value: 'cardiology', label: 'Cardiology' },
    { value: 'general', label: 'General' }
  ];

  const priorities = [
    { value: 'low', label: 'Low', color: 'bg-gray-100 text-gray-800' },
    { value: 'medium', label: 'Medium', color: 'bg-blue-100 text-blue-800' },
    { value: 'high', label: 'High', color: 'bg-yellow-100 text-yellow-800' },
    { value: 'critical', label: 'Critical', color: 'bg-red-100 text-red-800' }
  ];

  useEffect(() => {
    loadShifts();
    loadAllocations();
    loadCoverageAnalytics();
  }, [currentDate]);

  const loadShifts = async () => {
    try {
      setIsLoading(true);
      const response = await shiftsAPI.getAll();
      setShifts(response.data);
    } catch (error) {
      console.error('Error loading shifts:', error);
      toast.error('Failed to load shifts');
    } finally {
      setIsLoading(false);
    }
  };

  const loadAllocations = async () => {
    try {
      const response = await allocationsAPI.getAll();
      setAllocations(response.data);
    } catch (error) {
      console.error('Error loading allocations:', error);
    }
  };

  const loadCoverageAnalytics = async () => {
    try {
      const startDate = format(startOfMonth(currentDate), 'yyyy-MM-dd');
      const endDate = format(endOfMonth(currentDate), 'yyyy-MM-dd');
      const response = await shiftsAPI.getCoverageAnalytics(startDate, endDate);
      setCoverageAnalytics(response.data);
    } catch (error) {
      console.error('Error loading coverage analytics:', error);
    }
  };

  const handleAddShift = async (e) => {
    e.preventDefault();
    try {
      await shiftsAPI.create(formData);
      toast.success('Shift added successfully!');
      setShowAddModal(false);
      resetForm();
      loadShifts();
      loadCoverageAnalytics();
    } catch (error) {
      console.error('Error adding shift:', error);
      toast.error('Failed to add shift');
    }
  };

  const handleUpdateShift = async (e) => {
    e.preventDefault();
    try {
      await shiftsAPI.update(editingShift.id, formData);
      toast.success('Shift updated successfully!');
      setEditingShift(null);
      setShowAddModal(false);
      resetForm();
      loadShifts();
      loadCoverageAnalytics();
    } catch (error) {
      console.error('Error updating shift:', error);
      toast.error('Failed to update shift');
    }
  };

  const handleDeleteShift = async (shiftId) => {
    if (window.confirm('Are you sure you want to delete this shift?')) {
      try {
        await shiftsAPI.delete(shiftId);
        toast.success('Shift deleted successfully!');
        loadShifts();
        loadCoverageAnalytics();
        setSelectedShift(null);
      } catch (error) {
        console.error('Error deleting shift:', error);
        toast.error('Failed to delete shift');
      }
    }
  };

  const startEditing = (shift) => {
    setEditingShift(shift);
    setFormData({
      date: shift.date,
      shift_type: shift.shift_type,
      department: shift.department,
      start_time: shift.start_time,
      end_time: shift.end_time,
      required_staff: shift.required_staff,
      minimum_skill_level: shift.minimum_skill_level,
      priority: shift.priority,
      special_requirements: shift.special_requirements || [],
      max_capacity: shift.max_capacity
    });
    setShowAddModal(true);
  };

  const resetForm = () => {
    setFormData({
      date: selectedDate ? format(selectedDate, 'yyyy-MM-dd') : '',
      shift_type: 'morning',
      department: 'general',
      start_time: '08:00',
      end_time: '16:00',
      required_staff: { doctor: 1, nurse: 2 },
      minimum_skill_level: 5,
      priority: 'medium',
      special_requirements: [],
      max_capacity: 5
    });
  };

  const closeModal = () => {
    setShowAddModal(false);
    setEditingShift(null);
    resetForm();
  };

  const navigateMonth = (direction) => {
    setCurrentDate(prev => direction === 'next' ? addMonths(prev, 1) : subMonths(prev, 1));
  };

  const getShiftsForDate = (date) => {
    const dateStr = format(date, 'yyyy-MM-dd');
    let dayShifts = shifts.filter(shift => shift.date === dateStr);
    
    if (filterDepartment) {
      dayShifts = dayShifts.filter(shift => shift.department === filterDepartment);
    }
    
    return dayShifts;
  };

  const getShiftCoverage = (shift) => {
    const shiftAllocations = allocations.filter(alloc => alloc.shift_id === shift.id);
    const confirmedAllocations = shiftAllocations.filter(alloc => alloc.status === 'confirmed');
    
    const totalRequired = Object.values(shift.required_staff).reduce((sum, count) => sum + count, 0);
    const totalAssigned = confirmedAllocations.length;
    
    return {
      assigned: totalAssigned,
      required: totalRequired,
      percentage: totalRequired > 0 ? (totalAssigned / totalRequired) * 100 : 0,
      isFullyCovered: totalAssigned >= totalRequired
    };
  };

  const getShiftTypeColor = (shiftType) => {
    const type = shiftTypes.find(t => t.value === shiftType);
    return type ? type.color : 'bg-gray-100 text-gray-800';
  };

  const getPriorityColor = (priority) => {
    const p = priorities.find(pr => pr.value === priority);
    return p ? p.color : 'bg-gray-100 text-gray-800';
  };

  // Generate calendar days
  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);
  const calendarDays = eachDayOfInterval({ start: monthStart, end: monthEnd });

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
          <h1 className="text-3xl font-bold text-gray-900">Shift Calendar</h1>
          <p className="text-gray-600">Manage shifts and view coverage</p>
        </div>
        <div className="flex space-x-3">
          <select
            value={filterDepartment}
            onChange={(e) => setFilterDepartment(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Departments</option>
            {departments.map(dept => (
              <option key={dept.value} value={dept.value}>{dept.label}</option>
            ))}
          </select>
          <button
            onClick={() => {
              setSelectedDate(new Date());
              setShowAddModal(true);
            }}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus size={20} />
            <span className="ml-2">Add Shift</span>
          </button>
        </div>
      </div>

      {/* Coverage Analytics */}
      {coverageAnalytics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Shifts</p>
                <p className="text-2xl font-bold text-gray-900">{coverageAnalytics.summary.total_shifts}</p>
              </div>
              <CalendarIcon className="w-8 h-8 text-blue-600" />
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Coverage Rate</p>
                <p className="text-2xl font-bold text-gray-900">
                  {Math.round(coverageAnalytics.summary.coverage_rate * 100)}%
                </p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Fully Covered</p>
                <p className="text-2xl font-bold text-gray-900">{coverageAnalytics.summary.fully_covered_shifts}</p>
              </div>
              <Users className="w-8 h-8 text-purple-600" />
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Uncovered</p>
                <p className="text-2xl font-bold text-gray-900">{coverageAnalytics.summary.uncovered_shifts}</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-red-600" />
            </div>
          </div>
        </div>
      )}

      {/* Calendar Navigation */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={() => navigateMonth('prev')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ChevronLeft size={20} />
          </button>
          <h2 className="text-xl font-semibold text-gray-900">
            {format(currentDate, 'MMMM yyyy')}
          </h2>
          <button
            onClick={() => navigateMonth('next')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ChevronRight size={20} />
          </button>
        </div>

        {/* Calendar Grid */}
        <div className="grid grid-cols-7 gap-2">
          {/* Day headers */}
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
            <div key={day} className="p-2 text-center text-sm font-medium text-gray-500">
              {day}
            </div>
          ))}
          
          {/* Calendar days */}
          {calendarDays.map(day => {
            const dayShifts = getShiftsForDate(day);
            const isSelected = selectedDate && isSameDay(day, selectedDate);
            const isToday = isSameDay(day, new Date());
            
            return (
              <div
                key={day.toISOString()}
                onClick={() => setSelectedDate(day)}
                className={`p-2 min-h-[100px] border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors ${
                  isSelected ? 'bg-blue-50 border-blue-300' : ''
                } ${isToday ? 'bg-yellow-50 border-yellow-300' : ''}`}
              >
                <div className={`text-sm font-medium mb-1 ${
                  isSameMonth(day, currentDate) ? 'text-gray-900' : 'text-gray-400'
                }`}>
                  {format(day, 'd')}
                </div>
                
                <div className="space-y-1">
                  {dayShifts.slice(0, 3).map(shift => {
                    const coverage = getShiftCoverage(shift);
                    return (
                      <div
                        key={shift.id}
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedShift(shift);
                        }}
                        className={`text-xs p-1 rounded cursor-pointer ${getShiftTypeColor(shift.shift_type)} hover:opacity-80`}
                      >
                        <div className="font-medium truncate">{shift.shift_type}</div>
                        <div className="flex items-center justify-between">
                          <span className="truncate">{shift.department}</span>
                          <span className={`w-2 h-2 rounded-full ${
                            coverage.isFullyCovered ? 'bg-green-500' : 'bg-red-500'
                          }`}></span>
                        </div>
                      </div>
                    );
                  })}
                  {dayShifts.length > 3 && (
                    <div className="text-xs text-gray-500 text-center">
                      +{dayShifts.length - 3} more
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Selected Shift Details */}
      {selectedShift && (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Shift Details</h3>
            <div className="flex space-x-2">
              <button
                onClick={() => startEditing(selectedShift)}
                className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              >
                <Edit2 size={16} />
              </button>
              <button
                onClick={() => handleDeleteShift(selectedShift.id)}
                className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              >
                <Trash2 size={16} />
              </button>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Basic Information</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Date:</span>
                  <span>{selectedShift.date}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Type:</span>
                  <span className={`px-2 py-1 rounded text-xs ${getShiftTypeColor(selectedShift.shift_type)}`}>
                    {selectedShift.shift_type}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Time:</span>
                  <span>{selectedShift.start_time} - {selectedShift.end_time}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Department:</span>
                  <span className="capitalize">{selectedShift.department}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Priority:</span>
                  <span className={`px-2 py-1 rounded text-xs ${getPriorityColor(selectedShift.priority)}`}>
                    {selectedShift.priority}
                  </span>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Requirements</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Min Skill Level:</span>
                  <span>{selectedShift.minimum_skill_level}/10</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Max Capacity:</span>
                  <span>{selectedShift.max_capacity}</span>
                </div>
                <div>
                  <span className="text-gray-600">Required Staff:</span>
                  <div className="mt-1">
                    {Object.entries(selectedShift.required_staff).map(([role, count]) => (
                      <div key={role} className="flex justify-between ml-2">
                        <span className="capitalize">{role}:</span>
                        <span>{count}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Coverage Status</h4>
              {(() => {
                const coverage = getShiftCoverage(selectedShift);
                return (
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Assigned:</span>
                      <span>{coverage.assigned}/{coverage.required}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Coverage:</span>
                      <span className={coverage.isFullyCovered ? 'text-green-600' : 'text-red-600'}>
                        {Math.round(coverage.percentage)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${coverage.isFullyCovered ? 'bg-green-500' : 'bg-red-500'}`}
                        style={{ width: `${Math.min(coverage.percentage, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })()}
            </div>
          </div>
        </div>
      )}

      {/* Add/Edit Shift Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              {editingShift ? 'Edit Shift' : 'Add New Shift'}
            </h2>
            
            <form onSubmit={editingShift ? handleUpdateShift : handleAddShift} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
                  <input
                    type="date"
                    required
                    value={formData.date}
                    onChange={(e) => setFormData({...formData, date: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Shift Type</label>
                  <select
                    value={formData.shift_type}
                    onChange={(e) => setFormData({...formData, shift_type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {shiftTypes.map(type => (
                      <option key={type.value} value={type.value}>{type.label}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
                  <select
                    value={formData.department}
                    onChange={(e) => setFormData({...formData, department: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {departments.map(dept => (
                      <option key={dept.value} value={dept.value}>{dept.label}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                  <select
                    value={formData.priority}
                    onChange={(e) => setFormData({...formData, priority: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {priorities.map(priority => (
                      <option key={priority.value} value={priority.value}>{priority.label}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Start Time</label>
                  <input
                    type="time"
                    required
                    value={formData.start_time}
                    onChange={(e) => setFormData({...formData, start_time: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">End Time</label>
                  <input
                    type="time"
                    required
                    value={formData.end_time}
                    onChange={(e) => setFormData({...formData, end_time: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Min Skill Level (1-10)</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    required
                    value={formData.minimum_skill_level}
                    onChange={(e) => setFormData({...formData, minimum_skill_level: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Max Capacity</label>
                  <input
                    type="number"
                    min="1"
                    required
                    value={formData.max_capacity}
                    onChange={(e) => setFormData({...formData, max_capacity: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Required Staff</label>
                <div className="space-y-2">
                  {['doctor', 'nurse', 'technician'].map(role => (
                    <div key={role} className="flex items-center space-x-2">
                      <label className="w-24 text-sm capitalize">{role}:</label>
                      <input
                        type="number"
                        min="0"
                        value={formData.required_staff[role] || 0}
                        onChange={(e) => setFormData({
                          ...formData,
                          required_staff: {
                            ...formData.required_staff,
                            [role]: parseInt(e.target.value) || 0
                          }
                        })}
                        className="w-20 px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={closeModal}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  {editingShift ? 'Update' : 'Add'} Shift
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ShiftCalendar;