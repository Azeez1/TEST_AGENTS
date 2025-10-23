/**
 * AgentStatusGrid Component
 *
 * Grid container for displaying multiple AgentStatusCards with responsive layout,
 * filtering, sorting, and empty states.
 *
 * Usage:
 * <AgentStatusGrid
 *   agents={agentData}
 *   onAgentClick={(agent) => console.log('Selected:', agent)}
 *   filterStatus="active"
 * />
 */

import React, { useMemo, useState } from 'react';
import { AgentStatusCard, AgentStatus } from './AgentStatusCard';

export interface Agent {
  id: string;
  name: string;
  status: AgentStatus;
  lastRunTime: Date | null;
  description?: string;
}

export interface AgentStatusGridProps {
  /** Array of agent data */
  agents: Agent[];

  /** Callback when an agent card is clicked */
  onAgentClick?: (agent: Agent) => void;

  /** Optional status filter */
  filterStatus?: AgentStatus | 'all';

  /** Show agent descriptions (default: false) */
  showDetails?: boolean;

  /** Sort order (default: 'name') */
  sortBy?: 'name' | 'status' | 'lastRun';

  /** Optional CSS class */
  className?: string;
}

/**
 * Sort agents based on selected criteria
 */
const sortAgents = (agents: Agent[], sortBy: 'name' | 'status' | 'lastRun'): Agent[] => {
  return [...agents].sort((a, b) => {
    switch (sortBy) {
      case 'name':
        return a.name.localeCompare(b.name);

      case 'status':
        const statusOrder: Record<AgentStatus, number> = {
          active: 0,
          idle: 1,
          error: 2,
          offline: 3,
        };
        return statusOrder[a.status] - statusOrder[b.status];

      case 'lastRun':
        const timeA = a.lastRunTime?.getTime() ?? 0;
        const timeB = b.lastRunTime?.getTime() ?? 0;
        return timeB - timeA; // Most recent first

      default:
        return 0;
    }
  });
};

/**
 * Main AgentStatusGrid Component
 */
export const AgentStatusGrid: React.FC<AgentStatusGridProps> = ({
  agents,
  onAgentClick,
  filterStatus = 'all',
  showDetails = false,
  sortBy = 'name',
  className = '',
}) => {
  // Filter and sort agents
  const processedAgents = useMemo(() => {
    let filtered = agents;

    // Apply status filter
    if (filterStatus !== 'all') {
      filtered = agents.filter(agent => agent.status === filterStatus);
    }

    // Apply sorting
    return sortAgents(filtered, sortBy);
  }, [agents, filterStatus, sortBy]);

  // Status counts for summary
  const statusCounts = useMemo(() => {
    return agents.reduce((acc, agent) => {
      acc[agent.status] = (acc[agent.status] || 0) + 1;
      return acc;
    }, {} as Record<AgentStatus, number>);
  }, [agents]);

  return (
    <div className={className}>
      {/* Summary Stats */}
      <div className="mb-6 flex flex-wrap gap-4" role="status" aria-live="polite">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-700">Total Agents:</span>
          <span className="text-sm font-semibold text-gray-900">{agents.length}</span>
        </div>

        {statusCounts.active > 0 && (
          <div className="flex items-center gap-2">
            <span className="inline-block w-2 h-2 rounded-full bg-green-500" aria-hidden="true" />
            <span className="text-sm text-gray-600">
              {statusCounts.active} Active
            </span>
          </div>
        )}

        {statusCounts.idle > 0 && (
          <div className="flex items-center gap-2">
            <span className="inline-block w-2 h-2 rounded-full bg-blue-500" aria-hidden="true" />
            <span className="text-sm text-gray-600">
              {statusCounts.idle} Idle
            </span>
          </div>
        )}

        {statusCounts.error > 0 && (
          <div className="flex items-center gap-2">
            <span className="inline-block w-2 h-2 rounded-full bg-red-500" aria-hidden="true" />
            <span className="text-sm text-gray-600">
              {statusCounts.error} Error
            </span>
          </div>
        )}

        {statusCounts.offline > 0 && (
          <div className="flex items-center gap-2">
            <span className="inline-block w-2 h-2 rounded-full bg-gray-400" aria-hidden="true" />
            <span className="text-sm text-gray-600">
              {statusCounts.offline} Offline
            </span>
          </div>
        )}
      </div>

      {/* Grid or Empty State */}
      {processedAgents.length > 0 ? (
        <div
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
          role="list"
          aria-label="Agent status cards"
        >
          {processedAgents.map((agent) => (
            <AgentStatusCard
              key={agent.id}
              name={agent.name}
              status={agent.status}
              lastRunTime={agent.lastRunTime}
              description={agent.description}
              showDetails={showDetails}
              onClick={onAgentClick ? () => onAgentClick(agent) : undefined}
            />
          ))}
        </div>
      ) : (
        <div
          className="flex flex-col items-center justify-center py-12 px-4 text-center"
          role="status"
        >
          <svg
            className="w-12 h-12 text-gray-400 mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No agents found
          </h3>
          <p className="text-sm text-gray-600">
            {filterStatus !== 'all'
              ? `No agents with status "${filterStatus}"`
              : 'No agents available'}
          </p>
        </div>
      )}
    </div>
  );
};

// Display name for React DevTools
AgentStatusGrid.displayName = 'AgentStatusGrid';

export default AgentStatusGrid;
