import React from 'react';
import { FileText, Edit3, X, Plus, SlidersHorizontal } from 'lucide-react';
import JdFormEditor from '../../../components/JdFormEditor';

const ReviewJdStep = ({
  editedJdJson,
  skillCategories,
  newSkill,
  showJsonView,
  setEditedJdJson,
  moveSkill,
  addSkill,
  removeSkill,
  setNewSkill,
  setShowJsonView,
  extractResumes,
  saveJd,
  resetApp,
  processing,
  user
}) => {
  const hasCvFiles = user?.role !== 'recruiter'; // Simplified logic, adjust as needed

  return (
  <div className="space-y-8">
    <div className="text-center mb-8">
      <h2 className="text-3xl font-bold text-gray-800 mb-4">Review & Categorize JD Skills</h2>
      <p className="text-gray-600 text-lg">Categorize required skills and edit other JD fields if needed.</p>
    </div>
    <div className="bg-white rounded-2xl p-8 shadow-lg border border-red-100">
      {/* Skill Categorization UI */}
      <div className="mb-6">
        <label className="block font-semibold mb-2 text-gray-700">Required Skills Categorization</label>
        <div className="flex flex-wrap gap-4 mb-4">
          {['critical', 'important', 'extra'].map(cat => (
            <div key={cat} className="flex-1 min-w-[180px]">
              <div className={`font-semibold mb-2 capitalize ${cat === 'critical' ? 'text-red-700' : cat === 'important' ? 'text-yellow-700' : 'text-blue-700'}`}>{cat}</div>
        <div className="flex flex-wrap gap-2 mb-2">
                {skillCategories[cat].map((skill, idx) => (
                  <span key={idx} className="inline-flex items-center bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm font-medium">
              {skill}
              <button
                className="ml-2 text-red-500 hover:text-red-700"
                      onClick={() => removeSkill(skill, cat)}
              >
                <X className="w-4 h-4" />
              </button>
                    <span className="ml-2 flex gap-1">
                      {['critical', 'important', 'extra'].filter(c => c !== cat).map(targetCat => (
                        <button
                          key={targetCat}
                          className={`text-xs px-1 py-0.5 rounded ${targetCat === 'critical' ? 'bg-red-200 text-red-700' : targetCat === 'important' ? 'bg-yellow-200 text-yellow-700' : 'bg-blue-200 text-blue-700'}`}
                          onClick={() => moveSkill(skill, cat, targetCat)}
                        >
                          {targetCat.charAt(0).toUpperCase()}
                        </button>
                      ))}
                    </span>
            </span>
          ))}
        </div>
              <div className="flex gap-2 mt-2">
          <input
            type="text"
            value={newSkill}
            onChange={e => setNewSkill(e.target.value)}
            className="border rounded px-2 py-1 text-sm"
                  placeholder={`Add to ${cat}`}
            onKeyDown={e => {
              if (e.key === 'Enter' && newSkill.trim()) {
                      addSkill(newSkill, cat);
              }
            }}
          />
          <button
            className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600"
                  onClick={() => addSkill(newSkill, cat)}
          >
            <Plus className="w-4 h-4" />
          </button>
              </div>
            </div>
          ))}
        </div>
      </div>
      {/* Collapsible advanced JSON editor */}
      {/* Weights & Rejection Rules */}
      <div className="mt-6 p-4 border rounded-lg bg-gray-50">
        <div className="flex items-center gap-2 mb-3 text-gray-800 font-semibold">
          <SlidersHorizontal className="w-4 h-4" />
          Skill Weights & Rejection Rules (optional)
        </div>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="grid grid-cols-2 gap-2 items-center">
            <label className="text-sm text-gray-700">Critical Weight</label>
            <input type="number" step="0.01" min="0" max="1"
                   className="border rounded px-2 py-1 text-sm"
                   value={(editedJdJson?.skillWeights?.critical ?? '')}
                   onChange={e => setEditedJdJson(prev => ({
                     ...prev,
                     skillWeights: { ...(prev?.skillWeights||{}), critical: Number(e.target.value) }
                   }))}
                   placeholder="Default 0.4" />
            <label className="text-sm text-gray-700">Important Weight</label>
            <input type="number" step="0.01" min="0" max="1"
                   className="border rounded px-2 py-1 text-sm"
                   value={(editedJdJson?.skillWeights?.important ?? '')}
                   onChange={e => setEditedJdJson(prev => ({
                     ...prev,
                     skillWeights: { ...(prev?.skillWeights||{}), important: Number(e.target.value) }
                   }))}
                   placeholder="Default 0.3" />
            <label className="text-sm text-gray-700">Desired Weight</label>
            <input type="number" step="0.01" min="0" max="1"
                   className="border rounded px-2 py-1 text-sm"
                   value={(editedJdJson?.skillWeights?.desired ?? '')}
                   onChange={e => setEditedJdJson(prev => ({
                     ...prev,
                     skillWeights: { ...(prev?.skillWeights||{}), desired: Number(e.target.value) }
                   }))}
                   placeholder="Default 0.2" />
            <label className="text-sm text-gray-700">Base Skill Score</label>
            <input type="number" step="0.01" min="0" max="1"
                   className="border rounded px-2 py-1 text-sm"
                   value={(editedJdJson?.skillWeights?.base ?? '')}
                   onChange={e => setEditedJdJson(prev => ({
                     ...prev,
                     skillWeights: { ...(prev?.skillWeights||{}), base: Number(e.target.value) }
                   }))}
                   placeholder="Default 0.1" />
          </div>
          <div className="grid grid-cols-2 gap-2 items-center">
            <label className="text-sm text-gray-700">Critical Min % (Reject if below)</label>
            <input type="number" step="1" min="0" max="100"
                   className="border rounded px-2 py-1 text-sm"
                   value={(editedJdJson?.rejectionRules?.criticalMinPercent ?? '')}
                   onChange={e => setEditedJdJson(prev => ({
                     ...prev,
                     rejectionRules: { ...(prev?.rejectionRules||{}), criticalMinPercent: Number(e.target.value) }
                   }))}
                   placeholder="Default 70" />
            <label className="text-sm text-gray-700">Pass Min Overall</label>
            <input type="number" step="0.01" min="0" max="1"
                   className="border rounded px-2 py-1 text-sm"
                   value={(editedJdJson?.rejectionRules?.passMin ?? '')}
                   onChange={e => setEditedJdJson(prev => ({
                     ...prev,
                     rejectionRules: { ...(prev?.rejectionRules||{}), passMin: Number(e.target.value) }
                   }))}
                   placeholder="Default 0.7" />
            <label className="text-sm text-gray-700">Reject Below Overall</label>
            <input type="number" step="0.01" min="0" max="1"
                   className="border rounded px-2 py-1 text-sm"
                   value={(editedJdJson?.rejectionRules?.rejectBelow ?? '')}
                   onChange={e => setEditedJdJson(prev => ({
                     ...prev,
                     rejectionRules: { ...(prev?.rejectionRules||{}), rejectBelow: Number(e.target.value) }
                   }))}
                   placeholder="Default 0.4" />
          </div>
        </div>
        <div className="text-xs text-gray-500 mt-2">Leave blank to use defaults.</div>
      </div>

      {/* Collapsible advanced JSON editor */}
      <div className="flex justify-between items-center mb-2">
        <span className="font-semibold text-gray-700">JD Form Editor</span>
        <button
          className="flex items-center px-3 py-1 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-lg shadow hover:from-red-600 hover:to-red-700 transition-colors duration-200"
          onClick={() => setShowJsonView(!showJsonView)}
        >
          {showJsonView ? <Edit3 className="w-4 h-4 mr-1" /> : <FileText className="w-4 h-4 mr-1" />}
          {showJsonView ? 'Edit Form' : 'View JSON'}
        </button>
      </div>
      {showJsonView ? (
        <pre className="bg-gray-50 rounded p-4 text-xs overflow-x-auto">{JSON.stringify(editedJdJson, null, 2)}</pre>
      ) : (
        <JdFormEditor jdData={editedJdJson} onUpdate={setEditedJdJson} />
      )}
    </div>
    <div className="text-center flex gap-4 justify-center">
      <button
        onClick={extractResumes}
        disabled={processing || !hasCvFiles}
        className="px-8 py-4 bg-gradient-to-r from-red-500 to-red-600 text-white font-semibold rounded-xl hover:from-red-600 hover:to-red-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <FileText className="w-5 h-5 inline mr-2" />
        Extract Resumes
      </button>
      {(user?.role === 'admin' || user?.role === 'backend_team') && (
        <button
          onClick={saveJd}
          disabled={processing}
          className="px-8 py-4 bg-blue-500 text-white font-semibold rounded-xl hover:bg-blue-600 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
        >
          Save JD
        </button>
      )}
      <button
        onClick={resetApp}
        className="px-8 py-4 bg-gray-200 text-gray-700 font-semibold rounded-xl hover:bg-gray-300 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
      >
        Reset
      </button>
    </div>
  </div>
)};

export default ReviewJdStep;
