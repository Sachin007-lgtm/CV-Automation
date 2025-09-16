import React from 'react';
import { Upload, FileText, Brain, BarChart3, CheckCircle, Edit3, ArrowLeft } from 'lucide-react';

const Stepper = ({ step, onBack }) => (
  <div className="mb-12 flex items-center justify-between">
    {step > 1 ? (
      <button onClick={onBack} className="p-2 rounded-full bg-gray-200 hover:bg-gray-300">
        <ArrowLeft className="w-6 h-6" />
      </button>
    ) : (
      <div className="w-10 h-10" /> // Placeholder to keep alignment
    )}
    <div className="flex items-center justify-center space-x-8">
      {[
        { num: 1, label: 'Upload Files', icon: Upload },
        { num: 2, label: 'Extract JD', icon: FileText },
        { num: 3, label: 'Review JD & Categorize Skills', icon: Edit3 },
        { num: 4, label: 'Extract Resumes', icon: FileText },
        { num: 5, label: 'Match', icon: Brain },
        { num: 6, label: 'Results', icon: BarChart3 }
      ].map(({ num, label, icon: Icon }) => (
        <div key={num} className="flex items-center space-x-3">
          <div className={`w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300 ${
            step >= num
              ? 'bg-gradient-to-r from-red-500 to-red-600 text-white shadow-lg scale-110' 
              : 'bg-gray-200 text-gray-500'
          }`}>
            {step > num ? <CheckCircle className="w-6 h-6" /> : <Icon className="w-6 h-6" />}
          </div>
          <span className={`text-sm font-medium ${
            step >= num ? 'text-gray-800' : 'text-gray-500'
          }`}>{label}</span>
        </div>
      ))}
    </div>
    <div className="w-10 h-10" />
  </div>
);

export default Stepper;