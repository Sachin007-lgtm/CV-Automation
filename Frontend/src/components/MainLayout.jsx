import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import { Brain, Briefcase, Clock, LogOut, Users } from 'lucide-react';
import useAuth from '../hooks/useAuth';

const MainLayout = () => {
    const { user, logout } = useAuth();

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-red-50">
            <div className="absolute inset-0 bg-gradient-to-br from-red-500/5 via-transparent to-red-500/10"></div>
            <header className="relative z-10 bg-white shadow-lg border-b border-red-100 sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <Link to="/" className="flex items-center space-x-3">
                            <div className="p-2 bg-gradient-to-r from-red-500 to-red-600 rounded-lg shadow-lg">
                                <Brain className="w-6 h-6 text-white" />
                            </div>
                            <h1 className="text-2xl font-bold text-gray-800">JD-CV Matcher</h1>
                        </Link>
                        <div className="flex items-center space-x-4">
                            {user && user.role === 'admin' && (
                                <Link
                                    to="/users"
                                    className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
                                >
                                    <Users className="w-5 h-5 text-gray-600" />
                                    <span className="text-sm font-medium text-gray-700">
                                        Manage Users
                                    </span>
                                </Link>
                            )}
                            {user && (user.role === 'admin' || user.role === 'backend_team') && (
                                <Link
                                    to="/jds"
                                    className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
                                >
                                    <Briefcase className="w-5 h-5 text-gray-600" />
                                    <span className="text-sm font-medium text-gray-700">
                                        Manage JDs
                                    </span>
                                </Link>
                            )}
                            <Link
                                to="/past-analyses"
                                className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors"
                            >
                                <Clock className="w-5 h-5 text-gray-600" />
                                <span className="text-sm font-medium text-gray-700">
                                    View Past Analyses
                                </span>
                            </Link>
                            <button
                                onClick={logout}
                                className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-red-100 hover:bg-red-200 transition-colors"
                            >
                                <LogOut className="w-5 h-5 text-red-600" />
                                <span className="text-sm font-medium text-red-700">
                                    Logout
                                </span>
                            </button>
                        </div>
                    </div>
                </div>
            </header>
            <main className="relative z-10 max-w-7xl mx-auto px-6 py-8">
                <Outlet />
            </main>
        </div>
    );
};

export default MainLayout;