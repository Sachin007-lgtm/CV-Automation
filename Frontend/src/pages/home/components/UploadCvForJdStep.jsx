import React from 'react';
import { Upload, FileText, CheckCircle } from 'lucide-react';

const UploadCvForJdStep = ({ jd, files, dragOver, handleDrop, handleDragOver, handleDragLeave, handleFileSelect, extractResumes, processing }) => (
    <div className="space-y-8">
        <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-800 mb-4">Upload CVs for: {jd.job_title}</h2>
            <p className="text-gray-600 text-lg">Upload one or more candidate resumes for this job description.</p>
        </div>
        <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-200">
            <div
                className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 ${
                    dragOver
                        ? 'border-red-400 bg-red-50'
                        : files.length > 0
                        ? 'border-green-400 bg-green-50'
                        : 'border-gray-300 hover:border-red-400 hover:bg-red-50'
                }`}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
            >
                {files.length > 0 ? (
                    <div className="text-green-600">
                        <CheckCircle className="w-8 h-8 mx-auto mb-2" />
                        <ul className="text-gray-800">
                            {files.map((file, idx) => (
                                <li key={idx}>{file.name}</li>
                            ))}
                        </ul>
                        <p className="text-sm text-gray-500 mt-1">Ready to extract</p>
                    </div>
                ) : (
                    <>
                        <Upload className="w-8 h-8 text-gray-400 mx-auto mb-3" />
                        <p className="text-gray-600 mb-2">Drop your CV(s) here or</p>
                        <input
                            type="file"
                            id="cv-upload"
                            className="hidden"
                            accept=".pdf,.doc,.docx,.txt"
                            multiple
                            onChange={handleFileSelect}
                        />
                        <label
                            htmlFor="cv-upload"
                            className="inline-block px-4 py-2 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-lg cursor-pointer hover:from-red-600 hover:to-red-700 transition-colors duration-200 shadow-md"
                        >
                            Browse Files
                        </label>
                    </>
                )}
            </div>
        </div>
        {files.length > 0 && (
            <div className="text-center">
                <button
                    onClick={extractResumes}
                    className="px-8 py-4 bg-gradient-to-r from-red-500 to-red-600 text-white font-semibold rounded-xl hover:from-red-600 hover:to-red-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
                    disabled={processing}
                >
                    <FileText className="w-5 h-5 inline mr-2" />
                    Extract Resumes
                </button>
            </div>
        )}
    </div>
);

export default UploadCvForJdStep;
