import React from 'react';

const SelectJdStep = ({ jds, onSelectJd, processing }) => {
    if (jds.length === 0) {
        return <div className="text-center p-8">No Job Descriptions available. Please contact the backend team.</div>;
    }

    return (
        <div className="container mx-auto p-8">
            <h1 className="text-3xl font-bold mb-6 text-gray-800">Select a Job Description</h1>
            <p className="text-gray-600 text-lg mb-8 text-center">Choose a JD to upload CVs against.</p>
            
            <div className="bg-white shadow-lg rounded-lg">
                <ul className="divide-y divide-gray-200">
                    {jds.map((jd) => (
                        <li key={jd.id} className="p-6 hover:bg-gray-50 transition-colors">
                            <div className="flex items-center justify-between">
                                <div className="flex-grow">
                                    <p className="text-xl font-semibold text-gray-900">{jd.job_title}</p>
                                    <p className="text-md text-gray-600">{jd.company_name}</p>
                                    <p className="text-sm text-gray-500 mt-1">{jd.location}</p>
                                </div>
                                <div className="text-right flex-shrink-0 ml-6">
                                    <p className="text-md text-gray-700">CTC: {jd.ctc || 'N/A'}</p>
                                    <p className={`text-md font-medium ${
                                        jd.status === 'Active' ? 'text-green-500' :
                                        jd.status === 'Hold' ? 'text-yellow-500' : 'text-red-500'
                                    }`}>
                                        {jd.status}
                                    </p>
                                    <button
                                        onClick={() => onSelectJd(jd)}
                                        disabled={processing || jd.status !== 'Active'}
                                        className="mt-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:bg-gray-400"
                                        title={jd.status !== 'Active' ? 'This JD is not active' : 'Select this JD'}
                                    >
                                        Select and Upload CVs
                                    </button>
                                </div>
                            </div>
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default SelectJdStep;
