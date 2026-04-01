import { useEffect, useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import Nav from '../components/Nav';

export default function Cart() {
  const [cart, setCart] = useState([]);

  useEffect(() => {
    setCart(JSON.parse(localStorage.getItem('shopEasyCart') || '[]'));
  }, []);

  const total = cart.reduce((s, i) => s + i.price, 0);

  return (
    <>
      <Head><title>ShopEasy - Cart</title></Head>
      <Nav />
      <div className="container">
        <h1>Shopping Cart</h1>
        <p>Review your items before checkout.</p>

        <table className="cart-table">
          <thead><tr><th>Item</th><th>Price</th></tr></thead>
          <tbody>
            {cart.length === 0 ? (
              <tr><td colSpan={2} style={{ textAlign: 'center', color: '#999' }}>Cart is empty</td></tr>
            ) : (
              cart.map((item, i) => (
                <tr key={i}><td>{item.name}</td><td>${item.price.toFixed(2)}</td></tr>
              ))
            )}
          </tbody>
        </table>
        {cart.length > 0 && (
          <div className="cart-total">Total: ${total.toFixed(2)}</div>
        )}

        <p style={{ marginTop: 20, textAlign: 'center' }}>
          <Link href="/checkout" className="back-link">Proceed to Checkout &rarr;</Link>
        </p>
      </div>
    </>
  );
}
