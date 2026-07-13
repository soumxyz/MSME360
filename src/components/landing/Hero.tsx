import React from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { Link } from 'react-router-dom';
import { ArrowRight, Database, ShieldCheck } from 'lucide-react';

export const FadeIn = ({ children, delay = 0, className = "" }: { children: React.ReactNode, delay?: number, className?: string }) => (
  <motion.div
    initial={{ opacity: 0, y: 30 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true, margin: "-50px" }}
    transition={{ duration: 0.7, delay, ease: [0.21, 0.47, 0.32, 0.98] }}
    className={className}
  >
    {children}
  </motion.div>
);

export function Hero() {
  const { scrollY } = useScroll();
  const y1 = useTransform(scrollY, [0, 1000], [0, 200]);
  const y2 = useTransform(scrollY, [0, 1000], [0, -100]);
  const opacity = useTransform(scrollY, [0, 500], [1, 0]);

  return (
    <section className="relative min-h-[90vh] bg-background flex items-center pt-28 pb-16 overflow-hidden">
      {/* Dynamic Background Gradients - Light Mode Safe */}
      <div className="absolute top-0 inset-x-0 h-full overflow-hidden pointer-events-none">
        <div className="absolute -top-[40%] -right-[10%] w-[70%] h-[70%] rounded-full bg-primary-soft/50 blur-[120px]" />
        <div className="absolute top-[20%] -left-[10%] w-[50%] h-[50%] rounded-full bg-accent-soft/50 blur-[120px]" />
      </div>

      <div className="max-w-[1440px] mx-auto px-6 lg:px-12 relative z-10 w-full">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          
          <motion.div style={{ opacity }} className="max-w-2xl">
            <FadeIn delay={0.1}>
              <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-primary-soft border border-primary/10 rounded-full text-xs font-medium text-primary mb-8">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
                </span>
                Live Connected Data Feeds
              </div>
            </FadeIn>
            
            <FadeIn delay={0.2}>
              <h1 className="font-display text-5xl md:text-7xl font-bold text-text-primary leading-[1.1] tracking-tight mb-6">
                Institutional Trust <br />
                <span className="text-primary">
                  Meets Next-Gen AI.
                </span>
              </h1>
            </FadeIn>
            
            <FadeIn delay={0.3}>
              <p className="text-lg md:text-xl text-text-secondary mb-10 leading-relaxed max-w-xl font-light">
                Securely connect your GST, Bank, and UPI data. Our enterprise-grade underwriting engine provides instant, explainable credit decisions for modern MSMEs.
              </p>
            </FadeIn>
            
            <FadeIn delay={0.4}>
              <div className="flex flex-wrap items-center gap-4">
                <Link 
                  to="/register" 
                  className="group bg-primary hover:bg-primary-hover text-white px-8 py-4 rounded-card font-semibold flex items-center gap-2 transition-all shadow-card focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
                >
                  Start Assessment 
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" aria-hidden="true" />
                </Link>
              </div>
            </FadeIn>
          </motion.div>

          {/* Floating UI Elements */}
          <div className="hidden lg:block relative h-[600px] w-full perspective-1000" aria-hidden="true">
            <motion.div style={{ y: y1 }} className="absolute top-[10%] right-[10%] w-[320px] bg-white border border-border rounded-card p-6 shadow-card">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-primary-soft flex items-center justify-center">
                    <ShieldCheck className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <div className="text-text-primary font-medium text-sm">Credit Score</div>
                    <div className="text-text-secondary text-xs">Updated just now</div>
                  </div>
                </div>
                <div className="text-primary font-display font-bold text-2xl">845</div>
              </div>
              <div className="space-y-3">
                <div className="h-2 w-full bg-background-muted rounded-full overflow-hidden">
                  <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: "85%" }}
                    transition={{ duration: 1.5, delay: 1 }}
                    className="h-full bg-primary"
                  />
                </div>
                <div className="flex justify-between text-xs text-text-secondary">
                  <span>Risk: Low</span>
                  <span>Probability: 98%</span>
                </div>
              </div>
            </motion.div>

            <motion.div style={{ y: y2 }} className="absolute top-[45%] left-[5%] w-[280px] bg-white border border-border rounded-card p-5 shadow-card">
              <div className="flex items-center gap-3 mb-4">
                <Database className="w-5 h-5 text-accent" />
                <span className="text-text-primary font-medium text-sm">Data Pipeline Active</span>
              </div>
              <div className="space-y-4">
                {[
                  { name: 'GST Returns', status: 'Synced', color: 'text-success' },
                  { name: 'Bank Statements', status: 'Processing', color: 'text-warning' },
                  { name: 'UPI Transactions', status: 'Synced', color: 'text-success' }
                ].map((item, i) => (
                  <div key={i} className="flex items-center justify-between">
                    <span className="text-text-secondary text-xs font-medium">{item.name}</span>
                    <span className={`text-[10px] uppercase tracking-wider font-bold ${item.color}`}>{item.status}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
          
        </div>
      </div>
      
    </section>
  );
}
