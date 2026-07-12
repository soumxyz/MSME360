import React from 'react';
import { Database, BrainCircuit, ShieldCheck, LineChart, Building2 } from 'lucide-react';
import { FadeIn } from './Hero';

export function FeaturesBento() {
  return (
    <section id="features" className="py-24 bg-background-muted relative z-30 border-t border-border">
      <div className="max-w-[1440px] mx-auto px-6 lg:px-12">
        <FadeIn className="text-left max-w-3xl mb-16">
          <h2 className="font-display text-4xl md:text-5xl font-bold text-text-primary mb-6 tracking-tight">Complete Underwriting Infrastructure</h2>
          <p className="text-text-secondary text-lg">Everything an institution needs to evaluate MSME creditworthiness at scale, unified in a single intelligence layer.</p>
        </FadeIn>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-min md:auto-rows-[280px]">
          
          {/* Large Feature 1 */}
          <FadeIn delay={0.1} className="md:col-span-2 bg-white rounded-card p-10 shadow-card border border-border relative overflow-hidden group hover:shadow-lg transition-shadow duration-300">
            <div className="relative z-10 md:w-2/3 h-full flex flex-col">
              <div className="w-12 h-12 bg-primary-soft text-primary rounded-xl flex items-center justify-center mb-6">
                <BrainCircuit className="w-6 h-6" />
              </div>
              <h3 className="text-2xl font-bold font-display text-text-primary mb-4">Explainable AI Core</h3>
              <p className="text-text-secondary">Our models don't just output a number. Every credit decision is backed by a generated executive memo explaining exactly which data points drove the outcome.</p>
            </div>
          </FadeIn>

          {/* Square Feature 1 */}
          <FadeIn delay={0.2} className="bg-primary rounded-card p-8 shadow-card border border-primary relative overflow-hidden group hover:shadow-lg hover:shadow-primary/20 transition-shadow duration-300">
            <div className="w-12 h-12 bg-white/20 text-white rounded-xl flex items-center justify-center mb-6">
              <Database className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold font-display text-white mb-3">Consent Pipelines</h3>
            <p className="text-primary-soft text-sm">Direct integrations with Account Aggregators and GSTN for tamper-proof data.</p>
          </FadeIn>

          {/* Square Feature 2 */}
          <FadeIn delay={0.3} className="bg-white rounded-card p-8 shadow-card border border-border hover:shadow-lg transition-shadow duration-300">
            <div className="w-12 h-12 bg-accent-soft text-accent rounded-xl flex items-center justify-center mb-6">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold font-display text-text-primary mb-3">Fraud Detection</h3>
            <p className="text-text-secondary text-sm">Automated ledger scanning for circular flows and balance manipulation.</p>
          </FadeIn>

          {/* Square Feature 3 */}
          <FadeIn delay={0.4} className="bg-white rounded-card p-8 shadow-card border border-border hover:shadow-lg transition-shadow duration-300">
             <div className="w-12 h-12 bg-background-muted text-text-primary rounded-xl flex items-center justify-center mb-6">
              <LineChart className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold font-display text-text-primary mb-3">Dynamic Scoring</h3>
            <p className="text-text-secondary text-sm">Real-time health grading across liquidity, stability, and growth axes.</p>
          </FadeIn>

          {/* Square Feature 4 */}
          <FadeIn delay={0.5} className="bg-white rounded-card p-8 shadow-card border border-border hover:shadow-lg transition-shadow duration-300">
             <div className="w-12 h-12 bg-accent-soft text-accent rounded-xl flex items-center justify-center mb-6">
              <Building2 className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold font-display text-text-primary mb-3">Registry Checks</h3>
            <p className="text-text-secondary text-sm">Instant KYB validation against PAN, Udyam, and MCA databases.</p>
          </FadeIn>

        </div>
      </div>
    </section>
  );
}
