/**
 * AgentStatusCard Unit Tests
 *
 * Tests for the AgentStatusCard component covering:
 * - Rendering with different statuses
 * - Accessibility features
 * - Time formatting
 * - User interactions
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { AgentStatusCard } from './AgentStatusCard';

describe('AgentStatusCard', () => {
  const mockDate = new Date('2025-10-22T10:00:00');
  const twoMinutesAgo = new Date('2025-10-22T09:58:00');
  const twoHoursAgo = new Date('2025-10-22T08:00:00');
  const twoDaysAgo = new Date('2025-10-20T10:00:00');

  beforeAll(() => {
    jest.useFakeTimers();
    jest.setSystemTime(mockDate);
  });

  afterAll(() => {
    jest.useRealTimers();
  });

  describe('Rendering', () => {
    it('renders agent name correctly', () => {
      render(
        <AgentStatusCard
          name="copywriter"
          status="idle"
          lastRunTime={null}
        />
      );

      expect(screen.getByRole('article')).toHaveTextContent('Copywriter');
    });

    it('formats multi-word agent names', () => {
      render(
        <AgentStatusCard
          name="social-media-manager"
          status="idle"
          lastRunTime={null}
        />
      );

      expect(screen.getByRole('article')).toHaveTextContent('Social Media Manager');
    });

    it('displays active status correctly', () => {
      render(
        <AgentStatusCard
          name="test-agent"
          status="active"
          lastRunTime={null}
        />
      );

      expect(screen.getByText('Active')).toBeInTheDocument();
    });

    it('displays idle status correctly', () => {
      render(
        <AgentStatusCard
          name="test-agent"
          status="idle"
          lastRunTime={null}
        />
      );

      expect(screen.getByText('Idle')).toBeInTheDocument();
    });

    it('displays error status correctly', () => {
      render(
        <AgentStatusCard
          name="test-agent"
          status="error"
          lastRunTime={null}
        />
      );

      expect(screen.getByText('Error')).toBeInTheDocument();
    });

    it('displays offline status correctly', () => {
      render(
        <AgentStatusCard
          name="test-agent"
          status="offline"
          lastRunTime={null}
        />
      );

      expect(screen.getByText('Offline')).toBeInTheDocument();
    });

    it('shows description when showDetails is true', () => {
      render(
        <AgentStatusCard
          name="test-agent"
          status="idle"
          lastRunTime={null}
          description="Test description"
          showDetails={true}
        />
      );

      expect(screen.getByText('Test description')).toBeInTheDocument();
    });

    it('hides description when showDetails is false', () => {
      render(
        <AgentStatusCard
          name="test-agent"
          status="idle"
          lastRunTime={null}
          description="Test description"
          showDetails={false}
        />
      );

      expect(screen.queryByText('Test description')).not.toBeInTheDocument();
    });
  });

  describe('Time Formatting', () => {
    it('shows "Never" when lastRunTime is null', () => {
      render(
        <AgentStatusCard
          name="test-agent"
          status="idle"
          lastRunTime={null}
        />
      );

      expect(screen.getByText(/Never/)).toBeInTheDocument();
    });

    it('shows "Just now" for recent runs', () => {
      const justNow = new Date('2025-10-22T09:59:30');
      render(
        <AgentStatusCard
          name="test-agent"
          status="idle"
          lastRunTime={justNow}
        />
      );

      expect(screen.getByText(/Just now/)).toBeInTheDocument();
    });

    it('shows minutes for runs within the hour', () => {
      render(
        <AgentStatusCard
          name="test-agent"
          status="idle"
          lastRunTime={twoMinutesAgo}
        />
      );

      expect(screen.getByText(/2 minutes ago/)).toBeInTheDocument();
    });

    it('shows hours for runs within the day', () => {
      render(
        <AgentStatusCard
          name="test-agent"
          status="idle"
          lastRunTime={twoHoursAgo}
        />
      );

      expect(screen.getByText(/2 hours ago/)).toBeInTheDocument();
    });

    it('shows days for runs within the week', () => {
      render(
        <AgentStatusCard
          name="test-agent"
          status="idle"
          lastRunTime={twoDaysAgo}
        />
      );

      expect(screen.getByText(/2 days ago/)).toBeInTheDocument();
    });

    it('uses singular form for 1 minute ago', () => {
      const oneMinuteAgo = new Date('2025-10-22T09:59:00');
      render(
        <AgentStatusCard
          name="test-agent"
          status="idle"
          lastRunTime={oneMinuteAgo}
        />
      );

      expect(screen.getByText(/1 minute ago/)).toBeInTheDocument();
    });
  });

  describe('Interactions', () => {
    it('calls onClick when card is clicked', () => {
      const handleClick = jest.fn();
      render(
        <AgentStatusCard
          name="test-agent"
          status="idle"
          lastRunTime={null}
          onClick={handleClick}
        />
      );

      const card = screen.getByRole('button');
      fireEvent.click(card);

      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('calls onClick when Enter key is pressed', () => {
      const handleClick = jest.fn();
      render(
        <AgentStatusCard
          name="test-agent"
          status="idle"
          lastRunTime={null}
          onClick={handleClick}
        />
      );

      const card = screen.getByRole('button');
      fireEvent.keyDown(card, { key: 'Enter' });

      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('calls onClick when Space key is pressed', () => {
      const handleClick = jest.fn();
      render(
        <AgentStatusCard
          name="test-agent"
          status="idle"
          lastRunTime={null}
          onClick={handleClick}
        />
      );

      const card = screen.getByRole('button');
      fireEvent.keyDown(card, { key: ' ' });

      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('does not have button role when onClick is not provided', () => {
      render(
        <AgentStatusCard
          name="test-agent"
          status="idle"
          lastRunTime={null}
        />
      );

      expect(screen.queryByRole('button')).not.toBeInTheDocument();
      expect(screen.getByRole('article')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper aria-label for active status', () => {
      render(
        <AgentStatusCard
          name="test-agent"
          status="active"
          lastRunTime={twoMinutesAgo}
        />
      );

      const card = screen.getByRole('article');
      expect(card).toHaveAttribute(
        'aria-label',
        expect.stringContaining('Agent is currently active')
      );
    });

    it('has proper aria-label for error status', () => {
      render(
        <AgentStatusCard
          name="test-agent"
          status="error"
          lastRunTime={null}
        />
      );

      const card = screen.getByRole('article');
      expect(card).toHaveAttribute(
        'aria-label',
        expect.stringContaining('Agent encountered an error')
      );
    });

    it('has tabIndex when interactive', () => {
      render(
        <AgentStatusCard
          name="test-agent"
          status="idle"
          lastRunTime={null}
          onClick={() => {}}
        />
      );

      const card = screen.getByRole('button');
      expect(card).toHaveAttribute('tabIndex', '0');
    });

    it('has proper time element with datetime attribute', () => {
      render(
        <AgentStatusCard
          name="test-agent"
          status="idle"
          lastRunTime={twoMinutesAgo}
        />
      );

      const timeElement = screen.getByText(/2 minutes ago/).closest('time');
      expect(timeElement).toHaveAttribute('dateTime', twoMinutesAgo.toISOString());
    });
  });

  describe('Custom Styling', () => {
    it('applies custom className', () => {
      const { container } = render(
        <AgentStatusCard
          name="test-agent"
          status="idle"
          lastRunTime={null}
          className="custom-class"
        />
      );

      const card = container.querySelector('.custom-class');
      expect(card).toBeInTheDocument();
    });
  });
});
