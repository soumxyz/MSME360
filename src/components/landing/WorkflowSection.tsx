import React from 'react';
import { motion } from 'framer-motion';
import { Database, BrainCircuit } from 'lucide-react';
import { FadeIn } from './Hero';

export function WorkflowSection() {
  return (
    <section id="workflow" className="py-24 bg-white relative border-t border-border">
      <div className="max-w-[1440px] mx-auto px-6 lg:px-12">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          
          <FadeIn>
            <h2 className="font-display text-4xl font-bold text-text-primary mb-6 tracking-tight">The Fastest Path to Approval</h2>
            <p className="text-lg text-text-secondary mb-10">We've collapsed a 3-week manual underwriting process into a 3-minute digital flow. Secure, compliant, and frictionless.</p>
            
            <div className="space-y-8">
              {[
                { step: "01", title: "Digital Intake", desc: "Borrower securely authenticates via Aadhaar and inputs basic parameters." },
                { step: "02", title: "Data Pull", desc: "System instantly fetches tax filings and bank statements via consent pipelines." },
                { step: "03", title: "AI Generation", desc: "Our engine cross-references millions of data points to draft the credit memo." },
                { step: "04", title: "Human Finalization", desc: "Officer reviews the AI recommendation, adjusts limits in the simulator, and approves." }
              ].map((item, i) => (
                <div key={i} className="flex gap-6 group">
                  <div className="flex-shrink-0 mt-1">
                    <span className="text-sm font-bold font-display text-primary bg-primary-soft px-3 py-1 rounded-full group-hover:bg-primary group-hover:text-white transition-colors">{item.step}</span>
                  </div>
                  <div>
                    <h4 className="text-lg font-bold text-text-primary mb-2">{item.title}</h4>
                    <p className="text-text-secondary">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </FadeIn>

          <FadeIn delay={0.2} className="relative h-[600px] w-full rounded-card bg-background border border-border overflow-hidden flex items-center justify-center p-8 shadow-inner">
             {/* Animated graphic representing data flow */}
             <div className="absolute inset-0 bg-[linear-gradient(to_right,#cbd5e144_1px,transparent_1px),linear-gradient(to_bottom,#cbd5e144_1px,transparent_1px)] bg-[size:24px_24px]" aria-hidden="true"></div>
             
             <div className="relative z-10 w-full max-w-sm" aria-hidden="true">
                <div className="bg-white rounded-card shadow-card p-6 border border-border mb-6 transform translate-x-4">
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-xs font-bold uppercase tracking-wider text-text-secondary">Input Data</span>
                    <Database className="w-4 h-4 text-primary" />
                  </div>
                  <div className="space-y-3">
                    <div className="h-2 bg-background-muted rounded-full w-3/4"></div>
                    <div className="h-2 bg-background-muted rounded-full w-1/2"></div>
                  </div>
                </div>

                <div className="flex justify-center mb-6">
                  <div className="h-12 w-px bg-primary-soft relative">
                    <motion.div 
                      animate={{ top: ["0%", "100%"] }}
                      transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                      className="absolute left-1/2 -translate-x-1/2 w-2 h-2 rounded-full bg-primary shadow-glow"
                    />
                  </div>
                </div>

                <div className="bg-white rounded-card shadow-card p-6 border border-primary transform -translate-x-4 relative overflow-hidden">
                  <div className="absolute inset-0 bg-primary-soft/30"></div>
                  <div className="relative z-10">
                    <div className="flex justify-between items-center mb-4">
                      <span className="text-xs font-bold uppercase tracking-wider text-primary">AI Engine Output</span>
                      <BrainCircuit className="w-4 h-4 text-primary" />
                    </div>
                    <div className="text-3xl font-display font-bold text-text-primary mb-2">Approved</div>
                    <div className="text-text-secondary text-sm">Limit: ₹50,00,000</div>
                  </div>
                </div>
             </div>
          </FadeIn>

        </div>
      </div>
    </section>
  );
}
