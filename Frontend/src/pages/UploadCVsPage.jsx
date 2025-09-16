import React, { useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import api from '../api';
import { UploadCloud } from 'lucide-react';

const UploadCVsPage = () => {
    const { jdId } = useParams();
    const [files, setFiles] = useState([]);
    const [dragOver, setDragOver] = useState(false);
    const [processing, setProcessing] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        setDragOver(false);
        const droppedFiles = Array.from(e.dataTransfer.files);
        setFiles(droppedFiles);
    }, []);

    const handleDragOver = useCallback((e) => {
        e.preventDefault();
        setDragOver(true);
    }, []);

    const handleDragLeave = useCallback((e) => {
        e.preventDefault();
        setDragOver(false);
    }, []);

    const handleFileSelect = (e) => {
        const selectedFiles = Array.from(e.target.files);
        setFiles(selectedFiles);
    };

    const handleUpload = async () => {
        if (files.length === 0) {
            setError('Please select at least one CV to upload.');
            return;
        }

        setProcessing(true);
        setError('');
        setSuccess('');

        const formData = new FormData();
        const jdResponse = await api.get(`/jds/${jdId}`);
        formData.append('jd_json', JSON.stringify(jdResponse.data.details));
        for (let i = 0; i < files.length; i++) {
            formData.append('resume_files', files[i]);
        }

        try {
            await api.post('/extract_resumes', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setSuccess('CVs uploaded and processed successfully!');
            setFiles([]);
        } catch (err) {
            setError('Failed to upload CVs.');
        } finally {
            setProcessing(false);
        }
    };

    return (
        <div className="container mx-auto p-8">
            <h1 className="text-3xl font-bold mb-6 text-gray-800">Upload CVs for JD: {jdId}</h1>
            <div
                className={`border-2 border-dashed rounded-lg p-8 text-center ${dragOver ? 'border-red-500 bg-red-50' : 'border-gray-300'}`}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
            >
                <UploadCloud className="w-16 h-16 mx-auto text-gray-400" />
                <p className="mt-4 text-lg text-gray-600">Drag and drop your CVs here, or click to select files.</p>
                <input
                    type="file"
                    multiple
                    className="hidden"
                    id="cv-upload"
                    onChange={handleFileSelect}
                />
                <label htmlFor="cv-upload" className="mt-4 inline-block px-6 py-2 bg-red-500 text-white rounded-lg cursor-pointer hover:bg-red-600">
                    Select Files
                </label>
                {files.length > 0 && (
                    <div className="mt-4 text-sm text-gray-500">
                        {files.length} file(s) selected: {files.map(f => f.name).join(', ')}
                    </div>
                )}
            </div>
            <div className="mt-6 text-center">
                <button
                    onClick={handleUpload}
                    disabled={processing || files.length === 0}
                    className="px-8 py-3 bg-green-500 text-white rounded-lg disabled:bg-gray-400 hover:bg-green-600"
                >
                    {processing ? 'Processing...' : 'Upload and Process CVs'}
                </button>
            </div>
            {error && <p className="mt-4 text-center text-red-500">{error}</p>}
            {success && <p className="mt-4 text-center text-green-500">{success}</p>}
        </div>
    );
};

export default UploadCVsPage;
