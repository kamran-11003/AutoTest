import { useState } from 'react';

export default function SettingsForm() {
  const [errors, setErrors] = useState({});
  const [success, setSuccess] = useState(false);

  function handleSubmit(e) {
    e.preventDefault();
    const errs = {};
    const fd = new FormData(e.target);

    const dn = (fd.get('displayName') || '').trim();
    if (dn.length < 2 || dn.length > 50) errs.displayName = 'Display name must be 2-50 characters';

    const bio = (fd.get('bio') || '').trim();
    if (bio.length > 200) errs.bio = 'Bio must be 200 characters or fewer';

    if (!fd.get('timezone')) errs.timezone = 'Please select a timezone';

    setErrors(errs);
    if (Object.keys(errs).length === 0) setSuccess(true);
  }

  return (
    <div className="section-card" id="settings-section">
      <h2>Profile Settings</h2>
      <p>Update your display preferences.</p>

      {!success ? (
        <form id="settingsForm" noValidate onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="displayName">Display Name</label>
            <input type="text" id="displayName" name="displayName"
                   placeholder="2-50 characters" required minLength={2} maxLength={50} />
            <div className="error-msg" id="displayName-error">{errors.displayName || ''}</div>
          </div>

          <div className="form-group">
            <label htmlFor="bio">Bio</label>
            <textarea id="bio" name="bio" rows={3}
                      placeholder="Short bio (max 200 chars)" maxLength={200} />
            <div className="error-msg" id="bio-error">{errors.bio || ''}</div>
          </div>

          <div className="form-group">
            <label htmlFor="timezone">Timezone</label>
            <select id="timezone" name="timezone" required defaultValue="">
              <option value="" disabled>-- Select timezone --</option>
              <option value="UTC-8">Pacific (UTC-8)</option>
              <option value="UTC-5">Eastern (UTC-5)</option>
              <option value="UTC+0">GMT (UTC+0)</option>
              <option value="UTC+1">CET (UTC+1)</option>
              <option value="UTC+5">PKT (UTC+5)</option>
              <option value="UTC+8">CST (UTC+8)</option>
            </select>
            <div className="error-msg" id="timezone-error">{errors.timezone || ''}</div>
          </div>

          <div className="form-group">
            <div className="checkbox-group">
              <input type="checkbox" id="emailNotify" name="emailNotify" />
              <label htmlFor="emailNotify" style={{ fontWeight: 'normal' }}>
                Receive email notifications for task updates
              </label>
            </div>
          </div>

          <button type="submit">Save Settings</button>
        </form>
      ) : (
        <div className="success-banner" id="settingsSuccess">
          <h3>&#10004; Settings Saved</h3>
          <p>Your profile has been updated.</p>
        </div>
      )}
    </div>
  );
}
