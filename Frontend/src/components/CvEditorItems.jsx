import React from 'react';
import { StringInput, TextAreaInput, StringListInput } from './ui/FormControls';

export const ExperienceItemEditor = ({ item, onUpdate, onRemove }) => (
    <div className="p-4 border rounded-lg mb-2 bg-white">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <StringInput label="Job Title" value={item.jobTitle} onChange={v => onUpdate({ ...item, jobTitle: v })} />
            <StringInput label="Company" value={item.company} onChange={v => onUpdate({ ...item, company: v })} />
            <StringInput label="Location" value={item.location} onChange={v => onUpdate({ ...item, location: v })} />
            <StringInput label="Start Date" value={item.startDate} onChange={v => onUpdate({ ...item, startDate: v })} />
            <StringInput label="End Date" value={item.endDate} onChange={v => onUpdate({ ...item, endDate: v })} />
            <div className="md:col-span-2">
                <StringListInput label="Description" values={item.description || []} onChange={v => onUpdate({ ...item, description: v })} />
            </div>
            <div className="md:col-span-2">
                <StringListInput label="Technologies Used" values={item.technologiesUsed || []} onChange={v => onUpdate({ ...item, technologiesUsed: v })} />
            </div>
        </div>
        <button onClick={onRemove} className="mt-2 text-sm text-red-600 hover:text-red-800">Remove Experience</button>
    </div>
);

export const EducationItemEditor = ({ item, onUpdate, onRemove }) => (
    <div className="p-4 border rounded-lg mb-2 bg-white">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <StringInput label="Institution" value={item.institution} onChange={v => onUpdate({ ...item, institution: v })} />
            <StringInput label="Degree" value={item.degree} onChange={v => onUpdate({ ...item, degree: v })} />
            <StringInput label="Field of Study" value={item.fieldOfStudy} onChange={v => onUpdate({ ...item, fieldOfStudy: v })} />
            <StringInput label="Start Date" value={item.startDate} onChange={v => onUpdate({ ...item, startDate: v })} />
            <StringInput label="End Date" value={item.endDate} onChange={v => onUpdate({ ...item, endDate: v })} />
            <StringInput label="Grade" value={item.grade} onChange={v => onUpdate({ ...item, grade: v })} />
            <div className="md:col-span-2">
                <TextAreaInput label="Description" value={item.description} onChange={v => onUpdate({ ...item, description: v })} />
            </div>
        </div>
        <button onClick={onRemove} className="mt-2 text-sm text-red-600 hover:text-red-800">Remove Education</button>
    </div>
);

export const ProjectItemEditor = ({ item, onUpdate, onRemove }) => (
    <div className="p-4 border rounded-lg mb-2 bg-white">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <StringInput label="Project Name" value={item.projectName} onChange={v => onUpdate({ ...item, projectName: v })} />
            <StringInput label="Link" value={item.link} onChange={v => onUpdate({ ...item, link: v })} />
            <StringInput label="Start Date" value={item.startDate} onChange={v => onUpdate({ ...item, startDate: v })} />
            <StringInput label="End Date" value={item.endDate} onChange={v => onUpdate({ ...item, endDate: v })} />
            <div className="md:col-span-2">
                <TextAreaInput label="Description" value={item.description} onChange={v => onUpdate({ ...item, description: v })} />
            </div>
            <div className="md:col-span-2">
                <StringListInput label="Technologies Used" values={item.technologiesUsed || []} onChange={v => onUpdate({ ...item, technologiesUsed: v })} />
            </div>
        </div>
        <button onClick={onRemove} className="mt-2 text-sm text-red-600 hover:text-red-800">Remove Project</button>
    </div>
);

export const SkillItemEditor = ({ item, onUpdate, onRemove }) => (
    <div className="p-4 border rounded-lg mb-2 bg-white flex items-center gap-4">
        <StringInput label="Category" value={item.category} onChange={v => onUpdate({ ...item, category: v })} />
        <StringInput label="Skill Name" value={item.skillName} onChange={v => onUpdate({ ...item, skillName: v })} />
        <button onClick={onRemove} className="mt-6 text-sm text-red-600 hover:text-red-800">Remove</button>
    </div>
);
