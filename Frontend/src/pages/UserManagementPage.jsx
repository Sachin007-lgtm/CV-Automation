import React, { useState, useEffect } from 'react';
import api from '../api';
import useAuth from '../hooks/useAuth';
import { Plus, Trash2, Edit } from 'lucide-react';

const UserManagementPage = () => {
    const { user } = useAuth();
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [newUser, setNewUser] = useState({ username: '', email: '', password: '', role: 'recruiter' });
    const [showCreateForm, setShowCreateForm] = useState(false);

    useEffect(() => {
        fetchUsers();
    }, []);

    const fetchUsers = async () => {
        try {
            setLoading(true);
            const response = await api.get('/users/');
            setUsers(response.data);
        } catch (err) {
            setError('Failed to fetch users.');
        } finally {
            setLoading(false);
        }
    };

    const handleCreateUser = async (e) => {
        e.preventDefault();
        try {
            await api.post('/users/', newUser);
            setNewUser({ username: '', email: '', password: '', role: 'recruiter' });
            setShowCreateForm(false);
            fetchUsers();
        } catch (err) {
            setError('Failed to create user: ' + (err.response?.data?.detail || err.message));
        }
    };

    const handleDeleteUser = async (userId) => {
        if (window.confirm('Are you sure you want to delete this user?')) {
            try {
                await api.delete(`/users/${userId}`);
                fetchUsers();
            } catch (err) {
                setError('Failed to delete user: ' + (err.response?.data?.detail || err.message));
            }
        }
    };

    if (loading) {
        return <div className="text-center p-8">Loading...</div>;
    }

    if (error) {
        return <div className="text-center p-8 text-red-500">{error}</div>;
    }

    return (
        <div className="container mx-auto p-8">
            <h1 className="text-3xl font-bold mb-6 text-gray-800">User Management</h1>
            
            <div className="mb-6">
                <button
                    onClick={() => setShowCreateForm(!showCreateForm)}
                    className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 flex items-center"
                >
                    <Plus className="w-5 h-5 mr-2" />
                    {showCreateForm ? 'Cancel' : 'Create New User'}
                </button>
            </div>

            {showCreateForm && (
                <div className="bg-white p-6 rounded-lg shadow-md mb-6">
                    <h2 className="text-xl font-semibold mb-4">Create New User</h2>
                    <form onSubmit={handleCreateUser} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Username</label>
                            <input
                                type="text"
                                value={newUser.username}
                                onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                                className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Email</label>
                            <input
                                type="email"
                                value={newUser.email}
                                onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                                className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Password</label>
                            <input
                                type="password"
                                value={newUser.password}
                                onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                                className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Role</label>
                            <select
                                value={newUser.role}
                                onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                                className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
                            >
                                <option value="recruiter">Recruiter</option>
                                <option value="admin">Admin</option>
                                <option value="backend_team">Backend Team</option>
                            </select>
                        </div>
                        <div className="md:col-span-2">
                            <button
                                type="submit"
                                className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
                            >
                                Create User
                            </button>
                        </div>
                    </form>
                </div>
            )}

            <div className="bg-white shadow-lg rounded-lg">
                <ul className="divide-y divide-gray-200">
                    {users.length > 0 ? users.map((u) => (
                        <li key={u.id} className="p-6 hover:bg-gray-50 transition-colors">
                            <div className="flex items-center justify-between">
                                <div className="flex-grow">
                                    <p className="text-xl font-semibold text-gray-900">{u.username}</p>
                                    <p className="text-md text-gray-600">{u.email}</p>
                                    <p className="text-sm text-gray-500 mt-1">Role: {u.role}</p>
                                </div>
                                <div className="text-right flex-shrink-0 ml-6">
                                    <p className={`text-md font-medium ${u.is_active ? 'text-green-500' : 'text-red-500'}`}>
                                        {u.is_active ? 'Active' : 'Inactive'}
                                    </p>
                                    <div className="mt-2">
                                        <button
                                            onClick={() => handleDeleteUser(u.id)}
                                            className="px-3 py-1 bg-red-500 text-white rounded-lg hover:bg-red-600 flex items-center"
                                        >
                                            <Trash2 className="w-4 h-4 mr-1" /> Delete
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </li>
                    )) : (
                        <li className="p-6 text-center text-gray-500">No users found.</li>
                    )}
                </ul>
            </div>
        </div>
    );
};

export default UserManagementPage;
