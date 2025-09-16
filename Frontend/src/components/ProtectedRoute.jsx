import React from 'react';
import { Navigate } from 'react-router-dom';
import useAuth from '../hooks/useAuth';

const ProtectedRoute = ({ children, adminOnly = false }) => {
    const { user, loading } = useAuth();
    const token = localStorage.getItem('token') || sessionStorage.getItem('token');

    if (loading) {
        return <div>Loading...</div>; // Or a spinner component
    }

    if (!token || !user) {
        return <Navigate to="/login" />;
    }

    if (adminOnly && user.role !== 'admin') {
        return <Navigate to="/" />;
    }

    return children;
};

export default ProtectedRoute;