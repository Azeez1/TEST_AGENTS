# Quick Start Guide - Agent Status Components

Get the agent status dashboard running in under 5 minutes.

## Prerequisites

- Node.js 18+ and npm
- React 18+
- Basic knowledge of React and TypeScript

---

## Installation

### Step 1: Install Dependencies

```bash
cd ENGINEERING_TEAM/components

# Install all dependencies
npm install

# Or with yarn
yarn install
```

### Step 2: Set Up Tailwind CSS

**Create `tailwind.config.js`:**
```javascript
module.exports = {
  content: [
    './**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**Create `postcss.config.js`:**
```javascript
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

**Create `styles.css`:**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Step 3: Set Up Jest (Optional - for testing)

**Create `jest.setup.js`:**
```javascript
import '@testing-library/jest-dom';
```

---

## Usage

### Option 1: Use Individual Components

```tsx
import { AgentStatusCard } from './AgentStatusCard';

function MyComponent() {
  return (
    <AgentStatusCard
      name="copywriter"
      status="active"
      lastRunTime={new Date()}
      description="Blog posts and articles"
      onClick={() => console.log('Clicked!')}
    />
  );
}
```

### Option 2: Use Grid Component

```tsx
import { AgentStatusGrid } from './AgentStatusGrid';

const agents = [
  {
    id: '1',
    name: 'copywriter',
    status: 'active',
    lastRunTime: new Date(),
    description: 'Blog posts and articles',
  },
  {
    id: '2',
    name: 'visual-designer',
    status: 'idle',
    lastRunTime: new Date(Date.now() - 3600000),
    description: 'GPT-4o image generation',
  },
];

function MyDashboard() {
  return (
    <AgentStatusGrid
      agents={agents}
      onAgentClick={(agent) => console.log('Selected:', agent)}
      showDetails={true}
    />
  );
}
```

### Option 3: Run Complete Example App

```tsx
import AgentDashboardApp from './example-app';

function App() {
  return <AgentDashboardApp />;
}
```

---

## Next.js Integration

### Step 1: Create a New Next.js App (if needed)

```bash
npx create-next-app@latest agent-dashboard --typescript --tailwind --app
cd agent-dashboard
```

### Step 2: Copy Component Files

```bash
# Copy components to Next.js project
cp AgentStatusCard.tsx app/components/
cp AgentStatusGrid.tsx app/components/
```

### Step 3: Create Dashboard Page

**File: `app/dashboard/page.tsx`**
```tsx
'use client';

import { AgentStatusGrid } from '@/components/AgentStatusGrid';
import { useState, useEffect } from 'react';

export default function DashboardPage() {
  const [agents, setAgents] = useState([]);

  useEffect(() => {
    // Fetch your agent data
    fetch('/api/agents')
      .then(res => res.json())
      .then(setAgents);
  }, []);

  return (
    <main className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Agent Status Dashboard</h1>
      <AgentStatusGrid
        agents={agents}
        onAgentClick={(agent) => console.log('Selected:', agent)}
      />
    </main>
  );
}
```

### Step 4: Run Development Server

```bash
npm run dev
```

Visit `http://localhost:3000/dashboard`

---

## Create React App Integration

### Step 1: Create New CRA Project (if needed)

```bash
npx create-react-app agent-dashboard --template typescript
cd agent-dashboard
```

### Step 2: Install Tailwind

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Step 3: Configure Tailwind

**File: `tailwind.config.js`**
```javascript
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**File: `src/index.css`**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Step 4: Copy Components

```bash
# Copy to src/components
mkdir src/components
cp AgentStatusCard.tsx src/components/
cp AgentStatusGrid.tsx src/components/
```

### Step 5: Use in App

**File: `src/App.tsx`**
```tsx
import { AgentStatusGrid } from './components/AgentStatusGrid';
import './index.css';

const mockAgents = [
  {
    id: '1',
    name: 'copywriter',
    status: 'active' as const,
    lastRunTime: new Date(),
  },
];

function App() {
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-3xl font-bold mb-6">Agent Dashboard</h1>
      <AgentStatusGrid agents={mockAgents} />
    </div>
  );
}

export default App;
```

---

## Run Tests

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Watch mode
npm run test:watch
```

**Expected output:**
```
PASS  ./AgentStatusCard.test.tsx
  AgentStatusCard
    Rendering
      ✓ renders agent name correctly (25ms)
      ✓ displays active status correctly (15ms)
    Time Formatting
      ✓ shows "Never" when lastRunTime is null (10ms)
      ✓ shows minutes for runs within the hour (12ms)
    Interactions
      ✓ calls onClick when card is clicked (8ms)
    Accessibility
      ✓ has proper aria-label for active status (10ms)

Test Suites: 1 passed, 1 total
Tests:       24 passed, 24 total
Coverage:    100% statements, 100% branches, 100% functions
```

