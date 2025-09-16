import React, { useState } from 'react';
import { FormSection, StringInput } from './ui/FormControls';
import ObjectListEditor from './ObjectListEditor';
import { ExperienceItemEditor, EducationItemEditor, ProjectItemEditor, SkillItemEditor } from './CvEditorItems';

const CvFormEditor = ({ cvData, onUpdate, onCancel }) => {
    const [editedCv, setEditedCv] = useState(cvData);

    const handleUpdate = (path, value) => {
        const newCvData = updateDeep(editedCv, path, value);
        setEditedCv(newCvData);
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

    const handleSave = () => {
        onUpdate(editedCv);
    };

    if (!editedCv) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
                <h3 className="text-2xl font-bold text-gray-800 mb-6">Edit CV: {editedCv["Personal Data"]?.firstName} {editedCv["Personal Data"]?.lastName}</h3>
                
                <div className="space-y-6">
                    <FormSection title="Personal Data">
                        <StringInput label="First Name" value={editedCv["Personal Data"]?.firstName} onChange={v => handleUpdate('Personal Data.firstName', v)} />
                        <StringInput label="Last Name" value={editedCv["Personal Data"]?.lastName} onChange={v => handleUpdate('Personal Data.lastName', v)} />
                        <StringInput label="Email" value={editedCv["Personal Data"]?.email} onChange={v => handleUpdate('Personal Data.email', v)} />
                        <StringInput label="Phone" value={editedCv["Personal Data"]?.phone} onChange={v => handleUpdate('Personal Data.phone', v)} />
                        <StringInput label="LinkedIn" value={editedCv["Personal Data"]?.linkedin} onChange={v => handleUpdate('Personal Data.linkedin', v)} />
                        <StringInput label="Portfolio" value={editedCv["Personal Data"]?.portfolio} onChange={v => handleUpdate('Personal Data.portfolio', v)} />
                        <StringInput label="City" value={editedCv["Personal Data"]?.location?.city} onChange={v => handleUpdate('Personal Data.location.city', v)} />
                        <StringInput label="State" value={editedCv["Personal Data"]?.location?.state} onChange={v => handleUpdate('Personal Data.location.state', v)} />
                        <StringInput label="Country" value={editedCv["Personal Data"]?.location?.country} onChange={v => handleUpdate('Personal Data.location.country', v)} />
                        <StringInput label="Age" value={editedCv["Personal Data"]?.age} onChange={v => handleUpdate('Personal Data.age', v)} />
                        <StringInput label="Gender" value={editedCv["Personal Data"]?.gender} onChange={v => handleUpdate('Personal Data.gender', v)} />
                    </FormSection>

                    <FormSection title="Experiences">
                        <ObjectListEditor
                            label="Experiences"
                            items={editedCv.Experiences || []}
                            onUpdate={v => handleUpdate('Experiences', v)}
                            itemEditor={ExperienceItemEditor}
                            newItem={{ jobTitle: '', company: '', location: '', startDate: '', endDate: '', description: [], technologiesUsed: [] }}
                        />
                    </FormSection>

                    <FormSection title="Education">
                        <ObjectListEditor
                            label="Education"
                            items={editedCv.Education || []}
                            onUpdate={v => handleUpdate('Education', v)}
                            itemEditor={EducationItemEditor}
                            newItem={{ institution: '', degree: '', fieldOfStudy: '', startDate: '', endDate: '', grade: '', description: '' }}
                        />
                    </FormSection>

                    <FormSection title="Projects">
                        <ObjectListEditor
                            label="Projects"
                            items={editedCv.Projects || []}
                            onUpdate={v => handleUpdate('Projects', v)}
                            itemEditor={ProjectItemEditor}
                            newItem={{ projectName: '', description: '', technologiesUsed: [], link: '', startDate: '', endDate: '' }}
                        />
                    </FormSection>

                    <FormSection title="Skills">
                         <ObjectListEditor
                            label="Skills"
                            items={editedCv.Skills || []}
                            onUpdate={v => handleUpdate('Skills', v)}
                            itemEditor={SkillItemEditor}
                            newItem={{ category: '', skillName: '' }}
                        />
                    </FormSection>
                </div>

                <div className="mt-8 flex justify-end gap-4">
                    <button onClick={onCancel} className="px-6 py-2 bg-gray-200 text-gray-700 font-semibold rounded-lg hover:bg-gray-300 transition-colors">Cancel</button>
                    <button onClick={handleSave} className="px-6 py-2 bg-gradient-to-r from-red-500 to-red-600 text-white font-semibold rounded-lg hover:from-red-600 hover:to-red-700 transition-colors shadow-md">Save Changes</button>
                </div>
            </div>
        </div>
    );
};

export default CvFormEditor;
