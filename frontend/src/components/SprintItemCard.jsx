import React from 'react';
import { useSprint } from '../context/SprintContext';

export default function SprintItemCard() {
  const { selectedSprintItem } = useSprint();

  if (!selectedSprintItem) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-4 mb-4">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="text-sm font-medium text-gray-900 mb-1">
            {selectedSprintItem.sprint_title}
          </h3>
          <p className="text-sm text-gray-700">
            {selectedSprintItem.task}
          </p>
        </div>
        <div className="ml-4 flex-shrink-0">
          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
            selectedSprintItem.status === 'completed' 
              ? 'bg-green-100 text-green-800'
              : selectedSprintItem.status === 'in_progress'
              ? 'bg-yellow-100 text-yellow-800'
              : 'bg-gray-100 text-gray-800'
          }`}>
            {selectedSprintItem.status === 'completed' 
              ? 'Completed'
              : selectedSprintItem.status === 'in_progress'
              ? 'In Progress'
              : 'Pending'
            }
          </span>
        </div>
      </div>
    </div>
  );
}
