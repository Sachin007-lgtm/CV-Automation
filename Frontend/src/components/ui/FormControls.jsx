import React from 'react';
import { X, Plus } from 'lucide-react';

export const FormSection = ({ title, children }) => (
  <div className="mb-6 p-4 border rounded-lg bg-gray-50">
    <h4 className="text-lg font-semibold text-gray-800 mb-4">{title}</h4>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {children}
    </div>
  </div>
);

export const StringInput = ({ label, value, onChange }) => {
  const inputId = `string-input-${label.replace(/\s+/g, '-').toLowerCase()}`;
  return (
    <div>
      <label htmlFor={inputId} className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <input
        id={inputId}
        type="text"
        value={value || ''}
        onChange={e => onChange(e.target.value)}
        className="w-full border rounded px-3 py-2 text-sm shadow-sm focus:ring-red-500 focus:border-red-500"
      />
    </div>
  );
};

export const TextAreaInput = ({ label, value, onChange, rows = 3 }) => {
  const textareaId = `textarea-input-${label.replace(/\s+/g, '-').toLowerCase()}`;
  return (
    <div>
      <label htmlFor={textareaId} className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <textarea
        id={textareaId}
        value={value || ''}
        onChange={e => onChange(e.target.value)}
        rows={rows}
        className="w-full border rounded px-3 py-2 text-sm shadow-sm focus:ring-red-500 focus:border-red-500"
      />
    </div>
  );
};

export const StringListInput = ({ label, values, onChange }) => {
  const listId = `string-list-${label.replace(/\s+/g, '-').toLowerCase()}`;
  const handleItemChange = (index, newValue) => {
    const newValues = [...values];
    newValues[index] = newValue;
    onChange(newValues);
  };

  const handleAddItem = () => {
    onChange([...values, '']);
  };

  const handleRemoveItem = (index) => {
    onChange(values.filter((_, i) => i !== index));
  };

  return (
    <div className="md:col-span-2">
      <label htmlFor={listId} className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      {values.map((item, index) => {
        const itemId = `${listId}-item-${index}`;
        return (
          <div key={index} className="flex items-center gap-2 mb-2">
            <input
              id={itemId}
              type="text"
              value={item}
              onChange={e => handleItemChange(index, e.target.value)}
              className="w-full border rounded px-3 py-2 text-sm shadow-sm focus:ring-red-500 focus:border-red-500"
            />
            <button onClick={() => handleRemoveItem(index)} className="text-red-500 hover:text-red-700 p-1 rounded-full bg-red-100 hover:bg-red-200">
              <X className="w-4 h-4" />
            </button>
          </div>
        );
      })}
      <button onClick={handleAddItem} className="text-sm text-red-600 hover:text-red-800 font-medium flex items-center gap-1">
        <Plus className="w-4 h-4" /> Add Item
      </button>
    </div>
  );
};
