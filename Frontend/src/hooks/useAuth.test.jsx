import { renderHook, act } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import useAuth from '../hooks/useAuth';

// Mock window.localStorage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => { store[key] = value.toString(); },
    removeItem: (key) => { delete store[key]; },
    clear: () => { store = {}; }
  };
})();

Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Wrapper component to provide router context
const wrapper = ({ children }) => (
  <BrowserRouter>
    {children}
  </BrowserRouter>
);

describe('useAuth', () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it('should initialize with no user', () => {
    const { result } = renderHook(() => useAuth(), { wrapper });
    expect(result.current.user).toBeNull();
  });

  it('should load user from localStorage', () => {
    const mockUser = { id: 1, username: 'testuser', role: 'recruiter' };
    window.localStorage.setItem('user', JSON.stringify(mockUser));
    
    const { result } = renderHook(() => useAuth(), { wrapper });
    expect(result.current.user).toEqual(mockUser);
  });

  it('should logout and clear storage', () => {
    const mockUser = { id: 1, username: 'testuser', role: 'recruiter' };
    window.localStorage.setItem('user', JSON.stringify(mockUser));
    window.localStorage.setItem('token', 'mock-token');
    
    const { result } = renderHook(() => useAuth(), { wrapper });
    expect(result.current.user).toEqual(mockUser);
    
    act(() => {
      result.current.logout();
    });
    
    expect(result.current.user).toBeNull();
    expect(window.localStorage.getItem('user')).toBeNull();
    expect(window.localStorage.getItem('token')).toBeNull();
  });
});