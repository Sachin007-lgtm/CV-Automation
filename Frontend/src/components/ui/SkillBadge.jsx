import React from 'react';

const SkillBadge = ({ text, type }) => {
  const color = type === "present" ? "bg-green-100 text-green-700"
    : type === "partial" ? "bg-yellow-100 text-yellow-700"
    : "bg-red-100 text-red-700";
  return <span className={`inline-block px-2 py-1 rounded-full text-xs font-semibold mr-1 mb-1 ${color}`}>{text}</span>;
};

export default SkillBadge;
