import { useState } from 'react';

export default function SignupForm() {
  const [errors, setErrors] = useState({});
  const [success, setSuccess] = useState(false);

  function handleSubmit(e) {
    e.preventDefault();
    const errs = {};
    const fd = new FormData(e.target);

    const user = (fd.get('username') || '').trim();
    if (!/^[a-zA-Z0-9_]{3,20}$/.test(user)) {
      errs.username = 'Username must be 3-20 alphanumeric characters';
    }

    const email = (fd.get('signupEmail') || '').trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errs.signupEmail = 'Enter a valid email address';
    }

    const pw = fd.get('signupPassword') || '';
    if (pw.length < 8) {
      errs.signupPassword = 'Password must be at least 8 characters';
    } else if (!/[A-Z]/.test(pw) || !/\d/.test(pw)) {
      errs.signupPassword = 'Must contain an uppercase letter and a digit';
    }

    if (!fd.get('role')) errs.role = 'Please select a role';

    setErrors(errs);
    if (Object.keys(errs).length === 0) setSuccess(true);
  }

  return (
    <div className="section-card" id="signup-section">
      <h2>Create Account</h2>
      <p>Sign up to start managing your tasks.</p>

      {!success ? (
        <form id="signupForm" noValidate onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input type="text" id="username" name="username"
                   placeholder="3-20 characters, letters/numbers only"
                   required minLength={3} maxLength={20} />
            <div className="error-msg" id="username-error">{errors.username || ''}</div>
          </div>

          <div className="form-group">
            <label htmlFor="signupEmail">Email</label>
            <input type="email" id="signupEmail" name="signupEmail"
                   placeholder="you@example.com" required />
            <div className="error-msg" id="signupEmail-error">{errors.signupEmail || ''}</div>
          </div>

          <div className="form-group">
            <label htmlFor="signupPassword">Password</label>
            <input type="password" id="signupPassword" name="signupPassword"
                   placeholder="Min 8 chars, 1 uppercase, 1 digit"
                   required minLength={8} />
            <div className="error-msg" id="signupPassword-error">{errors.signupPassword || ''}</div>
          </div>

          <div className="form-group">
            <label htmlFor="role">Role</label>
            <select id="role" name="role" required defaultValue="">
              <option value="" disabled>-- Select role --</option>
              <option value="developer">Developer</option>
              <option value="designer">Designer</option>
              <option value="manager">Project Manager</option>
              <option value="qa">QA Tester</option>
            </select>
            <div className="error-msg" id="role-error">{errors.role || ''}</div>
          </div>

          <button type="submit">Create Account</button>
        </form>
      ) : (
        <div className="success-banner" id="signupSuccess">
          <h3>&#10004; Account Created</h3>
          <p>You can now create tasks.</p>
        </div>
      )}
    </div>
  );
}
