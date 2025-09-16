import React from 'react';
import { Upload, FileText, CheckCircle, X } from 'lucide-react';

const UploadStep = ({ files, dragOver, handleDrop, handleDragOver, handleDragLeave, handleFileSelect, handleRemoveFile, extractJD, processing }) => (
  <div className="space-y-8">
    <div className="text-center mb-8">
      <h2 className="text-3xl font-bold text-gray-800 mb-4">Upload Your Documents</h2>
      <p className="text-gray-600 text-lg">Upload a Job Description to get started. You can upload resumes now or later.</p>
    </div>
    <div className="grid md:grid-cols-2 gap-8">
      <div className="bg-white rounded-2xl p-8 shadow-lg border border-red-100">
        <div className="text-center mb-6">
          <FileText className="w-12 h-12 text-red-500 mx-auto mb-3" />
          <h3 className="text-xl font-semibold text-gray-800 mb-2">Job Description</h3>
          <p className="text-gray-600">Upload the job posting or requirements</p>
        </div>
        <div
          className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 ${
            dragOver.jd
              ? 'border-red-400 bg-red-50'
              : files.jd
              ? 'border-green-400 bg-green-50'
              : 'border-gray-300 hover:border-red-400 hover:bg-red-50'
          }`}
          onDrop={(e) => handleDrop(e, 'jd')}
          onDragOver={(e) => handleDragOver(e, 'jd')}
          onDragLeave={(e) => handleDragLeave(e, 'jd')}
        >
          {files.jd ? (
            <div className="text-green-600">
              <CheckCircle className="w-8 h-8 mx-auto mb-2" />
              <div className="flex items-center justify-center">
                <p className="font-medium text-gray-800">{files.jd.name}</p>
                <button onClick={() => handleRemoveFile('jd')} className="ml-2 text-red-500 hover:text-red-700 p-1 rounded-full bg-red-100 hover:bg-red-200">
                  <X className="w-4 h-4" />
                </button>
              </div>
              <p className="text-sm text-gray-500 mt-1">Ready to extract</p>
            </div>
          ) : (
            <>
              <Upload className="w-8 h-8 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600 mb-2">Drop your JD here or</p>
              <input
                type="file"
                id="jd-upload"
                className="hidden"
                accept=".pdf,.doc,.docx,.txt"
                onChange={(e) => handleFileSelect(e, 'jd')}
              />
              <label
                htmlFor="jd-upload"
                className="inline-block px-4 py-2 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-lg cursor-pointer hover:from-red-600 hover:to-red-700 transition-colors duration-200 shadow-md"
              >
                Browse Files
              </label>
            </>
          )}
        </div>
      </div>
      <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-200">
        <div className="text-center mb-6">
          <FileText className="w-12 h-12 text-gray-500 mx-auto mb-3" />
          <h3 className="text-xl font-semibold text-gray-800 mb-2">Resume / CV(s)</h3>
          <p className="text-gray-600">Upload one or more candidate resumes</p>
        </div>
        <div
          className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 ${
            dragOver.cv
              ? 'border-gray-400 bg-gray-50'
              : files.cv && files.cv.length > 0
              ? 'border-green-400 bg-green-50'
              : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
          }`}
          onDrop={(e) => handleDrop(e, 'cv')}
          onDragOver={(e) => handleDragOver(e, 'cv')}
          onDragLeave={(e) => handleDragLeave(e, 'cv')}
        >
          {files.cv && files.cv.length > 0 ? (
            <div className="text-green-600">
              <CheckCircle className="w-8 h-8 mx-auto mb-2" />
              <ul className="text-gray-800">
                {files.cv.map((file, idx) => (
                  <li key={idx} className="flex items-center justify-center">
                    <span>{file.name}</span>
                    <button onClick={() => handleRemoveFile('cv', idx)} className="ml-2 text-red-500 hover:text-red-700 p-1 rounded-full bg-red-100 hover:bg-red-200">
                      <X className="w-4 h-4" />
                    </button>
                  </li>
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
                onChange={(e) => handleFileSelect(e, 'cv')}
              />
              <label
                htmlFor="cv-upload"
                className="inline-block px-4 py-2 bg-gray-600 text-white rounded-lg cursor-pointer hover:bg-gray-700 transition-colors duration-200 shadow-md"
              >
                Browse Files
              </label>
            </>
          )}
        </div>
      </div>
    </div>
    {files.jd && (
      <div className="text-center">
        <button
          onClick={extractJD}
          className="px-8 py-4 bg-gradient-to-r from-red-500 to-red-600 text-white font-semibold rounded-xl hover:from-red-600 hover:to-red-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
          disabled={processing}
        >
          <FileText className="w-5 h-5 inline mr-2" />
          {files.cv.length > 0 ? 'Extract JD & Resumes' : 'Extract JD'}
        </button>
      </div>
    )}
  </div>
);

export default UploadStep;
