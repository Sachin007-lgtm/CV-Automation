import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../api';
import JdFormEditor from '../components/JdFormEditor';
import ProcessingLoader from '../components/ui/ProcessingLoader';

const JDEditPage = () => {
    const { jdId } = useParams();
    const [jd, setJd] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchJdDetails = async () => {
            try {
                setLoading(true);
                const jdResponse = await api.get(`/jds/${jdId}`);
                setJd(jdResponse.data);
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
        </div>
    );
};

export default JDEditPage;
