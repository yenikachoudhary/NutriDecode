import React, { useState, useEffect } from 'react';
import { 
  Search, 
  ExternalLink, 
  ShieldCheck, 
  Filter, 
  RefreshCw, 
  BookOpen, 
  Calculator, 
  CheckCircle2,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { api } from '../services/api';

export default function EvidenceCatalogue({ onNavigateToExposure }) {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [expandedCode, setExpandedCode] = useState(null);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    api.listEvidence()
      .then(data => {
        if (isMounted) {
          setRecords(data.records || []);
          setError(null);
        }
      })
      .catch(err => {
        if (isMounted) setError(err.message || 'Could not load evidence records.');
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });
    return () => { isMounted = false; };
  }, []);

  const categories = ['All', 'Acidity regulator', 'Preservative', 'Colouring agent', 'Flavour enhancer', 'Emulsifier', 'Raising agent', 'Antioxidant', 'Anti-caking agent'];

  const filteredRecords = records.filter(item => {
    const matchesSearch = 
      item.name?.toLowerCase().includes(search.toLowerCase()) ||
      item.code?.toLowerCase().includes(search.toLowerCase()) ||
      item.purpose?.toLowerCase().includes(search.toLowerCase());

    const matchesCat = 
      categoryFilter === 'All' || 
      item.purpose?.toLowerCase().includes(categoryFilter.toLowerCase()) ||
      item.functional_classes?.some(fc => fc.toLowerCase().includes(categoryFilter.toLowerCase()));

    return matchesSearch && matchesCat;
  });

  return (
    <div className="max-w-6xl mx-auto px-6 py-10 space-y-10">
      {/* Header */}
      <div>
        <span className="text-xs font-bold uppercase tracking-widest text-[#A8472A]">
          Authoritative Reference Repository
        </span>
        <h2 className="font-serif-heading text-3xl sm:text-4xl font-semibold text-[#221F1D] mt-1 uppercase">
          WHO/FAO & FSSAI Additive Evidence Database
        </h2>
        <p className="text-xs sm:text-sm text-[#67625B] mt-2 max-w-2xl leading-relaxed">
          Explore source-linked evaluations for standard food additives permitted under Indian regulations and evaluated by the WHO/FAO Joint Expert Committee on Food Additives (JECFA).
        </p>
      </div>

      {/* SEARCH & FILTERS */}
      <div className="bg-white rounded-2xl border border-[#E2E6DF] p-6 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-[#67625B] absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search additive by code (e.g. 330, 150d) or name (citric acid, caramel)..."
              className="w-full pl-10 pr-4 py-2.5 bg-[#F8F6F0] rounded-xl border border-[#E2E6DF] focus:border-[#A8472A] focus:outline-none text-xs"
            />
          </div>

          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-[#67625B] hidden sm:block" />
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="text-xs py-2.5 px-3 bg-[#F8F6F0] rounded-xl border border-[#E2E6DF] focus:border-[#A8472A] focus:outline-none text-[#221F1D]"
            >
              {categories.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex justify-between items-center text-xs text-[#67625B] pt-2 border-t border-[#E8E4DC]">
          <span>Showing {filteredRecords.length} of {records.length} documented catalogue records</span>
          <span className="text-[11px] text-[#3D4F40] font-semibold">100% Traceable Direct URLs</span>
        </div>
      </div>

      {/* ERROR */}
      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800">
          {error}
        </div>
      )}

      {/* LOADING */}
      {loading && (
        <div className="p-12 text-center text-xs text-[#67625B]">
          <RefreshCw className="w-6 h-6 animate-spin mx-auto text-[#A8472A] mb-2" />
          Loading evidence records...
        </div>
      )}

      {/* RECORDS ACCORDION LIST */}
      {!loading && (
        <div className="space-y-4">
          {filteredRecords.map((item) => {
            const isExpanded = expandedCode === item.code;
            const adi = item.adi;
            const scientific = item.scientific_findings;
            const regulatory = item.regulatory_details;

            return (
              <div 
                key={item.code}
                className="bg-white rounded-2xl border border-[#E2E6DF] overflow-hidden shadow-sm transition-all"
              >
                {/* Accordion Row Header */}
                <div
                  onClick={() => setExpandedCode(isExpanded ? null : item.code)}
                  className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 cursor-pointer hover:bg-[#F8F6F0] transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className="font-mono font-bold text-xs bg-[#A8472A] text-white px-2.5 py-1 rounded-lg">
                      INS {item.code}
                    </span>
                    <div>
                      <h4 className="font-serif-heading text-lg font-bold text-[#221F1D]">
                        {item.name}
                      </h4>
                      <p className="text-xs text-[#67625B]">
                        Purpose: <strong className="text-[#3D4F40]">{item.purpose}</strong>
                        {item.e_number && ` • EU: ${item.e_number}`}
                        {item.chemical_identity?.cas_number && ` • CAS: ${item.chemical_identity.cas_number}`}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 self-end sm:self-auto">
                    <span className="text-[11px] font-semibold text-emerald-800 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200 whitespace-nowrap">
                      {adi?.status === 'numeric' ? `ADI: ${adi.value} mg/kg` : 'ADI: Safe at GMP'}
                    </span>
                    <button
                      type="button"
                      className="p-1 text-[#67625B] hover:text-[#221F1D]"
                    >
                      {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="p-6 bg-[#F8F6F0] border-t border-[#E8E4DC] space-y-6 text-xs">
                    
                    {/* Top Identity Grid */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                      <div className="bg-white p-3 rounded-xl border border-[#E2E6DF]">
                        <div className="text-[10px] uppercase font-bold text-[#67625B]">Formula</div>
                        <div className="font-mono font-bold text-[#221F1D] mt-0.5">{item.chemical_identity?.formula || 'N/A'}</div>
                      </div>
                      <div className="bg-white p-3 rounded-xl border border-[#E2E6DF]">
                        <div className="text-[10px] uppercase font-bold text-[#67625B]">CAS Registry</div>
                        <div className="font-mono font-bold text-[#221F1D] mt-0.5">{item.chemical_identity?.cas_number || 'N/A'}</div>
                      </div>
                      <div className="bg-white p-3 rounded-xl border border-[#E2E6DF]">
                        <div className="text-[10px] uppercase font-bold text-[#67625B]">Functional Classes</div>
                        <div className="font-semibold text-[#3D4F40] mt-0.5">
                          {item.functional_classes?.join(', ') || item.purpose}
                        </div>
                      </div>
                    </div>

                    {/* Scientific vs Regulatory Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* Left: Scientific Evaluation */}
                      <div className="bg-white p-5 rounded-xl border border-[#E2E6DF] space-y-3">
                        <div className="font-bold text-xs uppercase tracking-wider text-[#3D4F40] flex items-center gap-1.5 pb-2 border-b border-[#E8E4DC]">
                          <ShieldCheck className="w-4 h-4 text-[#3D4F40]" />
                          WHO/FAO JECFA Toxicological Evaluation
                        </div>

                        <div className="text-[#221F1D]">
                          <strong>Acceptable Daily Intake (ADI):</strong>{' '}
                          <span className="text-[#A8472A] font-semibold">{adi?.text}</span>
                        </div>

                        {scientific?.summary && (
                          <p className="text-[11px] text-[#50544E] leading-relaxed italic">
                            "{scientific.summary}"
                          </p>
                        )}

                        {scientific?.acute_effects && (
                          <div className="text-[11px] text-[#50544E]">
                            <strong>Acute Findings:</strong> {scientific.acute_effects}
                          </div>
                        )}

                        {scientific?.chronic_effects && (
                          <div className="text-[11px] text-[#50544E]">
                            <strong>Chronic Toxicity:</strong> {scientific.chronic_effects}
                          </div>
                        )}

                        {scientific?.sensitivities && (
                          <div className="text-[11px] text-[#67625B]">
                            <strong>Sensitivities / Allergen Notice:</strong> {scientific.sensitivities}
                          </div>
                        )}

                        {scientific?.jecfa_url && (
                          <div className="pt-2">
                            <a
                              href={scientific.jecfa_url}
                              target="_blank"
                              rel="noreferrer"
                              className="inline-flex items-center gap-1 text-[11px] text-[#A8472A] font-bold hover:underline"
                            >
                              Official JECFA Chemical Record <ExternalLink className="w-3 h-3" />
                            </a>
                          </div>
                        )}
                      </div>

                      {/* Right: Indian Regulatory Standard */}
                      <div className="bg-white p-5 rounded-xl border border-[#E2E6DF] space-y-3">
                        <div className="font-bold text-xs uppercase tracking-wider text-[#A8472A] flex items-center gap-1.5 pb-2 border-b border-[#E8E4DC]">
                          <BookOpen className="w-4 h-4 text-[#A8472A]" />
                          FSSAI Indian Regulatory Standard
                        </div>

                        <div className="text-[#221F1D]">
                          <strong>Standard Schedule:</strong>{' '}
                          <span className="text-emerald-700 font-semibold">{regulatory?.standard}</span>
                        </div>

                        {regulatory?.conditions && (
                          <p className="text-[11px] text-[#50544E] leading-relaxed">
                            <strong>Permitted Conditions:</strong> {regulatory.conditions}
                          </p>
                        )}

                        <div className="p-3 bg-[#F8F6F0] rounded-lg border border-[#E8E4DC] text-[11px] text-[#67625B]">
                          <strong>Citizen Guidance:</strong> Additives are permitted by FSSAI for specific technological functions. Permitted limits vary across food categories (e.g. confectionery vs edible oil).
                        </div>

                        {regulatory?.source_url && (
                          <div className="pt-2">
                            <a
                              href={regulatory.source_url}
                              target="_blank"
                              rel="noreferrer"
                              className="inline-flex items-center gap-1 text-[11px] text-[#3D4F40] font-bold hover:underline"
                            >
                              FSSAI Food Additives Schedule (PDF) <ExternalLink className="w-3 h-3" />
                            </a>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Bottom Action */}
                    {onNavigateToExposure && (
                      <div className="pt-2 flex justify-end">
                        <button
                          onClick={() => onNavigateToExposure(item.code, adi?.value || 30)}
                          className="bg-[#A8472A] hover:bg-[#933B20] text-white text-xs font-bold uppercase tracking-wider px-5 py-2.5 rounded-full transition-colors flex items-center gap-1.5 shadow-sm"
                        >
                          <Calculator className="w-4 h-4" />
                          Simulate Exposure for INS {item.code} &rarr;
                        </button>
                      </div>
                    )}

                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
