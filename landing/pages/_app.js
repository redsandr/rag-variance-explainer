import '../styles/globals.css';
import '../styles/vernie-animations.css';
import ScrollProgress from '../components/ScrollProgress';
import BackToTop from '../components/BackToTop';

export default function App({ Component, pageProps }) {
  return (
    <>
      <ScrollProgress />
      <Component {...pageProps} />
      <BackToTop />
    </>
  );
}
