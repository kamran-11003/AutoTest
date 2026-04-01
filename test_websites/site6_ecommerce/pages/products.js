import Head from 'next/head';
import Link from 'next/link';
import Nav from '../components/Nav';

const PRODUCTS = [
  { name: 'Wireless Headphones', price: 49.99 },
  { name: 'USB-C Hub', price: 29.99 },
  { name: 'Laptop Stand', price: 39.99 },
];

export default function Products() {
  function addToCart(name, price) {
    if (typeof window === 'undefined') return;
    const cart = JSON.parse(localStorage.getItem('shopEasyCart') || '[]');
    cart.push({ name, price });
    localStorage.setItem('shopEasyCart', JSON.stringify(cart));
    alert(name + ' added to cart!');
  }

  return (
    <>
      <Head><title>ShopEasy - Products</title></Head>
      <Nav />
      <div className="container" style={{ maxWidth: 720 }}>
        <h1>Our Products</h1>
        <p>Click &quot;Add to Cart&quot; then proceed to checkout.</p>

        <div className="product-grid">
          {PRODUCTS.map((p) => (
            <div className="product-card" key={p.name}>
              <h3>{p.name}</h3>
              <div className="price">${p.price.toFixed(2)}</div>
              <button className="btn-primary"
                      onClick={() => addToCart(p.name, p.price)}>Add to Cart</button>
            </div>
          ))}
        </div>

        <p style={{ marginTop: 24, textAlign: 'center' }}>
          <Link href="/cart" className="back-link">View Cart &rarr;</Link>
        </p>
      </div>
    </>
  );
}
