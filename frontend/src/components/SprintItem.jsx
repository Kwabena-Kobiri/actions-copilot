import React, { useState } from 'react';
import { useSprint } from '../context/SprintContext';

export default function SprintItem({ sprint }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const { selectSprintItem } = useSprint();

  const handleSprintItemClick = (item) => {
    selectSprintItem(item, sprint);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'pending':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'in_progress':
        return 'In Progress';
      case 'pending':
        return 'Pending';
      default:
        return 'Unknown';
    }
  };

  return (
    <div className="border-b border-gray-200">
      {/* Sprint Header */}
      <div
        className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <h3 className="text-sm font-medium text-gray-900">
              {sprint.title}
            </h3>
            <p className="text-xs text-gray-500 mt-1">
              {sprint.duration} • {sprint.total_items} items
            </p>
          </div>
          <div className="ml-2">
            <svg
              className={`w-5 h-5 text-gray-400 transition-transform ${
                isExpanded ? 'rotate-180' : ''
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </div>
        </div>
      </div>

      {/* Sprint Items */}
      {isExpanded && (
        <div className="bg-gray-50 border-t border-gray-200">
          {sprint.items.map((item) => (
            <div
              key={item.item_id}
              className="p-3 border-b border-gray-200 last:border-b-0 cursor-pointer hover:bg-gray-100 transition-colors"
              onClick={() => handleSprintItemClick(item)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {item.task}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    Due: {item.due_date}
                  </p>
                </div>
                <div className="ml-2 flex-shrink-0">
                  <span
                    className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(
                      item.status
                    )}`}
                  >
                    {getStatusText(item.status)}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
