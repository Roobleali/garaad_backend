# Garaad Frontend Gamification Documentation

## Overview
This documentation explains how to integrate with Garaad's gamification system from the frontend. The system includes XP tracking, streaks, leagues, and real-time progress updates.

## Core Concepts

### 1. XP (Experience Points)
- Each problem awards XP (default: 10 XP)
- XP is tracked in multiple timeframes:
  - Daily
  - Weekly
  - Monthly
  - Total

### 2. Streaks
- Streaks are updated after solving 2-3 problems
- Each streak day awards bonus XP
- Streaks can be maintained using energy

### 3. Leagues
- Users are placed in leagues based on total XP
- Weekly competitions within leagues
- Promotions/demotions based on performance

## API Integration

### 1. Problem Solving Flow

#### Get Problem Details
```typescript
interface Problem {
  id: number;
  question_text: string;
  question_type: 'multiple_choice' | 'single_choice' | 'true_false' | 'fill_blank' | 'matching' | 'open_ended' | 'math_expression' | 'code' | 'diagram';
  xp: number;
  attempts_allowed: number;
  hints_available: boolean;
  options?: Array<{
    id: string;
    text: string;
  }>;
  correct_answer: Array<{
    id: string;
  }>;
  lesson: {
    id: number;
    title: string;
  };
}

// API Call
const getProblem = async (problemId: number): Promise<Problem> => {
  const response = await fetch(`/api/problems/${problemId}/`);
  return response.json();
};
```

#### Problem Solved Response
```typescript
interface ProblemSolvedResponse {
  success: boolean;
  xp_earned: number;
  streak_updated: boolean;
  problems_solved_today: number;
  next_streak_problem: number;
  energy: {
    current: number;
    max: number;
    next_update: string;
  };
  progress: {
    lesson_progress: number;
    total_xp: number;
    daily_xp: number;
    weekly_xp: number;
    monthly_xp: number;
  };
  league: {
    current_league: string;
    weekly_points: number;
    rank: number;
  };
}
```

### 2. Streak Management

#### Get Streak Status
```typescript
interface StreakStatus {
  current_streak: number;
  max_streak: number;
  problems_solved_today: number;
  problems_to_next_streak: number;
  energy: {
    current: number;
    max: number;
    next_update: string;
  };
  daily_activity: Array<{
    date: string;
    status: 'complete' | 'incomplete';
    problems_solved: number;
  }>;
}

// API Call
const getStreakStatus = async (): Promise<StreakStatus> => {
  const response = await fetch('/api/gamification/streak/');
  return response.json();
};
```

#### Use Energy
```typescript
interface EnergyResponse {
  success: boolean;
  remaining_energy: number;
  message: string;
}

// API Call
const useEnergy = async (): Promise<EnergyResponse> => {
  const response = await fetch('/api/gamification/use_energy/', {
    method: 'POST'
  });
  return response.json();
};
```

### 3. Progress Tracking

#### Get User Progress
```typescript
interface UserProgress {
  xp: {
    total: number;
    daily: number;
    weekly: number;
    monthly: number;
  };
  problems: {
    total_solved: number;
    solved_today: number;
    solved_this_week: number;
  };
  lessons: {
    completed: number;
    in_progress: number;
  };
  courses: {
    enrolled: number;
    completed: number;
  };
}

// API Call
const getUserProgress = async (): Promise<UserProgress> => {
  const response = await fetch('/api/gamification/progress/');
  return response.json();
};
```

### 4. League System

#### Get League Status
```typescript
interface LeagueStatus {
  current_league: {
    id: number;
    name: string;
    somali_name: string;
    min_xp: number;
    rank: number;
  };
  next_league: {
    id: number;
    name: string;
    somali_name: string;
    min_xp: number;
    points_needed: number;
  };
  weekly_stats: {
    rank: number;
    points: number;
    problems_solved: number;
  };
}

// API Call
const getLeagueStatus = async (): Promise<LeagueStatus> => {
  const response = await fetch('/api/gamification/league/');
  return response.json();
};
```

#### Get Leaderboard
```typescript
interface Leaderboard {
  league: {
    id: number;
    name: string;
  };
  time_period: 'weekly' | 'monthly' | 'all_time';
  standings: Array<{
    rank: number;
    user: {
      id: number;
      name: string;
    };
    points: number;
    streak: number;
    problems_solved: number;
  }>;
  my_standing: {
    rank: number;
    points: number;
    streak: number;
    problems_solved: number;
  };
}

// API Call
const getLeaderboard = async (
  leagueId: number,
  timePeriod: 'weekly' | 'monthly' | 'all_time' = 'weekly',
  limit: number = 100
): Promise<Leaderboard> => {
  const response = await fetch(
    `/api/gamification/league/${leagueId}/leaderboard/?time_period=${timePeriod}&limit=${limit}`
  );
  return response.json();
};
```

## Real-time Updates

