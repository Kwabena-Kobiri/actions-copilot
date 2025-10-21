import React from 'react';
import { useSprint } from '../context/SprintContext';

export default function ConfirmationModal() {
  const { showConfirmation, pendingSprintItem, confirmSwitch, cancelSwitch } = useSprint();

  if (!showConfirmation || !pendingSprintItem) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
        <div className="mb-4">
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Switch Sprint Item?
          </h3>
          <p className="text-sm text-gray-600">
            Do you want to switch to "{pendingSprintItem.task}" from {pendingSprintItem.sprint_title}?
          </p>
        </div>
        
        <div className="flex justify-end space-x-3">
          <button
            onClick={cancelSwitch}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Cancel
          </button>
          <button
            onClick={confirmSwitch}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Yes, Switch
          </button>
        </div>
      </div>
    </div>
  );
}
