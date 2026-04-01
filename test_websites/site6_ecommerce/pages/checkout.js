import { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import Nav from '../components/Nav';

export default function Checkout() {
  const [errors, setErrors] = useState({});
  const [success, setSuccess] = useState(false);

  function handleSubmit(e) {
    e.preventDefault();
    const errs = {};
    const fd = new FormData(e.target);

    const name = (fd.get('fullName') || '').trim();
    if (name.length < 2 || name.length > 60) errs.fullName = 'Name must be 2-60 characters';

    const email = (fd.get('shippingEmail') || '').trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errs.shippingEmail = 'Enter a valid email';

    const addr = (fd.get('address') || '').trim();
    if (addr.length < 5 || addr.length > 120) errs.address = 'Address must be 5-120 characters';

    const city = (fd.get('city') || '').trim();
    if (city.length < 2 || city.length > 50) errs.city = 'City must be 2-50 characters';

    const zip = (fd.get('zipCode') || '').trim();
    if (!/^\d{5}$/.test(zip)) errs.zipCode = 'ZIP must be exactly 5 digits';

    const card = (fd.get('cardNumber') || '').replace(/\s/g, '');
    if (!/^\d{13,19}$/.test(card)) errs.cardNumber = 'Card number must be 13-19 digits';

    const expiry = (fd.get('expiry') || '').trim();
    if (!/^(0[1-9]|1[0-2])\/\d{2}$/.test(expiry)) {
      errs.expiry = 'Enter expiry as MM/YY';
    } else {
      const [mm, yy] = expiry.split('/');
      const expYear = parseInt('20' + yy, 10);
      const expMonth = parseInt(mm, 10);
      const now = new Date();
      if (expYear < now.getFullYear() || (expYear === now.getFullYear() && expMonth < now.getMonth() + 1)) {
        errs.expiry = 'Card has expired';
      }
    }

    const cvv = (fd.get('cvv') || '').trim();
    if (!/^\d{3,4}$/.test(cvv)) errs.cvv = 'CVV must be 3 or 4 digits';

    setErrors(errs);
    if (Object.keys(errs).length === 0) {
      if (typeof window !== 'undefined') localStorage.removeItem('shopEasyCart');
      setSuccess(true);
    }
  }

  return (
    <>
      <Head><title>ShopEasy - Checkout</title></Head>
      <Nav />
      <div className="container">
        <h1>Checkout</h1>
        <p>Enter your shipping and payment details.</p>

        {!success ? (
          <form id="checkoutForm" noValidate onSubmit={handleSubmit}>
            <h2>Shipping</h2>

            <div className="form-group">
              <label htmlFor="fullName">Full Name</label>
              <input type="text" id="fullName" name="fullName"
                     placeholder="John Doe" required minLength={2} maxLength={60} />
              <div className="error-msg" id="fullName-error">{errors.fullName || ''}</div>
            </div>

            <div className="form-group">
              <label htmlFor="shippingEmail">Email</label>
              <input type="email" id="shippingEmail" name="shippingEmail"
                     placeholder="you@example.com" required />
              <div className="error-msg" id="shippingEmail-error">{errors.shippingEmail || ''}</div>
            </div>

            <div className="form-group">
              <label htmlFor="address">Street Address</label>
              <input type="text" id="address" name="address"
                     placeholder="123 Main St" required minLength={5} maxLength={120} />
              <div className="error-msg" id="address-error">{errors.address || ''}</div>
            </div>

            <div className="row-2col">
              <div className="form-group">
                <label htmlFor="city">City</label>
                <input type="text" id="city" name="city"
                       placeholder="New York" required minLength={2} maxLength={50} />
                <div className="error-msg" id="city-error">{errors.city || ''}</div>
              </div>
              <div className="form-group">
                <label htmlFor="zipCode">ZIP Code</label>
                <input type="text" id="zipCode" name="zipCode"
                       placeholder="10001" required />
                <div className="error-msg" id="zipCode-error">{errors.zipCode || ''}</div>
              </div>
            </div>

            <h2 style={{ marginTop: 24 }}>Payment</h2>

            <div className="form-group">
              <label htmlFor="cardNumber">Card Number</label>
              <input type="text" id="cardNumber" name="cardNumber"
                     placeholder="1234 5678 9012 3456" required minLength={13} maxLength={19} />
              <div className="error-msg" id="cardNumber-error">{errors.cardNumber || ''}</div>
            </div>

            <div className="row-2col">
              <div className="form-group">
                <label htmlFor="expiry">Expiry (MM/YY)</label>
                <input type="text" id="expiry" name="expiry"
                       placeholder="12/26" required />
                <div className="error-msg" id="expiry-error">{errors.expiry || ''}</div>
              </div>
              <div className="form-group">
                <label htmlFor="cvv">CVV</label>
                <input type="text" id="cvv" name="cvv"
                       placeholder="123" required minLength={3} maxLength={4} />
                <div className="error-msg" id="cvv-error">{errors.cvv || ''}</div>
              </div>
            </div>

            <button type="submit">Place Order</button>
          </form>
        ) : (
          <div className="success-banner" id="checkoutSuccess" style={{ display: 'block' }}>
            <h1>&#10004; Order Placed!</h1>
            <p>Thank you for your purchase.</p>
            <Link href="/" className="back-link">&larr; Back to Home</Link>
          </div>
        )}
      </div>
    </>
  );
}
