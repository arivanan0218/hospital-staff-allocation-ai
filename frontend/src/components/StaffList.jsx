// frontend/src/components/StaffList.jsx

import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Search, 
  Filter, 
  Edit2, 
  Trash2, 
  Star, 
  Clock, 
  DollarSign,
  Building,
  UserCheck,
  AlertCircle
} from 'lucide-react';
import toast from 'react-hot-toast';

import { staffAPI } from '../services/api';
import LoadingSpinner from './LoadingSpinner';

const StaffList = () => {
  const [staff, setStaff] = useState([]);
  const [filteredStaff, setFilteredStaff] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDepartment, setSelectedDepartment] = useState('');
  const [selectedRole, setSelectedRole] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingStaff, setEditingStaff] = useState(null);
  const [staffAnalysis, setStaffAnalysis] = useState(null);

  // Form state for adding/editing staff
  const [formData, setFormData] = useState({
    name: '',
    role: 'nurse',
    department: 'general',
    skill_level: 5,
    max_hours_per_week: 40,
    preferred_shifts: [],
    unavailable_dates: [],
    certification_level: 'basic',
    experience_years: 0,
    hourly_rate: 25.0
  });

  const roles = [
    { value: 'doctor', label: 'Doctor' },
    { value: 'nurse', label: 'Nurse' },
    { value: 'technician', label: 'Technician' },
    { value: 'administrative', label: 'Administrative' },
    { value: 'support', label: 'Support' }
  ];

  const departments = [
    { value: 'emergency', label: 'Emergency' },
    { value: 'icu', label: 'ICU' },
    { value: 'surgery', label: 'Surgery' },
    { value: 'pediatrics', label: 'Pediatrics' },
    { value: 'cardiology', label: 'Cardiology' },
    { value: 'general', label: 'General' }
  ];

  const shiftTypes = ['morning', 'afternoon', 'evening', 'night'];

  useEffect(() => {
    loadStaff();
    loadStaffAnalysis();
  }, []);

  useEffect(() => {
    filterStaff();
  }, [staff, searchTerm, selectedDepartment, selectedRole]);

  const loadStaff = async () => {
    try {
      const response = await staffAPI.getAll();
      setStaff(response.data);
    } catch (error) {
      console.error('Error loading staff:', error);
      toast.error('Failed to load staff data');
    } finally {
      setIsLoading(false);
    }
  };

  const loadStaffAnalysis = async () => {
    try {
      const response = await staffAPI.getSkillsAnalysis();
      setStaffAnalysis(response.data);
    } catch (error) {
      console.error('Error loading staff analysis:', error);
    }
  };

  const filterStaff = () => {
    let filtered = staff;

    if (searchTerm) {
      filtered = filtered.filter(member =>
        member.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        member.role.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (selectedDepartment) {
      filtered = filtered.filter(member => member.department === selectedDepartment);
    }

    if (selectedRole) {
      filtered = filtered.filter(member => member.role === selectedRole);
    }

    setFilteredStaff(filtered);
  };

  const handleAddStaff = async (e) => {
    e.preventDefault();
    try {
      await staffAPI.create(formData);
      toast.success('Staff member added successfully!');
      setShowAddModal(false);
      resetForm();
      loadStaff();
      loadStaffAnalysis();
    } catch (error) {
      console.error('Error adding staff:', error);
      toast.error('Failed to add staff member');
    }
  };

  const handleUpdateStaff = async (e) => {
    e.preventDefault();
    try {
      await staffAPI.update(editingStaff.id, formData);
      toast.success('Staff member updated successfully!');
      setEditingStaff(null);
      resetForm();
      loadStaff();
      loadStaffAnalysis();
    } catch (error) {
      console.error('Error updating staff:', error);
      toast.error('Failed to update staff member');
    }
  };

  const handleDeleteStaff = async (staffId, staffName) => {
    if (window.confirm(`Are you sure you want to delete ${staffName}?`)) {
      try {
        await staffAPI.delete(staffId);
        toast.success('Staff member deleted successfully!');
        loadStaff();
        loadStaffAnalysis();
      } catch (error) {
        console.error('Error deleting staff:', error);
        toast.error('Failed to delete staff member');
      }
    }
  };

  const startEditing = (staffMember) => {
    setEditingStaff(staffMember);
    setFormData({
      name: staffMember.name,
      role: staffMember.role,
      department: staffMember.department,
      skill_level: staffMember.skill_level,
      max_hours_per_week: staffMember.max_hours_per_week,
      preferred_shifts: staffMember.preferred_shifts || [],
      unavailable_dates: staffMember.unavailable_dates || [],
      certification_level: staffMember.certification_level,
      experience_years: staffMember.experience_years,
      hourly_rate: staffMember.hourly_rate
    });
    setShowAddModal(true);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      role: 'nurse',
      department: 'general',
      skill_level: 5,
      max_hours_per_week: 40,
      preferred_shifts: [],
      unavailable_dates: [],
      certification_level: 'basic',
      experience_years: 0,
      hourly_rate: 25.0
    });
  };

  const closeModal = () => {
    setShowAddModal(false);
    setEditingStaff(null);
    resetForm();
  };

  const handleShiftPreferenceChange = (shiftType) => {
    const currentPreferences = formData.preferred_shifts;
    if (currentPreferences.includes(shiftType)) {
      setFormData({
        ...formData,
        preferred_shifts: currentPreferences.filter(s => s !== shiftType)
      });
    } else {
      setFormData({
        ...formData,
        preferred_shifts: [...currentPreferences, shiftType]
      });
    }
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
          <h1 className="text-3xl font-bold text-gray-900">Staff Management</h1>
          <p className="text-gray-600">Manage hospital staff members and their details</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus size={20} />
          <span className="ml-2">Add Staff</span>
        </button>
      </div>

      {/* Staff Analysis Summary */}
      {staffAnalysis && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Staff</p>
                <p className="text-2xl font-bold text-gray-900">{staffAnalysis.total_staff}</p>
              </div>
              <UserCheck className="w-8 h-8 text-blue-600" />
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Skill Level</p>
                <p className="text-2xl font-bold text-gray-900">{staffAnalysis.average_skill_level?.toFixed(1)}</p>
              </div>
              <Star className="w-8 h-8 text-yellow-600" />
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Experience</p>
                <p className="text-2xl font-bold text-gray-900">{staffAnalysis.average_experience?.toFixed(1)}y</p>
              </div>
              <Clock className="w-8 h-8 text-green-600" />
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Skill Gaps</p>
                <p className="text-2xl font-bold text-gray-900">{staffAnalysis.skill_gaps?.length || 0}</p>
              </div>
              <AlertCircle className="w-8 h-8 text-red-600" />
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-64">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Search staff by name or role..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <select
            value={selectedDepartment}
            onChange={(e) => setSelectedDepartment(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Departments</option>
            {departments.map(dept => (
              <option key={dept.value} value={dept.value}>{dept.label}</option>
            ))}
          </select>
          <select
            value={selectedRole}
            onChange={(e) => setSelectedRole(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Roles</option>
            {roles.map(role => (
              <option key={role.value} value={role.value}>{role.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Staff List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Staff Member
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role & Department
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Skills & Experience
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Availability
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rate
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredStaff.map((member) => (
                <tr key={member.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-blue-600 font-medium">
                          {member.name.split(' ').map(n => n[0]).join('')}
                        </span>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">{member.name}</div>
                        <div className="text-sm text-gray-500">ID: {member.id}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900 capitalize">{member.role}</div>
                    <div className="text-sm text-gray-500 capitalize flex items-center">
                      <Building size={14} className="mr-1" />
                      {member.department}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      <div className="flex items-center">
                        <Star size={14} className="text-yellow-500 mr-1" />
                        <span className="text-sm text-gray-900">{member.skill_level}/10</span>
                      </div>
                      <div className="text-sm text-gray-500">
                        {member.experience_years}y exp
                      </div>
                    </div>
                    <div className="text-xs text-gray-500 capitalize">
                      {member.certification_level}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{member.max_hours_per_week}h/week</div>
                    <div className="text-xs text-gray-500">
                      {member.preferred_shifts?.length > 0 
                        ? member.preferred_shifts.join(', ') 
                        : 'No preferences'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center text-sm text-gray-900">
                      <DollarSign size={14} />
                      {member.hourly_rate}/hr
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => startEditing(member)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        <Edit2 size={16} />
                      </button>
                      <button
                        onClick={() => handleDeleteStaff(member.id, member.name)}
                        className="text-red-600 hover:text-red-900"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add/Edit Staff Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              {editingStaff ? 'Edit Staff Member' : 'Add New Staff Member'}
            </h2>
            
            <form onSubmit={editingStaff ? handleUpdateStaff : handleAddStaff} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                  <select
                    value={formData.role}
                    onChange={(e) => setFormData({...formData, role: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {roles.map(role => (
                      <option key={role.value} value={role.value}>{role.label}</option>
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
                  <label className="block text-sm font-medium text-gray-700 mb-1">Skill Level (1-10)</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    required
                    value={formData.skill_level}
                    onChange={(e) => setFormData({...formData, skill_level: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Max Hours/Week</label>
                  <input
                    type="number"
                    min="20"
                    max="60"
                    required
                    value={formData.max_hours_per_week}
                    onChange={(e) => setFormData({...formData, max_hours_per_week: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Experience (Years)</label>
                  <input
                    type="number"
                    min="0"
                    required
                    value={formData.experience_years}
                    onChange={(e) => setFormData({...formData, experience_years: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Hourly Rate ($)</label>
                  <input
                    type="number"
                    step="0.50"
                    min="15"
                    required
                    value={formData.hourly_rate}
                    onChange={(e) => setFormData({...formData, hourly_rate: parseFloat(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Certification Level</label>
                  <select
                    value={formData.certification_level}
                    onChange={(e) => setFormData({...formData, certification_level: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="basic">Basic</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                    <option value="expert">Expert</option>
                  </select>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Preferred Shifts</label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {shiftTypes.map(shift => (
                    <label key={shift} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={formData.preferred_shifts.includes(shift)}
                        onChange={() => handleShiftPreferenceChange(shift)}
                        className="mr-2"
                      />
                      <span className="text-sm capitalize">{shift}</span>
                    </label>
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
                  {editingStaff ? 'Update' : 'Add'} Staff
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default StaffList;