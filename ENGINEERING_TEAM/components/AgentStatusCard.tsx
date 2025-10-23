/**
 * AgentStatusCard Component
 *
 * Displays individual agent status with name, status indicator, and last run time.
 * Features: Responsive design, accessibility, status animations, and relative time formatting.
 *
 * Usage:
 * <AgentStatusCard
 *   name="copywriter"
 *   status="active"
 *   lastRunTime={new Date('2025-10-22T10:30:00')}
 *   onClick={() => console.log('Agent clicked')}
 * />
 */

import React, { useMemo } from 'react';

// Type definitions
export type AgentStatus = 'active' | 'idle' | 'error' | 'offline';

export interface AgentStatusCardProps {
  /** Agent name (e.g., 'copywriter', 'visual-designer') */
  name: string;

  /** Current status of the agent */
  status: AgentStatus;

  /** Last time the agent ran */
  lastRunTime: Date | null;

  /** Optional description or capability summary */
  description?: string;

  /** Optional click handler for card interaction */
  onClick?: () => void;

  /** Optional CSS class for custom styling */
  className?: string;

  /** Show detailed view with description (default: false) */
  showDetails?: boolean;
}

/**
 * Formats a date to relative time (e.g., "2 minutes ago", "1 hour ago")
 */
const formatRelativeTime = (date: Date | null): string => {
  if (!date) return 'Never';

  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSecs < 60) return 'Just now';
  if (diffMins < 60) return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
  if (diffDays < 7) return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;

  return date.toLocaleDateString();
};

/**
 * Returns status-specific styling configuration
 */
const getStatusConfig = (status: AgentStatus) => {
  const configs = {
    active: {
      color: 'bg-green-500',
      ring: 'ring-green-500/20',
      pulse: 'animate-pulse',
      text: 'text-green-700',
      label: 'Active',
      ariaLabel: 'Agent is currently active',
    },
    idle: {
      color: 'bg-blue-500',
      ring: 'ring-blue-500/20',
      pulse: '',
      text: 'text-blue-700',
      label: 'Idle',
      ariaLabel: 'Agent is idle',
    },
    error: {
      color: 'bg-red-500',
      ring: 'ring-red-500/20',
      pulse: '',
      text: 'text-red-700',
      label: 'Error',
      ariaLabel: 'Agent encountered an error',
    },
    offline: {
      color: 'bg-gray-400',
      ring: 'ring-gray-400/20',
      pulse: '',
      text: 'text-gray-700',
      label: 'Offline',
      ariaLabel: 'Agent is offline',
    },
  };

  return configs[status];
};

/**
 * Main AgentStatusCard Component
 */
export const AgentStatusCard: React.FC<AgentStatusCardProps> = ({
  name,
  status,
  lastRunTime,
  description,
  onClick,
  className = '',
  showDetails = false,
}) => {
  // Memoize expensive computations
  const statusConfig = useMemo(() => getStatusConfig(status), [status]);
  const relativeTime = useMemo(() => formatRelativeTime(lastRunTime), [lastRunTime]);
  const formattedName = useMemo(() =>
    name.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '),
    [name]
  );

  // Determine if card is interactive
  const isInteractive = Boolean(onClick);

  return (
    <article
      className={`
        relative overflow-hidden
        rounded-lg border border-gray-200 bg-white
        shadow-sm hover:shadow-md
        transition-all duration-200 ease-in-out
        ${isInteractive ? 'cursor-pointer hover:border-gray-300' : ''}
        ${className}
      `}
      onClick={onClick}
      role={isInteractive ? 'button' : 'article'}
      tabIndex={isInteractive ? 0 : undefined}
      onKeyDown={isInteractive ? (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick?.();
        }
      } : undefined}
      aria-label={`${formattedName} agent, ${statusConfig.ariaLabel}, last run ${relativeTime}`}
    >
      {/* Top accent bar based on status */}
      <div className={`h-1 ${statusConfig.color}`} aria-hidden="true" />

      {/* Card content */}
      <div className="p-4">
        {/* Header: Name and Status Indicator */}
        <div className="flex items-start justify-between gap-3 mb-3">
          {/* Agent Name */}
          <h3 className="text-lg font-semibold text-gray-900 truncate flex-1">
            {formattedName}
          </h3>

          {/* Status Indicator */}
          <div
            className="flex items-center gap-2 flex-shrink-0"
            aria-label={statusConfig.ariaLabel}
          >
            <span
              className={`
                relative flex h-3 w-3
              `}
            >
              {/* Pulsing ring for active status */}
              {status === 'active' && (
                <span className={`
                  absolute inline-flex h-full w-full
                  rounded-full ${statusConfig.color}
                  opacity-75 ${statusConfig.pulse}
                `} />
              )}

              {/* Status dot */}
              <span className={`
                relative inline-flex rounded-full
                h-3 w-3 ${statusConfig.color}
              `} />
            </span>

            {/* Status label */}
            <span className={`
              text-sm font-medium ${statusConfig.text}
            `}>
              {statusConfig.label}
            </span>
          </div>
        </div>

        {/* Last Run Time */}
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <time dateTime={lastRunTime?.toISOString()}>
            Last run: {relativeTime}
          </time>
        </div>

        {/* Optional Description */}
        {showDetails && description && (
          <p className="mt-3 text-sm text-gray-600 line-clamp-2">
            {description}
          </p>
        )}
      </div>

      {/* Focus ring for keyboard navigation */}
      {isInteractive && (
        <div
          className="absolute inset-0 ring-2 ring-blue-500 ring-offset-2 rounded-lg opacity-0 focus-within:opacity-100 pointer-events-none"
          aria-hidden="true"
        />
      )}
    </article>
  );
};

// Display name for React DevTools
AgentStatusCard.displayName = 'AgentStatusCard';

export default AgentStatusCard;
