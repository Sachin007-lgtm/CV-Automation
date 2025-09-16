import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../api';
import JdFormEditor from '../components/JdFormEditor';
import ProcessingLoader from '../components/ui/ProcessingLoader';

const JDDetailPage = () => {
    const { jdId } = useParams();
    const [jd, setJd] = useState(null);
    const [analyses, setAnalyses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchJdDetails = async () => {
            try {
                setLoading(true);
                const jdResponse = await api.get(`/jds/${jdId}`);
                setJd(jdResponse.data);
                const analysesResponse = await api.get(`/jds/${jdId}/results`);
                setAnalyses(analysesResponse.data);
            } catch (err) {
                setError('Failed to fetch job description details.');
            } finally {
                setLoading(false);
            }
        };
        fetchJdDetails();
    }, [jdId]);

    const handleUpdateJd = async (updatedJdDetails) => {
        try {
            setLoading(true);
            const payload = { details: updatedJdDetails };
            const response = await api.put(`/jds/${jdId}`, payload);
            setJd(response.data);
            alert('Job Description updated successfully!');
        } catch (err) {
            setError('Failed to update job description.');
            alert('Error: ' + (err.response?.data?.detail || err.message));
        } finally {
            setLoading(false);
        }
    };

    if (loading && !jd) {
        return <ProcessingLoader />;
    }

    if (error) {
        return <div className="text-center p-8 text-red-500">{error}</div>;
    }

    return (
        <div className="container mx-auto p-8">
            <h1 className="text-3xl font-bold mb-6 text-gray-800">Edit Job Description</h1>
            {jd && (
                <div className="bg-white p-6 rounded-lg shadow-md mb-8">
                    <JdFormEditor jdData={jd.details} onUpdate={(newDetails) => setJd(prev => ({...prev, details: newDetails}))} />
                    <div className="text-right mt-4">
                        <button
                            onClick={() => handleUpdateJd(jd.details)}
                            className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
                            disabled={loading}
                        >
                            {loading ? 'Saving...' : 'Save Changes'}
                        </button>
                    </div>
                </div>
            )}

            <h2 className="text-2xl font-bold mb-4 text-gray-800">Analyses for this JD</h2>
            <div className="bg-white shadow-lg rounded-lg">
                <ul className="divide-y divide-gray-200">
                    {analyses.length > 0 ? analyses.map((analysis) => (
                        <li key={analysis.id} className="p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-lg font-semibold">{analysis.candidate.name}</p>
                                    <p className="text-sm text-gray-600">{analysis.candidate.email}</p>
                                </div>
                                <div className="text-right">
                                    <p className="text-xl font-bold text-red-500">{analysis.score?.toFixed(2)}%</p>
                                    <p className="text-md text-gray-500">{analysis.match_level}</p>
                                </div>
                            </div>
                        </li>
                    )) : (
                        <li className="p-6 text-center text-gray-500">No analyses found for this job description.</li>
                    )}
                </ul>
            </div>
        </div>
    );
};

export default JDDetailPage;
