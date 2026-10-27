import React, { useState, useEffect } from 'react';
import { ShieldCheck, Activity } from 'lucide-react';
import { api } from '../services/api';

export const BrandLogo = ({ className = "w-8 h-8 text-[#F2B731]" }) => (
  <svg className={className} viewBox="0 0 48 48" fill="currentColor">
    <path d="M18 4C18 2.89543 18.8954 2 20 2H28C29.1046 2 30 2.89543 30 4V8H34C35.1046 8 36 8.89543 36 10V14C36 15.1046 35.1046 16 34 16H32V18C38.6274 18 44 23.3726 44 30V44C44 45.1046 43.1046 46 42 46H6C4.89543 46 4 45.1046 4 44V30C4 23.3726 9.37258 18 16 18V16H14C12.8954 16 12 15.1046 12 14V10C12 8.89543 12.8954 8 14 8H18V4Z" />
    <rect x="22" y="34" width="12" height="6" rx="2" fill="#221F1D" opacity="0.15" />
  </svg>
);

export default function Navbar({ activeTab, setActiveTab }) {
  const [backendStatus, setBackendStatus] = useState('checking'); // 'ok', 'error', 'checking'

  useEffect(() => {
    let isMounted = true;
    api.checkHealth()
      .then(() => {
        if (isMounted) setBackendStatus('ok');
      })
      .catch(() => {
        if (isMounted) setBackendStatus('error');
      });
    return () => { isMounted = false; };
  }, []);

  const navItems = [
    { id: 'overview', label: 'Overview' },
    { id: 'workspace', label: 'Label Scanner' },
    { id: 'barcode', label: 'Barcode Lookup' },
    { id: 'exposure', label: 'Exposure Calculator' },
    { id: 'evidence', label: 'Evidence Database' },
    { id: 'anveshana', label: 'Citizen Science' },
  ];

  return (
    <header className="w-full bg-[#F8F6F0] border-b border-[#E8E4DC] sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-6 py-3.5 flex items-center justify-between">
        {/* Brand */}
        <button 
          onClick={() => setActiveTab('overview')} 
          className="flex items-center gap-3 group cursor-pointer text-left focus:outline-none"
        >
          <BrandLogo className="w-8 h-8 text-[#F2B731] transition-transform group-hover:scale-105" />
          <div className="flex flex-col">
            <span className="font-serif-heading font-bold text-xl tracking-wide text-[#221F1D]">
              NUTRIDECODE <span className="text-[#A8472A]">AI</span>
            </span>
            <span className="text-[10px] uppercase tracking-widest text-[#67625B] font-medium">
              Food-Label Intelligence & Safety
            </span>
          </div>
        </button>

        {/* Navigation */}
        <nav className="hidden lg:flex items-center gap-6 text-[11px] font-semibold tracking-widest uppercase text-[#221F1D]">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`hover:text-[#A8472A] transition-colors pb-1 border-b-2 font-bold ${
                activeTab === item.id
                  ? 'border-[#A8472A] text-[#A8472A]'
                  : 'border-transparent text-[#221F1D]'
              }`}
            >
              {item.label}
            </button>
          ))}
        </nav>

        {/* Status & CTA */}
        <div className="flex items-center gap-3">
          <div 
            title={backendStatus === 'ok' ? 'FastAPI Backend Online' : 'Backend Disconnected (Ensure server is running on :8000)'}
            className={`hidden sm:inline-flex items-center gap-1.5 text-[11px] font-bold px-2.5 py-1 rounded-full border ${
              backendStatus === 'ok'
                ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                : backendStatus === 'checking'
                ? 'bg-amber-50 text-amber-800 border-amber-200'
                : 'bg-rose-50 text-rose-800 border-rose-200'
            }`}
          >
            <span className={`w-2 h-2 rounded-full ${
              backendStatus === 'ok' ? 'bg-emerald-500 animate-pulse' : backendStatus === 'checking' ? 'bg-amber-500' : 'bg-rose-500'
            }`} />
            {backendStatus === 'ok' ? 'API Active' : backendStatus === 'checking' ? 'Connecting...' : 'API Offline'}
          </div>

          <button
            onClick={() => setActiveTab('workspace')}
            className="bg-[#A8472A] hover:bg-[#933B20] text-[#F8F6F0] text-xs font-semibold uppercase tracking-wider px-5 py-2 rounded-full transition-all duration-200 shadow-sm active:scale-95"
          >
            Scan Label
          </button>
        </div>
      </div>

      {/* Mobile Nav Bar */}
      <div className="lg:hidden flex overflow-x-auto border-t border-[#E8E4DC] px-4 py-2 gap-4 text-xs font-semibold uppercase tracking-wider no-scrollbar">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`whitespace-nowrap pb-1 ${
              activeTab === item.id ? 'text-[#A8472A] font-bold border-b-2 border-[#A8472A]' : 'text-[#67625B]'
            }`}
          >
            {item.label}
          </button>
        ))}
      </div>
    </header>
  );
}
