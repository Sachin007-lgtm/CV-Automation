import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import LoginPage from './LoginPage';

// Mock the api module
vi.mock('../api', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn()
  }
}));

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate
  };
});

import api from '../api';

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    localStorage.clear();
    sessionStorage.clear();
  });

  it('should render login form', () => {
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );
    
    expect(screen.getByLabelText('Username')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
    expect(screen.getByText('Sign in')).toBeInTheDocument();
  });

  it('should handle successful login', async () => {
    // Mock API responses
    api.post.mockResolvedValueOnce({
      data: { access_token: 'mock-token' }
    });
    
    api.get.mockResolvedValueOnce({
      data: { id: 1, username: 'testuser', role: 'recruiter' }
    });
    
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );
    
    // Fill in the form
    fireEvent.change(screen.getByLabelText('Username'), {
      target: { value: 'testuser' }
    });
    fireEvent.change(screen.getByLabelText('Password'), {
      target: { value: 'testpassword' }
    });
    
    // Submit the form
    fireEvent.click(screen.getByText('Sign in'));
    
    // Wait for the API calls to complete
    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/token', expect.any(URLSearchParams));
    });
    
    // Check that token and user were saved to sessionStorage (default)
    expect(sessionStorage.getItem('token')).toBe('mock-token');
    expect(JSON.parse(sessionStorage.getItem('user'))).toEqual({
      id: 1,
      username: 'testuser',
      role: 'recruiter'
    });
  });

  it('should show error on failed login', async () => {
    // Mock API error
    api.post.mockRejectedValueOnce(new Error('Invalid credentials'));
    
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );
    
    // Fill in the form
    fireEvent.change(screen.getByLabelText('Username'), {
      target: { value: 'testuser' }
    });
    fireEvent.change(screen.getByLabelText('Password'), {
      target: { value: 'wrongpassword' }
    });
    
    // Submit the form
    fireEvent.click(screen.getByText('Sign in'));
    
    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText('Invalid username or password')).toBeInTheDocument();
    });
  });
});