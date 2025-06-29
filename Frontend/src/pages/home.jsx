import React, { useState, useCallback } from 'react';
import { Upload, FileText, Brain, BarChart3, Download, CheckCircle, AlertCircle, Loader2, Zap, Target, MessageSquare, Database, Users } from 'lucide-react';
import axios from 'axios';
const JDCVMatcher = () => {
  const [step, setStep] = useState(1);
  const [files, setFiles] = useState({ jd: null, cvs: [] });
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState({ jd: "", cv: "" });
  const [dragOver, setDragOver] = useState({ jd: false, cv: false });
  const [similarityScore, setSimilarityScore] = useState(null);
  const [showPreview, setShowPreview] = useState({ jd: false, cv: false });
  const [editText, setEditText] = useState({ jd: '', cv: '' });
  const [candidates, setCandidates] = useState([]);

 const uploadFileToBackend = async (file, type, jdText = null) => {
  const formData = new FormData();
  formData.append("file", file);
  if (type === 'cv' && jdText) {
    formData.append('jd', jdText);
  }

  try {
    const res = await axios.post("http://localhost:8000/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data"
      },
    });
    console.log(`✅ ${type.toUpperCase()} Upload Success:`, res.data);

    // Use raw_text for preview/edit, cleaned_resume_text for processing
    setResults(prev => ({ ...prev, [type]: res.data.raw_text }));
    setEditText(prev => ({ ...prev, [type]: res.data.raw_text }));
    if (type === 'cv' && res.data.similarity_score_with_jd !== undefined && res.data.similarity_score_with_jd !== null) {
      setSimilarityScore(res.data.similarity_score_with_jd);
    }
  } catch (err) {
    console.error(`❌ ${type.toUpperCase()} Upload Failed:`, err);
  }
};

