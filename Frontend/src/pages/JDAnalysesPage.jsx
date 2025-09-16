import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../api';
import ProcessingLoader from '../components/ui/ProcessingLoader';

const JDAnalysesPage = () => {
    const { jdId } = useParams();
    const [analyses, setAnalyses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchAnalyses = async () => {
            try {
                setLoading(true);
                const analysesResponse = await api.get(`/jds/${jdId}/results`);
                setAnalyses(analysesResponse.data);
            } catch (err) {
                setError('Failed to fetch analyses.');
            } finally {
                setLoading(false);
            }
        };
        fetchAnalyses();
    }, [jdId]);

    if (loading) {
        return <ProcessingLoader />;
    }

    if (error) {
        return <div className="text-center p-8 text-red-500">{error}</div>;
    }

    return (
        <div className="container mx-auto p-8">
            <h1 className="text-3xl font-bold mb-6 text-gray-800">Analyses for JD: Page {jdId}</h1>
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

export default JDAnalysesPage;
