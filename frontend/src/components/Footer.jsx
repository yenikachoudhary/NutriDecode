import React from 'react';
import { Leaf, ShieldCheck, ExternalLink } from 'lucide-react';

export default function Footer({ setActiveTab }) {
  return (
    <footer className="w-full bg-[#221F1D] text-[#CBD3C6] pt-12 pb-8 border-t border-black/20 mt-16">
      <div className="max-w-6xl mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 pb-10 border-b border-white/10 text-xs">
          {/* Column 1 */}
          <div className="space-y-3 md:col-span-1">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-[#F2B731]"></span>
              <span className="font-serif-heading font-bold text-base text-white tracking-wide">
                NUTRIDECODE AI
              </span>
            </div>
            <p className="text-[#A6AEA2] text-xs leading-relaxed">
              Open food-label intelligence and preliminary risk assessment platform for packaged foods in India.
            </p>
            <div className="text-[11px] text-[#869083]">
              Prototype Version 0.1.0 • Citizen Science Initiative
            </div>
          </div>

          {/* Column 2: Navigation */}
          <div>
            <h4 className="font-bold text-white uppercase tracking-wider mb-3 text-[11px]">Features</h4>
            <ul className="space-y-2 text-[#A6AEA2]">
              <li><button onClick={() => setActiveTab('workspace')} className="hover:text-white transition-colors">Food Label Scanner</button></li>
              <li><button onClick={() => setActiveTab('barcode')} className="hover:text-white transition-colors">Barcode Database Lookup</button></li>
              <li><button onClick={() => setActiveTab('exposure')} className="hover:text-white transition-colors">Dietary Exposure Calculator</button></li>
              <li><button onClick={() => setActiveTab('evidence')} className="hover:text-white transition-colors">Verified Additive Catalogue</button></li>
              <li><button onClick={() => setActiveTab('anveshana')} className="hover:text-white transition-colors">Anveshana 2026 Proposal</button></li>
            </ul>
          </div>

          {/* Column 3: Scientific References */}
          <div>
            <h4 className="font-bold text-white uppercase tracking-wider mb-3 text-[11px]">Primary Sources</h4>
            <ul className="space-y-2 text-[#A6AEA2]">
              <li>
                <a 
                  href="https://fssai.gov.in/" 
                  target="_blank" 
                  rel="noreferrer" 
                  className="hover:text-white inline-flex items-center gap-1 transition-colors"
                >
                  FSSAI India <ExternalLink className="w-3 h-3" />
                </a>
              </li>
              <li>
                <a 
                  href="https://apps.who.int/food-additives-contaminants-jecfa-database/" 
                  target="_blank" 
                  rel="noreferrer" 
                  className="hover:text-white inline-flex items-center gap-1 transition-colors"
                >
                  WHO/FAO JECFA Monographs <ExternalLink className="w-3 h-3" />
                </a>
              </li>
              <li>
                <a 
                  href="https://world.openfoodfacts.org/" 
                  target="_blank" 
                  rel="noreferrer" 
                  className="hover:text-white inline-flex items-center gap-1 transition-colors"
                >
                  Open Food Facts Database <ExternalLink className="w-3 h-3" />
                </a>
              </li>
            </ul>
          </div>

          {/* Column 4: Transparent Disclaimers */}
          <div>
            <h4 className="font-bold text-white uppercase tracking-wider mb-3 text-[11px]">Important Disclaimer</h4>
            <p className="text-[11px] text-[#A6AEA2] leading-relaxed">
              NutriDecode AI is an educational food-literacy and preliminary evidence-screening prototype. It is <strong>not</strong> a medically validated toxicity detector or safety guarantee. Always inspect the physical package and consult healthcare professionals for medical or dietary needs.
            </p>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="pt-6 flex flex-col sm:flex-row items-center justify-between text-[11px] tracking-wider uppercase text-[#A6AEA2] gap-3">
          <div>
            People • Machines • The Planet
          </div>
          <div>
            © {new Date().getFullYear()} NutriDecode AI • Anveshana Science & Engineering Exhibition
          </div>
        </div>
      </div>
    </footer>
  );
}
