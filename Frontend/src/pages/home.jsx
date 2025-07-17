import React, { useState, useCallback } from 'react';
import { Upload, FileText, Brain, BarChart3, CheckCircle, Loader2, Zap, Target, ChevronDown, ChevronUp, X, Plus, Save, Edit3 } from 'lucide-react';
import axios from 'axios';

const defaultSkillCategories = (skills = []) => ({
  critical: skills,
  important: [],
  extra: []
});

const JDCVMatcher = () => {
  const [step, setStep] = useState(1);
  const [files, setFiles] = useState({ jd: null, cv: [] });
  const [processing, setProcessing] = useState(false);
  const [jdJson, setJdJson] = useState(null);
  const [editedJdJson, setEditedJdJson] = useState(null);
  const [skillCategories, setSkillCategories] = useState(defaultSkillCategories());
  const [cvExtractionResults, setCvExtractionResults] = useState(null);
  const [finalResults, setFinalResults] = useState(null);
  const [dragOver, setDragOver] = useState({ jd: false, cv: false });
  const [expandedIdx, setExpandedIdx] = useState(null);
  const [newSkill, setNewSkill] = useState("");
  const [editMode, setEditMode] = useState(false);
  const [skillEditMode, setSkillEditMode] = useState(false);

  // --- File Handlers ---
  const handleDrop = useCallback((e, type) => {
  e.preventDefault();
  setDragOver(prev => ({ ...prev, [type]: false }));
  const droppedFiles = Array.from(e.dataTransfer.files);
  if (droppedFiles.length > 0) {
      if (type === 'cv') {
        setFiles(prev => ({ ...prev, [type]: droppedFiles }));
      } else {
        setFiles(prev => ({ ...prev, [type]: droppedFiles[0] }));
      }
  }
}, []);

  const handleDragOver = useCallback((e, type) => {
    e.preventDefault();
    setDragOver({ ...dragOver, [type]: true });
  }, [dragOver]);

  const handleDragLeave = useCallback((e, type) => {
    e.preventDefault();
    setDragOver({ ...dragOver, [type]: false });
  }, [dragOver]);

 const handleFileSelect = (e, type) => {
    const selectedFiles = Array.from(e.target.files);
    if (type === 'cv') {
      setFiles(prev => ({ ...prev, [type]: selectedFiles }));
    } else {
      setFiles(prev => ({ ...prev, [type]: selectedFiles[0] }));
  }
};

  // --- Step 2: Extract JD JSON ---
  const extractJD = async () => {
    if (!files.jd) return;
    setProcessing(true);
    setStep(2);
    const formData = new FormData();
    formData.append('jd_file', files.jd);
    const localApi = import.meta.env.VITE_API_URL;
    const networkApi = import.meta.env.VITE_API_URL_NETWORK;
    const isLocalhost = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
    const apiUrl = isLocalhost ? localApi : networkApi;
    try {
      const res = await axios.post(`${apiUrl}/extract_jd`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setJdJson(res.data);
      setEditedJdJson(res.data);
      setSkillCategories(defaultSkillCategories(res.data.requiredSkills || []));
      setProcessing(false);
      setStep(3);
    } catch (err) {
      setProcessing(false);
      alert('Error extracting JD: ' + (err.response?.data?.error || err.message));
    }
  };

  // --- Skill Categorization Handlers ---
  const moveSkill = (skill, from, to) => {
    if (from === to) return;
    setSkillCategories(prev => {
      const updated = { ...prev };
      updated[from] = updated[from].filter(s => s !== skill);
      updated[to] = [...updated[to], skill];
      return updated;
    });
  };

  const addSkill = (skill, category) => {
    if (!skill.trim()) return;
    setSkillCategories(prev => ({
      ...prev,
      [category]: [...prev[category], skill.trim()]
    }));
    setNewSkill("");
  };

  const removeSkill = (skill, category) => {
    setSkillCategories(prev => ({
      ...prev,
      [category]: prev[category].filter(s => s !== skill)
    }));
  };

  // --- Step 4: Extract Resumes ---
  const extractResumes = async () => {
    if (!editedJdJson || !files.cv || files.cv.length === 0) return;
    setProcessing(true);
    setStep(4);
    // Merge skillCategories into editedJdJson
    const jdWithCategories = {
      ...editedJdJson,
      requiredSkills: skillCategories, // keep categories for backend LLM
      skillCategories // for frontend display (optional)
    };
    const formData = new FormData();
    formData.append('jd_json', JSON.stringify(jdWithCategories));
    for (let i = 0; i < files.cv.length; i++) {
      formData.append('resume_files', files.cv[i]);
    }
    const localApi = import.meta.env.VITE_API_URL;
    const networkApi = import.meta.env.VITE_API_URL_NETWORK;
    const isLocalhost = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
    const apiUrl = isLocalhost ? localApi : networkApi;
    try {
      const res = await axios.post(`${apiUrl}/extract_resumes`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setCvExtractionResults(res.data);
      setProcessing(false);
      setStep(5);
    } catch (err) {
      setProcessing(false);
      alert('Error extracting resumes: ' + (err.response?.data?.error || err.message));
    }
  };

  // --- Step 5: Match ---
  const matchResults = async () => {
    if (!editedJdJson || !cvExtractionResults) return;
    setProcessing(true);
    setStep(6);
    // Flatten requiredSkills for backend matching, but keep categories for display
    const flatSkills = [
      ...skillCategories.critical,
      ...skillCategories.important,
      ...skillCategories.extra
    ];
    const jdWithCategories = {
      ...editedJdJson,
      requiredSkills: flatSkills,
      skillCategories // for frontend display (optional)
    };
    const localApi = import.meta.env.VITE_API_URL;
    const networkApi = import.meta.env.VITE_API_URL_NETWORK;
    const isLocalhost = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
    const apiUrl = isLocalhost ? localApi : networkApi;
    try {
      const res = await axios.post(`${apiUrl}/match`, {
        jd_json: jdWithCategories,
        cvs: cvExtractionResults
      });
      setFinalResults(res.data);
      setProcessing(false);
      setStep(7);
    } catch (err) {
      setProcessing(false);
      alert('Error matching results: ' + (err.response?.data?.error || err.message));
    }
  };

  // --- Reset ---
  const resetApp = () => {
    setStep(1);
    setFiles({ jd: null, cv: [] });
    setJdJson(null);
    setEditedJdJson(null);
    setSkillCategories(defaultSkillCategories());
    setCvExtractionResults(null);
    setFinalResults(null);
    setProcessing(false);
  };

  // --- Skill Badge ---
  const SkillBadge = ({ text, type }) => {
    const color = type === "present" ? "bg-green-100 text-green-700"
      : type === "partial" ? "bg-yellow-100 text-yellow-700"
      : "bg-red-100 text-red-700";
    return <span className={`inline-block px-2 py-1 rounded-full text-xs font-semibold mr-1 mb-1 ${color}`}>{text}</span>;
  };

  // --- UI ---
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-red-50">
      <div className="absolute inset-0 bg-gradient-to-br from-red-500/5 via-transparent to-red-500/10"></div>
      <header className="relative z-10 bg-white shadow-lg border-b border-red-100 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-r from-red-500 to-red-600 rounded-lg shadow-lg">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-gray-800">JD-CV Matcher</h1>
            </div>
            <div className="flex items-center space-x-4 text-gray-600 text-sm">
              <div className="flex items-center space-x-1">
                <Zap className="w-4 h-4 text-red-500" />
                <span>AI Powered</span>
              </div>
              <div className="flex items-center space-x-1">
                <Target className="w-4 h-4 text-red-500" />
                <span>Smart Matching</span>
              </div>
            </div>
          </div>
        </div>
      </header>
      <main className="relative z-10 max-w-7xl mx-auto px-6 py-8">
        {/* Stepper */}
        <div className="mb-12">
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
                  step >= num + 1
                    ? 'bg-gradient-to-r from-red-500 to-red-600 text-white shadow-lg scale-110' 
                    : 'bg-gray-200 text-gray-500'
                }`}>
                  {step > num + 1 ? <CheckCircle className="w-6 h-6" /> : <Icon className="w-6 h-6" />}
                </div>
                <span className={`text-sm font-medium ${
                  step >= num + 1 ? 'text-gray-800' : 'text-gray-500'
                }`}>{label}</span>
              </div>
            ))}
          </div>
        </div>
        {/* Step 1: Upload */}
        {step === 1 && (
          <div className="space-y-8">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-800 mb-4">Upload Your Documents</h2>
              <p className="text-gray-600 text-lg">Upload both Job Description and one or more Resumes to get started</p>
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
                      <p className="font-medium text-gray-800">{files.jd.name}</p>
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
            {files.jd && files.cv && files.cv.length > 0 && (
              <div className="text-center">
                <button
                  onClick={extractJD}
                  className="px-8 py-4 bg-gradient-to-r from-red-500 to-red-600 text-white font-semibold rounded-xl hover:from-red-600 hover:to-red-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
                  disabled={processing}
                >
                  <FileText className="w-5 h-5 inline mr-2" />
                  Extract JD
                </button>
              </div>
            )}
          </div>
        )}
        {/* Step 3: JD JSON Review & Skill Categorization */}
        {step === 3 && editedJdJson && (
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
              <div className="flex justify-between items-center mb-2">
                <span className="font-semibold text-gray-700">Advanced JD JSON Editor</span>
                <button
                  className="flex items-center px-3 py-1 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-lg shadow hover:from-red-600 hover:to-red-700 transition-colors duration-200"
                  onClick={() => setEditMode(!editMode)}
                >
                  {editMode ? <Save className="w-4 h-4 mr-1" /> : <Edit3 className="w-4 h-4 mr-1" />}
                  {editMode ? 'Save' : 'Edit'}
                </button>
              </div>
              {editMode ? (
                <textarea
                  value={JSON.stringify(editedJdJson, null, 2)}
                  onChange={e => {
                    try {
                      setEditedJdJson(JSON.parse(e.target.value));
                    } catch {}
                  }}
                  rows={20}
                  className="w-full border rounded p-2 font-mono text-xs"
                />
              ) : (
                <pre className="bg-gray-50 rounded p-4 text-xs overflow-x-auto">{JSON.stringify(editedJdJson, null, 2)}</pre>
              )}
            </div>
            <div className="text-center flex gap-4 justify-center">
              <button
                onClick={extractResumes}
                disabled={processing}
                className="px-8 py-4 bg-gradient-to-r from-red-500 to-red-600 text-white font-semibold rounded-xl hover:from-red-600 hover:to-red-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                <FileText className="w-5 h-5 inline mr-2" />
                Extract Resumes
              </button>
              <button
                onClick={resetApp}
                className="px-8 py-4 bg-gray-200 text-gray-700 font-semibold rounded-xl hover:bg-gray-300 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                Reset
              </button>
            </div>
          </div>
        )}
        {/* Step 5: Extracted Resumes (show summary, allow to proceed to match) */}
        {step === 5 && cvExtractionResults && (
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
        )}
        {/* Step 7: Results Table */}
        {step === 7 && finalResults && (
          <div className="space-y-8">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-800 mb-4">Analysis Complete!</h2>
              <p className="text-gray-600 text-lg">Here's your comprehensive JD-CV match analysis</p>
            </div>
            {/* Top Match Score Card */}
            <div className="flex justify-center mb-8">
              <div className="bg-white rounded-2xl shadow-lg p-8 flex flex-col items-center" style={{ minWidth: 400 }}>
                <div className="w-40 h-40 flex items-center justify-center rounded-full bg-gradient-to-r from-red-500 to-red-600 shadow-lg mb-4">
                  <span className="text-4xl font-bold text-white">
                    {finalResults.matching_metadata.top_match_score?.toFixed(2)}%
                  </span>
                </div>
                <h3 className="text-2xl font-bold text-gray-800 mb-2">Top Match Score</h3>
                <p className="text-gray-600">Best candidate alignment with job requirements</p>
              </div>
            </div>
            {/* Candidates Table */}
            <div className="max-w-7xl mx-auto">
              <div className="mb-2 font-semibold text-gray-700">
                Total Candidates: {finalResults.matching_metadata.candidates_evaluated}
              </div>
              <div className="overflow-x-auto rounded-2xl shadow-lg">
                <table className="min-w-full bg-white rounded-2xl overflow-hidden">
                <thead>
                    <tr className="bg-red-100 text-gray-800 text-sm">
                    <th className="px-4 py-2 text-left">Name</th>
                    <th className="px-4 py-2 text-left">% Match</th>
                    <th className="px-4 py-2 text-left">Critical Skills</th>
                      <th className="px-4 py-2 text-left">Title Sim.</th>
                      <th className="px-4 py-2 text-left">Resp. Sim.</th>
                      <th className="px-4 py-2 text-left">Exp. Match</th>
                      <th className="px-4 py-2 text-left">Skill Match</th>
                      <th className="px-4 py-2 text-left">Edu. Match</th>
                    <th className="px-4 py-2 text-left">More Details</th>
                  </tr>
                </thead>
                <tbody>
                    {finalResults.results.map((candidate, idx) => {
                      // For critical skills
                      const critStatus = candidate.critical_skill_status;
                      const critColor = critStatus === 'All Present' ? 'bg-green-100 text-green-700' : critStatus === 'All Absent' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700';
                      return (
                    <React.Fragment key={idx}>
                          <tr className="border-t hover:bg-red-50 text-sm">
                            <td className="px-4 py-2 font-semibold whitespace-nowrap">{candidate.candidate_name}</td>
                            <td className="px-4 py-2 font-bold text-lg text-gray-800 whitespace-nowrap">{candidate.match_score?.toFixed(2)}%</td>
                            <td className={`px-4 py-2 font-semibold whitespace-nowrap ${critColor}`}> 
                              {critStatus}
                              <button
                                className="ml-2 text-xs underline text-blue-600 hover:text-blue-800"
                                onClick={() => setExpandedIdx(expandedIdx === idx ? null : idx)}
                                title="Show critical skill details"
                              >
                                {expandedIdx === idx ? 'Hide' : 'Show'}
                              </button>
                        </td>
                            <td className="px-4 py-2 whitespace-nowrap">{(candidate.match_details?.job_title_similarity * 100)?.toFixed(1)}%</td>
                            <td className="px-4 py-2 whitespace-nowrap">{(candidate.match_details?.responsibilities_similarity * 100)?.toFixed(1)}%</td>
                            <td className="px-4 py-2 whitespace-nowrap">{(candidate.match_details?.experience_suitability * 100)?.toFixed(1)}%</td>
                            <td className="px-4 py-2 whitespace-nowrap">{(candidate.match_details?.skills_similarity * 100)?.toFixed(1)}%</td>
                            <td className="px-4 py-2 whitespace-nowrap">{(candidate.match_details?.education_relevance * 100)?.toFixed(1)}%</td>
                        <td className="px-4 py-2">
                          <button
                            className="flex items-center px-3 py-1 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-lg shadow hover:from-red-600 hover:to-red-700 transition-colors duration-200"
                            onClick={() => setExpandedIdx(expandedIdx === idx ? null : idx)}
                          >
                            {expandedIdx === idx ? <ChevronUp className="w-4 h-4 mr-1" /> : <ChevronDown className="w-4 h-4 mr-1" />}
                            {expandedIdx === idx ? 'Hide' : 'Show'}
                          </button>
                        </td>
                      </tr>
                          {/* Critical skills details row */}
                      {expandedIdx === idx && (
                        <tr>
                              <td colSpan={9} className="bg-gray-50 px-6 py-4 border-t">
                                <div className="mb-4">
                                  <h4 className="font-semibold text-red-700 mb-2 text-lg">Critical Skills Breakdown</h4>
                                  <div className="flex flex-wrap gap-2 mb-2">
                                    {candidate.critical_present && candidate.critical_present.map((s, i) => (
                                      <SkillBadge key={i} text={s} type="present" />
                                    ))}
                                    {candidate.critical_absent && candidate.critical_absent.map((s, i) => (
                                      <SkillBadge key={i} text={s} type="absent" />
                                    ))}
                                  </div>
                                </div>
                                <div className="grid md:grid-cols-3 gap-6">
                                  <div className="bg-white rounded-xl shadow p-6">
                                    <h4 className="font-semibold text-gray-800 mb-2">Interview Questions</h4>
                                    <ul className="list-disc pl-6 space-y-1">
                                      {candidate.interview_questions?.length > 0 ? candidate.interview_questions.map((q, i) => (
                                        <li key={i} className="text-gray-700">{q}</li>
                                      )) : <li className="text-gray-400">No questions generated.</li>}
                                    </ul>
                                  </div>
                                  <div className="bg-white rounded-xl shadow p-6">
                                    <h4 className="font-semibold text-gray-800 mb-2">Profile Insights</h4>
                                    {candidate.disclaimer && (
                                      <div className="mb-4 p-4 border border-red-400 bg-red-50 rounded-lg text-red-700 font-semibold">
                                        {candidate.disclaimer}
                                      </div>
                                    )}
                                    <div className="mb-1"><span className="font-medium">Job Stability:</span> {candidate.job_stability?.average_duration_years} yrs avg, {candidate.job_stability?.frequent_switching_flag ? <span className="text-red-500 font-semibold">Frequent Switcher</span> : <span className="text-green-600 font-semibold">Stable</span>}</div>
                                    <div className="mb-1"><span className="font-medium">Education Gap:</span> {candidate.education_gap?.has_gap ? <span className="text-red-500 font-semibold">Yes</span> : <span className="text-green-600 font-semibold">No</span>} {candidate.education_gap?.has_gap && `(${candidate.education_gap.gap_duration_years} yrs)`}</div>
                                    <div className="mb-1"><span className="font-medium">Suggested Role:</span> <span className="text-blue-700 font-semibold">{candidate.suggested_role}</span></div>
                                    <div className="mt-4">
                                      <h5 className="font-semibold text-gray-700 mb-1">Skill Presence Table</h5>
                                      <div className="overflow-x-auto">
                                        <table className="min-w-[350px] text-sm border rounded">
                                          <thead>
                                            <tr className="bg-gray-100">
                                              <th className="px-2 py-1 text-left">Category</th>
                                              <th className="px-2 py-1 text-left">Present</th>
                                              <th className="px-2 py-1 text-left">Absent</th>
                                            </tr>
                                          </thead>
                                          <tbody>
                                            {['critical', 'important', 'extra'].map(cat => {
                                              const present = skillCategories[cat].filter(s => candidate.skill_presence?.[s] === true);
                                              const absent = skillCategories[cat].filter(s => candidate.skill_presence?.[s] === false);
                                              const total = skillCategories[cat].length;
                                              return (
                                                <tr key={cat}>
                                                  <td className={`px-2 py-1 font-semibold ${cat === 'critical' ? 'text-red-700' : cat === 'important' ? 'text-yellow-700' : 'text-blue-700'}`}>
                                                    {cat.charAt(0).toUpperCase() + cat.slice(1)} ({present.length}/{total})
                                                  </td>
                                                  <td className="px-2 py-1">
                                                    {present.length > 0 ? present.map((s, i) => <SkillBadge key={i} text={s} type="present" />) : <span className="text-gray-400">None</span>}
                                                  </td>
                                                  <td className="px-2 py-1">
                                                    {absent.length > 0 ? absent.map((s, i) => <SkillBadge key={i} text={s} type="absent" />) : <span className="text-gray-400">None</span>}
                                                  </td>
                                                </tr>
                                              );
                                            })}
                                          </tbody>
                                        </table>
                                      </div>
                                    </div>
                                  </div>
                                  <div className="bg-white rounded-xl shadow p-6">
                                    <h4 className="font-semibold text-gray-800 mb-2">Match Details</h4>
                                    <ul className="list-disc pl-6 space-y-1 text-sm">
                                      <li><b>Candidate Experience Years:</b> {candidate.match_details?.candidate_exp_years}</li>
                                      <li><b>Required Experience Years:</b> {candidate.match_details?.required_exp_years}</li>
                                      <li><b>Job Title Similarity:</b> {(candidate.match_details?.job_title_similarity * 100)?.toFixed(2)}%</li>
                                      <li><b>Responsibilities Similarity:</b> {(candidate.match_details?.responsibilities_similarity * 100)?.toFixed(2)}%</li>
                                      <li><b>Experience Suitability:</b> {(candidate.match_details?.experience_suitability * 100)?.toFixed(2)}%</li>
                                      <li><b>Skills Similarity:</b> {(candidate.match_details?.skills_similarity * 100)?.toFixed(2)}%</li>
                                      <li><b>Education Relevance:</b> {(candidate.match_details?.education_relevance * 100)?.toFixed(2)}%</li>
                                      <li><b>Location Compatibility:</b> {(candidate.match_details?.location_compatibility * 100)?.toFixed(2)}%</li>
                                      <li><b>Role Relevance:</b> {(candidate.match_details?.role_relevance * 100)?.toFixed(2)}%</li>
                                      <li><b>Summary:</b> {candidate.match_details?.match_summary}</li>
                                    </ul>
                                  </div>
                                  
                                </div>
                              </td>
                            </tr>
                          )}
                        </React.Fragment>
                      );
                    })}
                </tbody>
              </table>
              </div>
            </div>
            <div className="text-center mt-8">
              <button
                onClick={resetApp}
                className="px-8 py-4 bg-gray-200 text-gray-700 font-semibold rounded-xl hover:bg-gray-300 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                Start Over
              </button>
            </div>
          </div>
        )}
        {/* Loader */}
        {processing && (
          <div className="fixed inset-0 bg-black bg-opacity-20 flex items-center justify-center z-50">
            <div className="bg-white p-8 rounded-xl shadow-lg flex flex-col items-center">
              <Loader2 className="animate-spin w-10 h-10 text-red-500 mb-4" />
              <div className="text-lg font-semibold text-gray-700">Processing...</div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default JDCVMatcher;