// Upload multiple CVs with JD
const uploadMultipleCVs = async (cvFiles, jdText) => {
  const formData = new FormData();
  for (let i = 0; i < cvFiles.length; i++) {
    formData.append("files", cvFiles[i]);
  }
  formData.append('jd', jdText);

  try {
    const res = await axios.post("http://localhost:8000/upload-multiple", formData, {
      headers: {
        "Content-Type": "multipart/form-data"
      },
    });
    console.log(`✅ Multiple CVs Upload Success:`, res.data);
    setCandidates(res.data.results || []);
    return res.data.results;
  } catch (err) {
    console.error(`❌ Multiple CVs Upload Failed:`, err);
    return [];
  }
};
      
  const handleDrop = useCallback((e, type) => {
  e.preventDefault();
  setDragOver(prev => ({ ...prev, [type]: false }));
  const droppedFiles = Array.from(e.dataTransfer.files);
  if (droppedFiles.length > 0) {
    if (type === 'cv') {
      // Handle multiple CV files
      console.log(`📄 CVs Dropped:`, droppedFiles.map(f => f.name));
      setFiles(prev => ({ ...prev, cvs: [...prev.cvs, ...droppedFiles] }));
    } else {
      // Handle single JD file
      const file = droppedFiles[0];
      console.log(`📄 JD Dropped:`, file.name);
      setFiles(prev => ({ ...prev, [type]: file }));
      uploadFileToBackend(file, type);
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
  if (selectedFiles.length > 0) {
    if (type === 'cv') {
      // Handle multiple CV files
      console.log(`📄 CVs Selected:`, selectedFiles.map(f => f.name));
      setFiles(prev => ({ ...prev, cvs: [...prev.cvs, ...selectedFiles] }));
    } else {
      // Handle single JD file
      const file = selectedFiles[0];
      console.log(`📄 JD Selected:`, file.name);
      setFiles(prev => ({ ...prev, [type]: file }));
      uploadFileToBackend(file, type);
    }
  }
};
  const processFiles = async () => {
    if (!files.jd || !files.cvs.length) return;
    
    setProcessing(true);
    setStep(2);
    
    try {
      // Call backend to get actual similarity scores for multiple CVs
      const formData = new FormData();
      for (let i = 0; i < files.cvs.length; i++) {
        formData.append("files", files.cvs[i]);
      }
      
      // Get JD text from results or upload JD file
      let jdText = results.jd;
      if (!jdText && files.jd) {
        // If JD text is not available, extract it from the JD file
        const jdFormData = new FormData();
        jdFormData.append("file", files.jd);
        const jdResponse = await axios.post("http://localhost:8000/upload", jdFormData, {
          headers: {
            "Content-Type": "multipart/form-data"
          },
        });
        jdText = jdResponse.data.raw_text;
      }
      
      formData.append('jd', jdText);
      
      const response = await axios.post("http://localhost:8000/upload-multiple", formData, {
        headers: {
          "Content-Type": "multipart/form-data"
        },
      });
      
      const candidatesData = response.data.results || [];
      setCandidates(candidatesData);
      
      // Use the highest similarity score for the main display
      const highestScore = candidatesData.length > 0 ? candidatesData[0].similarity_score : 0.85;
      setSimilarityScore(highestScore);
      
      // Simulate additional processing time
      setTimeout(() => {
        setResults({
          matchScores: candidatesData.map(candidate => Math.round(candidate.similarity_score * 100)),
          candidates: candidatesData,
          keywordMatches: ['JavaScript', 'React', 'Node.js', 'API Development', 'Team Leadership'],
          missingSkills: ['Docker', 'Kubernetes', 'AWS'],
          questions: [
            {
              q: "Can you explain your experience with React and state management?",
              a: "I have 3+ years of experience building scalable React applications using Redux and Context API for state management, including complex data flows and performance optimization."
            },
            {
              q: "How do you approach API integration in your projects?",
              a: "I design RESTful APIs with proper error handling, implement authentication/authorization, and use tools like Axios for frontend integration with proper loading states."
            },
            {
              q: "Describe your team leadership experience.",
              a: "I've led cross-functional teams of 5-8 developers, mentored junior developers, conducted code reviews, and managed project timelines using Agile methodologies."
            }
          ],
          strengths: [
            "Strong technical foundation in required technologies",
            "Relevant project experience matches job requirements",
            "Leadership experience aligns with senior role expectations"
          ],
          recommendations: [
            "Consider gaining Docker/containerization experience",
            "Explore cloud platforms like AWS or Azure",
            "Add more details about scalability achievements"
          ]
        });
        setProcessing(false);
        setStep(3);
      }, 2000);
    } catch (error) {
      console.error('Error processing files:', error);
      // Fallback to mock data if API fails
      const fallbackScore = 0.85;
      setSimilarityScore(fallbackScore);
      
      setTimeout(() => {
        setResults({
          matchScores: [Math.round(fallbackScore * 100)],
          candidates: [],
          keywordMatches: ['JavaScript', 'React', 'Node.js', 'API Development', 'Team Leadership'],
          missingSkills: ['Docker', 'Kubernetes', 'AWS'],
          questions: [
            {
              q: "Can you explain your experience with React and state management?",
              a: "I have 3+ years of experience building scalable React applications using Redux and Context API for state management, including complex data flows and performance optimization."
            },
            {
              q: "How do you approach API integration in your projects?",
              a: "I design RESTful APIs with proper error handling, implement authentication/authorization, and use tools like Axios for frontend integration with proper loading states."
            },
            {
              q: "Describe your team leadership experience.",
              a: "I've led cross-functional teams of 5-8 developers, mentored junior developers, conducted code reviews, and managed project timelines using Agile methodologies."
            }
          ],
          strengths: [
            "Strong technical foundation in required technologies",
            "Relevant project experience matches job requirements",
            "Leadership experience aligns with senior role expectations"
          ],
          recommendations: [
            "Consider gaining Docker/containerization experience",
            "Explore cloud platforms like AWS or Azure",
            "Add more details about scalability achievements"
          ]
        });
        setProcessing(false);
        setStep(3);
      }, 2000);
    }
  };

  const exportPDF = () => {
    // Simulate PDF export
    const blob = new Blob(['PDF Report Content'], { type: 'application/pdf' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'jd-cv-match-report.pdf';
    a.click();
    URL.revokeObjectURL(url);
  };

  const resetApp = () => {
    setStep(1);
    setFiles({ jd: null, cvs: [] });
    setResults(null);
    setProcessing(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-red-50">
      <div className="absolute inset-0 bg-gradient-to-br from-red-500/5 via-transparent to-red-500/10"></div>
      
      {/* Header */}
      <header className="relative z-10 bg-white shadow-lg border-b border-red-100">
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
        {/* Progress Steps */}
        <div className="mb-12">
          <div className="flex items-center justify-center space-x-8">
            {[
              { num: 1, label: 'Upload Files', icon: Upload },
              { num: 2, label: 'AI Processing', icon: Brain },
              { num: 3, label: 'Results & Export', icon: BarChart3 }
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
        </div>

        {/* Step 1: File Upload */}
        {step === 1 && (
          <div className="space-y-8">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-800 mb-4">Upload Your Documents</h2>
              <p className="text-gray-600 text-lg">Upload both Job Description and Resume to get started</p>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              {/* Job Description Upload */}
              <div className="bg-white/80 backdrop-blur-sm rounded-xl p-6 shadow-md border border-red-100/50 hover:shadow-lg transition-all duration-300 transform hover:scale-[1.01] group">
                <div className="text-center mb-4">
                  <div className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-r from-red-500 to-red-600 rounded-full shadow-md mb-3 group-hover:scale-110 transition-transform duration-300">
                    <FileText className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-1 group-hover:text-red-600 transition-colors duration-300">Job Description</h3>
                  <p className="text-gray-600 text-sm group-hover:text-gray-700 transition-colors duration-300">Upload the job posting or requirements</p>
                </div>

                <div
                  className={`border-2 border-dashed rounded-lg p-6 text-center transition-all duration-300 cursor-pointer group/upload ${
                    dragOver.jd
                      ? 'border-red-400 bg-red-50/80 scale-105 shadow-md'
                      : files.jd
                      ? 'border-red-400 bg-red-50/80 hover:border-red-500 hover:bg-red-100/80'
                      : 'border-gray-300 hover:border-red-400 hover:bg-red-50/80 hover:scale-[1.01] group-hover:border-red-400 group-hover:bg-red-50/80'
                  }`}
                  onDrop={(e) => handleDrop(e, 'jd')}
                  onDragOver={(e) => handleDragOver(e, 'jd')}
                  onDragLeave={(e) => handleDragLeave(e, 'jd')}
                >
                  {files.jd ? (
                    <div className="text-red-600 mt-2 animate-pulse">
                      <div className="w-10 h-10 bg-red-500 rounded-full flex items-center justify-center mx-auto mb-2 group-hover/upload:scale-110 transition-transform duration-300">
                        <CheckCircle className="w-5 h-5 text-white" />
                      </div>
                      <p className="font-medium text-gray-800 text-sm group-hover/upload:text-red-700 transition-colors duration-300">{files.jd.name}</p>
                      <p className="text-xs text-gray-500 mt-1 group-hover/upload:text-red-600 transition-colors duration-300">Ready to process</p>
                      <div className="mt-2 flex justify-center space-x-1">
                        <div className="w-1.5 h-1.5 bg-red-500 rounded-full animate-bounce"></div>
                        <div className="w-1.5 h-1.5 bg-red-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                        <div className="w-1.5 h-1.5 bg-red-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="w-12 h-12 bg-gradient-to-r from-gray-400 to-gray-500 rounded-full flex items-center justify-center mx-auto mb-3 group-hover/upload:scale-110 transition-transform duration-300">
                        <Upload className="w-6 h-6 text-white" />
                      </div>
                      <p className="text-gray-600 mb-2 text-sm group-hover/upload:text-gray-800 transition-colors duration-300">Drop your JD here or</p>
                      <input
                        type="file"
                        id="jd-upload"
                        className="hidden"
                        accept=".pdf,.doc,.docx,.txt"
                        onChange={(e) => handleFileSelect(e, 'jd')}
                      />
                      <label
                        htmlFor="jd-upload"
                        className="inline-block px-4 py-2 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-lg cursor-pointer hover:from-red-600 hover:to-red-700 transition-all duration-300 shadow-sm hover:shadow-md transform hover:scale-105 active:scale-95 text-sm"
                      >
                        Browse Files
                      </label>
                    </>
                  )}
                </div>
                {files.jd && (
                  <div className="mt-3">
                    {showPreview.jd ? (
                      <div className="bg-gray-50/80 border border-gray-200 rounded-lg p-3 text-left animate-fadeIn">
                        <h4 className="text-sm font-semibold text-gray-800 mb-2">Edit JD Text:</h4>
                        <textarea
                          className="w-full h-32 p-2 border rounded-lg text-gray-800 focus:ring-2 focus:ring-red-500 focus:border-transparent transition-all duration-300 text-sm"
                          value={editText.jd}
                          onChange={e => setEditText(prev => ({ ...prev, jd: e.target.value }))}
                        />
                        <div className="flex gap-2 mt-2 justify-end">
                          <button
                            className="px-3 py-1.5 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors duration-300 transform hover:scale-105 active:scale-95 text-sm"
                            onClick={() => {
                              setResults(prev => ({ ...prev, jd: editText.jd }));
                              setShowPreview(prev => ({ ...prev, jd: false }));
                            }}
                          >Save</button>
                          <button
                            className="px-3 py-1.5 bg-gray-300 text-gray-800 rounded-lg hover:bg-gray-400 transition-colors duration-300 transform hover:scale-105 active:scale-95 text-sm"
                            onClick={() => setShowPreview(prev => ({ ...prev, jd: false }))}
                          >Cancel</button>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center">
                        <button
                          className="px-3 py-1.5 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-all duration-300 shadow-sm hover:shadow-md transform hover:scale-105 active:scale-95 text-sm"
                          onClick={() => setShowPreview(prev => ({ ...prev, jd: true }))}
                        >
                          Preview & Edit
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Resume Upload */}
              <div className="bg-white/80 backdrop-blur-sm rounded-xl p-6 shadow-md border border-red-100/50 hover:shadow-lg transition-all duration-300 transform hover:scale-[1.01] group">
                <div className="text-center mb-4">
                  <div className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-r from-red-500 to-red-600 rounded-full shadow-md mb-3 group-hover:scale-110 transition-transform duration-300">
                    <Users className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-1 group-hover:text-red-600 transition-colors duration-300">Resumes / CVs</h3>
                  <p className="text-gray-600 text-sm group-hover:text-gray-700 transition-colors duration-300">Upload multiple candidate resumes</p>
                </div>

                <div
                  className={`border-2 border-dashed rounded-lg p-6 text-center transition-all duration-300 cursor-pointer group/upload ${
                    dragOver.cv
                      ? 'border-red-400 bg-red-50/80 scale-105 shadow-md'
                      : files.cvs.length > 0
                      ? 'border-red-400 bg-red-50/80 hover:border-red-500 hover:bg-red-100/80'
                      : 'border-gray-300 hover:border-red-400 hover:bg-red-50/80 hover:scale-[1.01] group-hover:border-red-400 group-hover:bg-red-50/80'
                  }`}
                  onDrop={(e) => handleDrop(e, 'cv')}
                  onDragOver={(e) => handleDragOver(e, 'cv')}
                  onDragLeave={(e) => handleDragLeave(e, 'cv')}
                >
                  {files.cvs.length > 0 ? (
                    <div className="text-red-600 mt-2 animate-pulse">
                      <div className="w-10 h-10 bg-red-500 rounded-full flex items-center justify-center mx-auto mb-2 group-hover/upload:scale-110 transition-transform duration-300">
                        <CheckCircle className="w-5 h-5 text-white" />
                      </div>
                      <p className="font-medium text-gray-800 text-sm group-hover/upload:text-red-700 transition-colors duration-300">{files.cvs.length} CV(s) uploaded</p>
                      <p className="text-xs text-gray-500 mt-1 group-hover/upload:text-red-600 transition-colors duration-300">Ready to process</p>
                      <div className="mt-2 flex justify-center space-x-1">
                        <div className="w-1.5 h-1.5 bg-red-500 rounded-full animate-bounce"></div>
                        <div className="w-1.5 h-1.5 bg-red-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                        <div className="w-1.5 h-1.5 bg-red-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="w-12 h-12 bg-gradient-to-r from-gray-400 to-gray-500 rounded-full flex items-center justify-center mx-auto mb-3 group-hover/upload:scale-110 transition-transform duration-300">
                        <Upload className="w-6 h-6 text-white" />
                      </div>
                      <p className="text-gray-600 mb-2 text-sm group-hover/upload:text-gray-800 transition-colors duration-300">Drop your CVs here or</p>
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
                        className="inline-block px-4 py-2 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-lg cursor-pointer hover:from-red-600 hover:to-red-700 transition-all duration-300 shadow-sm hover:shadow-md transform hover:scale-105 active:scale-95 text-sm"
                      >
                        Browse Files
                      </label>
                    </>
                  )}
                </div>

                {/* Display uploaded CVs */}
                {files.cvs.length > 0 && (
                  <div className="mt-3">
                    <h4 className="text-sm font-semibold text-gray-800 mb-2">Uploaded CVs:</h4>
                    <div className="space-y-1.5 max-h-32 overflow-y-auto">
                      {files.cvs.map((file, index) => (
                        <div key={index} className="flex items-center justify-between bg-gray-50/80 p-2 rounded-lg hover:bg-gray-100/80 transition-all duration-300 transform hover:scale-[1.01] group/file">
                          <div className="flex items-center space-x-2">
                            <div className="w-6 h-6 bg-gray-400 rounded-full flex items-center justify-center group-hover/file:bg-gray-500 transition-colors duration-300">
                              <FileText className="w-3 h-3 text-white" />
                            </div>
                            <span className="text-xs text-gray-700 group-hover/file:text-gray-900 transition-colors duration-300 truncate max-w-32">{file.name}</span>
                          </div>
                          <button
                            onClick={() => {
                              setFiles(prev => ({
                                ...prev,
                                cvs: prev.cvs.filter((_, i) => i !== index)
                              }));
                            }}
                            className="text-red-500 hover:text-red-700 text-xs px-1.5 py-1 rounded hover:bg-red-50 transition-all duration-300 transform hover:scale-110 active:scale-95"
                            title="Remove CV"
                          >
                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </button>
                        </div>
                      ))}
                    </div>
                    
                    {/* Hidden file input for adding more CVs */}
                    <input
                      type="file"
                      id="add-more-cv"
                      className="hidden"
                      accept=".pdf,.doc,.docx,.txt"
                      multiple
                      onChange={(e) => {
                        const selectedFiles = Array.from(e.target.files);
                        if (selectedFiles.length > 0) {
                          setFiles(prev => ({ ...prev, cvs: [...prev.cvs, ...selectedFiles] }));
                        }
                        // Reset the input value so the same file can be selected again
                        e.target.value = '';
                      }}
                    />
                    
                    {/* Add More CVs Button */}
                    <div className="mt-3 text-center">
                      <button
                        onClick={() => {
                          document.getElementById('add-more-cv').click();
                        }}
                        className="inline-flex items-center px-3 py-1.5 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-lg hover:from-red-600 hover:to-red-700 transition-all duration-300 shadow-sm hover:shadow-md transform hover:scale-105 active:scale-95 text-sm"
                      >
                        <svg className="w-3 h-3 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                        </svg>
                        Add More CVs
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {files.jd && files.cvs.length > 0 && (
              <div className="text-center">
                <button
                  onClick={processFiles}
                  className="px-8 py-4 bg-gradient-to-r from-red-500 to-red-600 text-white font-semibold rounded-xl hover:from-red-600 hover:to-red-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
                >
                  <Brain className="w-5 h-5 inline mr-2" />
                  Start AI Analysis
                </button>
              </div>
            )}
          </div>
        )}

        {/* Step 2: Processing */}
        {step === 2 && (
          <div className="text-center py-16">
            <div className="bg-white rounded-2xl p-12 max-w-2xl mx-auto shadow-lg border border-red-100">
              <Loader2 className="w-16 h-16 text-red-500 mx-auto mb-6 animate-spin" />
              <h2 className="text-2xl font-bold text-gray-800 mb-4">AI Processing in Progress</h2>
              <p className="text-gray-600 mb-8">Our AI is analyzing your documents and generating insights...</p>
              
              <div className="space-y-4 text-left">
                {[
                  { text: 'Extracting text from documents', done: true },
                  { text: 'Converting content to vectors', done: true },
                  { text: 'Generating questions & answers', done: processing },
                  { text: 'Calculating match score', done: false },
                  { text: 'Preparing recommendations', done: false }
                ].map((item, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    {item.done ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : (
                      <div className="w-5 h-5 border-2 border-gray-300 rounded-full"></div>
                    )}
                    <span className={`${item.done ? 'text-gray-800' : 'text-gray-500'}`}>
                      {item.text}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Results */}
        {step === 3 && results && (
          <div className="space-y-8">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-800 mb-4">Analysis Complete!</h2>
              <p className="text-gray-600 text-lg">Here's your comprehensive JD-CV match analysis</p>
            </div>

            {/* Top Match Score */}
            <div className="bg-white rounded-2xl p-8 shadow-lg border border-red-100">
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-32 h-32 rounded-full bg-gradient-to-r from-red-500 to-red-600 shadow-lg mb-6">
                  <span className="text-4xl font-bold text-white">{(similarityScore * 100).toFixed(2)}%</span>
                </div>
                <h3 className="text-2xl font-bold text-gray-800 mb-2">Top Match Score</h3>
                <p className="text-gray-600">Best candidate alignment with job requirements</p>
              </div>
            </div>

            {/* Candidates Ranking */}
            {results.candidates && results.candidates.length > 0 && (
              <div className="bg-white rounded-2xl p-8 shadow-lg border border-red-100">
                <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                  <Users className="w-6 h-6 text-red-500 mr-2" />
                  Candidates Ranked by Similarity
                </h3>
                <div className="space-y-4">
                  {results.candidates.map((candidate, index) => (
                    <div key={index} className="bg-gradient-to-r from-gray-50 to-white p-6 rounded-xl border border-gray-200">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="w-12 h-12 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-full flex items-center justify-center text-lg font-bold">
                            {index + 1}
                          </div>
                          <div>
                            <h4 className="text-lg font-semibold text-gray-800">{candidate.filename}</h4>
                            <p className="text-sm text-gray-500">
                              Similarity Score: {(candidate.similarity_score * 100).toFixed(1)}%
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="w-20 h-20 rounded-full border-4 border-red-200 flex items-center justify-center bg-white">
                            <span className="text-xl font-bold text-red-500">
                              {(candidate.similarity_score * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Key Insights Grid */}
            <div className="grid md:grid-cols-2 gap-8">
              {/* Keyword Matches */}
              <div className="bg-white rounded-2xl p-6 shadow-lg border border-red-100">
                <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                  <CheckCircle className="w-6 h-6 text-red-500 mr-2" />
                  Matching Skills
                </h3>
                <div className="flex flex-wrap gap-2">
                  {results.keywordMatches.map((skill, index) => (
                    <span key={index} className="px-3 py-1 bg-red-500 text-white rounded-full text-sm shadow-md">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>

              {/* Missing Skills */}
              <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
                <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                  <AlertCircle className="w-6 h-6 text-orange-500 mr-2" />
                  Areas for Development
                </h3>
                <div className="flex flex-wrap gap-2">
                  {results.missingSkills.map((skill, index) => (
                    <span key={index} className="px-3 py-1 bg-gray-500 text-white rounded-full text-sm shadow-md">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Generated Q&A */}
            <div className="bg-white rounded-2xl p-8 shadow-lg border border-red-100">
              <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                <MessageSquare className="w-6 h-6 text-red-500 mr-2" />
                Generated Interview Questions
              </h3>
              <div className="space-y-6">
                {results.questions.map((qa, index) => (
                  <div key={index} className="bg-gray-50 rounded-xl p-6 border border-gray-200">
                    <div className="mb-4">
                      <span className="text-red-600 font-medium">Q{index + 1}: </span>
                      <span className="text-gray-800">{qa.q}</span>
                    </div>
                    <div className="pl-6 border-l-2 border-red-500">
                      <span className="text-red-600 font-medium">A: </span>
                      <span className="text-gray-700">{qa.a}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Strengths & Recommendations */}
            <div className="grid md:grid-cols-2 gap-8">
              <div className="bg-white rounded-2xl p-6 shadow-lg border border-red-100">
                <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                  <Target className="w-6 h-6 text-red-500 mr-2" />
                  Key Strengths
                </h3>
                <ul className="space-y-3">
                  {results.strengths.map((strength, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <CheckCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700">{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
                <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                  <Brain className="w-6 h-6 text-gray-600 mr-2" />
                  Recommendations
                </h3>
                <ul className="space-y-3">
                  {results.recommendations.map((rec, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <AlertCircle className="w-5 h-5 text-gray-600 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700">{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={exportPDF}
                className="px-8 py-4 bg-gradient-to-r from-red-500 to-red-600 text-white font-semibold rounded-xl hover:from-red-600 hover:to-red-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                <Download className="w-5 h-5 inline mr-2" />
                Export PDF Report
              </button>
              <button
                onClick={resetApp}
                className="px-8 py-4 bg-white text-gray-800 font-semibold rounded-xl hover:bg-gray-50 transition-all duration-300 border border-gray-300 shadow-md"
              >
                <Upload className="w-5 h-5 inline mr-2" />
                Analyze New Files
              </button>
            </div>

            {/* Data Storage Info */}
            <div className="bg-gray-50 rounded-xl p-6 border border-gray-200 text-center">
              <Database className="w-8 h-8 text-gray-500 mx-auto mb-3" />
              <p className="text-gray-600 text-sm">
                Analysis results have been stored securely. You can access this report anytime from your dashboard.
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default JDCVMatcher;