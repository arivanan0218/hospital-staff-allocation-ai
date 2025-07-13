// frontend/src/utils/helpers.js
/**
 * Utility functions for the frontend application
 */

// Format date for display
export const formatDate = (date) => {
    if (!date) return '';
    
    if (typeof date === 'string') {
      date = new Date(date);
    }
    
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };
  
  // Format time for display
  export const formatTime = (time) => {
    if (!time) return '';
    
    // Convert 24-hour format to 12-hour format
    const [hours, minutes] = time.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    
    return `${displayHour}:${minutes} ${ampm}`;
  };
  
  // Calculate duration between two times
  export const calculateDuration = (startTime, endTime) => {
    if (!startTime || !endTime) return 0;
    
    const [startHours, startMinutes] = startTime.split(':').map(Number);
    const [endHours, endMinutes] = endTime.split(':').map(Number);
    
    const startTotalMinutes = startHours * 60 + startMinutes;
    let endTotalMinutes = endHours * 60 + endMinutes;
    
    // Handle overnight shifts
    if (endTotalMinutes < startTotalMinutes) {
      endTotalMinutes += 24 * 60;
    }
    
    return (endTotalMinutes - startTotalMinutes) / 60; // Return hours
  };
  
  // Get status color class
  export const getStatusColor = (status) => {
    const colors = {
      confirmed: 'bg-green-100 text-green-800',
      pending: 'bg-yellow-100 text-yellow-800',
      rejected: 'bg-red-100 text-red-800',
      completed: 'bg-blue-100 text-blue-800'
    };
    
    return colors[status] || 'bg-gray-100 text-gray-800';
  };
  
  // Get priority color class
  export const getPriorityColor = (priority) => {
    const colors = {
      low: 'bg-gray-100 text-gray-800',
      medium: 'bg-blue-100 text-blue-800',
      high: 'bg-yellow-100 text-yellow-800',
      critical: 'bg-red-100 text-red-800'
    };
    
    return colors[priority] || 'bg-gray-100 text-gray-800';
  };
  
  // Capitalize first letter
  export const capitalize = (str) => {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
  };
  
  // Generate random color for avatars
  export const generateAvatarColor = (name) => {
    const colors = [
      'bg-red-500', 'bg-yellow-500', 'bg-green-500', 'bg-blue-500',
      'bg-indigo-500', 'bg-purple-500', 'bg-pink-500', 'bg-gray-500'
    ];
    
    let hash = 0;
    for (let i = 0; i < name.length; i++) {
      hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }
    
    return colors[Math.abs(hash) % colors.length];
  };
  
  // Format currency
  export const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };
  
  // Calculate confidence level text
  export const getConfidenceLevel = (score) => {
    if (score >= 0.9) return 'Very High';
    if (score >= 0.8) return 'High';
    if (score >= 0.7) return 'Medium';
    if (score >= 0.6) return 'Low';
    return 'Very Low';
  };
  
  // Debounce function
  export const debounce = (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  };
  
  // Deep clone object
  export const deepClone = (obj) => {
    return JSON.parse(JSON.stringify(obj));
  };
  
  // Check if object is empty
  export const isEmpty = (obj) => {
    return Object.keys(obj).length === 0;
  };
  
  // Group array by key
  export const groupBy = (array, key) => {
    return array.reduce((result, item) => {
      const group = item[key];
      if (!result[group]) {
        result[group] = [];
      }
      result[group].push(item);
      return result;
    }, {});
  };
  
  // Sort array by multiple criteria
  export const multiSort = (array, ...criteria) => {
    return array.sort((a, b) => {
      for (const criterion of criteria) {
        const { key, direction = 'asc' } = criterion;
        const aVal = a[key];
        const bVal = b[key];
        
        if (aVal < bVal) return direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return direction === 'asc' ? 1 : -1;
      }
      return 0;
    });
  };
  
  // Validate email
  export const isValidEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };
  
  // Generate unique ID
  export const generateId = () => {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  };
  
  // Get today's date in YYYY-MM-DD format
  export const getTodayDate = () => {
    return new Date().toISOString().split('T')[0];
  };
  
  // Add days to date
  export const addDays = (date, days) => {
    const result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
  };
  
  // Get week range
  export const getWeekRange = (date) => {
    const start = new Date(date);
    const day = start.getDay();
    const diff = start.getDate() - day;
    
    start.setDate(diff);
    const end = new Date(start);
    end.setDate(start.getDate() + 6);
    
    return { start, end };
  };
  
  // Export all utilities
  export default {
    formatDate,
    formatTime,
    calculateDuration,
    getStatusColor,
    getPriorityColor,
    capitalize,
    generateAvatarColor,
    formatCurrency,
    getConfidenceLevel,
    debounce,
    deepClone,
    isEmpty,
    groupBy,
    multiSort,
    isValidEmail,
    generateId,
    getTodayDate,
    addDays,
    getWeekRange
  };