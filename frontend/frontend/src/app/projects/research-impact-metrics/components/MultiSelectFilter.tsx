import React from 'react';

interface MultiSelectFilterProps {
    label: string;
    options: string[];
    selectedOptions: string[];
    searchTerm: string;
    onSearchChange: (term: string) => void;
    onSelectionChange: (selected: string[]) => void;
    onSelectAll: () => void;
    onDeselectAll: () => void;
}

export default function MultiSelectFilter({
    label,
    options,
    selectedOptions,
    searchTerm,
    onSearchChange,
    onSelectionChange,
    onSelectAll,
    onDeselectAll
}: MultiSelectFilterProps) {
    // Filter options based on search term
    const filteredOptions = options.filter(option =>
        option.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const handleOptionChange = (option: string) => {
        if (selectedOptions.includes(option)) {
            onSelectionChange(selectedOptions.filter(item => item !== option));
        } else {
            onSelectionChange([...selectedOptions, option]);
        }
    };

    return (
        <div className="space-y-2">
            <div className="flex justify-between items-center">
                <label className="text-sm font-semibold">{label}:</label>
                <div className="space-x-2">
                    <button
                        onClick={onSelectAll}
                        className="text-sm text-blue-600 hover:text-blue-800"
                    >
                        Select All
                    </button>
                    <button
                        onClick={onDeselectAll}
                        className="text-sm text-blue-600 hover:text-blue-800"
                    >
                        Deselect All
                    </button>
                </div>
            </div>
            <input
                type="text"
                placeholder={`Search ${label.toLowerCase()}...`}
                value={searchTerm}
                onChange={(e) => onSearchChange(e.target.value)}
                className="w-full p-2 border rounded text-sm"
            />
            <div className="border rounded max-h-48 overflow-y-auto">
                {filteredOptions.map(option => (
                    <label
                        key={option}
                        className="flex items-center p-2 hover:bg-gray-50 cursor-pointer"
                    >
                        <input
                            type="checkbox"
                            checked={selectedOptions.includes(option)}
                            onChange={() => handleOptionChange(option)}
                            className="mr-2"
                        />
                        <span className="text-sm">{option}</span>
                    </label>
                ))}
                {filteredOptions.length === 0 && (
                    <div className="p-2 text-gray-500 text-sm">
                        No matches found
                    </div>
                )}
            </div>
            <div className="text-sm text-gray-500">
                {selectedOptions.length} of {options.length} selected
            </div>
        </div>
    );
} 