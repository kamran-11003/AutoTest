import Link from 'next/link';
import { useRouter } from 'next/router';

export default function Nav() {
  const { pathname } = useRouter();
  return (
    <nav>
      <span className="brand">ShopEasy</span>
      <Link href="/" className={pathname === '/' ? 'active' : ''}>Home</Link>
      <Link href="/products" className={pathname === '/products' ? 'active' : ''}>Products</Link>
      <Link href="/cart" className={pathname === '/cart' ? 'active' : ''}>Cart</Link>
      <Link href="/checkout" className={pathname === '/checkout' ? 'active' : ''}>Checkout</Link>
    </nav>
  );
}