---

## Type Checking

```bash
# Check TypeScript types
npm run type-check
```

---

## Common Issues

### Issue: Tailwind classes not working

**Solution:** Ensure you've:
1. Created `tailwind.config.js` with correct content paths
2. Imported Tailwind in your CSS: `@tailwind base; @tailwind components; @tailwind utilities;`
3. Restarted your dev server

### Issue: Module not found errors

**Solution:** Check import paths match your project structure:
```tsx
// Adjust based on your setup
import { AgentStatusCard } from './components/AgentStatusCard';  // Relative
import { AgentStatusCard } from '@/components/AgentStatusCard';  // Alias (Next.js)
```

### Issue: Date formatting not updating

**Solution:** Component uses `useMemo` - ensure `lastRunTime` prop changes to trigger re-render:
```tsx
// Force re-render by passing new Date object
setAgents(prev => prev.map(agent => ({
  ...agent,
  lastRunTime: new Date(agent.lastRunTime)  // Create new Date instance
})));
```

---

## Performance Tips

### 1. Memoize Large Lists

```tsx
import { memo } from 'react';

const AgentStatusCard = memo(({ name, status, lastRunTime }) => {
  // Component code
}, (prev, next) => {
  // Custom comparison
  return prev.status === next.status &&
         prev.lastRunTime === next.lastRunTime;
});
```

### 2. Virtualize Long Lists

```bash
npm install react-window
```

```tsx
import { FixedSizeGrid } from 'react-window';

function VirtualizedGrid({ agents }) {
  return (
    <FixedSizeGrid
      columnCount={4}
      columnWidth={300}
      height={600}
      rowCount={Math.ceil(agents.length / 4)}
      rowHeight={150}
      width={1200}
    >
      {({ columnIndex, rowIndex, style }) => {
        const index = rowIndex * 4 + columnIndex;
        const agent = agents[index];
        return agent ? (
          <div style={style}>
            <AgentStatusCard {...agent} />
          </div>
        ) : null;
      }}
    </FixedSizeGrid>
  );
}
```

### 3. Lazy Load Components

```tsx
import { lazy, Suspense } from 'react';

const AgentStatusGrid = lazy(() => import('./AgentStatusGrid'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <AgentStatusGrid agents={agents} />
    </Suspense>
  );
}
```

---

## API Integration Example

### REST API

```tsx
// api/agents.ts
export async function fetchAgents() {
  const response = await fetch('https://api.example.com/agents');
  if (!response.ok) throw new Error('Failed to fetch');
  return response.json();
}

// Component
import { fetchAgents } from './api/agents';

function Dashboard() {
  const [agents, setAgents] = useState([]);

  useEffect(() => {
    fetchAgents().then(setAgents).catch(console.error);
  }, []);

  return <AgentStatusGrid agents={agents} />;
}
```

### WebSocket Real-Time Updates

```tsx
function Dashboard() {
  const [agents, setAgents] = useState([]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/agents');

    ws.onmessage = (event) => {
      const update = JSON.parse(event.data);
      setAgents(prev =>
        prev.map(agent =>
          agent.id === update.id ? { ...agent, ...update } : agent
        )
      );
    };

    return () => ws.close();
  }, []);

  return <AgentStatusGrid agents={agents} />;
}
```

---

## Production Build

### Next.js

```bash
npm run build
npm run start
```

### Create React App

```bash
npm run build
# Serve with static server
npx serve -s build
```

---

## Deployment

### Vercel (Next.js)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Netlify (CRA)

```bash
# Build
npm run build

# Deploy
netlify deploy --prod --dir=build
```

---

## Next Steps

1. **Customize styling** - Modify Tailwind classes in components
2. **Add features** - Progress bars, notifications, filters
3. **Connect to backend** - Integrate with your agent API
4. **Add authentication** - Protect dashboard with auth
5. **Real-time updates** - WebSocket or polling

---

## Resources

- [Component Documentation](./README.md)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [React Testing Library](https://testing-library.com/react)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)

---

## Support

For issues or questions:
1. Check [README.md](./README.md) for detailed documentation
2. Review [example-app.tsx](./example-app.tsx) for complete working example
3. See [ENGINEERING_TEAM/README.md](../README.md) for team documentation

---

**Ready to use!** Start with `example-app.tsx` for a complete working dashboard with all 35 agents.
