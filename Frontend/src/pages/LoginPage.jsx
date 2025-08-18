import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

const LoginPage = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [keepSignedIn, setKeepSignedIn] = useState(false);
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');
        
        try {
            const response = await api.post('/token', new URLSearchParams({
                username,
                password,
                keep_signed_in: keepSignedIn
            }));
            
            const storage = keepSignedIn ? localStorage : sessionStorage;
            storage.setItem('token', response.data.access_token);

            // Fetch user data and store it
            const userResponse = await api.get('/users/me');
            const user = userResponse.data;
            if (user) {
                storage.setItem('user', JSON.stringify(user));
            }

            navigate('/');
        } catch (err) {
            setError('Invalid username or password');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-100">
            <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md">
                <h1 className="text-2xl font-bold text-center text-gray-900">Login</h1>
                <form className="space-y-6" onSubmit={handleLogin}>
                    <div>
                        <label
                            htmlFor="username"
                            className="block text-sm font-medium text-gray-700"
                        >
                            Username
                        </label>
                        <input
                            id="username"
                            name="username"
                            type="text"
                            required
                            disabled={isLoading}
                            className="block w-full px-3 py-2 mt-1 text-gray-900 placeholder-gray-500 border border-gray-300 rounded-md shadow-sm appearance-none focus:outline-none focus:ring-red-500 focus:border-red-500 sm:text-sm disabled:bg-gray-100 disabled:cursor-not-allowed"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                        />
                    </div>
                    <div>
                        <label
                            htmlFor="password"
                            className="block text-sm font-medium text-gray-700"
                        >
                            Password
                        </label>
                        <input
                            id="password"
                            name="password"
                            type="password"
                            required
                            disabled={isLoading}
                            className="block w-full px-3 py-2 mt-1 text-gray-900 placeholder-gray-500 border border-gray-300 rounded-md shadow-sm appearance-none focus:outline-none focus:ring-red-500 focus:border-red-500 sm:text-sm disabled:bg-gray-100 disabled:cursor-not-allowed"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>
                    <div className="flex items-center">
                        <input
                            id="keep-signed-in"
                            name="keep-signed-in"
                            type="checkbox"
                            disabled={isLoading}
                            className="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500 disabled:cursor-not-allowed"
                            checked={keepSignedIn}
                            onChange={(e) => setKeepSignedIn(e.target.checked)}
                        />
                        <label
                            htmlFor="keep-signed-in"
                            className="ml-2 block text-sm text-gray-900"
                        >
                            Keep me signed in
                        </label>
                    </div>
                    {error && <p className="text-sm text-red-600">{error}</p>}
                    <div>
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="flex justify-center w-full px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:bg-gray-400 disabled:cursor-not-allowed disabled:hover:bg-gray-400"
                        >
                            {isLoading ? 'Signing in...' : 'Sign in'}
                        </button>
                    </div>
                </form>
                
                {/* Loading indicator below the form */}
                {isLoading && (
                    <div className="flex items-center justify-center space-x-2 text-gray-600">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-red-500"></div>
                        <span className="text-sm">Signing you in...</span>
                    </div>
                )}
            </div>
        </div>
    );
};

export default LoginPage;