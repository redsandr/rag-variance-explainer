import Head from 'next/head';

import Navbar from '../components/Navbar';
import HeroSection from '../components/HeroSection';
import HeroDemoCard from '../components/HeroDemoCard';
import TrustBar from '../components/TrustBar';
import ProblemSection from '../components/ProblemSection';
import DifferenceSection from '../components/DifferenceSection';
import DemoSample from '../components/DemoSample';
import HowItWorks from '../components/HowItWorks';
import EvidenceSection from '../components/EvidenceSection';
import UseCases from '../components/UseCases';
import FeaturesSection from '../components/FeaturesSection';
import QuickStart from '../components/QuickStart';
import RoadmapSection from '../components/RoadmapSection';
import StarOnGitHub from '../components/StarOnGitHub';
import AnimatedSection from '../components/AnimatedSection';
import Footer from '../components/Footer';

export default function Home() {
  return (
    <div className="antialiased bg-mesh min-h-screen">
      <Head>
        <title>RAG Variance Explainer &mdash; Ask why a metric moved</title>
        <meta
          name="description"
          content="A grounded RAG pipeline over real SEC 10-K/10-Q filings. Ask why a number moved and get a plain-English answer cited to the exact page, tested across 7 companies and 4 industries."
        />
      </Head>
      <Navbar />
      <main>
        <HeroSection />
        <AnimatedSection><HeroDemoCard /></AnimatedSection>
        <AnimatedSection><TrustBar /></AnimatedSection>
        <AnimatedSection><ProblemSection /></AnimatedSection>
        <AnimatedSection><DifferenceSection /></AnimatedSection>
        <AnimatedSection><DemoSample /></AnimatedSection>
        <AnimatedSection><HowItWorks /></AnimatedSection>
        <AnimatedSection><EvidenceSection /></AnimatedSection>
        <AnimatedSection><UseCases /></AnimatedSection>
        <AnimatedSection><FeaturesSection /></AnimatedSection>
        <AnimatedSection><QuickStart /></AnimatedSection>
        <AnimatedSection><RoadmapSection /></AnimatedSection>
        <AnimatedSection><StarOnGitHub /></AnimatedSection>
      </main>
      <Footer />
    </div>
  );
}
