import { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import Nav from '../components/Nav';

export default function Home() {
  const [errors, setErrors] = useState({});
  const [success, setSuccess] = useState(false);

  function handleSubmit(e) {
    e.preventDefault();
    const errs = {};
    const fd = new FormData(e.target);

    const email = (fd.get('loginEmail') || '').trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errs.loginEmail = 'Enter a valid email address';
    }

    const pw = fd.get('loginPassword') || '';
    if (pw.length < 6) {
      errs.loginPassword = 'Password must be at least 6 characters';
    }

    setErrors(errs);
    if (Object.keys(errs).length === 0) setSuccess(true);
  }

  return (
    <>
      <Head><title>ShopEasy - Home</title></Head>
      <Nav />
      <div className="container">
        <h1>Welcome to ShopEasy</h1>
        <p>Sign in to your account to start shopping.</p>

        {!success ? (
          <form id="loginForm" noValidate onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="loginEmail">Email Address</label>
              <input type="email" id="loginEmail" name="loginEmail"
                     placeholder="you@example.com" required />
              <div className="error-msg" id="loginEmail-error">{errors.loginEmail || ''}</div>
            </div>

            <div className="form-group">
              <label htmlFor="loginPassword">Password</label>
              <input type="password" id="loginPassword" name="loginPassword"
                     placeholder="Min 6 characters" required minLength={6} />
              <div className="error-msg" id="loginPassword-error">{errors.loginPassword || ''}</div>
            </div>

            <button type="submit">Sign In</button>
          </form>
        ) : (
          <div className="success-banner" id="loginSuccess" style={{ display: 'block' }}>
            <h1>&#10004; Signed In</h1>
            <p>Welcome back! <Link href="/products">Browse products &rarr;</Link></p>
          </div>
        )}
      </div>
    </>
  );
}