### WebSocket Events
```typescript
interface WebSocketEvents {
  'problem_solved': {
    event: 'problem_solved';
    user_id: number;
    problem_id: number;
    xp_earned: number;
    timestamp: string;
  };
  'streak_updated': {
    event: 'streak_updated';
    user_id: number;
    new_streak: number;
    xp_earned: number;
    timestamp: string;
  };
  'league_promotion': {
    event: 'league_promotion';
    user_id: number;
    old_league: string;
    new_league: string;
    timestamp: string;
  };
}

// WebSocket Connection
const ws = new WebSocket('wss://api.garaad.org/ws/gamification/');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  switch (data.event) {
    case 'problem_solved':
      updateProgress(data);
      break;
    case 'streak_updated':
      updateStreak(data);
      break;
    case 'league_promotion':
      updateLeague(data);
      break;
  }
};
```

## UI Components

### 1. Progress Bar
```typescript
interface ProgressBarProps {
  current: number;
  total: number;
  label: string;
  showPercentage?: boolean;
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  current,
  total,
  label,
  showPercentage = true
}) => {
  const percentage = (current / total) * 100;
  
  return (
    <div className="progress-bar">
      <div className="progress-label">{label}</div>
      <div className="progress-track">
        <div 
          className="progress-fill"
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showPercentage && (
        <div className="progress-percentage">
          {Math.round(percentage)}%
        </div>
      )}
    </div>
  );
};
```

### 2. Streak Counter
```typescript
interface StreakCounterProps {
  currentStreak: number;
  maxStreak: number;
  problemsToNextStreak: number;
}

const StreakCounter: React.FC<StreakCounterProps> = ({
  currentStreak,
  maxStreak,
  problemsToNextStreak
}) => {
  return (
    <div className="streak-counter">
      <div className="streak-icon">🔥</div>
      <div className="streak-info">
        <div className="current-streak">
          {currentStreak} days
        </div>
        <div className="streak-progress">
          {problemsToNextStreak} problems to next streak
        </div>
      </div>
    </div>
  );
};
```

### 3. League Badge
```typescript
interface LeagueBadgeProps {
  league: {
    name: string;
    somali_name: string;
    rank: number;
  };
  points: number;
  pointsToNext: number;
}

const LeagueBadge: React.FC<LeagueBadgeProps> = ({
  league,
  points,
  pointsToNext
}) => {
  return (
    <div className="league-badge">
      <div className="league-name">
        {league.somali_name}
      </div>
      <div className="league-rank">
        Rank #{league.rank}
      </div>
      <div className="league-progress">
        <ProgressBar
          current={points}
          total={points + pointsToNext}
          label="Points to next league"
        />
      </div>
    </div>
  );
};
```

## Error Handling

### Common Error Responses
```typescript
interface ErrorResponse {
  error: string;
  detail: string;
  code?: string;
}

// Example error handling
const handleApiError = (error: ErrorResponse) => {
  switch (error.error) {
    case 'Insufficient energy':
      showEnergyModal();
      break;
    case 'League requirements not met':
      showLeagueRequirementsModal(error.detail);
      break;
    default:
      showErrorNotification(error.detail);
  }
};
```

## Best Practices

1. **Real-time Updates**
   - Use WebSocket for live updates
   - Implement optimistic UI updates
   - Show loading states during API calls

2. **Error Handling**
   - Implement retry logic for failed API calls
   - Show user-friendly error messages
   - Handle offline scenarios gracefully

3. **Performance**
   - Cache frequently accessed data
   - Implement pagination for leaderboards
   - Use debouncing for rapid API calls

4. **User Experience**
   - Show progress animations
   - Implement sound effects for achievements
   - Use consistent Somali translations

## Example Implementation

```typescript
// Example of a complete problem-solving flow
const solveProblem = async (problemId: number, answer: string) => {
  try {
    // 1. Get problem details
    const problem = await getProblem(problemId);
    
    // 2. Submit answer
    const result = await submitAnswer(problemId, answer);
    
    // 3. Update UI with results
    if (result.success) {
      // Update progress bars
      updateProgressBars(result.progress);
      
      // Update streak counter
      if (result.streak_updated) {
        updateStreakCounter(result.current_streak);
        showStreakAnimation();
      }
      
      // Update league status
      updateLeagueBadge(result.league);
      
      // Show XP earned animation
      showXpAnimation(result.xp_earned);
      
      // Update energy display
      updateEnergyDisplay(result.energy);
    }
    
    // 4. Handle errors
  } catch (error) {
    handleApiError(error);
  }
};
```

## Testing

### Unit Tests
```typescript
describe('Gamification Components', () => {
  test('ProgressBar renders correctly', () => {
    const { getByText } = render(
      <ProgressBar current={50} total={100} label="Test Progress" />
    );
    expect(getByText('50%')).toBeInTheDocument();
  });
  
  test('StreakCounter updates correctly', () => {
    const { getByText } = render(
      <StreakCounter
        currentStreak={5}
        maxStreak={10}
        problemsToNextStreak={2}
      />
    );
    expect(getByText('5 days')).toBeInTheDocument();
  });
});
```

### Integration Tests
```typescript
describe('Gamification Flow', () => {
  test('Complete problem-solving flow', async () => {
    // Mock API responses
    mockApiResponses();
    
    // Render component
    const { getByText, getByTestId } = render(<ProblemSolver />);
    
    // Solve problem
    await solveProblem(1, 'correct_answer');
    
    // Verify updates
    expect(getByText('XP Earned: 10')).toBeInTheDocument();
    expect(getByTestId('streak-counter')).toHaveTextContent('1');
  });
});
``` 