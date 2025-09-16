import React from 'react';
import { Brain, Edit3 } from 'lucide-react';
import SkillBadge from '../../../components/ui/SkillBadge';

const ReviewResumesStep = ({ cvExtractionResults, setEditingCvIndex, matchResults, resetApp, processing }) => (
  <div className="space-y-8">
    <div className="text-center mb-8">
      <h2 className="text-3xl font-bold text-gray-800 mb-4">Resumes Extracted</h2>
      <p className="text-gray-600 text-lg">Review extracted CVs and skill presence. Proceed to match.</p>
    </div>
    <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-200">
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white rounded-2xl shadow-lg overflow-hidden">
          <thead>
            <tr className="bg-red-100 text-gray-800">
              <th className="px-4 py-2 text-left">Candidate</th>
              <th className="px-4 py-2 text-left">Skill Presence</th>
              <th className="px-4 py-2 text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {cvExtractionResults.map((cv, idx) => (
              <tr key={idx} className="border-t hover:bg-red-50">
                <td className="px-4 py-2 font-semibold">{cv.cv_json["Personal Data"]?.firstName} {cv.cv_json["Personal Data"]?.lastName}</td>
                <td className="px-4 py-2">
                  {Object.keys(cv.skill_presence || {}).length > 0 ? (
                    Object.entries(cv.skill_presence || {}).map(([skill, isPresent], i) => (
                      <SkillBadge key={i} text={skill} type={isPresent ? "present" : "absent"} />
                    ))
                  ) : (
                    <span className="text-gray-400 text-sm">No skills analyzed</span>
                  )}
                </td>
                <td className="px-4 py-2">
                    <button
                        onClick={() => setEditingCvIndex(idx)}
                        className="flex items-center px-3 py-1 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                    >
                        <Edit3 className="w-4 h-4 mr-1" />
                        Edit
                    </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
    <div className="text-center flex gap-4 justify-center">
      <button
        onClick={matchResults}
        disabled={processing}
        className="px-8 py-4 bg-gradient-to-r from-red-500 to-red-600 text-white font-semibold rounded-xl hover:from-red-600 hover:to-red-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
      >
        <Brain className="w-5 h-5 inline mr-2" />
        Run Matching
      </button>
      <button
        onClick={resetApp}
        className="px-8 py-4 bg-gray-200 text-gray-700 font-semibold rounded-xl hover:bg-gray-300 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
      >
        Reset
      </button>
    </div>
  </div>
);

export default ReviewResumesStep;
