import React from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import SkillBadge from '../../../components/ui/SkillBadge';

const ResultsStep = ({ finalResults, expandedIdx, setExpandedIdx, skillCategories, resetApp }) => (
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
            <th className="px-4 py-2 text-left">Match Status</th>
            <th className="px-4 py-2 text-left">Filter Status</th>
            <th className="px-4 py-2 text-left">Critical Skill Score</th>
            <th className="px-4 py-2 text-left">Important Skill Score</th>
            <th className="px-4 py-2 text-left">Desired Skill Score</th>
            <th className="px-4 py-2 text-left">Skills Match</th>
            <th className="px-4 py-2 text-left">More Details</th>
          </tr>
        </thead>
        <tbody>
            {finalResults.results.map((candidate, idx) => {
              const filterStatus = candidate.filter_status;
              const filterColor = filterStatus.passed ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700';
              
              // Match status styling
              const matchStatus = candidate.match_details?.status || 'Pending';
              const statusColor = matchStatus === 'Pass' ? 'bg-green-100 text-green-700' : 
                                 matchStatus === 'Rejected' ? 'bg-red-100 text-red-700' : 
                                 'bg-yellow-100 text-yellow-700';

              // Category scores (presence ratios converted to %)
              const sd = candidate.match_details?.skills_details || {};
              const critPct = sd.critical ? (sd.critical.presence_ratio * 100).toFixed(1) + '%' : 'N/A';
              const impPct = sd.important ? (sd.important.presence_ratio * 100).toFixed(1) + '%' : 'N/A';
              const desPct = sd.extra ? (sd.extra.presence_ratio * 100).toFixed(1) + '%' : 'N/A';

              return (
            <React.Fragment key={idx}>
                  <tr className={`border-t text-sm ${matchStatus === 'Rejected' ? 'bg-red-100' : ''}`}>
                    <td className="px-4 py-2 font-semibold whitespace-nowrap">{candidate.candidate_name}</td>
                    <td className="px-4 py-2 font-bold text-lg text-gray-800 whitespace-nowrap">{candidate.match_score?.toFixed(2)}%</td>
                    <td className={`px-4 py-2 font-semibold whitespace-nowrap ${statusColor}`}> 
                      {matchStatus}
                    </td>
                    <td className={`px-4 py-2 font-semibold whitespace-nowrap ${filterColor}`} title={filterStatus.reason}> 
                      {filterStatus.passed ? 'Pass' : 'Fail'}
                    </td>
                    <td className="px-4 py-2 whitespace-nowrap font-semibold">{critPct}</td>
                    <td className="px-4 py-2 whitespace-nowrap font-semibold">{impPct}</td>
                    <td className="px-4 py-2 whitespace-nowrap font-semibold">{desPct}</td>
                    <td className="px-4 py-2 whitespace-nowrap">
                      <div className="flex flex-col">
                        <span className="font-semibold">{(candidate.match_details?.skills_match * 100)?.toFixed(1)}%</span>
                        <span className="text-xs text-gray-500">{candidate.match_details?.skills_match_type || 'semantic'}</span>
                      </div>
                    </td>
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
                      <td colSpan={10} className="bg-gray-50 px-6 py-4 border-t">
                        <div className="mb-4">
                          {matchStatus === 'Rejected' && (
                            <div className="mb-4 p-4 border border-red-400 bg-red-50 rounded-lg text-red-700 font-semibold">
                              This resume is Rejected based on skill criteria.
                            </div>
                          )}
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
                        
                        {/* Weighted Skills Matching Details */}
                        {candidate.match_details?.skills_match_type === 'weighted' && candidate.match_details?.skills_details && (
                          <div className="mb-6">
                            <h4 className="font-semibold text-blue-700 mb-3 text-lg">Weighted Skills Matching Analysis</h4>
                            <div className="grid md:grid-cols-3 gap-4">
                              {Object.entries(candidate.match_details.skills_details).map(([category, details]) => (
                                <div key={category} className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-400">
                                  <div className="flex justify-between items-center mb-2">
                                    <h5 className={`font-semibold capitalize ${category === 'critical' ? 'text-red-700' : category === 'important' ? 'text-yellow-700' : 'text-blue-700'}`}>
                                      {category} Skills
                                    </h5>
                                    <span className="text-sm font-bold text-gray-800">
                                      {details.present_count}/{details.total}
                                    </span>
                                  </div>
                                  <div className="mb-2">
                                    <div className="flex justify-between text-sm mb-1">
                                      <span>Match Score:</span>
                                      <span className="font-semibold">{(details.score * 100).toFixed(1)}%</span>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-2">
                                      <div 
                                        className={`h-2 rounded-full ${category === 'critical' ? 'bg-red-500' : category === 'important' ? 'bg-yellow-500' : 'bg-blue-500'}`}
                                        style={{ width: `${(details.presence_ratio * 100)}%` }}
                                      ></div>
                                    </div>
                                  </div>
                                  <div className="text-xs text-gray-600">
                                    <div>Present: {details.present.length > 0 ? details.present.join(', ') : 'None'}</div>
                                    <div>Absent: {details.absent.length > 0 ? details.absent.join(', ') : 'None'}</div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                        
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
);

export default ResultsStep;
