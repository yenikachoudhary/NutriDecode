import React from 'react';
import { 
  Users, 
  Cpu, 
  Leaf, 
  ArrowRight, 
  ShieldCheck, 
  CheckCircle2, 
  AlertTriangle, 
  Camera, 
  FileSearch,
  ExternalLink,
  BookOpen
} from 'lucide-react';
import { BrandLogo } from './Navbar';

export default function HomeTab({ setActiveTab, onSelectSample }) {
  const sampleScenarios = [
    {
      id: 'masala-crackers',
      title: 'Masala Crackers',
      brand: 'Prakriti Organics',
      summary: '62% Whole Wheat Flour, Acidity Regulator (INS 330), Flavor Enhancers (INS 627, 631), Emulsifier (INS 322).',
      sampleText: 'Ingredients: Whole Wheat Flour (62%), Refined Rice Bran Oil, Seasoning (Iodised Salt, Chilli Powder, Cumin, Dehydrated Onion & Garlic, Acidity Regulator (INS 330), Flavour Enhancer (INS 627, INS 631)), Raising Agents (INS 500(ii), INS 503(ii)), Emulsifier (INS 322 from Soy), Antioxidant (INS 307b). Contains Wheat (Gluten) and Soy.\nNutrition Information per 100g: Energy 462 kcal, Protein 8.4g, Carbohydrates 65.2g, Sugars 4.8g, Saturated Fat 3.1g, Salt 1.7g, Dietary Fibre 6.2g.',
    },
    {
      id: 'instant-noodles',
      title: 'Instant Masala Noodles',
      brand: 'QuickBite India',
      summary: 'Refined Wheat Flour (Maida), Palm Oil, INS 508, Flavor Enhancer (INS 635), Class IV Caramel (INS 150d).',
      sampleText: 'Noodle Cake: Refined Wheat Flour (Maida), Palm Oil, Iodised Salt, Wheat Gluten, Thickener (INS 508), Acidity Regulators (INS 501(i), INS 500(i)). Tastemaker: Hydrolysed Peanut Protein, Mixed Spices (20%), Sugar, Edible Starch, Flavour Enhancer (INS 635), Caramel (INS 150d), Palm Oil. Contains Wheat, Peanuts.\nNutrition Information per 100g: Energy 448 kcal, Protein 7.8g, Carbohydrates 64g, Sugars 2.5g, Saturated Fat 8.4g, Salt 2.95g.',
    },
    {
      id: 'mango-nectar',
      title: 'Alphonso Mango Nectar',
      brand: 'OrchardPure',
      summary: 'Alphonso Mango Pulp (25%), Sugar, Acidity Regulator (INS 330), Pectin (INS 440), Vitamin C (INS 300), Beta-Carotene (INS 160a).',
      sampleText: 'Ingredients: Water, Alphonso Mango Pulp (25%), Sugar, Acidity Regulator (INS 330), Stabilizer (INS 440), Vitamin C (INS 300), Permitted Natural Colour (INS 160a(ii)) and Nature Identical Flavouring Substances (Mango). No Preservatives Added.\nNutrition Information per 100ml: Energy 64 kcal, Protein 0.4g, Carbohydrates 15.6g, Sugars 14.8g, Saturated Fat 0.0g, Salt 0.03g.',
    },
  ];

  return (
    <div className="space-y-16 pb-12">
      {/* HERO SECTION */}
      <section className="max-w-6xl mx-auto px-6 pt-10 sm:pt-16">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          
          {/* Left Column: Vision & Action */}
          <div className="lg:col-span-7 flex flex-col justify-center">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#E2E6DF] rounded-full text-xs font-semibold tracking-wider text-[#3D4F40] uppercase w-fit mb-4">
              <span className="w-2 h-2 rounded-full bg-[#A8472A] animate-pulse"></span>
              Citizen Science Food Intelligence Platform
            </div>

            <h1 className="font-serif-heading text-4xl sm:text-5xl lg:text-[50px] leading-[1.12] font-semibold text-[#221F1D] tracking-tight uppercase">
              DECODE INGREDIENTS.<br />
              TRACE EVIDENCE.<br />
              PROTECT HEALTH.
            </h1>

            <p className="font-serif italic text-lg sm:text-xl text-[#67625B] mt-5 mb-6 leading-relaxed">
              Empowering consumers and student citizen scientists to cut through confusing INS codes, regional Indian names, and ultra-processed food claims with verifiable scientific evidence.
            </p>

            <div className="flex flex-wrap items-center gap-4 pt-2">
              <button 
                onClick={() => setActiveTab('workspace')}
                className="bg-[#A8472A] hover:bg-[#933B20] text-[#F8F6F0] text-xs font-bold uppercase tracking-wider px-7 py-3.5 rounded-full transition-all duration-200 shadow-sm hover:shadow active:scale-95 flex items-center gap-2"
              >
                Launch Label Scanner <ArrowRight className="w-4 h-4" />
              </button>
              <button 
                onClick={() => setActiveTab('barcode')}
                className="border border-[#A8472A] text-[#A8472A] hover:bg-[#A8472A]/10 text-xs font-bold uppercase tracking-wider px-6 py-3.5 rounded-full transition-all duration-200"
              >
                Lookup Barcode
              </button>
              <button 
                onClick={() => setActiveTab('exposure')}
                className="border border-[#3D4F40] text-[#3D4F40] hover:bg-[#3D4F40]/10 text-xs font-bold uppercase tracking-wider px-5 py-3.5 rounded-full transition-all duration-200"
              >
                Exposure Calculator
              </button>
            </div>

            {/* Quick Metrics */}
            <div className="grid grid-cols-3 gap-6 pt-10 border-t border-[#E8E4DC] mt-10">
              <div>
                <div className="font-serif-heading text-2xl font-bold text-[#A8472A]">FSSAI & JECFA</div>
                <div className="text-xs uppercase tracking-wider text-[#67625B] mt-1">Direct Source Traced</div>
              </div>
              <div>
                <div className="font-serif-heading text-2xl font-bold text-[#3D4F40]">500+ Regional</div>
                <div className="text-xs uppercase tracking-wider text-[#67625B] mt-1">Indian Aliases Mapped</div>
              </div>
              <div>
                <div className="font-serif-heading text-2xl font-bold text-[#221F1D]">100% Transparent</div>
                <div className="text-xs uppercase tracking-wider text-[#67625B] mt-1">No Fake Safety Scores</div>
              </div>
            </div>
          </div>

          {/* Right Column: Hero Interactive Preview Card */}
          <div className="lg:col-span-5 relative">
            <div className="bg-[#EFECE5] rounded-2xl p-6 sm:p-7 border border-[#E2E6DF] shadow-md relative">
              <div className="flex items-center justify-between pb-4 border-b border-[#E2E6DF]">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-[#A8472A]"></span>
                  <span className="text-xs font-bold tracking-wider uppercase text-[#221F1D]">
                    Instant Label Test Drive
                  </span>
                </div>
                <span className="bg-[#3D4F40] text-white text-[10px] font-bold uppercase tracking-widest px-2.5 py-1 rounded-full">
                  Live OCR Ready
                </span>
              </div>

              <div className="mt-4 space-y-3">
                <p className="text-xs text-[#67625B]">
                  Select a pre-loaded packaged food sample from Indian supermarket shelves:
                </p>

                {sampleScenarios.map((item) => (
                  <div 
                    key={item.id}
                    className="p-3.5 bg-white rounded-xl border border-[#E2E6DF] hover:border-[#A8472A]/60 transition-all cursor-pointer group shadow-sm"
                    onClick={() => onSelectSample(item.sampleText, item.title)}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-serif-heading font-bold text-sm text-[#221F1D] group-hover:text-[#A8472A] transition-colors">
                          {item.title}
                        </h4>
                        <div className="text-[11px] text-[#A8472A] font-semibold">{item.brand}</div>
                      </div>
                      <span className="text-[10px] uppercase font-bold text-[#3D4F40] bg-[#E2E6DF] px-2 py-0.5 rounded">
                        Try Sample &rarr;
                      </span>
                    </div>
                    <p className="text-[11px] text-[#67625B] mt-2 line-clamp-2">
                      {item.summary}
                    </p>
                  </div>
                ))}
              </div>

              <div className="mt-4 pt-3 border-t border-[#E2E6DF] flex items-center justify-between text-[11px] text-[#67625B]">
                <span>Have a real photo?</span>
                <button 
                  onClick={() => setActiveTab('workspace')}
                  className="text-[#A8472A] font-bold hover:underline uppercase tracking-wider flex items-center gap-1"
                >
                  Upload your label <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* 5-STAGE METHODOLOGY PIPELINE */}
      <section className="w-full bg-[#E2E6DF] py-14 border-y border-[#CBD3C6]">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-10">
            <span className="text-xs uppercase tracking-widest font-bold text-[#3D4F40]">
              Transparent Pipeline
            </span>
            <h2 className="font-serif-heading text-3xl font-semibold text-[#221F1D] mt-1 tracking-wide uppercase">
              How Food-Label Intelligence Works
            </h2>
            <div className="w-12 h-0.5 bg-[#A8472A] mx-auto mt-3"></div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {[
              {
                step: '01',
                title: 'Capture & Preprocess',
                desc: 'Label photos are normalized via CLAHE adaptive contrast and noise filtration to sharpen micro-print text.',
              },
              {
                step: '02',
                title: 'Tesseract OCR',
                desc: 'Computer vision extracts character streams and segments ingredient clauses and nutritional tables.',
              },
              {
                step: '03',
                title: 'Indian Alias Resolution',
                desc: 'Regional names (haldi, maida, uppu, methi) map to canonical ingredients using a verified dictionary.',
              },
              {
                step: '04',
                title: 'Evidence Retrieval',
                desc: 'INS/E-numbers are cross-matched with authoritative WHO/FAO JECFA monographs and FSSAI standards.',
              },
              {
                step: '05',
                title: 'Exposure & Nutrition',
                desc: 'Calculates nutrient balance indicators and evaluates exposure against verified Acceptable Daily Intakes (ADI).',
              },
            ].map((st) => (
              <div key={st.step} className="bg-white rounded-xl p-5 border border-[#CBD3C6] shadow-sm flex flex-col justify-between">
                <div>
                  <span className="font-serif-heading text-xl font-bold text-[#A8472A]">{st.step}</span>
                  <h3 className="font-bold text-xs uppercase tracking-wider text-[#221F1D] mt-2 mb-2">{st.title}</h3>
                  <p className="text-[11px] text-[#50544E] leading-relaxed">{st.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CORE PHILOSOPHY / THE THREE DISTINCTIONS */}
      <section className="max-w-6xl mx-auto px-6 py-4">
        <div className="text-center mb-12">
          <span className="text-xs uppercase tracking-widest font-bold text-[#67625B]">
            Scientific Integrity
          </span>
          <h2 className="font-serif-heading text-3xl font-semibold text-[#221F1D] mt-1 tracking-wide uppercase">
            Why NutriDecode Refuses Fake Safety Scores
          </h2>
          <div className="w-12 h-0.5 bg-[#A8472A] mx-auto mt-3"></div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-[#EFECE5] rounded-xl p-6 border border-[#E2E6DF]">
            <div className="w-10 h-10 rounded-full bg-[#A8472A]/15 text-[#A8472A] flex items-center justify-center font-bold mb-4">
              1
            </div>
            <h3 className="font-bold text-sm uppercase tracking-wider text-[#221F1D] mb-2">
              Identification ≠ Toxicity
            </h3>
            <p className="text-xs text-[#50544E] leading-relaxed">
              Detecting an INS code (such as citric acid or baking soda) does not make a food dangerous. Additives serve technological purposes like preservation, acidity control, or leavening, evaluated rigorously by JECFA and permitted by FSSAI.
            </p>
          </div>

          <div className="bg-[#EFECE5] rounded-xl p-6 border border-[#E2E6DF]">
            <div className="w-10 h-10 rounded-full bg-[#3D4F40]/15 text-[#3D4F40] flex items-center justify-center font-bold mb-4">
              2
            </div>
            <h3 className="font-bold text-sm uppercase tracking-wider text-[#221F1D] mb-2">
              Hazard Under Lab Conditions ≠ Risk
            </h3>
            <p className="text-xs text-[#50544E] leading-relaxed">
              Substances that irritate when concentrated in industrial settings are harmless at parts-per-million levels in food. Real risk depends on <strong>concentration</strong> and <strong>quantity consumed per kg of body weight</strong>.
            </p>
          </div>

          <div className="bg-[#EFECE5] rounded-xl p-6 border border-[#E2E6DF]">
            <div className="w-10 h-10 rounded-full bg-[#F2B731]/30 text-[#9E6E00] flex items-center justify-center font-bold mb-4">
              3
            </div>
            <h3 className="font-bold text-sm uppercase tracking-wider text-[#221F1D] mb-2">
              Traceable Primary Sources Only
            </h3>
            <p className="text-xs text-[#50544E] leading-relaxed">
              We never link generic search engines or uncited blogs. Every claim is linked directly to authoritative public-health evaluations: WHO/FAO JECFA chemical monographs and official FSSAI regulatory schedules.
            </p>
          </div>
        </div>
      </section>

      {/* CALL TO ACTION BANNER */}
      <section className="max-w-6xl mx-auto px-6">
        <div className="bg-[#3D4F40] rounded-2xl p-8 sm:p-12 text-white flex flex-col md:flex-row items-center justify-between gap-8 shadow-md">
          <div className="max-w-xl">
            <span className="text-[11px] font-bold tracking-widest uppercase text-[#F2B731]">
              Ready to Inspect a Food Label?
            </span>
            <h3 className="font-serif-heading text-2xl sm:text-3xl font-semibold mt-2 leading-snug">
              Turn Grocery Confusions into Clear Scientific Facts.
            </h3>
            <p className="text-xs text-[#CBD3C6] mt-3 leading-relaxed">
              Upload a photograph of any Indian packaged food or enter its barcode to view ingredient breakdowns, regional aliases, and verified additive evidence.
            </p>
          </div>
          <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
            <button
              onClick={() => setActiveTab('workspace')}
              className="bg-[#A8472A] hover:bg-[#933B20] text-white text-xs font-bold uppercase tracking-wider px-7 py-3.5 rounded-full transition-colors whitespace-nowrap text-center shadow"
            >
              Start Analysis Now
            </button>
            <button
              onClick={() => setActiveTab('barcode')}
              className="border border-[#CBD3C6] hover:bg-white/10 text-white text-xs font-bold uppercase tracking-wider px-6 py-3.5 rounded-full transition-colors whitespace-nowrap text-center"
            >
              Scan Barcode
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
