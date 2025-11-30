'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { ArrowRight, Shield, Brain, FileCheck, Link2, Lock, Activity, Stethoscope, Database, Zap, Upload, Award, TrendingUp, BarChart3 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function LandingPage() {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <div className="min-h-screen bg-black relative overflow-hidden">
        <div className="fixed inset-0 blockchain-grid opacity-40" />
        <div className="fixed inset-0 hex-pattern opacity-25" />
        <div className="fixed inset-0 particle-bg" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black relative overflow-hidden">
      {/* Premium animated background elements */}
      <div className="fixed inset-0 blockchain-grid opacity-40" />
      <div className="fixed inset-0 hex-pattern opacity-25" />
      <div className="fixed inset-0 particle-bg" />
      
      {/* Enhanced floating blockchain blocks with premium animations */}
      <motion.div
        className="fixed top-20 left-10 w-20 h-20 blockchain-block rounded-xl animate-pulse-glow opacity-30"
        animate={{
          y: [0, -20, 0],
          rotate: [0, 5, 0],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
      <motion.div
        className="fixed top-40 right-20 w-16 h-16 blockchain-block rounded-xl animate-pulse-glow opacity-20"
        animate={{
          y: [0, 15, 0],
          rotate: [0, -5, 0],
        }}
        transition={{
          duration: 5,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 1
        }}
      />
      <motion.div
        className="fixed bottom-20 left-1/4 w-18 h-18 blockchain-block rounded-xl animate-pulse-glow opacity-25"
        animate={{
          y: [0, -10, 0],
          x: [0, 10, 0],
        }}
        transition={{
          duration: 6,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 2
        }}
      />
      
      {/* DNA Helix Visual Elements */}
      <div className="fixed top-1/4 right-10 w-32 h-32 opacity-20">
        <div className="dna-helix-container w-full h-full">
          <div className="dna-strand-enhanced" />
          <div className="dna-strand-enhanced" />
        </div>
      </div>
      
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-24 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center max-w-6xl mx-auto"
        >
          {/* Premium Logo with Enhanced Animation */}
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ delay: 0.3, type: "spring", stiffness: 200 }}
            className="flex justify-center mb-8"
          >
            <div className="relative">
              <div className="absolute inset-0 bg-green-500/30 rounded-full blur-3xl animate-pulse" />
              <div className="absolute inset-0 bg-green-500/20 rounded-full blur-2xl animate-pulse delay-1000" />
              <div className="relative bg-gradient-to-br from-green-500 via-green-600 to-emerald-700 p-8 rounded-3xl green-glow-intense animate-premium-glow">
                <Stethoscope className="h-16 w-16 text-white drop-shadow-lg" />
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-400 rounded-full animate-sparkle" />
              </div>
            </div>
          </motion.div>

          {/* Premium Heading */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <div className="inline-block mb-4 px-6 py-2 rounded-full clinical-badge">
              <span className="text-green-400 text-sm font-semibold flex items-center gap-2">
                <Award className="h-4 w-4" />
                Enterprise-Grade Platform
              </span>
            </div>
            
            <h1 className="text-6xl md:text-8xl font-extrabold mb-6 tracking-tight">
              <span className="text-white drop-shadow-[0_0_30px_rgba(34,197,94,0.3)]">TrialEquity</span>
              <br />
              <span className="text-premium-gradient text-5xl md:text-7xl font-light mt-2 block">
                Secure Clinical Trials
              </span>
              <span className="text-3xl md:text-4xl text-white/70 font-normal block mt-4">
                with AI & Blockchain Excellence
              </span>
            </h1>
          </motion.div>
          
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="text-xl md:text-2xl text-white mb-12 leading-relaxed max-w-4xl mx-auto"
          >
            Premium AI-Enhanced Blockchain Platform for Secure, Fair, and Regulatory-Compliant 
            <br className="hidden md:block" />
            <span className="text-green-400 font-semibold">Clinical Trial Data Management</span>
            <br className="hidden md:block" />
            <span className="text-white/70 text-lg">Trusted by leading pharmaceutical companies worldwide</span>
          </motion.p>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9 }}
            className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-12"
          >
            <Link href="/upload">
              <Button 
                size="lg" 
                className="text-lg px-12 py-8 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white border-2 border-green-400 green-glow-hover transition-all duration-300 group btn-premium relative overflow-hidden"
              >
                <Upload className="mr-3 h-6 w-6 group-hover:animate-bounce" />
                Upload Trial Data
                <ArrowRight className="ml-3 h-6 w-6 group-hover:translate-x-2 transition-transform" />
              </Button>
            </Link>
            <Link href="/blockchain">
              <Button 
                size="lg" 
                variant="outline"
                className="text-lg px-12 py-8 border-2 border-green-500/60 text-green-400 hover:bg-green-950/40 hover:border-green-400 transition-all duration-300 glass-effect-premium group"
              >
                <Link2 className="mr-3 h-6 w-6 group-hover:rotate-45 transition-transform" />
                Explore Blockchain
              </Button>
            </Link>
          </motion.div>

          {/* Premium Stats Bar */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.1 }}
            className="mt-16 glass-effect-premium rounded-2xl p-6 max-w-5xl mx-auto"
          >
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {[
                { icon: TrendingUp, value: '96%+', label: 'ML Accuracy', sublabel: 'Bias Detection' },
                { icon: Shield, value: '100%', label: 'Data Integrity', sublabel: 'Blockchain Verified' },
                { icon: Zap, value: '<1s', label: 'Processing', sublabel: 'Lightning Fast' },
                { icon: Award, value: '24/7', label: 'Enterprise', sublabel: 'Always On' },
              ].map((stat, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 1.3 + idx * 0.1 }}
                  className="text-center group cursor-default"
                >
                  <div className="inline-flex items-center justify-center w-14 h-14 bg-gradient-to-br from-green-500/20 to-emerald-500/20 rounded-xl mb-3 green-glow group-hover:scale-110 transition-transform">
                    <stat.icon className="h-7 w-7 text-green-400" />
                  </div>
                  <div className="text-3xl md:text-4xl font-bold text-white mb-1 text-premium-glow">
                    {stat.value}
                  </div>
                  <div className="text-sm font-semibold text-green-400">{stat.label}</div>
                  <div className="text-xs text-white/60">{stat.sublabel}</div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </motion.div>
      </section>

      {/* Premium Features Section */}
      <section className="container mx-auto px-4 py-32 relative z-10">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
          className="text-center mb-20"
        >
          <div className="inline-block mb-4 px-6 py-2 rounded-full clinical-badge">
            <span className="text-green-400 text-sm font-semibold">Core Capabilities</span>
          </div>
          <h2 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Powered by <span className="text-premium-gradient">Cutting-Edge Technology</span>
          </h2>
          <p className="text-xl text-white/70 max-w-3xl mx-auto leading-relaxed">
            Combining advanced AI, enterprise blockchain, and clinical research expertise 
            <br />to deliver unparalleled trial integrity and regulatory compliance
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-10 max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 1.7 }}
            whileHover={{ y: -15, transition: { duration: 0.3 } }}
          >
            <Card className="h-full premium-card blockchain-block glass-effect-premium border-green-500/40 hover:border-green-500/80 group">
              <CardHeader className="pb-6">
                <div className="relative mb-8">
                  <div className="absolute inset-0 bg-green-500/30 rounded-2xl blur-2xl group-hover:blur-3xl transition-all" />
                  <div className="relative w-20 h-20 bg-gradient-to-br from-green-500 to-emerald-700 rounded-2xl flex items-center justify-center green-glow-intense group-hover:scale-110 transition-transform">
                    <Brain className="h-10 w-10 text-white drop-shadow-lg animate-pulse" />
                  </div>
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full animate-sparkle" />
                </div>
                <CardTitle className="text-2xl md:text-3xl text-white mb-4 text-premium-glow">
                  ML Bias Detection
                </CardTitle>
                <CardDescription className="text-white text-base leading-relaxed">
                  Advanced machine learning models with 96%+ accuracy detect biased age groups, demographic 
                  imbalances, and invalid eligibility matches before trials enter the blockchain.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-4 text-sm text-white">
                  {[
                    'Isolation Forest outlier detection',
                    'XGBoost + Random Forest ensemble',
                    'SHAP/LIME explainability',
                    'Fairness metrics analysis',
                    'Statistical validation tests'
                  ].map((item, idx) => (
                    <motion.li
                      key={idx}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 1.9 + idx * 0.1 }}
                      className="flex items-center gap-3"
                    >
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse flex-shrink-0" style={{ animationDelay: `${idx * 100}ms` }} />
                      <span>{item}</span>
                    </motion.li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 1.9 }}
            whileHover={{ y: -15, transition: { duration: 0.3 } }}
          >
            <Card className="h-full premium-card blockchain-block glass-effect-premium border-green-500/40 hover:border-green-500/80 group">
              <CardHeader className="pb-6">
                <div className="relative mb-8">
                  <div className="absolute inset-0 bg-green-500/30 rounded-2xl blur-2xl group-hover:blur-3xl transition-all" />
                  <div className="relative w-20 h-20 bg-gradient-to-br from-green-500 to-emerald-700 rounded-2xl flex items-center justify-center green-glow-intense group-hover:scale-110 transition-transform">
                    <Link2 className="h-10 w-10 text-white drop-shadow-lg" />
                  </div>
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full animate-sparkle" style={{ animationDelay: '1000ms' }} />
                </div>
                <CardTitle className="text-2xl md:text-3xl text-white mb-4 text-premium-glow">
                  Blockchain Integrity
                </CardTitle>
                <CardDescription className="text-white text-base leading-relaxed">
                  Hyperledger Fabric ensures immutable, tamper-proof storage with 
                  real-time hash verification, instant tamper alerts, and multi-stakeholder consensus.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-4 text-sm text-white">
                  {[
                    'Permissioned blockchain network',
                    'Cryptographic hash verification',
                    'Multi-stakeholder consensus',
                    'Real-time tamper detection',
                    'Enterprise-grade security'
                  ].map((item, idx) => (
                    <motion.li
                      key={idx}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 2.1 + idx * 0.1 }}
                      className="flex items-center gap-3"
                    >
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse flex-shrink-0" />
                      <span>{item}</span>
                    </motion.li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 2.1 }}
            whileHover={{ y: -15, transition: { duration: 0.3 } }}
          >
            <Card className="h-full premium-card blockchain-block glass-effect-premium border-green-500/40 hover:border-green-500/80 group">
              <CardHeader className="pb-6">
                <div className="relative mb-8">
                  <div className="absolute inset-0 bg-green-500/30 rounded-2xl blur-2xl group-hover:blur-3xl transition-all" />
                  <div className="relative w-20 h-20 bg-gradient-to-br from-green-500 to-emerald-700 rounded-2xl flex items-center justify-center green-glow-intense group-hover:scale-110 transition-transform">
                    <Shield className="h-10 w-10 text-white drop-shadow-lg" />
                  </div>
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full animate-sparkle" style={{ animationDelay: '2000ms' }} />
                </div>
                <CardTitle className="text-2xl md:text-3xl text-white mb-4 text-premium-glow">
                  Regulatory Audit
                </CardTitle>
                <CardDescription className="text-white text-base leading-relaxed">
                  Comprehensive audit logs, digital signatures, and automated 
                  compliance reports for regulatory review and approval with full transparency.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-4 text-sm text-white">
                  {[
                    'Complete audit trail',
                    'Digital signature workflow',
                    'Auto-generated PDF reports',
                    'Role-based access control',
                    'Real-time compliance monitoring'
                  ].map((item, idx) => (
                    <motion.li
                      key={idx}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 2.3 + idx * 0.1 }}
                      className="flex items-center gap-3"
                    >
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse flex-shrink-0" />
                      <span>{item}</span>
                    </motion.li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </section>

      {/* Premium CTA Section */}
      <section className="container mx-auto px-4 py-32 text-center relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 2.5 }}
          className="max-w-4xl mx-auto"
        >
          <div className="blockchain-block glass-effect-premium rounded-3xl p-16 border-green-500/40 relative overflow-hidden">
            {/* Animated background effect */}
            <div className="absolute inset-0 animate-shimmer" />
            
            <motion.div
              initial={{ scale: 0.95 }}
              animate={{ scale: 1 }}
              transition={{ delay: 2.7, type: "spring", stiffness: 100 }}
              className="relative z-10"
            >
              <div className="inline-block mb-6 px-6 py-2 rounded-full clinical-badge">
                <span className="text-green-400 text-sm font-semibold flex items-center gap-2">
                  <BarChart3 className="h-4 w-4" />
                  Trusted Platform
                </span>
              </div>
              
              <h2 className="text-5xl md:text-6xl font-bold text-white mb-8">
                Ready to Secure Your
                <span className="text-premium-gradient block mt-2"> Clinical Trials?</span>
              </h2>
              <p className="text-xl text-white mb-12 leading-relaxed max-w-2xl mx-auto">
                Join leading pharmaceutical companies using enterprise blockchain technology 
                for unparalleled trial integrity and regulatory compliance
              </p>
              <div className="flex flex-col sm:flex-row gap-6 justify-center">
                <Link href="/upload">
                  <Button 
                    size="lg" 
                    className="text-lg px-14 py-9 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white border-2 border-green-400 green-glow-hover transition-all duration-300 group btn-premium relative overflow-hidden"
                  >
                    Get Started Now
                    <ArrowRight className="ml-3 h-6 w-6 group-hover:translate-x-2 transition-transform" />
                  </Button>
                </Link>
                <Link href="/compare">
                  <Button 
                    size="lg" 
                    variant="outline"
                    className="text-lg px-14 py-9 border-2 border-green-500/60 text-green-400 hover:bg-green-950/40 hover:border-green-400 transition-all duration-300 glass-effect-premium"
                  >
                    View Demo
                  </Button>
                </Link>
              </div>
            </motion.div>
          </div>
        </motion.div>
      </section>
    </div>
  )
}
