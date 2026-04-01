import { NavLink } from 'react-router-dom';

export default function Nav() {
  return (
    <nav>
      <span className="brand">TaskBoard</span>
      <NavLink to="/" end className={({ isActive }) => isActive ? 'active' : ''}>Sign Up</NavLink>
      <NavLink to="/tasks" className={({ isActive }) => isActive ? 'active' : ''}>New Task</NavLink>
      <NavLink to="/settings" className={({ isActive }) => isActive ? 'active' : ''}>Settings</NavLink>
    </nav>
  );
}
