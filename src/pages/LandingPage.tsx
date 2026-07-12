import React from 'react';
import { Navbar } from '../components/landing/Navbar';
import { Hero } from '../components/landing/Hero';
import { FeaturesBento } from '../components/landing/FeaturesBento';
import { WorkflowSection } from '../components/landing/WorkflowSection';
import { Footer } from '../components/landing/Footer';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background font-sans text-text-primary selection:bg-primary-soft selection:text-primary">
      <Navbar />
      <main>
        <Hero />
        <FeaturesBento />
        <WorkflowSection />
      </main>
      <Footer />
    </div>
  );
}
