import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        {/* Modern browsers use the SVG (crisp at any size); others fall back to the ICO */}
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
        <link rel="alternate icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <meta name="theme-color" content="#f8f7f2" />
        <script
          dangerouslySetInnerHTML={{
            __html: `try{k=localStorage.getItem('theme');if(k==='dark')document.documentElement.classList.add('dark')}catch(e){}`,
          }}
        />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
