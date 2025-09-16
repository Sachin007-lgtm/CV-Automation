import React, { useState, useEffect } from 'react';
import api from '../../../api';
import useAuth from '../../../hooks/useAuth';

const PastAnalyses = () => {
    const { user } = useAuth();
    const [analyses, setAnalyses] = useState([]);
    const [loading, setLoading] = useState(true); // Start with true since we're loading data
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchAnalyses = async () => {
            setLoading(true);
            try {
                const res = await api.get(`/analyses`);
                setAnalyses(res.data);
            } catch (err) {
                setError('Failed to fetch past analyses.');
                console.error('Error fetching analyses:', err); // Add error logging
            }
            setLoading(false);
        };

        if (user) {
            fetchAnalyses();
        } else {
            setLoading(false); // If no user, stop loading
        }
    }, [user]);

    if (loading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div className="text-red-500">{error}</div>;
    }

    // Add a safety check for analyses data
    if (!analyses || !Array.isArray(analyses)) {
        return <div className="text-red-500">Error: Invalid data format received.</div>;
    }

    return (
        <div className="space-y-8">
            <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-800 mb-4">Past Analyses</h2>
                <p className="text-gray-600 text-lg">Review candidates you have uploaded.</p>
            </div>

            {analyses.length > 0 ? (
                <div className="max-w-7xl mx-auto">
                    <div className="overflow-x-auto rounded-2xl shadow-lg">
                        <table className="min-w-full bg-white rounded-2xl overflow-hidden">
                            <thead>
                                <tr className="bg-red-100 text-gray-800 text-sm">
                                    <th className="px-4 py-2 text-left">Recruiter Name</th>
                                    <th className="px-4 py-2 text-left">Candidate Name</th>
                                    <th className="px-4 py-2 text-left">Date Uploaded</th>
                                    <th className="px-4 py-2 text-left">Candidate Mobile</th>
                                    <th className="px-4 py-2 text-left">Assessment Result</th>
                                </tr>
                            </thead>
                            <tbody>
                                {analyses.map((analysis, idx) => {
                                    // Add safety checks for analysis data
                                    if (!analysis || !analysis.candidate) {
                                        return (
                                            <tr key={idx} className="border-t hover:bg-red-50 text-sm">
                                                <td colSpan="5" className="px-4 py-2 text-red-500">
                                                    Error: Incomplete data for analysis #{idx}
                                                </td>
                                            </tr>
                                        );
                                    }
                                    
                                    return (
                                        <tr key={idx} className="border-t hover:bg-red-50 text-sm">
                                            <td className="px-4 py-2 whitespace-nowrap">{user.username}</td>
                                            <td className="px-4 py-2 font-semibold whitespace-nowrap">{analysis.candidate.name || 'N/A'}</td>
                                            <td className="px-4 py-2 whitespace-nowrap">
                                                {analysis.candidate.uploaded_at 
                                                    ? new Date(analysis.candidate.uploaded_at).toLocaleDateString()
                                                    : 'N/A'}
                                            </td>
                                            <td className="px-4 py-2 whitespace-nowrap">{analysis.candidate.phone || 'N/A'}</td>
                                            <td className="px-4 py-2 whitespace-nowrap">
                                                {analysis.score !== undefined && analysis.score !== null 
                                                    ? `${analysis.score.toFixed(2)}%` 
                                                    : 'N/A'}
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>
            ) : (
                <p className="text-center text-gray-500">No past analyses found.</p>
            )}
        </div>
    );
};

export default PastAnalyses;
