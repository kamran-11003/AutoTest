import { useState } from 'react';

export default function TaskForm() {
  const [errors, setErrors] = useState({});
  const [success, setSuccess] = useState(false);

  function handleSubmit(e) {
    e.preventDefault();
    const errs = {};
    const fd = new FormData(e.target);

    const title = (fd.get('taskTitle') || '').trim();
    if (title.length < 3 || title.length > 100) errs.taskTitle = 'Title must be 3-100 characters';

    const desc = (fd.get('taskDesc') || '').trim();
    if (desc.length < 10 || desc.length > 500) errs.taskDesc = 'Description must be 10-500 characters';

    if (!fd.get('priority')) errs.priority = 'Select a priority';
    if (!fd.get('category')) errs.category = 'Select a category';

    const due = fd.get('dueDate');
    if (!due) {
      errs.dueDate = 'Due date is required';
    } else {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      if (new Date(due) < today) errs.dueDate = 'Due date cannot be in the past';
    }

    setErrors(errs);
    if (Object.keys(errs).length === 0) setSuccess(true);
  }

  return (
    <div className="section-card" id="task-section">
      <h2>New Task</h2>
      <p>Add a task to your board.</p>

      {!success ? (
        <form id="taskForm" noValidate onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="taskTitle">Task Title</label>
            <input type="text" id="taskTitle" name="taskTitle"
                   placeholder="3-100 characters" required minLength={3} maxLength={100} />
            <div className="error-msg" id="taskTitle-error">{errors.taskTitle || ''}</div>
          </div>

          <div className="form-group">
            <label htmlFor="taskDesc">Description</label>
            <textarea id="taskDesc" name="taskDesc" rows={4}
                      placeholder="Describe the task (10-500 chars)"
                      required minLength={10} maxLength={500} />
            <div className="error-msg" id="taskDesc-error">{errors.taskDesc || ''}</div>
          </div>

          <div className="row-2col">
            <div className="form-group">
              <label htmlFor="priority">Priority</label>
              <select id="priority" name="priority" required defaultValue="">
                <option value="" disabled>-- Select --</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
              <div className="error-msg" id="priority-error">{errors.priority || ''}</div>
            </div>
            <div className="form-group">
              <label htmlFor="category">Category</label>
              <select id="category" name="category" required defaultValue="">
                <option value="" disabled>-- Select --</option>
                <option value="frontend">Frontend</option>
                <option value="backend">Backend</option>
                <option value="devops">DevOps</option>
                <option value="testing">Testing</option>
                <option value="design">Design</option>
              </select>
              <div className="error-msg" id="category-error">{errors.category || ''}</div>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="dueDate">Due Date</label>
            <input type="date" id="dueDate" name="dueDate" required />
            <div className="error-msg" id="dueDate-error">{errors.dueDate || ''}</div>
          </div>

          <button type="submit">Add Task</button>
        </form>
      ) : (
        <div className="success-banner" id="taskSuccess">
          <h3>&#10004; Task Added</h3>
          <p>Your task has been added to the board.</p>
        </div>
      )}
    </div>
  );
}
