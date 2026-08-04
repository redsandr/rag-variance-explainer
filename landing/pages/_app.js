import '../styles/globals.css';
import ScrollProgress from '../components/ScrollProgress';
import BackToTop from '../components/BackToTop';

function applyTheme() {
  try {
    const saved = localStorage.getItem('theme');
    const el = document.documentElement;
    if (saved === 'dark') el.classList.add('dark');
    else el.classList.remove('dark');
  } catch (e) { /* SSR / private mode */ }
}

export default function App({ Component, pageProps }) {
  if (typeof document !== 'undefined') applyTheme();
  return (
    <>
      <ScrollProgress />
      <Component {...pageProps} />
      <BackToTop />
    </>
  );
}
