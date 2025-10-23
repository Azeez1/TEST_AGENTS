/**
 * Example Application: Agent Dashboard
 *
 * Complete working example demonstrating AgentStatusCard and AgentStatusGrid
 * with real-time updates, filtering, and sorting.
 *
 * To run this example:
 * 1. npm install react react-dom tailwindcss
 * 2. Set up Tailwind CSS configuration
 * 3. Import this component in your Next.js or React app
 */

import React, { useState, useEffect } from 'react';
import { AgentStatusGrid, Agent } from './AgentStatusGrid';
import { AgentStatus } from './AgentStatusCard';

/**
 * Mock API function to simulate fetching agent data
 */
const fetchAgentsFromAPI = async (): Promise<Agent[]> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000));

  // Return mock data for all 35 agents from TEST_AGENTS repository
  return [
    // MARKETING_TEAM (17 agents)
    {
      id: 'm1',
      name: 'router-agent',
      status: 'active',
      lastRunTime: new Date(Date.now() - 300000), // 5 mins ago
      description: 'Campaign coordinator and agent orchestration',
    },
    {
      id: 'm2',
      name: 'copywriter',
      status: 'idle',
      lastRunTime: new Date(Date.now() - 1800000), // 30 mins ago
      description: 'Blog posts, articles, web copy (2000+ words)',
    },
    {
      id: 'm3',
      name: 'social-media-manager',
      status: 'active',
      lastRunTime: new Date(Date.now() - 60000), // 1 min ago
      description: 'X/Twitter and LinkedIn posts with hashtags',
    },
    {
      id: 'm4',
      name: 'visual-designer',
      status: 'idle',
      lastRunTime: new Date(Date.now() - 7200000), // 2 hours ago
      description: 'GPT-4o image generation',
    },
    {
      id: 'm5',
      name: 'video-producer',
      status: 'offline',
      lastRunTime: new Date(Date.now() - 86400000), // 1 day ago
      description: 'Sora video creation',
    },
    {
      id: 'm6',
      name: 'seo-specialist',
      status: 'idle',
      lastRunTime: new Date(Date.now() - 3600000), // 1 hour ago
      description: 'Keyword research and SERP analysis',
    },
    {
      id: 'm7',
      name: 'email-specialist',
      status: 'idle',
      lastRunTime: new Date(Date.now() - 5400000), // 90 mins ago
      description: 'Email campaigns and newsletters',
    },
    {
      id: 'm8',
      name: 'gmail-agent',
      status: 'active',
      lastRunTime: new Date(Date.now() - 120000), // 2 mins ago
      description: 'Email sending via Gmail API',
    },
    {
      id: 'm9',
      name: 'landing-page-specialist',
      status: 'idle',
      lastRunTime: new Date(Date.now() - 10800000), // 3 hours ago
      description: 'Conversion-focused landing pages',
    },
    {
      id: 'm10',
      name: 'pdf-specialist',
      status: 'idle',
      lastRunTime: new Date(Date.now() - 14400000), // 4 hours ago
      description: 'PDF whitepapers and reports',
    },
    {
      id: 'm11',
      name: 'presentation-designer',
      status: 'offline',
      lastRunTime: new Date(Date.now() - 172800000), // 2 days ago
      description: 'PowerPoint deck creation',
    },
    {
      id: 'm12',
      name: 'analyst',
      status: 'idle',
      lastRunTime: new Date(Date.now() - 7200000), // 2 hours ago
      description: 'Performance analysis and metrics',
    },
    {
      id: 'm13',
      name: 'content-strategist',
      status: 'idle',
      lastRunTime: new Date(Date.now() - 21600000), // 6 hours ago
      description: 'Campaign orchestration',
    },
    {
      id: 'm14',
      name: 'editor',
      status: 'active',
      lastRunTime: new Date(Date.now() - 180000), // 3 mins ago
      description: 'Content review and editing',
    },
    {
      id: 'm15',
      name: 'research-agent',
      status: 'active',
      lastRunTime: new Date(Date.now() - 240000), // 4 mins ago
      description: 'Web research and competitive intelligence',
    },
    {
      id: 'm16',
      name: 'lead-gen-agent',
      status: 'idle',
      lastRunTime: new Date(Date.now() - 28800000), // 8 hours ago
      description: 'B2B/local lead generation',
    },
    {
      id: 'm17',
      name: 'automation-agent',
      status: 'active',
      lastRunTime: new Date(Date.now() - 90000), // 1.5 mins ago
      description: 'n8n workflow automation',
    },

    // TEST_AGENT (5 agents)
    {
      id: 't1',
      name: 'test-orchestrator',
      status: 'idle',
      lastRunTime: new Date(Date.now() - 3600000), // 1 hour ago
      description: 'Testing coordinator',
    },
    {
      id: 't2',
      name: 'unit-test-agent',
      status: 'error',
      lastRunTime: new Date(Date.now() - 600000), // 10 mins ago
      description: 'Unit test generation',
    },
    {
      id: 't3',
      name: 'integration-test-agent',
      status: 'idle',
      lastRunTime: new Date(Date.now() - 7200000), // 2 hours ago
      description: 'End-to-end workflow tests',
    },
    {
      id: 't4',
      name: 'edge-case-agent',
      status: 'idle',
      lastRunTime: new Date(Date.now() - 10800000), // 3 hours ago
      description: 'Edge case identification',
    },
    {
      id: 't5',
      name: 'fixture-agent',
      status: 'idle',
      lastRunTime: new Date(Date.now() - 14400000), // 4 hours ago
      description: 'Pytest fixtures and mocks',
    },

    // ENGINEERING_TEAM (12 agents)
    {
      id: 'e1',
      name: 'devops-engineer',
      status: 'active',
      lastRunTime: new Date(Date.now() - 420000), // 7 mins ago
      description: 'CI/CD, Terraform, Kubernetes',
    },
    {
      id: 'e2',
      name: 'frontend-developer',
      status: 'idle',
      lastRunTime: new Date(Date.now() - 5400000), // 90 mins ago
      description: 'React components and responsive design',
    },
    {
      id: 'e3',
      name: 'backend-architect',
      status: 'idle',
      lastRunTime: new Date(Date.now() - 10800000), // 3 hours ago
      description: 'API design and microservices',
    },
    {
      id: 'e4',
      name: 'security-auditor',
      status: 'error',
      lastRunTime: new Date(Date.now() - 900000), // 15 mins ago
      description: 'Security analysis and compliance',
    },
    {
      id: 'e5',
      name: 'technical-writer',
      status: 'idle',
      lastRunTime: new Date(Date.now() - 7200000), // 2 hours ago
      description: 'PRDs and technical documentation',
    },
    {
      id: 'e6',
      name: 'ai-engineer',
      status: 'active',
      lastRunTime: new Date(Date.now() - 150000), // 2.5 mins ago
      description: 'LLM integration and RAG systems',
    },
    {
      id: 'e7',
      name: 'ui-ux-designer',
      status: 'idle',
      lastRunTime: new Date(Date.now() - 18000000), // 5 hours ago
      description: 'User research and wireframes',
    },
    {
      id: 'e8',
      name: 'code-reviewer',
      status: 'active',
      lastRunTime: new Date(Date.now() - 360000), // 6 mins ago
      description: 'Code quality and security reviews',
    },
    {
      id: 'e9',
      name: 'test-engineer',
      status: 'idle',
      lastRunTime: new Date(Date.now() - 10800000), // 3 hours ago
      description: 'Test automation and QA strategy',
    },
    {
      id: 'e10',
      name: 'prompt-engineer',
      status: 'idle',
      lastRunTime: new Date(Date.now() - 14400000), // 4 hours ago
      description: 'LLM prompt optimization',
    },
    {
      id: 'e11',
      name: 'database-architect',
      status: 'idle',
      lastRunTime: new Date(Date.now() - 21600000), // 6 hours ago
      description: 'Database design and data modeling',
    },
    {
      id: 'e12',
      name: 'debugger',
      status: 'active',
      lastRunTime: new Date(Date.now() - 480000), // 8 mins ago
      description: 'Root cause analysis and troubleshooting',
    },

    // USER_STORY_AGENT (1 system)
    {
      id: 'u1',
      name: 'user-story-agent',
      status: 'idle',
      lastRunTime: new Date(Date.now() - 43200000), // 12 hours ago
      description: 'Meeting notes to user stories with Excel export',
    },
  ];
};

