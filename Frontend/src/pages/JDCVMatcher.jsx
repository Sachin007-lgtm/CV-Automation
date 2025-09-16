import React, { useState, useCallback, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Brain, Zap, Target, Clock, Briefcase, LogOut, Users } from 'lucide-react';
import api from '../api';
import useAuth from '../hooks/useAuth';

import Stepper from '../components/ui/Stepper';
import ProcessingLoader from '../components/ui/ProcessingLoader';
import CvFormEditor from '../components/CvFormEditor';
import UploadStep from './home/components/UploadStep';
import ReviewJdStep from './home/components/ReviewJdStep';
import ReviewResumesStep from './home/components/ReviewResumesStep';
import ResultsStep from './home/components/ResultsStep';
import PastAnalyses from './home/components/PastAnalyses';
import SelectJdStep from './home/components/SelectJdStep';
import UploadCvForJdStep from './home/components/UploadCvForJdStep';

const defaultSkillCategories = (skills = []) => ({
  critical: skills,
  important: [],
  extra: []
});

const JDCVMatcher = ({ isPastAnalysesPage }) => {
  const { user, logout } = useAuth();
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
  const [showJsonView, setShowJsonView] = useState(false);
  const [editingCvIndex, setEditingCvIndex] = useState(null);
  const [view, setView] = useState(isPastAnalysesPage ? 'past' : 'main');

  // New state for recruiter flow
  const [jds, setJds] = useState([]);
  const [selectedJd, setSelectedJd] = useState(null);

  useEffect(() => {
    setView(isPastAnalysesPage ? 'past' : 'main');
  }, [isPastAnalysesPage]);

  useEffect(() => {
    if (user?.role === 'recruiter') {
      const fetchJds = async () => {
        setProcessing(true);
        try {
          const response = await api.get('/jds');
          setJds(response.data.filter(jd => jd.status === 'Active'));
        } catch (err) {
          alert('Failed to fetch job descriptions.');
        } finally {
          setProcessing(false);
        }
      };
      fetchJds();
    }
  }, [user]);

  const handleBack = () => {
    setStep(prev => {
      if (user?.role === 'recruiter') {
        if (prev === 6) return 4;
        if (prev === 4) return 2;
        if (prev === 2) return 1;
        return 1;
      } else { // Admin / Backend Team
        if (prev === 7) return 5;
        if (prev === 5) return 3;
        if (prev === 3) return 1;
        return 1;
      }
    });
  };

  const handleNext = () => {
    setStep(prev => prev + 1);
  };

  // --- File Handlers ---
  const handleDrop = useCallback((e, type) => {
    e.preventDefault();
    setDragOver(prev => ({ ...prev, [type]: false }));
    const droppedFiles = Array.from(e.dataTransfer.files);
    if (droppedFiles.length > 0) {
        if (type === 'cv') {
          setFiles(prev => ({ ...prev, cv: droppedFiles }));
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

  const handleRemoveFile = (type, index = null) => {
    setFiles(prev => {
      const newFiles = { ...prev };
      if (type === 'jd') {
        newFiles.jd = null;
      } else if (type === 'cv') {
        if (index !== null) {
          newFiles.cv.splice(index, 1);
        } else {
          newFiles.cv = [];
        }
      }
      return newFiles;
    });
  };

 const handleFileSelect = (e, type) => {
    const selectedFiles = Array.from(e.target.files);
    if (type === 'cv') {
      setFiles(prev => ({ ...prev, cv: selectedFiles }));
    } else {
      setFiles(prev => ({ ...prev, [type]: selectedFiles[0] }));
    }
  };

  const handleSelectJd = (jd) => {
    setSelectedJd(jd);
    const details = jd.details || {};
    setJdJson(details);
    setEditedJdJson(details);
    setSkillCategories(defaultSkillCategories(details.requiredSkills || []));
    setStep(2); // Move to CV upload step for recruiter
  };

  const saveJd = async () => {
    if (!editedJdJson) return;
    setProcessing(true);
    try {
      await api.post(`/save_jd`, editedJdJson);
      alert('Job Description saved successfully!');
      resetApp();
    } catch (err) {
      setProcessing(false);
      alert('Error saving JD: ' + (err.response?.data?.error || err.message));
    }
  };

  // --- Step 2: Extract JD JSON ---
  const extractJD = async () => {
    if (!files.jd) return;
    setProcessing(true);
    setStep(2);
    const formData = new FormData();
    formData.append('jd_file', files.jd);
    try {
      const res = await api.post(`/extract_jd`, formData, {
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
    const cvFiles = files.cv;
    if (!editedJdJson || !cvFiles || cvFiles.length === 0) return;
    
    setProcessing(true);
    setStep(user?.role === 'recruiter' ? 3 : 4);

    const jdWithCategories = {
      ...editedJdJson,
      requiredSkills: skillCategories,
    };
    const formData = new FormData();
    formData.append('jd_json', JSON.stringify(jdWithCategories));
    for (let i = 0; i < cvFiles.length; i++) {
      formData.append('resume_files', cvFiles[i]);
    }
    try {
      const res = await api.post(`/extract_resumes`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setCvExtractionResults(res.data);
      setProcessing(false);
      setStep(user?.role === 'recruiter' ? 4 : 5);
    } catch (err) {
      setProcessing(false);
      alert('Error extracting resumes: ' + (err.response?.data?.error || err.message));
    }
  };

  // --- Step 5: Match ---
  const matchResults = async () => {
    if (!editedJdJson || !cvExtractionResults) return;
    setProcessing(true);
    setStep(user?.role === 'recruiter' ? 5 : 6);
    
    // Send skill categories as structured data, not flattened
    const jdWithSkillCategories = {
      ...editedJdJson,
      requiredSkills: skillCategories, // Send the categorized structure
    };
    
    try {
      const res = await api.post(`/match`, {
        jd_json: jdWithSkillCategories, // Use the object with skill categories
        cvs: cvExtractionResults
      });
      setFinalResults(res.data);
      setProcessing(false);
      setStep(user?.role === 'recruiter' ? 6 : 7);
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
    setView('main');
    setSelectedJd(null);
  };

  const handleUpdateCv = (index, updatedCv) => {
    const newCvResults = [...cvExtractionResults];
    newCvResults[index].cv_json = updatedCv;
    setCvExtractionResults(newCvResults);
    setEditingCvIndex(null);
  };

  const renderContent = () => {
    if (view === 'past') {
      return <PastAnalyses />;
    }

    if (user?.role === 'recruiter') {
        switch (step) {
            case 1:
                return <SelectJdStep jds={jds} onSelectJd={handleSelectJd} processing={processing} />;
            case 2:
                return (
                    <UploadCvForJdStep
                        jd={selectedJd}
                        files={files.cv}
                        dragOver={dragOver.cv}
                        handleDrop={(e) => handleDrop(e, 'cv')}
                        handleDragOver={(e) => handleDragOver(e, 'cv')}
                        handleDragLeave={(e) => handleDragLeave(e, 'cv')}
                        handleFileSelect={(e) => handleFileSelect(e, 'cv')}
                        extractResumes={extractResumes}
                        processing={processing}
                    />
                );
            case 4: // Review resumes
                return (
                    <ReviewResumesStep
                        cvExtractionResults={cvExtractionResults}
                        setEditingCvIndex={setEditingCvIndex}
                        matchResults={matchResults}
                        resetApp={resetApp}
                        processing={processing}
                    />
                );
            case 6: // Results
                return (
                    <ResultsStep
                        finalResults={finalResults}
                        expandedIdx={expandedIdx}
                        setExpandedIdx={setExpandedIdx}
                        skillCategories={skillCategories}
                        resetApp={resetApp}
                    />
                );
            default:
                return null;
        }
    }

    // Admin / Backend Team Flow
    switch (step) {
      case 1:
        return (
          <UploadStep
            files={files}
            dragOver={dragOver}
            handleDrop={handleDrop}
            handleDragOver={handleDragOver}
            handleDragLeave={handleDragLeave}
            handleFileSelect={handleFileSelect}
            handleRemoveFile={handleRemoveFile}
            extractJD={extractJD}
            processing={processing}
          />
        );
      case 3:
        return (
          <ReviewJdStep
            editedJdJson={editedJdJson}
            skillCategories={skillCategories}
            newSkill={newSkill}
            showJsonView={showJsonView}
            setEditedJdJson={setEditedJdJson}
            moveSkill={moveSkill}
            addSkill={addSkill}
            removeSkill={removeSkill}
            setNewSkill={setNewSkill}
            setShowJsonView={setShowJsonView}
            extractResumes={extractResumes}
            saveJd={saveJd}
            resetApp={resetApp}
            processing={processing}
            user={user}
          />
        );
      case 5:
        return (
          <ReviewResumesStep
            cvExtractionResults={cvExtractionResults}
            setEditingCvIndex={setEditingCvIndex}
            matchResults={matchResults}
            resetApp={resetApp}
            processing={processing}
          />
        );
      case 7:
        return (
          <ResultsStep
            finalResults={finalResults}
            expandedIdx={expandedIdx}
            setExpandedIdx={setExpandedIdx}
            skillCategories={skillCategories}
            resetApp={resetApp}
          />
        );
      default:
        return null;
    }
  };

  return (
    <>
        {view === 'main' && user?.role !== 'recruiter' && <Stepper step={step} onBack={handleBack} />}
        
        {renderContent()}

        {processing && <ProcessingLoader />}

        {editingCvIndex !== null && (
            <CvFormEditor
                cvData={cvExtractionResults[editingCvIndex].cv_json}
                onUpdate={(updatedCv) => handleUpdateCv(editingCvIndex, updatedCv)}
                onCancel={() => setEditingCvIndex(null)}
            />
        )}
    </>
  );
};

export default JDCVMatcher;
