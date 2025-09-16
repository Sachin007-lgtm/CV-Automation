import React from 'react';
import { FormSection, StringInput, TextAreaInput, StringListInput } from './ui/FormControls';

const JdFormEditor = ({ jdData, onUpdate }) => {
  const handleUpdate = (path, value) => {
    const newJdData = updateDeep(jdData, path, value);
    onUpdate(newJdData);
  };

  const updateDeep = (obj, path, value) => {
    const newObj = JSON.parse(JSON.stringify(obj));
    const keys = path.split('.');
    let current = newObj;
    for (let i = 0; i < keys.length - 1; i++) {
      if (current[keys[i]] === undefined || current[keys[i]] === null) {
        current[keys[i]] = {};
      }
      current = current[keys[i]];
    }
    current[keys[keys.length - 1]] = value;
    return newObj;
  };

  if (!jdData) return null;

  return (
    <div>
      <FormSection title="Job Details">
        <StringInput label="Job Title" value={jdData.jobTitle} onChange={v => handleUpdate('jobTitle', v)} />
        <StringInput label="Job ID" value={jdData.jobId} onChange={v => handleUpdate('jobId', v)} />
        <StringInput label="Employment Type" value={jdData.employmentType} onChange={v => handleUpdate('employmentType', v)} />
        <StringInput label="Date Posted" value={jdData.datePosted} onChange={v => handleUpdate('datePosted', v)} />
        <div className="md:col-span-2">
          <TextAreaInput label="Job Summary" value={jdData.jobSummary} onChange={v => handleUpdate('jobSummary', v)} rows={5} />
        </div>
      </FormSection>

      <FormSection title="Company Profile">
        <StringInput label="Company Name" value={jdData.companyProfile?.companyName} onChange={v => handleUpdate('companyProfile.companyName', v)} />
        <StringInput label="Industry" value={jdData.companyProfile?.industry} onChange={v => handleUpdate('companyProfile.industry', v)} />
        <StringInput label="Website" value={jdData.companyProfile?.website} onChange={v => handleUpdate('companyProfile.website', v)} />
        <div className="md:col-span-2">
          <TextAreaInput label="Description" value={jdData.companyProfile?.description} onChange={v => handleUpdate('companyProfile.description', v)} />
        </div>
      </FormSection>

      <FormSection title="Location">
        <StringInput label="City" value={jdData.location?.city} onChange={v => handleUpdate('location.city', v)} />
        <StringInput label="State" value={jdData.location?.state} onChange={v => handleUpdate('location.state', v)} />
        <StringInput label="Country" value={jdData.location?.country} onChange={v => handleUpdate('location.country', v)} />
        <StringInput label="Remote Status" value={jdData.location?.remoteStatus} onChange={v => handleUpdate('location.remoteStatus', v)} />
      </FormSection>

      <FormSection title="Responsibilities & Qualifications">
        <StringListInput label="Key Responsibilities" values={jdData.keyResponsibilities || []} onChange={v => handleUpdate('keyResponsibilities', v)} />
        <StringListInput label="Required Qualifications" values={jdData.qualifications?.required || []} onChange={v => handleUpdate('qualifications.required', v)} />
        <StringListInput label="Preferred Qualifications" values={jdData.qualifications?.preferred || []} onChange={v => handleUpdate('qualifications.preferred', v)} />
        <StringListInput label="Education Required" values={jdData.educationRequired || []} onChange={v => handleUpdate('educationRequired', v)} />
      </FormSection>
      
      <FormSection title="Filters">
        <StringInput label="Min Age" value={jdData.age_filter?.min_age} onChange={v => handleUpdate('age_filter.min_age', v)} />
        <StringInput label="Max Age" value={jdData.age_filter?.max_age} onChange={v => handleUpdate('age_filter.max_age', v)} />
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Gender</label>
          <select
            value={jdData.gender_filter || 'Any'}
            onChange={e => handleUpdate('gender_filter', e.target.value)}
            className="w-full border rounded px-3 py-2 text-sm shadow-sm focus:ring-red-500 focus:border-red-500"
          >
            <option>Any</option>
            <option>Male</option>
            <option>Female</option>
          </select>
        </div>
      </FormSection>

      <FormSection title="Compensation & Application">
        <StringInput label="Salary Range" value={jdData.compensationAndBenefits?.salaryRange} onChange={v => handleUpdate('compensationAndBenefits.salaryRange', v)} />
        <StringListInput label="Benefits" values={jdData.compensationAndBenefits?.benefits || []} onChange={v => handleUpdate('compensationAndBenefits.benefits', v)} />
        <StringInput label="How to Apply" value={jdData.applicationInfo?.howToApply} onChange={v => handleUpdate('applicationInfo.howToApply', v)} />
        <StringInput label="Apply Link" value={jdData.applicationInfo?.applyLink} onChange={v => handleUpdate('applicationInfo.applyLink', v)} />
        <StringInput label="Contact Email" value={jdData.applicationInfo?.contactEmail} onChange={v => handleUpdate('applicationInfo.contactEmail', v)} />
      </FormSection>

      <FormSection title="Keywords">
        <StringListInput label="Extracted Keywords" values={jdData.extractedKeywords || []} onChange={v => handleUpdate('extractedKeywords', v)} />
      </FormSection>
    </div>
  );
};

export default JdFormEditor;
