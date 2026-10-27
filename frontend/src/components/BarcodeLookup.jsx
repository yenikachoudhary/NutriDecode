import React, { useState } from 'react';
import { 
  Barcode, 
  Search, 
  AlertTriangle, 
  CheckCircle2, 
  ExternalLink, 
  RefreshCw, 
  Camera, 
  ArrowRight, 
  ShieldCheck, 
  Package,
  Layers,
  Sparkles
} from 'lucide-react';
import { api } from '../services/api';

export default function BarcodeLookup({ onAnalyzeIngredients, initialSearchQuery = '' }) {
  const [searchMode, setSearchMode] = useState(initialSearchQuery ? 'candidate' : 'barcode'); // 'barcode' or 'candidate'
  const [barcode, setBarcode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  // Unknown Product Discovery State
  const [candidateQuery, setCandidateQuery] = useState(initialSearchQuery);
  const [candidateLoading, setCandidateLoading] = useState(false);
  const [candidateError, setCandidateError] = useState(null);
  const [candidateData, setCandidateData] = useState(null);

  const sampleBarcodes = [
    { code: '3017620422003', name: 'Nutella Ferrero (Live OFF Match)' },
    { code: '8901058852270', name: 'Maggi 2-Min Noodles' },
    { code: '8901030937667', name: 'Britannia Good Day' },
    { code: '8901030018045', name: 'Parle-G Glucose' },
    { code: '8901491101836', name: 'Real Fruit Power' },
  ];

  const sampleKeywords = [
    'Parle-G',
    'Maggi Masala',
    'Britannia Bourbon',
    'Haldiram Bhujia',
    'Real Mixed Fruit',
  ];

  const handleLookup = async (codeToSearch = barcode) => {
    const cleaned = String(codeToSearch).trim();
    if (!cleaned) {
      setError('Please enter a barcode number.');
      return;
    }

    if (!/^\d{8,14}$/.test(cleaned)) {
      setError('Barcode must contain between 8 and 14 digits.');
      return;
    }

    setBarcode(cleaned);
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await api.lookupBarcode(cleaned);
      if (!data.found) {
        setError(data.message || 'Product not found in Open Food Facts or UPCitemdb.');
      } else {
        setResult(data);
      }
    } catch (err) {
      setError(err.message || 'Failed to query barcode database.');
    } finally {
      setLoading(false);
    }
  };

  const handleCandidateSearch = async (queryToSearch = candidateQuery) => {
    const cleaned = String(queryToSearch).trim();
    if (!cleaned) {
      setCandidateError('Please enter a product title or keyword to search.');
      return;
    }

    setCandidateQuery(cleaned);
    setCandidateLoading(true);
    setCandidateError(null);

    try {
      const data = await api.searchProducts(cleaned, 6);
      setCandidateData(data);
    } catch (err) {
      setCandidateError(err.message || 'Candidate product search failed.');
    } finally {
      setCandidateLoading(false);
    }
  };

  // If initialSearchQuery was passed, trigger search on mount
  React.useEffect(() => {
    if (initialSearchQuery) {
      setCandidateQuery(initialSearchQuery);
      setSearchMode('candidate');
      handleCandidateSearch(initialSearchQuery);
    }
  }, [initialSearchQuery]);

  return (
    <div className="max-w-6xl mx-auto px-6 py-10 space-y-10">
      {/* Header */}
      <div>
        <span className="text-xs font-bold uppercase tracking-widest text-[#A8472A]">
          Direct Barcode & Registry Intelligence
        </span>
        <h2 className="font-serif-heading text-3xl sm:text-4xl font-semibold text-[#221F1D] mt-1 uppercase">
          Packaged Product Barcode & Discovery
        </h2>
        <p className="text-xs sm:text-sm text-[#67625B] mt-2 max-w-2xl leading-relaxed">
          Lookup products by exact barcode or discover candidate matches across public food registries when barcodes are uncatalogued or damaged.
        </p>
      </div>

      {/* MODE TABS: BARCODE vs CANDIDATE DISCOVERY */}
      <div className="flex gap-2 border-b border-[#E8E4DC] pb-3 text-xs font-semibold uppercase tracking-wider">
        <button
          type="button"
          onClick={() => { setSearchMode('barcode'); setError(null); }}
          className={`px-4 py-2 rounded-lg transition-all flex items-center gap-2 ${
            searchMode === 'barcode'
              ? 'bg-[#3D4F40] text-white shadow-sm'
              : 'bg-[#EFECE5] text-[#221F1D] hover:bg-[#E8E4DC]'
          }`}
        >
          <Barcode className="w-4 h-4" />
          Lookup by Exact Barcode
        </button>

        <button
          type="button"
          onClick={() => { setSearchMode('candidate'); setError(null); }}
          className={`px-4 py-2 rounded-lg transition-all flex items-center gap-2 ${
            searchMode === 'candidate'
              ? 'bg-[#A8472A] text-white shadow-sm'
              : 'bg-[#EFECE5] text-[#221F1D] hover:bg-[#E8E4DC]'
          }`}
        >
          <Sparkles className="w-4 h-4" />
          Unknown-Product Discovery
        </button>
      </div>

      {/* SEARCH MODE 1: EXACT BARCODE */}
      {searchMode === 'barcode' && (
        <div className="bg-white rounded-2xl border border-[#E2E6DF] p-6 shadow-sm space-y-5">
          <form 
            onSubmit={(e) => { e.preventDefault(); handleLookup(); }}
            className="flex flex-col sm:flex-row gap-3"
          >
            <div className="relative flex-1">
              <Barcode className="w-5 h-5 text-[#67625B] absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={barcode}
                onChange={(e) => setBarcode(e.target.value)}
                placeholder="Enter 8 to 14 digit barcode (e.g. 8901058852270)..."
                className="w-full pl-11 pr-4 py-3 bg-[#F8F6F0] rounded-xl border border-[#E2E6DF] focus:border-[#A8472A] focus:outline-none text-xs font-mono"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="bg-[#A8472A] hover:bg-[#933B20] text-white text-xs font-bold uppercase tracking-wider px-7 py-3 rounded-xl transition-all shadow-sm flex items-center justify-center gap-2 disabled:bg-neutral-300"
            >
              {loading ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Search className="w-4 h-4" />
              )}
              Lookup Barcode
            </button>
          </form>

          {/* Quick Sample Chips */}
          <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-[#E8E4DC]">
            <span className="text-[11px] uppercase font-bold tracking-wider text-[#67625B]">
              Sample Indian Barcodes:
            </span>
            {sampleBarcodes.map((item) => (
              <button
                key={item.code}
                type="button"
                onClick={() => handleLookup(item.code)}
                className="text-xs px-2.5 py-1 bg-[#EFECE5] hover:bg-[#E8E4DC] text-[#221F1D] rounded-lg border border-[#E2E6DF] transition-colors"
              >
                {item.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* SEARCH MODE 2: CANDIDATE DISCOVERY SEARCH */}
      {searchMode === 'candidate' && (
        <div className="bg-white rounded-2xl border border-[#E2E6DF] p-6 shadow-sm space-y-5">
          <form 
            onSubmit={(e) => { e.preventDefault(); handleCandidateSearch(); }}
            className="flex flex-col sm:flex-row gap-3"
          >
            <div className="relative flex-1">
              <Search className="w-5 h-5 text-[#67625B] absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={candidateQuery}
                onChange={(e) => setCandidateQuery(e.target.value)}
                placeholder="Search candidate product name or brand (e.g. Parle-G, Maggi, Britannia)..."
                className="w-full pl-11 pr-4 py-3 bg-[#F8F6F0] rounded-xl border border-[#E2E6DF] focus:border-[#A8472A] focus:outline-none text-xs"
              />
            </div>

            <button
              type="submit"
              disabled={candidateLoading}
              className="bg-[#3D4F40] hover:bg-[#2C3A2F] text-white text-xs font-bold uppercase tracking-wider px-7 py-3 rounded-xl transition-all shadow-sm flex items-center justify-center gap-2 disabled:bg-neutral-300"
            >
              {candidateLoading ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Sparkles className="w-4 h-4" />
              )}
              Discover Candidates
            </button>
          </form>

          {/* Quick Keywords Chips */}
          <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-[#E8E4DC]">
            <span className="text-[11px] uppercase font-bold tracking-wider text-[#67625B]">
              Popular Indian Food Searches:
            </span>
            {sampleKeywords.map((kw) => (
              <button
                key={kw}
                type="button"
                onClick={() => handleCandidateSearch(kw)}
                className="text-xs px-2.5 py-1 bg-[#EFECE5] hover:bg-[#E8E4DC] text-[#221F1D] rounded-lg border border-[#E2E6DF] transition-colors"
              >
                {kw}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* ERROR FEEDBACK / DISCOVERY HANDOFF */}
      {error && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-5 space-y-3 text-amber-900 text-xs">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div className="space-y-1">
              <div className="font-bold uppercase tracking-wider">Barcode Not Found in Official Registry</div>
              <p>{error}</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 pt-2 border-t border-amber-200/60">
            <button
              type="button"
              onClick={() => {
                setSearchMode('candidate');
                setCandidateQuery('');
              }}
              className="bg-[#3D4F40] text-white font-bold px-4 py-2 rounded-full uppercase tracking-wider text-[11px] inline-flex items-center gap-1.5 shadow-sm"
            >
              <Search className="w-3.5 h-3.5" />
              Search Registry Candidates by Product Name &rarr;
            </button>

            <button
              type="button"
              onClick={() => onAnalyzeIngredients?.('', 'Custom Product')}
              className="bg-[#A8472A] text-white font-bold px-4 py-2 rounded-full uppercase tracking-wider text-[11px] inline-flex items-center gap-1.5 shadow-sm"
            >
              <Camera className="w-3.5 h-3.5" />
              Upload Package Photo Instead &rarr;
            </button>
          </div>
        </div>
      )}

      {/* CANDIDATE DISCOVERY RESULTS */}
      {candidateData && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-[#E8E4DC]">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-widest text-[#A8472A]">
                Public Registry Search Results
              </span>
              <h3 className="font-serif-heading text-xl font-bold text-[#221F1D]">
                Found {candidateData.candidates_found} Candidate Product(s) for "{candidateData.query}"
              </h3>
            </div>
            <span className="text-[11px] text-[#67625B]">
              All candidates are unverified; verify against physical packaging.
            </span>
          </div>

          {/* Conflict warnings */}
          {candidateData.conflicts_detected?.length > 0 && (
            <div className="p-4 bg-amber-50 rounded-xl border border-amber-200 text-xs text-amber-900 space-y-1">
              <div className="font-bold uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4 text-amber-700" />
                Variant Formulation Discrepancies Detected:
              </div>
              <ul className="list-disc list-inside space-y-0.5 text-[11px]">
                {candidateData.conflicts_detected.map((conf, idx) => (
                  <li key={idx}>{conf}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Candidate Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {candidateData.candidates?.map((candidate, idx) => (
              <div
                key={idx}
                className="bg-white rounded-xl border border-[#E2E6DF] p-5 shadow-sm flex flex-col justify-between space-y-4 hover:border-[#A8472A]/50 transition-all"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex gap-3">
                      {candidate.image_url ? (
                        <img
                          src={candidate.image_url}
                          alt={candidate.name}
                          className="w-16 h-16 object-contain rounded-lg border border-[#E2E6DF] bg-[#F8F6F0] p-1 flex-shrink-0"
                        />
                      ) : (
                        <div className="w-16 h-16 rounded-lg bg-[#EFECE5] flex items-center justify-center text-[#CBD3C6] flex-shrink-0 border border-[#E2E6DF]">
                          <Package className="w-8 h-8" />
                        </div>
                      )}
                      <div>
                        <div className="text-[10px] uppercase font-bold tracking-wider text-[#A8472A]">
                          Barcode: {candidate.barcode}
                        </div>
                        <h4 className="font-serif-heading text-base font-bold text-[#221F1D]">
                          {candidate.name}
                        </h4>
                        <div className="text-xs text-[#67625B]">
                          Brand: <strong>{candidate.brands}</strong>
                          {candidate.quantity && ` • ${candidate.quantity}`}
                        </div>
                      </div>
                    </div>

                    <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-neutral-100 text-neutral-700 border border-neutral-300 whitespace-nowrap">
                      Unverified Candidate
                    </span>
                  </div>

                  {/* Completeness Bar */}
                  <div className="space-y-1">
                    <div className="flex justify-between text-[10px] text-[#67625B]">
                      <span>Data Completeness:</span>
                      <strong className="text-[#3D4F40]">{candidate.data_completeness_percent}%</strong>
                    </div>
                    <div className="w-full h-1.5 bg-[#EFECE5] rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          candidate.data_completeness_percent >= 75
                            ? 'bg-emerald-500'
                            : candidate.data_completeness_percent >= 40
                            ? 'bg-amber-500'
                            : 'bg-rose-400'
                        }`}
                        style={{ width: `${candidate.data_completeness_percent}%` }}
                      />
                    </div>
                  </div>

                  {/* Ingredients Snippet */}
                  <div className="p-3 bg-[#F8F6F0] rounded-lg border border-[#E8E4DC] text-xs font-mono text-[#50544E] line-clamp-3">
                    {candidate.ingredients_snippet}
                  </div>

                  <div className="text-[10px] text-[#67625B] italic">
                    {candidate.action_prompt}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex flex-wrap gap-2 pt-3 border-t border-[#E8E4DC]">
                  <button
                    type="button"
                    onClick={() => onAnalyzeIngredients?.(candidate.ingredients_snippet, candidate.name)}
                    className="flex-1 bg-[#3D4F40] hover:bg-[#2C3A2F] text-white text-xs font-bold uppercase tracking-wider py-2 px-3 rounded-lg transition-colors flex items-center justify-center gap-1.5 shadow-sm"
                  >
                    <ArrowRight className="w-3.5 h-3.5" />
                    Decode in Label Scanner
                  </button>

                  <button
                    type="button"
                    onClick={() => handleLookup(candidate.barcode)}
                    className="bg-[#EFECE5] hover:bg-[#E8E4DC] text-[#221F1D] text-xs font-bold uppercase tracking-wider py-2 px-3 rounded-lg border border-[#CBD3C6] transition-colors"
                  >
                    Full Profile
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* LOADING */}
      {loading && (
        <div className="bg-[#EFECE5] rounded-2xl p-8 border border-[#E2E6DF] text-center space-y-3">
          <div className="w-10 h-10 rounded-full border-4 border-[#CBD3C6] border-t-[#A8472A] animate-spin mx-auto" />
          <div className="font-bold text-sm text-[#221F1D]">Querying Open Food Facts & UPCitemdb...</div>
          <p className="text-xs text-[#67625B]">Fetching product registry record, ingredients, and nutrition facts.</p>
        </div>
      )}

      {/* SUCCESS RESULT CARD */}
      {result && result.found && (
        <div className="bg-white rounded-2xl border border-[#E2E6DF] p-6 sm:p-8 shadow-sm space-y-8">
          
          {/* Product Header */}
          <div className="flex flex-col md:flex-row items-start justify-between gap-6 pb-6 border-b border-[#E8E4DC]">
            <div className="flex gap-5 items-start">
              {result.product?.front_image_url ? (
                <img
                  src={result.product.front_image_url}
                  alt={result.product.name || 'Product'}
                  className="w-24 h-24 sm:w-28 sm:h-28 object-contain rounded-xl border border-[#E2E6DF] bg-[#F8F6F0] p-1 flex-shrink-0"
                />
              ) : (
                <div className="w-24 h-24 sm:w-28 sm:h-28 rounded-xl bg-[#EFECE5] flex items-center justify-center text-[#67625B] flex-shrink-0 border border-[#E2E6DF]">
                  <Package className="w-10 h-10 text-[#CBD3C6]" />
                </div>
              )}

              <div className="space-y-1">
                <span className="text-[10px] uppercase font-bold tracking-wider text-[#A8472A] bg-[#A8472A]/10 px-2.5 py-0.5 rounded">
                  Barcode {result.barcode}
                </span>
                <h3 className="font-serif-heading text-2xl font-bold text-[#221F1D] pt-1">
                  {result.product?.name || 'Unnamed Product'}
                </h3>
                <p className="text-xs text-[#67625B]">
                  Brand: <strong className="text-[#221F1D]">{result.product?.brands || 'Unknown'}</strong>
                  {result.product?.quantity && ` • Quantity: ${result.product.quantity}`}
                  {result.product?.countries && ` • Regions: ${result.product.countries}`}
                </p>
                <div className="text-[11px] text-[#3D4F40] font-medium pt-1">
                  Source: <a href={result.data_source_url} target="_blank" rel="noreferrer" className="underline font-bold inline-flex items-center gap-0.5">{result.data_source} <ExternalLink className="w-3 h-3" /></a>
                  {result.from_cache && <span className="ml-2 text-neutral-500 font-normal">(Cached)</span>}
                </div>
              </div>
            </div>

            {/* Score pill */}
            {result.product?.nutrition_grade && (
              <div className="bg-[#EFECE5] rounded-xl p-3 border border-[#E2E6DF] text-center min-w-[120px]">
                <div className="text-[10px] uppercase font-bold tracking-wider text-[#67625B]">Nutri-Score</div>
                <div className="font-serif-heading text-2xl font-bold text-[#A8472A] uppercase">
                  Grade {result.product.nutrition_grade}
                </div>
              </div>
            )}
          </div>

          {/* INCOMPLETE DATA WARNING BANNER */}
          {(!result.data_quality?.ingredients_available || !result.data_quality?.nutrition_available) && (
            <div className="bg-amber-50 rounded-xl p-4 border border-amber-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs text-amber-900">
              <div className="flex items-start gap-2.5">
                <AlertTriangle className="w-4 h-4 text-amber-700 flex-shrink-0 mt-0.5" />
                <div>
                  <strong className="uppercase tracking-wider">Incomplete Database Profile:</strong>{' '}
                  {result.data_quality?.warning}
                </div>
              </div>
              <button
                onClick={() => onAnalyzeIngredients?.(result.product?.ingredients_text || '', result.product?.name || 'Product')}
                className="bg-[#A8472A] hover:bg-[#933B20] text-white font-bold px-4 py-2 rounded-full uppercase tracking-wider text-[11px] whitespace-nowrap shadow-sm"
              >
                Scan Label Photo &rarr;
              </button>
            </div>
          )}

          {/* INGREDIENTS SECTION */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="font-bold text-xs uppercase tracking-wider text-[#3D4F40]">
                Declared Ingredients List
              </h4>
              {result.product?.ingredients_text && onAnalyzeIngredients && (
                <button
                  onClick={() => onAnalyzeIngredients(result.product.ingredients_text, result.product.name)}
                  className="text-xs text-[#A8472A] font-bold hover:underline uppercase tracking-wider flex items-center gap-1"
                >
                  Analyze with NutriDecode Scanner <ArrowRight className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            <div className="p-4 bg-[#F8F6F0] rounded-xl border border-[#E8E4DC] text-xs font-mono leading-relaxed text-[#221F1D]">
              {result.product?.ingredients_text || result.product?.ingredients_text_en || (
                <span className="italic text-[#67625B]">
                  No ingredient text provided by {result.data_source}. Photograph the package back panel to decode ingredients.
                </span>
              )}
            </div>

            {result.product?.allergens && (
              <div className="text-xs text-rose-800 bg-rose-50 p-3 rounded-lg border border-rose-200">
                <strong>Declared Allergens:</strong> {result.product.allergens}
              </div>
            )}
          </div>

          {/* NUTRITION TABLE (IF AVAILABLE) */}
          {result.data_quality?.nutrition_available && (
            <div className="space-y-3">
              <h4 className="font-bold text-xs uppercase tracking-wider text-[#3D4F40]">
                Nutritional Values (Per 100g / 100ml)
              </h4>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                {Object.entries(result.product.nutrition_per_100g).map(([key, val]) => {
                  if (val === null) return null;
                  return (
                    <div key={key} className="bg-[#F8F6F0] p-3 rounded-xl border border-[#E8E4DC]">
                      <div className="text-[#67625B] capitalize text-[11px]">{key.replace(/_/g, ' ')}</div>
                      <div className="font-bold text-base text-[#221F1D] mt-0.5">
                        {val} {key.includes('kcal') ? 'kcal' : key.includes('mg') ? 'mg' : 'g'}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* CTA TO WORKSPACE */}
          <div className="p-5 bg-[#EFECE5] rounded-xl border border-[#E2E6DF] flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="text-xs text-[#50544E]">
              Want to cross-check regional Indian aliases, verify E-numbers, or test dietary exposure for this product?
            </div>
            <button
              onClick={() => onAnalyzeIngredients?.(result.product?.ingredients_text || '', result.product?.name || 'Product')}
              className="bg-[#3D4F40] hover:bg-[#2C3A2F] text-white text-xs font-bold uppercase tracking-wider px-6 py-2.5 rounded-full transition-colors whitespace-nowrap shadow-sm"
            >
              Open in Label Scanner
            </button>
          </div>

        </div>
      )}
    </div>
  );
}
