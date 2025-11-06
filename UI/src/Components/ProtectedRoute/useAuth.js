import { useState, useEffect } from 'react';
import axios from 'axios';

export const useAuth = () => {
  // For development - always return authenticated
  return {
    isAuthenticated: true,
    userRoles: ['admin'], // Add any roles needed
    loading: false
  };

  // Original authentication logic commented out for reference
  /*
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userRoles, setUserRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // ... rest of original authentication logic ...
  */
};

export default useAuth;