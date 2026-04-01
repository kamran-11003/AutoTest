import { Routes, Route } from 'react-router-dom';
import Nav from './components/Nav';
import SignupForm from './components/SignupForm';
import TaskForm from './components/TaskForm';
import SettingsForm from './components/SettingsForm';

export default function App() {
  return (
    <>
      <Nav />
      <Routes>
        <Route path="/" element={<SignupForm />} />
        <Route path="/tasks" element={<TaskForm />} />
        <Route path="/settings" element={<SettingsForm />} />
      </Routes>
    </>
  );
}
