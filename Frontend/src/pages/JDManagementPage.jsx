import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../api';

const JDManagementPage = () => {
    const [jds, setJds] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState('All');
    const [editingJd, setEditingJd] = useState(null);
    const [newStatus, setNewStatus] = useState('');

    useEffect(() => {
        fetchJds();
    }, []);

    const fetchJds = async () => {
        try {
            setLoading(true);
            const response = await api.get('/jds');
            setJds(response.data);
        } catch (err) {
            setError('Failed to fetch job descriptions.');
        } finally {
            setLoading(false);
        }
    };

    const handleUpdateStatus = async (jdId) => {
        try {
            await api.patch(`/jds/${jdId}`, { status: newStatus });
            setEditingJd(null);
            fetchJds(); // Refetch to get the updated list
        } catch (err) {
            setError('Failed to update job description.');
        }
    };

    const filteredJds = jds.filter(jd => {
        const matchesSearch = jd.job_title.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesStatus = statusFilter === 'All' || jd.status === statusFilter;
        return matchesSearch && matchesStatus;
    });

    if (loading && jds.length === 0) {
        return <div className="text-center p-8">Loading...</div>;
    }

    if (error) {
        return <div className="text-center p-8 text-red-500">{error}</div>;
    }

    return (
        <div className="container mx-auto p-8">
            <h1 className="text-3xl font-bold mb-6 text-gray-800">Job Description Management</h1>
            
            <div className="mb-6 flex items-center space-x-4">
                <input
                    type="text"
                    placeholder="Search by position name..."
                    className="w-full p-2 border border-gray-300 rounded-lg"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                />
                <select
                    className="p-2 border border-gray-300 rounded-lg"
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                >
                    <option value="All">All Statuses</option>
                    <option value="Active">Active</option>
                    <option value="Hold">Hold</option>
                    <option value="Not Active">Not Active</option>
                </select>
            </div>

            <div className="bg-white shadow-lg rounded-lg">
                <ul className="divide-y divide-gray-200">
                    {filteredJds.length > 0 ? filteredJds.map((jd) => (
                        <li key={jd.id} className="p-6 hover:bg-gray-50 transition-colors">
                            <div className="flex items-center justify-between">
                                <div className="flex-grow">
                                    <p className="text-xl font-semibold text-gray-900">{jd.job_title}</p>
                                    <p className="text-md text-gray-600">{jd.company_name}</p>
                                    <p className="text-sm text-gray-500 mt-1">{jd.location}</p>
                                </div>
                                <div className="text-right flex-shrink-0 ml-6">
                                    <p className="text-md text-gray-700">CTC: {jd.ctc || 'N/A'}</p>
                                    {editingJd === jd.id ? (
                                        <div className="flex items-center space-x-2">
                                            <select
                                                value={newStatus}
                                                onChange={(e) => setNewStatus(e.target.value)}
                                                className="p-1 border border-gray-300 rounded-lg"
                                            >
                                                <option value="Active">Active</option>
                                                <option value="Hold">Hold</option>
                                                <option value="Not Active">Not Active</option>
                                            </select>
                                            <button
                                                onClick={() => handleUpdateStatus(jd.id)}
                                                className="px-3 py-1 bg-green-500 text-white rounded-lg hover:bg-green-600"
                                            >
                                                Save
                                            </button>
                                            <button
                                                onClick={() => setEditingJd(null)}
                                                className="px-3 py-1 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
                                            >
                                                Cancel
                                            </button>
                                        </div>
                                    ) : (
                                        <div className="flex items-center justify-end space-x-2">
                                            <p className={`text-md font-medium ${
                                                jd.status === 'Active' ? 'text-green-500' :
                                                jd.status === 'Hold' ? 'text-yellow-500' : 'text-red-500'
                                            }`}>
                                                {jd.status}
                                            </p>
                                            <button
                                                onClick={() => {
                                                    setEditingJd(jd.id);
                                                    setNewStatus(jd.status);
                                                }}
                                                className="px-3 py-1 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                                            >
                                                Edit Status
                                            </button>
                                            <Link to={`/jds/${jd.id}/edit`} className="px-3 py-1 bg-gray-500 text-white rounded-lg hover:bg-gray-600">
                                                Edit JD
                                            </Link>
                                            <Link to={`/jds/${jd.id}/analyses`} className="px-3 py-1 bg-purple-500 text-white rounded-lg hover:bg-purple-600">
                                                View Analyses
                                            </Link>
                                        </div>
                                    )}
                                    <p className="text-sm text-gray-500 mt-1">
                                        Created: {new Date(jd.created_at).toLocaleDateString()}
                                    </p>
                                </div>
                            </div>
                        </li>
                    )) : (
                        <li className="p-6 text-center text-gray-500">No job descriptions found.</li>
                    )}
                </ul>
            </div>
        </div>
    );
};

export default JDManagementPage;
