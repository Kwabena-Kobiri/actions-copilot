import React from 'react';
import SprintItem from './SprintItem';
import AutoModeToggle from './AutoModeToggle';
import { useSprint } from '../context/SprintContext';

export default function SprintList() {
  const { sprints } = useSprint();

  return (
    <div className="h-full flex flex-col bg-white border-r border-gray-200">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-gray-50">
        <h2 className="text-lg font-semibold text-gray-900">Sprints</h2>
      </div>

      {/* Sprint Items */}
      <div className="flex-1 overflow-y-auto">
        {sprints.map((sprint) => (
          <SprintItem key={sprint.sprint_id} sprint={sprint} />
        ))}
      </div>

      {/* Auto Mode Toggle */}
      <AutoModeToggle />
    </div>
  );
}
