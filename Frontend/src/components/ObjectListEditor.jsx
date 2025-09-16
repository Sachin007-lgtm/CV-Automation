import React from 'react';
import { Plus } from 'lucide-react';

const ObjectListEditor = ({ label, items, onUpdate, itemEditor: ItemEditor, newItem }) => {
    const handleUpdateItem = (index, updatedItem) => {
        const newItems = [...items];
        newItems[index] = updatedItem;
        onUpdate(newItems);
    };

    const handleAddItem = () => {
        onUpdate([...items, newItem]);
    };

    const handleRemoveItem = (index) => {
        onUpdate(items.filter((_, i) => i !== index));
    };

    return (
        <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">{label}</label>
            {items.map((item, index) => (
                <ItemEditor
                    key={index}
                    item={item}
                    onUpdate={(updatedItem) => handleUpdateItem(index, updatedItem)}
                    onRemove={() => handleRemoveItem(index)}
                />
            ))}
            <button onClick={handleAddItem} className="mt-2 text-sm text-red-600 hover:text-red-800 font-medium flex items-center gap-1">
                <Plus className="w-4 h-4" /> Add {label.slice(0, -1)}
            </button>
        </div>
    );
};

export default ObjectListEditor;