/**
 * Main Application Component
 */
export default function AgentDashboardApp() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<AgentStatus | 'all'>('all');
  const [sortBy, setSortBy] = useState<'name' | 'status' | 'lastRun'>('name');
  const [showDetails, setShowDetails] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);

  // Fetch agents on mount
  useEffect(() => {
    fetchAgentsFromAPI()
      .then((data) => {
        setAgents(data);
        setLoading(false);
      })
      .catch((error) => {
        console.error('Failed to fetch agents:', error);
        setLoading(false);
      });
  }, []);

  // Simulate real-time updates (every 30 seconds)
  useEffect(() => {
    const interval = setInterval(() => {
      setAgents((prevAgents) =>
        prevAgents.map((agent) => {
          // Randomly update some agents
          if (Math.random() > 0.7) {
            const statuses: AgentStatus[] = ['active', 'idle', 'error', 'offline'];
            return {
              ...agent,
              status: statuses[Math.floor(Math.random() * statuses.length)],
              lastRunTime: Math.random() > 0.5 ? new Date() : agent.lastRunTime,
            };
          }
          return agent;
        })
      );
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const handleAgentClick = (agent: Agent) => {
    setSelectedAgent(agent);
    console.log('Selected agent:', agent);
  };

  const handleCloseModal = () => {
    setSelectedAgent(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Agent Status Dashboard
              </h1>
              <p className="mt-1 text-sm text-gray-600">
                Monitor 35 agents across 4 systems
              </p>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="showDetails"
                  checked={showDetails}
                  onChange={(e) => setShowDetails(e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <label htmlFor="showDetails" className="text-sm text-gray-700">
                  Show details
                </label>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Controls */}
      <div className="container mx-auto px-6 py-6">
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
          <div className="flex flex-wrap gap-4">
            {/* Status Filter */}
            <div className="flex items-center gap-2">
              <label htmlFor="statusFilter" className="text-sm font-medium text-gray-700">
                Status:
              </label>
              <select
                id="statusFilter"
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value as AgentStatus | 'all')}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Agents</option>
                <option value="active">Active</option>
                <option value="idle">Idle</option>
                <option value="error">Error</option>
                <option value="offline">Offline</option>
              </select>
            </div>

            {/* Sort By */}
            <div className="flex items-center gap-2">
              <label htmlFor="sortBy" className="text-sm font-medium text-gray-700">
                Sort by:
              </label>
              <select
                id="sortBy"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'name' | 'status' | 'lastRun')}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="name">Name</option>
                <option value="status">Status</option>
                <option value="lastRun">Last Run</option>
              </select>
            </div>

            {/* Refresh Button */}
            <button
              onClick={() => {
                setLoading(true);
                fetchAgentsFromAPI().then((data) => {
                  setAgents(data);
                  setLoading(false);
                });
              }}
              className="ml-auto px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
            >
              Refresh
            </button>
          </div>
        </div>

        {/* Agent Grid */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
          </div>
        ) : (
          <AgentStatusGrid
            agents={agents}
            onAgentClick={handleAgentClick}
            filterStatus={filterStatus}
            sortBy={sortBy}
            showDetails={showDetails}
          />
        )}
      </div>

      {/* Agent Detail Modal */}
      {selectedAgent && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={handleCloseModal}
        >
          <div
            className="bg-white rounded-lg shadow-xl max-w-md w-full p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between mb-4">
              <h2 className="text-2xl font-bold text-gray-900">
                {selectedAgent.name.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
              </h2>
              <button
                onClick={handleCloseModal}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700">Status</label>
                <p className="mt-1 text-lg capitalize">{selectedAgent.status}</p>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700">Last Run</label>
                <p className="mt-1">
                  {selectedAgent.lastRunTime
                    ? selectedAgent.lastRunTime.toLocaleString()
                    : 'Never'}
                </p>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700">Description</label>
                <p className="mt-1 text-gray-600">
                  {selectedAgent.description || 'No description available'}
                </p>
              </div>

              <button
                onClick={handleCloseModal}
                className="w-full mt-6 px-4 py-2 bg-gray-100 text-gray-700 rounded-md font-medium hover:bg-gray-200 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
