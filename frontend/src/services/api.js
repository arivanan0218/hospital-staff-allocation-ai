// frontend/src/services/api.js

import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Staff API endpoints
export const staffAPI = {
  // Get all staff
  getAll: () => api.get('/staff/'),
  
  // Get staff by ID
  getById: (staffId) => api.get(`/staff/${staffId}`),
  
  // Create new staff
  create: (staffData) => api.post('/staff/', staffData),
  
  // Update staff
  update: (staffId, staffData) => api.put(`/staff/${staffId}`, staffData),
  
  // Delete staff
  delete: (staffId) => api.delete(`/staff/${staffId}`),
  
  // Get staff by department
  getByDepartment: (department) => api.get(`/staff/department/${department}`),
  
  // Get staff by role
  getByRole: (role) => api.get(`/staff/role/${role}`),
  
  // Get available staff
  getAvailable: (date, department = null) => {
    const params = department ? `?department=${department}` : '';
    return api.get(`/staff/available/${date}${params}`);
  },
  
  // Get skills analysis
  getSkillsAnalysis: (department = null) => {
    const params = department ? `?department=${department}` : '';
    return api.get(`/staff/analysis/skills${params}`);
  },
  
  // Get workload analysis
  getWorkloadAnalysis: (staffId = null, dateRange = null) => {
    const params = new URLSearchParams();
    if (staffId) params.append('staff_id', staffId);
    if (dateRange) params.append('date_range', dateRange);
    const queryString = params.toString();
    return api.get(`/staff/analysis/workload${queryString ? '?' + queryString : ''}`);
  },
  
  // Get staff suggestions for shift
  getSuggestionsForShift: (shiftId) => api.get(`/staff/suggestions/shift/${shiftId}`)
};

// Shifts API endpoints
export const shiftsAPI = {
  // Get all shifts
  getAll: () => api.get('/shifts/'),
  
  // Get shift by ID
  getById: (shiftId) => api.get(`/shifts/${shiftId}`),
  
  // Create new shift
  create: (shiftData) => api.post('/shifts/', shiftData),
  
  // Update shift
  update: (shiftId, shiftData) => api.put(`/shifts/${shiftId}`, shiftData),
  
  // Delete shift
  delete: (shiftId) => api.delete(`/shifts/${shiftId}`),
  
  // Get shifts by date
  getByDate: (date) => api.get(`/shifts/date/${date}`),
  
  // Get shifts by department
  getByDepartment: (department) => api.get(`/shifts/department/${department}`),
  
  // Search shifts
  search: (filters) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.append(key, value);
    });
    const queryString = params.toString();
    return api.get(`/shifts/search/${queryString ? '?' + queryString : ''}`);
  },
  
  // Get shift requirements
  getRequirements: (shiftId) => api.get(`/shifts/${shiftId}/requirements`),
  
  // Get coverage analytics
  getCoverageAnalytics: (startDate = null, endDate = null) => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const queryString = params.toString();
    return api.get(`/shifts/analytics/coverage${queryString ? '?' + queryString : ''}`);
  }
};

// Allocations API endpoints
export const allocationsAPI = {
  // Get all allocations
  getAll: () => api.get('/allocations/'),
  
  // Get allocation by ID
  getById: (allocationId) => api.get(`/allocations/${allocationId}`),
  
  // Create allocation manually
  create: (staffId, shiftId, confidenceScore = 0.5, reasoning = 'Manual allocation') => {
    return api.post('/allocations/create', null, {
      params: { staff_id: staffId, shift_id: shiftId, confidence_score: confidenceScore, reasoning }
    });
  },
  
  // Auto-allocate shifts
  autoAllocate: (allocationRequest) => api.post('/allocations/auto-allocate', allocationRequest),
  
  // Get allocations by staff
  getByStaff: (staffId) => api.get(`/allocations/staff/${staffId}`),
  
  // Get allocations by shift
  getByShift: (shiftId) => api.get(`/allocations/shift/${shiftId}`),
  
  // Get allocations by date
  getByDate: (date) => api.get(`/allocations/date/${date}`),
  
  // Update allocation status
  updateStatus: (allocationId, status) => api.put(`/allocations/${allocationId}/status`, null, {
    params: { status }
  }),
  
  // Delete allocation
  delete: (allocationId) => api.delete(`/allocations/${allocationId}`),
  
  // Get allocation summary
  getSummary: (dateRange) => api.get(`/allocations/summary/${dateRange}`),
  
  // Validate allocation
  validate: (allocationId) => api.get(`/allocations/${allocationId}/validate`),
  
  // Get alternative allocations
  getAlternatives: (shiftId, excludeStaff = []) => {
    const params = excludeStaff.length > 0 ? `?exclude_staff=${excludeStaff.join(',')}` : '';
    return api.get(`/allocations/alternatives/shift/${shiftId}${params}`);
  },
  
  // Optimize allocations
  optimize: (dateRange, strategy = 'balance', constraints = null) => {
    return api.post('/allocations/optimize', constraints, {
      params: { date_range: dateRange, strategy }
    });
  },
  
  // Get conflict analysis
  getConflicts: (dateRange) => api.get(`/allocations/conflicts/${dateRange}`),
  
  // Get utilization analytics
  getUtilizationAnalytics: () => api.get('/allocations/analytics/utilization'),
  
  // Create batch allocations
  createBatch: (allocationsData) => api.post('/allocations/batch-create', allocationsData)
};

// System API endpoints
export const systemAPI = {
  // Health check
  healthCheck: () => api.get('/health', { baseURL: 'http://localhost:8000' }),
  
  // Get API info
  getApiInfo: () => api.get('/info', { baseURL: 'http://localhost:8000/api' }),
  
  // Get system statistics
  getStats: () => api.get('/stats', { baseURL: 'http://localhost:8000/api' }),
  
  // Reset demo data
  resetDemoData: () => api.post('/demo/reset', {}, { baseURL: 'http://localhost:8000/api' })
};

// Utility functions
export const apiUtils = {
  // Handle API errors
  handleError: (error) => {
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      return {
        status,
        message: data.message || data.detail || 'An error occurred',
        details: data
      };
    } else if (error.request) {
      // Request made but no response
      return {
        status: 0,
        message: 'Network error - unable to connect to server',
        details: error.request
      };
    } else {
      // Something else happened
      return {
        status: -1,
        message: error.message || 'An unexpected error occurred',
        details: error
      };
    }
  },
  
  // Format date for API
  formatDate: (date) => {
    if (date instanceof Date) {
      return date.toISOString().split('T')[0];
    }
    return date;
  },
  
  // Create date range string
  createDateRange: (startDate, endDate) => {
    const start = apiUtils.formatDate(startDate);
    const end = apiUtils.formatDate(endDate);
    return start === end ? start : `${start} to ${end}`;
  }
};

export default api;