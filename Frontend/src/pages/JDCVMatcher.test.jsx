import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import JDCVMatcher from './JDCVMatcher';

// Mock the api module
vi.mock('../api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn()
  }
}));

// Mock useAuth hook
vi.mock('../hooks/useAuth', () => ({
  default: () => ({
    user: { id: 1, username: 'testuser', role: 'admin' },
    logout: vi.fn()
  })
}));

// Mock components that might cause issues in tests
vi.mock('../components/ui/Stepper', () => ({
  default: () => <div data-testid="stepper">Stepper</div>
}));

vi.mock('../components/ui/ProcessingLoader', () => ({
  default: () => <div data-testid="processing-loader">Processing...</div>
}));

vi.mock('../components/CvFormEditor', () => ({
  default: () => <div data-testid="cv-form-editor">CV Form Editor</div>
}));

import api from '../api';

describe('JDCVMatcher', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render the component and show stepper for admin user', () => {
    render(
      <BrowserRouter>
        <JDCVMatcher />
      </BrowserRouter>
    );
    
    expect(screen.getByTestId('stepper')).toBeInTheDocument();
  });

  it('should show error message when fetching past analyses fails', async () => {
    // Mock API error for analyses
    api.get.mockRejectedValueOnce(new Error('Failed to fetch'));
    
    render(
      <BrowserRouter>
        <JDCVMatcher isPastAnalysesPage={true} />
      </BrowserRouter>
    );
    
    // Wait for the error message to appear
    await waitFor(() => {
      expect(screen.getByText('Failed to fetch past analyses.')).toBeInTheDocument();
    });
  });

  it('should render without errors', () => {
    render(
      <BrowserRouter>
        <JDCVMatcher />
      </BrowserRouter>
    );
    
    // Basic check that the component renders
    expect(screen.getByText('Upload Your Documents')).toBeInTheDocument();
  });
});