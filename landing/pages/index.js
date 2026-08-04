import Head from 'next/head';

import { SEO, FAQ } from '../data/seo';

import Navbar from '../components/Navbar';
import HeroSection from '../components/HeroSection';
import ProblemSection from '../components/ProblemSection';
import HeroDemoCard from '../components/HeroDemoCard';
import HowItWorks from '../components/HowItWorks';
import EvidenceSection from '../components/EvidenceSection';
import UseCases from '../components/UseCases';
import FeaturesSection from '../components/FeaturesSection';
import FAQSection from '../components/FAQSection';
import QuickStart from '../components/QuickStart';
import RoadmapSection from '../components/RoadmapSection';
import StarOnGitHub from '../components/StarOnGitHub';
import AnimatedSection from '../components/AnimatedSection';
import Footer from '../components/Footer';

export default function Home() {
  return (
    <div className="antialiased bg-mesh min-h-screen dark">
      <Head>
        <title>{SEO.title}</title>
        <meta name="description" content={SEO.description} />
        <meta name="keywords" content={SEO.keywords} />
        <meta name="theme-color" content={SEO.themeColor} />
        <link rel="canonical" href={`${SEO.url}/`} />

        <meta property="og:type" content="website" />
        <meta property="og:site_name" content={SEO.siteName} />
        <meta property="og:title" content={SEO.title} />
        <meta property="og:description" content={SEO.description} />
        <meta property="og:url" content={`${SEO.url}/`} />
        <meta property="og:image" content={`${SEO.url}${SEO.ogImage}`} />

        <meta name="twitter:card" content={SEO.twitter.card} />
        <meta name="twitter:title" content={SEO.title} />
        <meta name="twitter:description" content={SEO.description} />
        <meta name="twitter:image" content={`${SEO.url}${SEO.ogImage}`} />
        {SEO.twitter.handle ? <meta name="twitter:creator" content={SEO.twitter.handle} /> : null}

        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'SoftwareApplication',
              name: SEO.siteName,
              url: `${SEO.url}/`,
              description: SEO.description,
              applicationCategory: 'DeveloperApplication',
              operatingSystem: 'Any (LLM via llama.cpp, local)',
              license: 'https://opensource.org/licenses/MIT',
              offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
            }),
          }}
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'FAQPage',
              mainEntity: FAQ.map((f) => ({
                '@type': 'Question',
                name: f.q,
                acceptedAnswer: { '@type': 'Answer', text: f.a },
              })),
            }),
          }}
        />
      </Head>
      <Navbar />
      <main>
        <AnimatedSection><HeroSection /></AnimatedSection>
        <hr className="divider" />
        <AnimatedSection><ProblemSection /></AnimatedSection>
        <hr className="divider" />
        <AnimatedSection><HeroDemoCard /></AnimatedSection>
        <hr className="divider" />
        <AnimatedSection><HowItWorks /></AnimatedSection>
        <hr className="divider" />
        <AnimatedSection><EvidenceSection /></AnimatedSection>
        <hr className="divider" />
        <AnimatedSection><UseCases /></AnimatedSection>
        <hr className="divider" />
        <AnimatedSection><FeaturesSection /></AnimatedSection>
        <hr className="divider" />
        <AnimatedSection><FAQSection /></AnimatedSection>
        <hr className="divider" />
        <AnimatedSection><QuickStart /></AnimatedSection>
        <hr className="divider" />
        <AnimatedSection><RoadmapSection /></AnimatedSection>
        <AnimatedSection><StarOnGitHub /></AnimatedSection>
      </main>
      <Footer />
    </div>
  );
}