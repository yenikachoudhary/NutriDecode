import React, { useState, useEffect } from 'react';
import { 
  Calculator, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  Info, 
  RefreshCw, 
  ExternalLink 
} from 'lucide-react';
import { api } from '../services/api';

export default function ExposureCalculator({ initialAdditiveCode = null, initialAdi = null }) {
  const [additivesList, setAdditivesList] = useState([]);
  const [selectedAdditive, setSelectedAdditive] = useState(initialAdditiveCode || '');
  
  // Calculator Form State
  const [concentration, setConcentration] = useState('200'); // mg/kg food
  const [servingSize, setServingSize] = useState('50'); // grams
  const [bodyWeight, setBodyWeight] = useState('60'); // kg
  const [adi, setAdi] = useState(initialAdi ? String(initialAdi) : '5.0'); // mg/kg bw/day
  const [servingsPerDay, setServingsPerDay] = useState('1');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  // Load available reference ADIs on mount
  useEffect(() => {
    let isMounted = true;
    api.listReferenceAdis()
      .then(items => {
        if (isMounted) setAdditivesList(items);
      })
      .catch(() => {});
    return () => { isMounted = false; };
  }, []);

  // When user picks an additive from the dropdown
  const handleSelectAdditive = (code) => {
    setSelectedAdditive(code);
    const found = additivesList.find(a => a.code === code);
    if (found && found.adi_value_numeric !== null) {
      setAdi(String(found.adi_value_numeric));
    }
  };

  // Run calculation
  const handleCalculate = async (e) => {
    if (e) e.preventDefault();
    setError(null);

    const concNum = Number(concentration);
    const servingNum = Number(servingSize);
    const weightNum = Number(bodyWeight);
    const adiNum = Number(adi);
    const servingsNum = Number(servingsPerDay);

    if (isNaN(concNum) || concNum < 0) {
      setError('Concentration must be a valid non-negative number in mg/kg.');
      return;
    }
    if (isNaN(servingNum) || servingNum <= 0) {
      setError('Serving size must be greater than zero grams.');
      return;
    }
    if (isNaN(weightNum) || weightNum <= 0) {
      setError('Body weight must be greater than zero kg.');
      return;
    }
    if (isNaN(adiNum) || adiNum <= 0) {
      setError('ADI must be a valid positive reference value (mg/kg bw/day).');
      return;
    }

    setLoading(true);
    try {
      const data = await api.calculateExposure({
        concentration: concNum,
        servingSize: servingNum,
        bodyWeight: weightNum,
        adi: adiNum,
        servingsPerDay: servingsNum,
        additiveCode: selectedAdditive || undefined,
      });
      setResult(data);
    } catch (err) {
      setError(err.message || 'Exposure calculation failed.');
    } finally {
      setLoading(false);
    }
  };

  // Auto-calculate on initial load if params are present
  useEffect(() => {
    handleCalculate();
  }, [selectedAdditive]);

  return (
    <div className="max-w-6xl mx-auto px-6 py-10 space-y-10">
      {/* Header */}
      <div>
        <span className="text-xs font-bold uppercase tracking-widest text-[#A8472A]">
          Quantitative Risk Assessment
        </span>
        <h2 className="font-serif-heading text-3xl sm:text-4xl font-semibold text-[#221F1D] mt-1 uppercase">
          Dietary Exposure & ADI Simulator
        </h2>
        <p className="text-xs sm:text-sm text-[#67625B] mt-2 max-w-2xl leading-relaxed">
          Simulate consumer intake for a given food additive concentration, serving size, and consumer body weight. Compare estimated exposure against the authoritative WHO/FAO JECFA Acceptable Daily Intake (ADI).
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left: Input Form */}
        <div className="lg:col-span-6 bg-white rounded-2xl border border-[#E2E6DF] p-6 sm:p-7 shadow-sm space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-[#E8E4DC]">
            <h3 className="font-bold text-xs uppercase tracking-wider text-[#221F1D] flex items-center gap-2">
              <Calculator className="w-4 h-4 text-[#A8472A]" />
              Exposure Simulation Parameters
            </h3>
            <span className="text-[11px] text-[#67625B]">Metric units only</span>
          </div>

          <form onSubmit={handleCalculate} className="space-y-4">
            {/* Additive Preset Selector */}
            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="block text-xs font-bold uppercase tracking-wider text-[#3D4F40]">
                  Select Food Additive (Optional JECFA Preset):
                </label>
                {selectedAdditive && (
                  <a
                    href={`https://apps.who.int/food-additives-contaminants-jecfa-database/Home/Search?search=${selectedAdditive.replace(/[^0-9]/g, '')}`}
                    target="_blank"
                    rel="noreferrer"
                    className="text-[10px] text-[#A8472A] font-bold hover:underline inline-flex items-center gap-0.5"
                  >
                    Query JECFA Registry <ExternalLink className="w-2.5 h-2.5" />
                  </a>
                )}
              </div>
              <select
                value={selectedAdditive}
                onChange={(e) => handleSelectAdditive(e.target.value)}
                className="w-full text-xs p-3 bg-[#F8F6F0] rounded-xl border border-[#E2E6DF] focus:border-[#A8472A] focus:outline-none"
              >
                <option value="">-- Choose an additive or enter custom ADI --</option>
                {additivesList.map((a) => (
                  <option key={a.code} value={a.code}>
                    INS {a.code} — {a.name} {a.adi_value_numeric !== null ? `(ADI: ${a.adi_value_numeric} mg/kg)` : `(GMP / Not specified)`}
                  </option>
                ))}
              </select>

              {/* UNKNOWN / GMP DISCOVERY GUIDANCE */}
              {selectedAdditive && (() => {
                const found = additivesList.find(a => a.code === selectedAdditive);
                if (found && found.adi_value_numeric === null) {
                  return (
                    <div className="mt-2.5 p-3 bg-amber-50 rounded-xl border border-amber-200 text-xs text-amber-950 space-y-1">
                      <div className="font-bold uppercase tracking-wider text-[10px] flex items-center gap-1.5 text-amber-900">
                        <Info className="w-3.5 h-3.5 text-amber-700" />
                        JECFA Evaluation: Acceptable Daily Intake Not Specified (Safe at GMP)
                      </div>
                      <p className="text-[11px] leading-relaxed">
                        WHO/FAO JECFA evaluated <strong>{found.name} (INS {found.code})</strong> and determined that a numeric limitation is unnecessary when used under Good Manufacturing Practice. For mathematical simulation purposes, you may enter an experimental reference value or leave the default.
                      </p>
                      <div className="pt-1">
                        <a
                          href="https://fssai.gov.in/"
                          target="_blank"
                          rel="noreferrer"
                          className="text-[10px] text-amber-800 font-bold underline inline-flex items-center gap-1"
                        >
                          Check FSSAI Food Additives Appendix A Permitted Categories <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                      </div>
                    </div>
                  );
                }
                return null;
              })()}
            </div>

            {/* Concentration */}
            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-xs font-bold uppercase tracking-wider text-[#221F1D]">
                  Concentration in Food (mg/kg):
                </label>
                <span className="text-[11px] text-[#67625B]">1 mg/kg = 1 ppm</span>
              </div>
              <input
                type="number"
                step="any"
                min="0"
                value={concentration}
                onChange={(e) => setConcentration(e.target.value)}
                className="w-full text-xs font-mono p-3 bg-[#F8F6F0] rounded-xl border border-[#E2E6DF] focus:border-[#A8472A] focus:outline-none"
                placeholder="e.g. 200"
                required
              />
              <p className="text-[10px] text-[#67625B] mt-1">
                Note: Retail package labels do not disclose concentration. Use tested laboratory values or statutory maximum limits (e.g. 200 mg/kg for preservatives).
              </p>
            </div>

            {/* Serving Size & Servings per Day */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-[#221F1D] mb-1">
                  Serving Size (grams):
                </label>
                <input
                  type="number"
                  step="any"
                  min="1"
                  value={servingSize}
                  onChange={(e) => setServingSize(e.target.value)}
                  className="w-full text-xs font-mono p-3 bg-[#F8F6F0] rounded-xl border border-[#E2E6DF] focus:border-[#A8472A] focus:outline-none"
                  placeholder="e.g. 50"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-[#221F1D] mb-1">
                  Servings Per Day:
                </label>
                <input
                  type="number"
                  step="any"
                  min="0.1"
                  value={servingsPerDay}
                  onChange={(e) => setServingsPerDay(e.target.value)}
                  className="w-full text-xs font-mono p-3 bg-[#F8F6F0] rounded-xl border border-[#E2E6DF] focus:border-[#A8472A] focus:outline-none"
                  placeholder="e.g. 1"
                  required
                />
              </div>
            </div>

            {/* Body Weight with Presets */}
            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-xs font-bold uppercase tracking-wider text-[#221F1D]">
                  Consumer Body Weight (kg):
                </label>
                <div className="flex gap-1.5">
                  <button
                    type="button"
                    onClick={() => setBodyWeight('25')}
                    className="text-[10px] px-2 py-0.5 rounded bg-[#EFECE5] text-[#3D4F40] font-semibold hover:bg-[#E8E4DC]"
                  >
                    Child (25kg)
                  </button>
                  <button
                    type="button"
                    onClick={() => setBodyWeight('45')}
                    className="text-[10px] px-2 py-0.5 rounded bg-[#EFECE5] text-[#3D4F40] font-semibold hover:bg-[#E8E4DC]"
                  >
                    Teen (45kg)
                  </button>
                  <button
                    type="button"
                    onClick={() => setBodyWeight('60')}
                    className="text-[10px] px-2 py-0.5 rounded bg-[#EFECE5] text-[#3D4F40] font-semibold hover:bg-[#E8E4DC]"
                  >
                    Adult (60kg)
                  </button>
                </div>
              </div>
              <input
                type="number"
                step="any"
                min="1"
                value={bodyWeight}
                onChange={(e) => setBodyWeight(e.target.value)}
                className="w-full text-xs font-mono p-3 bg-[#F8F6F0] rounded-xl border border-[#E2E6DF] focus:border-[#A8472A] focus:outline-none"
                placeholder="e.g. 60"
                required
              />
            </div>

            {/* ADI Reference Value */}
            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-xs font-bold uppercase tracking-wider text-[#221F1D]">
                  Applicable ADI (mg/kg bw/day):
                </label>
                <span className="text-[10px] text-[#A8472A] font-semibold">JECFA Threshold</span>
              </div>
              <input
                type="number"
                step="any"
                min="0.001"
                value={adi}
                onChange={(e) => setAdi(e.target.value)}
                className="w-full text-xs font-mono p-3 bg-[#F8F6F0] rounded-xl border border-[#E2E6DF] focus:border-[#A8472A] focus:outline-none"
                placeholder="e.g. 5.0"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-[#A8472A] hover:bg-[#933B20] text-white text-xs font-bold uppercase tracking-wider py-3 rounded-full transition-all shadow-sm flex items-center justify-center gap-2"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Calculator className="w-4 h-4" />}
              Compute Dietary Exposure
            </button>
          </form>
        </div>

        {/* Right: Results Card */}
        <div className="lg:col-span-6 space-y-6">
          {error && (
            <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 text-xs text-rose-800 flex items-start gap-2.5">
              <AlertTriangle className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />
              <div>{error}</div>
            </div>
          )}

          {result && (
            <div className="bg-white rounded-2xl border border-[#E2E6DF] p-6 sm:p-7 shadow-sm space-y-6">
              <div className="flex items-center justify-between pb-4 border-b border-[#E8E4DC]">
                <div>
                  <span className="text-[10px] uppercase font-bold tracking-widest text-[#A8472A]">
                    Calculated Intake Results
                  </span>
                  <h4 className="font-serif-heading text-xl font-bold text-[#221F1D] mt-0.5">
                    {result.adi_percentage}% of ADI Reference
                  </h4>
                </div>

                <span className={`text-xs font-bold px-3 py-1 rounded-full border ${
                  result.adi_percentage <= 100
                    ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                    : 'bg-amber-50 text-amber-800 border-amber-200'
                }`}>
                  {result.adi_percentage <= 100 ? 'Within Reference ADI' : 'Exceeds Reference ADI'}
                </span>
              </div>

              {/* Progress Bar Gauge */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs text-[#67625B]">
                  <span>0%</span>
                  <span>50%</span>
                  <span className="font-bold text-[#A8472A]">100% ADI Threshold</span>
                  <span>150%+</span>
                </div>
                <div className="w-full h-3 bg-[#EFECE5] rounded-full overflow-hidden border border-[#E2E6DF]">
                  <div
                    className={`h-full transition-all duration-500 rounded-full ${
                      result.adi_percentage <= 75
                        ? 'bg-emerald-500'
                        : result.adi_percentage <= 100
                        ? 'bg-amber-500'
                        : 'bg-rose-500'
                    }`}
                    style={{ width: `${Math.min(100, (result.adi_percentage / 150) * 100)}%` }}
                  />
                </div>
              </div>

              {/* Output Metrics Grid */}
              <div className="grid grid-cols-2 gap-4 text-xs">
                <div className="bg-[#F8F6F0] p-3.5 rounded-xl border border-[#E8E4DC]">
                  <div className="text-[11px] text-[#67625B]">Estimated Intake Per Day:</div>
                  <div className="font-mono font-bold text-base text-[#221F1D] mt-1">
                    {result.estimated_intake_mg_per_day} mg
                  </div>
                  <div className="text-[10px] text-[#67625B] mt-0.5">Across {result.servings_per_day} serving(s)</div>
                </div>

                <div className="bg-[#F8F6F0] p-3.5 rounded-xl border border-[#E8E4DC]">
                  <div className="text-[11px] text-[#67625B]">Body-Weight Normalized Exposure:</div>
                  <div className="font-mono font-bold text-base text-[#A8472A] mt-1">
                    {result.estimated_exposure_mg_per_kg_body_weight_day} mg/kg/day
                  </div>
                  <div className="text-[10px] text-[#67625B] mt-0.5">Target ADI: {result.adi_mg_per_kg_body_weight_day} mg/kg</div>
                </div>
              </div>

              {/* Interpretation Paragraph */}
              <div className="p-4 bg-[#EFECE5] rounded-xl border border-[#E2E6DF] text-xs space-y-1 text-[#221F1D]">
                <strong className="uppercase text-[11px] tracking-wider text-[#3D4F40] block">
                  Scientific Interpretation:
                </strong>
                <p className="leading-relaxed">
                  {result.interpretation}
                </p>
              </div>

              {/* Scientific Limitations */}
              <div className="space-y-2 border-t border-[#E8E4DC] pt-4">
                <div className="font-bold text-xs uppercase tracking-wider text-[#67625B] flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-[#3D4F40]" />
                  Calculation Assumptions & Limitations:
                </div>
                <ul className="text-[11px] text-[#50544E] space-y-1 list-disc list-inside">
                  {result.limitations?.map((lim, idx) => (
                    <li key={idx}>{lim}</li>
                  ))}
                </ul>
              </div>

            </div>
          )}

          {/* Educational Note */}
          <div className="bg-[#F8F6F0] rounded-xl p-5 border border-[#E8E4DC] text-xs text-[#50544E] space-y-2">
            <h5 className="font-bold text-[#221F1D] uppercase tracking-wider text-[11px]">
              What is an Acceptable Daily Intake (ADI)?
            </h5>
            <p className="leading-relaxed">
              The ADI is established by the WHO/FAO Joint Expert Committee on Food Additives (JECFA). It represents an estimate of the amount of a food additive, expressed on a body weight basis, that can be ingested daily over a lifetime without appreciable health risk. A single day's intake slightly above an ADI does not produce acute toxicity.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
