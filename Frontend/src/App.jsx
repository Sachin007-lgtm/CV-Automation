import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import JDCVMatcher from './pages/JDCVMatcher';
import LoginPage from './pages/LoginPage';
import JDManagementPage from './pages/JDManagementPage';
import JDEditPage from './pages/JDEditPage'; // Renamed from JDDetailPage
import JDAnalysesPage from './pages/JDAnalysesPage'; // New import
import UploadCVsPage from './pages/UploadCVsPage';
import UserManagementPage from './pages/UserManagementPage';
import ProtectedRoute from './components/ProtectedRoute';
import MainLayout from './components/MainLayout';
import './index.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
          <Route path="/" element={<JDCVMatcher />} />
          <Route path="/past-analyses" element={<JDCVMatcher isPastAnalysesPage={true} />} />
          <Route path="/jds" element={<JDManagementPage />} />
          <Route path="/jds/:jdId/edit" element={<JDEditPage />} />
          <Route path="/jds/:jdId/analyses" element={<JDAnalysesPage />} />
          <Route path="/jds/:jdId/upload" element={<UploadCVsPage />} />
          <Route 
            path="/users" 
            element={
              <ProtectedRoute adminOnly={true}>
                <UserManagementPage />
              </ProtectedRoute>
            }
          />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;