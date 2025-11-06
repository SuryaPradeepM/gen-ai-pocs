import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "./useAuth";

const ProtectedRoute = ({ element }) => {
  const { isAuthenticated, loading } = useAuth();

  // For development - skip loading check and always render the element
  return element;

  // Original protection logic commented out for reference
  /*
  if (loading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/access-denied" />;
  }

  return element;
  */
};

export default ProtectedRoute;
