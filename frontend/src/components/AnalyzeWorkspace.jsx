import React, { useState, useRef } from 'react';
import { 
  Camera, 
  Upload, 
  FileText, 
  AlertTriangle, 
  CheckCircle2, 
  ExternalLink, 
  RefreshCw, 
  ShieldCheck, 
  Calculator, 
  Edit3, 
  Check, 
  Info,
  Sparkles,
  ArrowRight,
  Sliders,
  ChevronDown,
  ChevronUp,
  X,
  Search,
  HelpCircle
} from 'lucide-react';
import { api } from '../services/api';

export default function AnalyzeWorkspace({ 
  initialText = '', 
  initialTitle = '', 
  onNavigateToExposure,
  onNavigateToBarcodeSearch,
}) {
  const [file, setFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [rawText, setRawText] = useState(initialText);
  const [productTitle, setProductTitle] = useState(initialTitle);
  const [isEditingText, setIsEditingText] = useState(!file && Boolean(initialText));
  
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState('');
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [activeSubTab, setActiveSubTab] = useState('all'); // 'all', 'ai-summary', 'ingredients', 'additives', 'nutrition'

  // AI Summary & Personalization State
  const [aiSummary, setAiSummary] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState(null);
  const [showPreferences, setShowPreferences] = useState(false);
  const [staleAiNotice, setStaleAiNotice] = useState(false);

  // User Personalization Preferences
  const [detailLevel, setDetailLevel] = useState('standard'); // concise, standard, detailed
  const [readingLevel, setReadingLevel] = useState('standard'); // simple, standard, technical
  const [dietaryPreferences, setDietaryPreferences] = useState(['vegetarian']);
  const [allergensOrExclusions, setAllergensOrExclusions] = useState(['palm oil']);
  const [customExclusion, setCustomExclusion] = useState('');
  const [servingsPerDay, setServingsPerDay] = useState(1);
  const [bodyWeightKg, setBodyWeightKg] = useState(60);

  const fileInputRef = useRef(null);

  const toggleDietaryPreference = (pref) => {
    setDietaryPreferences(prev => 
      prev.includes(pref) ? prev.filter(p => p !== pref) : [...prev, pref]
    );
  };

  const addExclusion = (exc) => {
    const cleaned = exc.trim().toLowerCase();
    if (cleaned && !allergensOrExclusions.includes(cleaned)) {
      setAllergensOrExclusions(prev => [...prev, cleaned]);
    }
    setCustomExclusion('');
  };

  const removeExclusion = (exc) => {
    setAllergensOrExclusions(prev => prev.filter(e => e !== exc));
  };

  // Generate AI Summary
  const handleGenerateAiSummary = async () => {
    if (!result) return;
    setAiLoading(true);
    setAiError(null);
    setStaleAiNotice(false);

    const preferences = {
      detail_level: detailLevel,
      reading_level: readingLevel,
      dietary_preferences: dietaryPreferences,
      allergens_or_exclusions: allergensOrExclusions,
      servings_per_day: Number(servingsPerDay) || 1.0,
      body_weight_kg: Number(bodyWeightKg) || 60.0,
    };

    try {
      const data = await api.generateAiSummary(result, preferences);
      setAiSummary(data);
    } catch (err) {
      setAiError(err.message || 'Failed to generate AI summary.');
    } finally {
      setAiLoading(false);
    }
  };

  // Handle file selection
  const handleFileChange = (e) => {
    const selected = e.target.files?.[0];
    if (!selected) return;

    if (selected.size > 8 * 1024 * 1024) {
      setError('File exceeds 8 MB size limit. Please upload a smaller image.');
      return;
    }

    const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!validTypes.includes(selected.type)) {
      setError('Unsupported image format. Please select a JPEG, PNG, or WebP photo.');
      return;
    }

    setError(null);
    setFile(selected);
    setImagePreview(URL.createObjectURL(selected));
    setResult(null);
    setAiSummary(null);
    setStaleAiNotice(false);
  };

  // Drag and drop handlers
  const handleDrop = (e) => {
    e.preventDefault();
    const dropped = e.dataTransfer.files?.[0];
    if (dropped) {
      if (dropped.size > 8 * 1024 * 1024) {
        setError('File exceeds 8 MB size limit. Please upload a smaller image.');
        return;
      }
      setError(null);
      setFile(dropped);
      setImagePreview(URL.createObjectURL(dropped));
      setResult(null);
      setAiSummary(null);
      setStaleAiNotice(false);
    }
  };

  // Run full image analysis via API
  const handleAnalyzeImage = async () => {
    if (!file) {
      setError('Please choose or drag-and-drop a food-label photograph.');
      return;
    }

    setLoading(true);
    setError(null);
    setLoadingStep('Uploading food label and applying image pre-processing...');

    try {
      setTimeout(() => setLoadingStep('Extracting text via Tesseract OCR engine...'), 1500);
      setTimeout(() => setLoadingStep('Normalizing ingredients and querying Indian regional aliases...'), 3500);
      setTimeout(() => setLoadingStep('Cross-referencing WHO/FAO JECFA monographs and FSSAI standards...'), 5500);

      const data = await api.analyzeImage(file);
      setResult(data);
      setRawText(data.ocr?.extracted_text || '');
      setIsEditingText(false);
      if (aiSummary) setStaleAiNotice(true);
    } catch (err) {
      setError(err.message || 'Image analysis failed. Please try a clearer photograph with good lighting.');
    } finally {
      setLoading(false);
    }
  };

  // Run text re-analysis (when user corrects OCR text)
  const handleAnalyzeText = async () => {
    if (!rawText.trim()) {
      setError('Please enter or paste ingredient text to analyze.');
      return;
    }

    setLoading(true);
    setError(null);
    setLoadingStep('Analyzing corrected label text and matching additives...');

    try {
      const data = await api.analyzeText(rawText, productTitle || 'Custom Label');
      setResult(data);
      setIsEditingText(false);
      if (aiSummary) setStaleAiNotice(true);
    } catch (err) {
      setError(err.message || 'Text analysis failed.');
    } finally {
      setLoading(false);
    }
  };

  // Trigger analysis if initial text was passed in from sample selector
  React.useEffect(() => {
    if (initialText && !result && !loading) {
      setRawText(initialText);
      setProductTitle(initialTitle);
      handleAnalyzeText();
    }
  }, [initialText]);

  return (
    <div className="max-w-6xl mx-auto px-6 py-10 space-y-10">
      {/* HEADER */}
      <div>
        <span className="text-xs font-bold uppercase tracking-widest text-[#A8472A]">
          Interactive Analysis Workspace
        </span>
        <h2 className="font-serif-heading text-3xl sm:text-4xl font-semibold text-[#221F1D] mt-1 uppercase">
          Food Label Intelligence Scanner
        </h2>
        <p className="text-xs sm:text-sm text-[#67625B] mt-2 max-w-2xl leading-relaxed">
          Upload a high-resolution photograph of any packaged food label or paste ingredient text. NutriDecode extracts micro-print, resolves Indian regional aliases, identifies additive codes, and fetches authoritative scientific evidence.
        </p>
      </div>

      {/* INPUT STAGE: FILE DROPZONE & TEXT CONTROLS */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left: Upload Box */}
        <div className="lg:col-span-6 bg-white rounded-2xl border border-[#E2E6DF] p-6 shadow-sm space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-[#E8E4DC]">
            <h3 className="font-bold text-xs uppercase tracking-wider text-[#221F1D] flex items-center gap-2">
              <Camera className="w-4 h-4 text-[#A8472A]" />
              Upload Package Photograph
            </h3>
            <span className="text-[11px] text-[#67625B]">Max 8 MB • JPEG, PNG, WebP</span>
          </div>

          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all ${
              imagePreview ? 'border-[#3D4F40] bg-[#F8F6F0]' : 'border-[#CBD3C6] hover:border-[#A8472A] hover:bg-[#F8F6F0]'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={handleFileChange}
              className="hidden"
            />

            {imagePreview ? (
              <div className="space-y-3">
                <img
                  src={imagePreview}
                  alt="Label preview"
                  className="max-h-56 mx-auto rounded-lg object-contain shadow-sm border border-[#E2E6DF]"
                />
                <div className="text-xs font-semibold text-[#3D4F40]">
                  {file?.name} ({(file?.size / (1024 * 1024)).toFixed(2)} MB)
                </div>
                <div className="text-[11px] text-[#A8472A] underline">
                  Click or drag to choose another photo
                </div>
              </div>
            ) : (
              <div className="py-6 space-y-3">
                <div className="w-14 h-14 rounded-full bg-[#EFECE5] text-[#A8472A] mx-auto flex items-center justify-center">
                  <Upload className="w-7 h-7" />
                </div>
                <div className="font-bold text-sm text-[#221F1D]">
                  Drag & Drop Food Label Photo Here
                </div>
                <p className="text-xs text-[#67625B] max-w-xs mx-auto">
                  Ensure the ingredient clause and nutrition table are in sharp focus and well illuminated.
                </p>
                <button
                  type="button"
                  className="bg-[#EFECE5] hover:bg-[#E8E4DC] text-[#221F1D] text-xs font-bold uppercase tracking-wider px-4 py-2 rounded-lg border border-[#CBD3C6]"
                >
                  Browse Files
                </button>
              </div>
            )}
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleAnalyzeImage}
              disabled={!file || loading}
              className={`flex-1 text-xs font-bold uppercase tracking-wider py-3 rounded-full transition-all flex items-center justify-center gap-2 ${
                !file || loading
                  ? 'bg-neutral-300 text-neutral-500 cursor-not-allowed'
                  : 'bg-[#A8472A] hover:bg-[#933B20] text-white shadow-sm active:scale-95'
              }`}
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Running AI Pipeline...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Extract & Analyze Photo
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right: Manual / Editable OCR Text Box */}
        <div className="lg:col-span-6 bg-white rounded-2xl border border-[#E2E6DF] p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#E8E4DC]">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-[#3D4F40]" />
              <h3 className="font-bold text-xs uppercase tracking-wider text-[#221F1D]">
                Label Text Editor & OCR Inspection
              </h3>
            </div>
            <span className="text-[11px] text-[#67625B]">
              {rawText ? `${rawText.length} characters` : 'Direct text input'}
            </span>
          </div>

          <p className="text-xs text-[#67625B]">
            Review extracted OCR text below. You can correct misread letters, paste text from e-groceries, or re-run analysis:
          </p>

          <textarea
            rows={8}
            value={rawText}
            onChange={(e) => {
              setRawText(e.target.value);
              setIsEditingText(true);
            }}
            placeholder="e.g. INGREDIENTS: Whole Wheat Flour (62%), Refined Rice Bran Oil, Seasoning (Iodised Salt, Chilli Powder, Acidity Regulator (INS 330), Flavour Enhancer (INS 627, INS 631)), Raising Agents (INS 500(ii), INS 503(ii))..."
            className="w-full text-xs font-mono p-3.5 bg-[#F8F6F0] rounded-xl border border-[#E2E6DF] focus:border-[#A8472A] focus:outline-none leading-relaxed text-[#221F1D]"
          />

          <div className="flex items-center justify-between pt-1">
            <span className="text-[11px] text-[#67625B]">
              {isEditingText && <span className="text-[#A8472A] font-semibold">● Modified text ready to re-analyze</span>}
            </span>
            <button
              onClick={handleAnalyzeText}
              disabled={!rawText.trim() || loading}
              className={`text-xs font-bold uppercase tracking-wider px-5 py-2.5 rounded-full transition-all flex items-center gap-1.5 ${
                !rawText.trim() || loading
                  ? 'bg-neutral-200 text-neutral-400 cursor-not-allowed'
                  : 'bg-[#3D4F40] hover:bg-[#2C3A2F] text-white'
              }`}
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              Re-Analyze Text
            </button>
          </div>
        </div>
      </div>

      {/* ERROR FEEDBACK */}
      {error && (
        <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 flex items-start gap-3 text-rose-800 text-xs">
          <AlertTriangle className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" />
          <div className="space-y-1">
            <div className="font-bold uppercase tracking-wider">Analysis Issue</div>
            <div>{error}</div>
            <div className="text-[11px] text-rose-700 mt-1">
              Tip: Ensure the packaging is flat, well lit, and in focus. You can also paste the ingredient clause directly into the text editor.
            </div>
          </div>
        </div>
      )}

      {/* LOADING STATE CARD */}
      {loading && (
        <div className="bg-[#EFECE5] rounded-2xl p-8 border border-[#E2E6DF] text-center space-y-4">
          <div className="w-12 h-12 rounded-full border-4 border-[#CBD3C6] border-t-[#A8472A] animate-spin mx-auto" />
          <h4 className="font-serif-heading font-bold text-lg text-[#221F1D]">
            Processing Label Intelligence
          </h4>
          <p className="text-xs text-[#67625B] max-w-md mx-auto animate-pulse">
            {loadingStep}
          </p>
        </div>
      )}

      {/* ANALYSIS RESULTS SECTION */}
      {result && !loading && (
        <div className="space-y-8 pt-4">
          
          {/* Top Banner: Status & Overview */}
          <div className="bg-white rounded-2xl border border-[#E2E6DF] p-6 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <span className={`inline-flex items-center gap-1 text-xs font-bold px-3 py-1 rounded-full ${
                  result.analysis_status === 'completed'
                    ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                    : 'bg-amber-100 text-amber-900 border border-amber-200'
                }`}>
                  {result.analysis_status === 'completed' ? (
                    <><CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Pipeline Completed</>
                  ) : (
                    <><AlertTriangle className="w-3.5 h-3.5 text-amber-600" /> Citizen Review Recommended</>
                  )}
                </span>
                <span className="text-xs text-[#67625B]">Source: {result.filename}</span>
              </div>

              <h3 className="font-serif-heading text-2xl font-bold text-[#221F1D] mt-2">
                Identified {result.ingredients?.length || 0} Ingredients & {result.additives?.length || 0} Additives
              </h3>
            </div>

            {/* Quick Stats */}
            <div className="flex gap-4 border-t md:border-t-0 md:border-l border-[#E8E4DC] pt-3 md:pt-0 md:pl-6 text-xs">
              <div>
                <div className="font-bold text-base text-[#A8472A]">{result.additives?.length || 0}</div>
                <div className="text-[10px] uppercase tracking-wider text-[#67625B]">INS Additives</div>
              </div>
              <div>
                <div className="font-bold text-base text-[#3D4F40]">
                  {result.ingredients?.filter(i => i.name_resolution?.matched).length || 0}
                </div>
                <div className="text-[10px] uppercase tracking-wider text-[#67625B]">Indian Aliases</div>
              </div>
              <div>
                <div className="font-bold text-base text-[#221F1D]">
                  {result.nutrition?.detected ? 'Detected' : 'None'}
                </div>
                <div className="text-[10px] uppercase tracking-wider text-[#67625B]">Nutrition Table</div>
              </div>
            </div>
          </div>

          {/* AI ASSISTANT & PERSONALIZATION CONTROLS */}
          <div className="bg-gradient-to-r from-[#F8F6F0] via-white to-[#F8F6F0] rounded-2xl border border-[#CBD3C6] p-6 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-bold uppercase tracking-widest text-[#A8472A] bg-[#A8472A]/10 px-2.5 py-0.5 rounded-full flex items-center gap-1">
                    <Sparkles className="w-3 h-3 text-[#A8472A]" />
                    Evidence-Grounded AI Assistant
                  </span>
                  {aiSummary && (
                    <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-800 bg-emerald-100 px-2.5 py-0.5 rounded-full">
                      {aiSummary.ai_enabled ? `Provider: ${aiSummary.provider}` : 'Deterministic Grounded'}
                    </span>
                  )}
                </div>
                <h4 className="font-serif-heading text-lg font-bold text-[#221F1D]">
                  Personalized Product Intelligence & Safety Assessment
                </h4>
                <p className="text-xs text-[#67625B] max-w-xl">
                  Produces plain-language explanations strictly grounded in verified JECFA monographs and FSSAI standards. Zero invented ADIs or medical safety verdicts.
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-2.5 self-start sm:self-auto">
                <button
                  type="button"
                  onClick={() => setShowPreferences(!showPreferences)}
                  className={`text-xs font-bold uppercase tracking-wider px-3.5 py-2.5 rounded-xl border transition-all flex items-center gap-1.5 ${
                    showPreferences 
                      ? 'bg-[#3D4F40] text-white border-[#3D4F40]' 
                      : 'bg-white text-[#221F1D] border-[#CBD3C6] hover:bg-[#EFECE5]'
                  }`}
                >
                  <Sliders className="w-3.5 h-3.5 text-[#A8472A]" />
                  Personalize
                  {showPreferences ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                </button>

                <button
                  type="button"
                  onClick={handleGenerateAiSummary}
                  disabled={aiLoading}
                  className="bg-[#A8472A] hover:bg-[#933B20] text-white text-xs font-bold uppercase tracking-wider px-5 py-2.5 rounded-xl transition-all shadow-sm flex items-center gap-2 active:scale-95 disabled:bg-neutral-300"
                >
                  {aiLoading ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      Synthesizing Evidence...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-3.5 h-3.5" />
                      {aiSummary ? 'Regenerate AI Summary' : 'Generate AI Summary'}
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* STALE RE-ANALYSIS NOTICE */}
            {staleAiNotice && (
              <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-900 flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-700 flex-shrink-0" />
                  <span>Label text was edited or re-analyzed. The displayed summary may be out of date.</span>
                </div>
                <button
                  onClick={handleGenerateAiSummary}
                  className="text-[11px] font-bold text-[#A8472A] underline uppercase tracking-wider whitespace-nowrap"
                >
                  Regenerate Now
                </button>
              </div>
            )}

            {/* PERSONALIZATION PREFERENCES DRAWER */}
            {showPreferences && (
              <div className="pt-4 border-t border-[#E8E4DC] grid grid-cols-1 md:grid-cols-2 gap-5 text-xs bg-white p-5 rounded-xl border border-[#E2E6DF]">
                {/* Reading Level & Detail */}
                <div className="space-y-3">
                  <div>
                    <label className="block font-bold text-[11px] uppercase tracking-wider text-[#3D4F40] mb-1">
                      Reading Style:
                    </label>
                    <div className="grid grid-cols-3 gap-2">
                      {[
                        { id: 'simple', label: 'Simple' },
                        { id: 'standard', label: 'Standard' },
                        { id: 'technical', label: 'Technical' },
                      ].map(lvl => (
                        <button
                          key={lvl.id}
                          type="button"
                          onClick={() => setReadingLevel(lvl.id)}
                          className={`py-1.5 px-2 rounded-lg font-bold text-center border transition-all ${
                            readingLevel === lvl.id
                              ? 'bg-[#3D4F40] text-white border-[#3D4F40]'
                              : 'bg-[#F8F6F0] text-[#221F1D] border-[#E8E4DC] hover:bg-[#EFECE5]'
                          }`}
                        >
                          {lvl.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block font-bold text-[11px] uppercase tracking-wider text-[#3D4F40] mb-1">
                      Explanation Depth:
                    </label>
                    <div className="grid grid-cols-3 gap-2">
                      {[
                        { id: 'concise', label: 'Concise' },
                        { id: 'standard', label: 'Standard' },
                        { id: 'detailed', label: 'Detailed' },
                      ].map(d => (
                        <button
                          key={d.id}
                          type="button"
                          onClick={() => setDetailLevel(d.id)}
                          className={`py-1.5 px-2 rounded-lg font-bold text-center border transition-all ${
                            detailLevel === d.id
                              ? 'bg-[#A8472A] text-white border-[#A8472A]'
                              : 'bg-[#F8F6F0] text-[#221F1D] border-[#E8E4DC] hover:bg-[#EFECE5]'
                          }`}
                        >
                          {d.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Body weight and servings */}
                  <div className="grid grid-cols-2 gap-3 pt-1">
                    <div>
                      <label className="block font-bold text-[11px] uppercase tracking-wider text-[#221F1D] mb-1">
                        Body Weight (kg):
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="250"
                        value={bodyWeightKg}
                        onChange={(e) => setBodyWeightKg(e.target.value)}
                        className="w-full p-2 bg-[#F8F6F0] border border-[#E2E6DF] rounded-lg font-mono text-xs"
                      />
                    </div>
                    <div>
                      <label className="block font-bold text-[11px] uppercase tracking-wider text-[#221F1D] mb-1">
                        Servings / Day:
                      </label>
                      <input
                        type="number"
                        min="0.1"
                        step="0.5"
                        max="20"
                        value={servingsPerDay}
                        onChange={(e) => setServingsPerDay(e.target.value)}
                        className="w-full p-2 bg-[#F8F6F0] border border-[#E2E6DF] rounded-lg font-mono text-xs"
                      />
                    </div>
                  </div>
                </div>

                {/* Dietary Patterns & Exclusions */}
                <div className="space-y-3">
                  <div>
                    <label className="block font-bold text-[11px] uppercase tracking-wider text-[#3D4F40] mb-1.5">
                      Dietary Preferences:
                    </label>
                    <div className="flex flex-wrap gap-1.5">
                      {['vegetarian', 'vegan', 'gluten-free', 'low-sodium', 'halal', 'jain'].map(pref => {
                        const active = dietaryPreferences.includes(pref);
                        return (
                          <button
                            key={pref}
                            type="button"
                            onClick={() => toggleDietaryPreference(pref)}
                            className={`px-2.5 py-1 rounded-full text-xs font-semibold border transition-all capitalize ${
                              active 
                                ? 'bg-[#3D4F40] text-white border-[#3D4F40]' 
                                : 'bg-[#F8F6F0] text-[#67625B] border-[#E2E6DF] hover:bg-[#EFECE5]'
                            }`}
                          >
                            {active ? '✓ ' : '+ '}{pref}
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  <div>
                    <label className="block font-bold text-[11px] uppercase tracking-wider text-[#A8472A] mb-1.5">
                      Flag Excluded Ingredients or Allergens:
                    </label>
                    <div className="flex flex-wrap gap-1.5 mb-2">
                      {allergensOrExclusions.map(exc => (
                        <span 
                          key={exc} 
                          className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs bg-rose-100 text-rose-800 border border-rose-200 capitalize font-medium"
                        >
                          {exc}
                          <button 
                            type="button" 
                            onClick={() => removeExclusion(exc)}
                            className="hover:text-rose-950 font-bold"
                          >
                            ×
                          </button>
                        </span>
                      ))}
                    </div>

                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={customExclusion}
                        onChange={(e) => setCustomExclusion(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            addExclusion(customExclusion);
                          }
                        }}
                        placeholder="Add exclusion (e.g. MSG, peanuts, tartrazine)..."
                        className="flex-1 p-2 bg-[#F8F6F0] border border-[#E2E6DF] rounded-lg text-xs"
                      />
                      <button
                        type="button"
                        onClick={() => addExclusion(customExclusion)}
                        className="px-3 py-1.5 bg-[#EFECE5] hover:bg-[#E8E4DC] text-[#221F1D] font-bold rounded-lg border border-[#CBD3C6] text-xs"
                      >
                        Add
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* AI ERROR */}
            {aiError && (
              <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800 flex items-center justify-between">
                <span>{aiError}</span>
                <button onClick={handleGenerateAiSummary} className="font-bold underline text-[11px]">Retry</button>
              </div>
            )}
          </div>

          {/* Sub-Tabs Selector */}
          <div className="flex flex-wrap gap-2 border-b border-[#E8E4DC] pb-3 text-xs font-semibold uppercase tracking-wider">
            {[
              { id: 'all', label: 'All Findings' },
              { id: 'ai-summary', label: 'AI Evidence Summary' },
              { id: 'ingredients', label: `Ingredients (${result.ingredients?.length || 0})` },
              { id: 'additives', label: `Additives & Evidence (${result.additives?.length || 0})` },
              { id: 'nutrition', label: 'Nutrition & Score' },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveSubTab(tab.id)}
                className={`px-4 py-2 rounded-lg transition-colors flex items-center gap-1.5 ${
                  activeSubTab === tab.id
                    ? 'bg-[#3D4F40] text-white shadow-sm'
                    : 'bg-[#EFECE5] text-[#221F1D] hover:bg-[#E8E4DC]'
                }`}
              >
                {tab.id === 'ai-summary' && <Sparkles className="w-3.5 h-3.5 text-[#F2B731]" />}
                {tab.label}
              </button>
            ))}
          </div>

          {/* SECTION: AI EVIDENCE SUMMARY CARD */}
          {(activeSubTab === 'all' || activeSubTab === 'ai-summary') && aiSummary && aiSummary.summary && (
            <div className="bg-white rounded-2xl border-2 border-[#CBD3C6] p-6 sm:p-8 shadow-sm space-y-7">
              {/* Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-5 border-b border-[#E8E4DC]">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-xs uppercase tracking-widest text-[#A8472A] bg-[#A8472A]/10 px-2.5 py-0.5 rounded">
                      Structured AI Product Summary
                    </span>
                    <span className="text-xs text-[#67625B]">
                      Model: {aiSummary.model || 'Grounded Assistant'}
                    </span>
                  </div>
                  <h3 className="font-serif-heading text-2xl font-bold text-[#221F1D] mt-1">
                    Plain-Language Health & Food Safety Overview
                  </h3>
                </div>

                <div className="text-xs text-[#3D4F40] bg-[#F8F6F0] p-2 rounded-xl border border-[#E8E4DC] text-right">
                  <div>Reading: <strong className="capitalize">{readingLevel}</strong></div>
                  <div>Depth: <strong className="capitalize">{detailLevel}</strong></div>
                </div>
              </div>

              {/* THREE TIERS OF TRANSPARENCY NOTICE */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-200 space-y-1 text-emerald-900">
                  <div className="font-bold uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" />
                    Verified Evidence
                  </div>
                  <p className="text-[11px] leading-relaxed">
                    Food additive safety, ADIs, and functions originate directly from WHO/FAO JECFA monographs and FSSAI schedules.
                  </p>
                </div>

                <div className="p-3 bg-purple-50 rounded-xl border border-purple-200 space-y-1 text-purple-900">
                  <div className="font-bold uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-purple-700" />
                    AI Synthesis
                  </div>
                  <p className="text-[11px] leading-relaxed">
                    Plain-language explanations synthesized strictly from verified label clauses. Zero invented concentrations.
                  </p>
                </div>

                <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 space-y-1 text-amber-900">
                  <div className="font-bold uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-700" />
                    Label Limitations
                  </div>
                  <p className="text-[11px] leading-relaxed">
                    Manufacturers list ingredients by descending weight but do not declare quantitative additive ppm concentrations.
                  </p>
                </div>
              </div>

              {/* 1. PRODUCT OVERVIEW */}
              <div className="space-y-2">
                <h4 className="font-bold text-xs uppercase tracking-wider text-[#3D4F40]">
                  1. Executive Product Overview
                </h4>
                <div className="p-4 bg-[#F8F6F0] rounded-xl border border-[#E8E4DC] text-xs leading-relaxed text-[#221F1D]">
                  {aiSummary.summary.product_overview}
                </div>
              </div>

              {/* 2. DIETARY & ALLERGEN ALIGNMENT */}
              <div className="space-y-3">
                <h4 className="font-bold text-xs uppercase tracking-wider text-[#3D4F40]">
                  2. Personal Dietary & Allergen Exclusions Check
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {aiSummary.summary.allergen_and_dietary_alignment?.map((item, idx) => {
                    const isExclusion = item.status === 'contains_exclusion';
                    const isMatch = item.status === 'matches';
                    return (
                      <div 
                        key={idx}
                        className={`p-3.5 rounded-xl border text-xs space-y-1.5 ${
                          isExclusion 
                            ? 'bg-rose-50 border-rose-300 text-rose-950'
                            : isMatch 
                            ? 'bg-emerald-50/70 border-emerald-200 text-emerald-950'
                            : 'bg-amber-50/70 border-amber-200 text-amber-950'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-bold capitalize">{item.preference_or_allergen}</span>
                          <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full ${
                            isExclusion
                              ? 'bg-rose-200 text-rose-900'
                              : isMatch 
                              ? 'bg-emerald-200 text-emerald-900'
                              : 'bg-amber-200 text-amber-900'
                          }`}>
                            {item.status.replace(/_/g, ' ')}
                          </span>
                        </div>
                        <p className="text-[11px] leading-relaxed opacity-90">{item.explanation}</p>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* 3. NUTRITIONAL OBSERVATIONS */}
              <div className="space-y-2">
                <h4 className="font-bold text-xs uppercase tracking-wider text-[#3D4F40]">
                  3. Key Nutritional Observations
                </h4>
                <div className="p-4 bg-[#F8F6F0] rounded-xl border border-[#E8E4DC] text-xs space-y-2">
                  <ul className="list-disc list-inside space-y-1 text-[#221F1D]">
                    {aiSummary.summary.nutritional_observations?.map((obs, idx) => (
                      <li key={idx} className="leading-relaxed">{obs}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* 4. INGREDIENT & ADDITIVE EXPLANATIONS */}
              <div className="space-y-3">
                <h4 className="font-bold text-xs uppercase tracking-wider text-[#3D4F40]">
                  4. Explained Ingredients & Identified Additives
                </h4>
                <div className="space-y-3">
                  {aiSummary.summary.ingredient_and_additive_explanations?.map((item, idx) => (
                    <div key={idx} className="p-4 bg-[#F8F6F0] rounded-xl border border-[#E8E4DC] text-xs space-y-2">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                        <div className="font-bold text-sm text-[#221F1D]">{item.name}</div>
                        <span className="text-[10px] uppercase font-semibold text-[#A8472A] bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                          {item.purpose}
                        </span>
                      </div>
                      <p className="text-[11px] text-[#50544E] leading-relaxed">
                        {item.scientific_findings}
                      </p>
                      {item.source_url && (
                        <div className="pt-1">
                          <a 
                            href={item.source_url} 
                            target="_blank" 
                            rel="noreferrer"
                            className="text-[11px] text-[#A8472A] font-bold inline-flex items-center gap-1 hover:underline"
                          >
                            Source: {item.source_name} <ExternalLink className="w-3 h-3" />
                          </a>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* 5. HEALTH EFFECTS SUPPORTED BY EVIDENCE */}
              <div className="space-y-3">
                <h4 className="font-bold text-xs uppercase tracking-wider text-[#3D4F40]">
                  5. Evidence-Supported Health Observations
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                  <div className="p-4 bg-[#F8F6F0] rounded-xl border border-[#E8E4DC] space-y-1.5">
                    <strong className="text-[11px] uppercase tracking-wider text-[#221F1D] block">
                      Short-Term / Acute Effects:
                    </strong>
                    <p className="text-[#50544E] leading-relaxed">
                      {aiSummary.summary.health_effects?.short_term_effects}
                    </p>
                  </div>

                  <div className="p-4 bg-[#F8F6F0] rounded-xl border border-[#E8E4DC] space-y-1.5">
                    <strong className="text-[11px] uppercase tracking-wider text-[#221F1D] block">
                      Long-Term / Chronic Findings:
                    </strong>
                    <p className="text-[#50544E] leading-relaxed">
                      {aiSummary.summary.health_effects?.long_term_effects}
                    </p>
                  </div>

                  <div className="p-4 bg-[#F8F6F0] rounded-xl border border-[#E8E4DC] space-y-1.5">
                    <strong className="text-[11px] uppercase tracking-wider text-[#A8472A] block">
                      Excessive Exposure Considerations:
                    </strong>
                    <p className="text-[#50544E] leading-relaxed">
                      {aiSummary.summary.health_effects?.excessive_exposure_effects}
                    </p>
                  </div>

                  <div className="p-4 bg-[#F8F6F0] rounded-xl border border-[#E8E4DC] space-y-1.5">
                    <strong className="text-[11px] uppercase tracking-wider text-[#3D4F40] block">
                      Sensitivities & Allergen Warnings:
                    </strong>
                    <p className="text-[#50544E] leading-relaxed">
                      {aiSummary.summary.health_effects?.sensitivities_and_allergens}
                    </p>
                  </div>
                </div>
              </div>

              {/* 6. QUANTITATIVE EXPOSURE EVALUATION */}
              <div className="space-y-2">
                <h4 className="font-bold text-xs uppercase tracking-wider text-[#3D4F40]">
                  6. Dietary Exposure Evaluation
                </h4>
                <div className="p-4 bg-[#EFECE5] rounded-xl border border-[#CBD3C6] text-xs space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-[11px] uppercase px-2.5 py-0.5 rounded bg-[#3D4F40] text-white">
                      Status: {aiSummary.summary.exposure_assessment?.status.replace(/_/g, ' ')}
                    </span>
                    {aiSummary.summary.exposure_assessment?.reference_adi && (
                      <span className="text-[11px] text-[#A8472A] font-semibold">
                        ADI: {aiSummary.summary.exposure_assessment.reference_adi}
                      </span>
                    )}
                  </div>
                  <p className="leading-relaxed text-[#221F1D]">
                    {aiSummary.summary.exposure_assessment?.explanation}
                  </p>
                  {onNavigateToExposure && (
                    <div className="pt-2">
                      <button
                        onClick={() => onNavigateToExposure()}
                        className="bg-[#A8472A] hover:bg-[#933B20] text-white text-[11px] font-bold uppercase tracking-wider px-4 py-1.5 rounded-full shadow-sm flex items-center gap-1"
                      >
                        <Calculator className="w-3 h-3" />
                        Simulate Quantitative Exposure &rarr;
                      </button>
                    </div>
                  )}
                </div>
              </div>

              {/* 7. MISSING INFORMATION & NEXT STEPS */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <div className="p-4 bg-amber-50/60 rounded-xl border border-amber-200 space-y-2 text-amber-950">
                  <h5 className="font-bold uppercase tracking-wider text-[11px] flex items-center gap-1.5 text-amber-900">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-700" />
                    Important Missing or Uncertain Information
                  </h5>
                  <ul className="list-disc list-inside space-y-1 text-[11px]">
                    {aiSummary.summary.missing_or_uncertain_information?.map((item, idx) => (
                      <li key={idx} className="leading-relaxed">{item}</li>
                    ))}
                  </ul>
                </div>

                <div className="p-4 bg-emerald-50/60 rounded-xl border border-emerald-200 space-y-2 text-emerald-950">
                  <h5 className="font-bold uppercase tracking-wider text-[11px] flex items-center gap-1.5 text-emerald-900">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" />
                    Practical Next Steps for Consumers
                  </h5>
                  <ul className="list-disc list-inside space-y-1 text-[11px]">
                    {aiSummary.summary.consumer_next_steps?.map((item, idx) => (
                      <li key={idx} className="leading-relaxed">{item}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* 8. SOURCE REFERENCES */}
              <div className="space-y-2 border-t border-[#E8E4DC] pt-4">
                <h5 className="font-bold text-xs uppercase tracking-wider text-[#67625B]">
                  Authoritative Scientific & Regulatory Sources
                </h5>
                <div className="flex flex-wrap gap-2 text-xs">
                  {aiSummary.summary.source_references?.map((src, idx) => (
                    <a
                      key={idx}
                      href={src.url}
                      target="_blank"
                      rel="noreferrer"
                      className="px-3 py-1.5 rounded-lg bg-[#F8F6F0] hover:bg-[#EFECE5] border border-[#E2E6DF] text-[#221F1D] inline-flex items-center gap-1.5 transition-colors font-medium text-[11px]"
                    >
                      <strong className="text-[#A8472A]">{src.organization}:</strong>
                      <span>{src.title}</span>
                      <ExternalLink className="w-3 h-3 text-[#67625B]" />
                    </a>
                  ))}
                </div>
              </div>

              {/* MANDATORY GROUNDING NOTICE */}
              <div className="p-3.5 bg-[#EFECE5] rounded-xl border border-[#CBD3C6] text-[11px] text-[#50544E] leading-relaxed">
                <strong>Grounding Transparency:</strong> {aiSummary.summary.grounding_statement}
              </div>
            </div>
          )}

          {/* SECTION 1: INGREDIENTS BREAKDOWN */}
          {(activeSubTab === 'all' || activeSubTab === 'ingredients') && (
            <div className="bg-white rounded-2xl border border-[#E2E6DF] p-6 shadow-sm space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-[#E8E4DC]">
                <div>
                  <h4 className="font-serif-heading text-lg font-bold text-[#221F1D]">
                    Ingredient Clauses & Regional Name Resolution
                  </h4>
                  <p className="text-xs text-[#67625B]">
                    Normalized chemical names and matched regional Indian designations (Hindi, Tamil, Marathi, etc.)
                  </p>
                </div>
                <span className="text-xs text-[#67625B]">
                  {result.ingredients?.filter(i => i.recognized).length} Recognized of {result.ingredients?.length}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {result.ingredients?.map((ing, idx) => {
                  const hasAlias = ing.name_resolution?.matched;
                  return (
                    <div 
                      key={idx}
                      className={`p-3.5 rounded-xl border text-xs flex flex-col justify-between transition-all ${
                        hasAlias 
                          ? 'bg-amber-50/50 border-amber-200' 
                          : ing.recognized 
                          ? 'bg-[#F8F6F0] border-[#E8E4DC]' 
                          : 'bg-rose-50/40 border-rose-200'
                      }`}
                    >
                      <div>
                        <div className="flex items-start justify-between gap-2">
                          <span className="font-bold text-[#221F1D] text-sm capitalize">
                            {ing.normalized_name}
                          </span>
                          {hasAlias ? (
                            <span className="text-[10px] font-bold text-[#A8472A] bg-amber-100 px-2 py-0.5 rounded uppercase">
                              Indian Alias
                            </span>
                          ) : ing.recognized ? (
                            <span className="text-[10px] font-bold text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded">
                              Known
                            </span>
                          ) : (
                            <span className="text-[10px] font-bold text-amber-800 bg-amber-100 px-2 py-0.5 rounded">
                              Review
                            </span>
                          )}
                        </div>

                        {/* Raw text difference */}
                        {ing.raw_text.toLowerCase() !== ing.normalized_name && (
                          <div className="text-[11px] text-[#67625B] mt-1 font-mono italic">
                            Label text: "{ing.raw_text}"
                          </div>
                        )}

                        {/* Indian Name Resolution Card */}
                        {hasAlias && (
                          <div className="mt-2.5 p-2 bg-white rounded-lg border border-amber-200/80 text-[11px] space-y-1">
                            <div className="text-[#3D4F40] font-semibold flex items-center gap-1">
                              <span>Canonical:</span>
                              <strong className="text-[#A8472A] uppercase">{ing.name_resolution.canonical_name}</strong>
                            </div>
                            <div className="text-[#67625B] flex justify-between">
                              <span>Language: {ing.name_resolution.language || 'Regional'}</span>
                              <span className="text-[10px] text-amber-700">Verified Dictionary</span>
                            </div>
                          </div>
                        )}

                        {/* Candidate Discovery Link for Unknown Terms */}
                        {!ing.recognized && !hasAlias && onNavigateToBarcodeSearch && (
                          <div className="mt-2 pt-2 border-t border-rose-200/80">
                            <button
                              type="button"
                              onClick={() => onNavigateToBarcodeSearch(ing.normalized_name)}
                              className="text-[10px] text-[#A8472A] hover:underline font-bold inline-flex items-center gap-1"
                            >
                              <Search className="w-3 h-3" />
                              Search Product Database &rarr;
                            </button>
                          </div>
                        )}
                      </div>

                      <div className="mt-2 pt-2 border-t border-black/5 text-[10px] text-[#67625B]">
                        Index #{idx + 1}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* SECTION 2: ADDITIVES & SOURCE EVIDENCE */}
          {(activeSubTab === 'all' || activeSubTab === 'additives') && (
            <div className="bg-white rounded-2xl border border-[#E2E6DF] p-6 shadow-sm space-y-5">
              <div className="flex items-center justify-between pb-3 border-b border-[#E8E4DC]">
                <div>
                  <h4 className="font-serif-heading text-lg font-bold text-[#221F1D]">
                    Identified Additive Codes & Authority Evidence
                  </h4>
                  <p className="text-xs text-[#67625B]">
                    Cross-referenced with WHO/FAO JECFA chemical monographs and FSSAI standards.
                  </p>
                </div>
                <span className="text-xs font-semibold text-[#A8472A]">
                  {result.additives?.length || 0} Additives Documented
                </span>
              </div>

              {result.additives?.length === 0 ? (
                <div className="p-6 text-center text-xs text-[#67625B] bg-[#F8F6F0] rounded-xl">
                  No standard additive codes (INS/E-numbers) were detected in this label.
                </div>
              ) : (
                <div className="space-y-4">
                  {result.additives?.map((additive) => {
                    const ev = additive.evidence;
                    const adi = ev?.adi;
                    const scientific = ev?.scientific_findings;
                    const regulatory = ev?.regulatory_details;

                    return (
                      <div 
                        key={additive.code}
                        className="bg-[#F8F6F0] rounded-xl border border-[#E8E4DC] p-5 space-y-4 hover:border-[#A8472A]/50 transition-all"
                      >
                        {/* Additive Header */}
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-[#E8E4DC]">
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-mono font-bold text-xs bg-[#A8472A] text-white px-2.5 py-0.5 rounded">
                                INS {additive.code}
                              </span>
                              <h5 className="font-serif-heading text-base font-bold text-[#221F1D]">
                                {additive.name}
                              </h5>
                            </div>
                            <div className="text-xs text-[#67625B] mt-0.5">
                              Functional Purpose: <strong className="text-[#3D4F40]">{additive.purpose}</strong>
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            <span className="text-[11px] font-semibold text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
                              {ev?.evidence_status === 'verified_evidence' ? 'Verified Evidence' : 'Catalogue Match'}
                            </span>
                            {onNavigateToExposure && (
                              <button
                                onClick={() => onNavigateToExposure(additive.code, adi?.value || 30)}
                                className="bg-white hover:bg-[#EFECE5] text-[#A8472A] text-[11px] font-bold uppercase tracking-wider px-3 py-1 rounded-full border border-[#A8472A] transition-colors flex items-center gap-1"
                              >
                                <Calculator className="w-3 h-3" />
                                Test Exposure
                              </button>
                            )}
                          </div>
                        </div>

                        {/* Evidence Findings Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                          {/* Left: Scientific Evaluation */}
                          <div className="bg-white p-3.5 rounded-lg border border-[#E2E6DF] space-y-2">
                            <div className="font-bold text-[11px] uppercase tracking-wider text-[#3D4F40] flex items-center gap-1">
                              <ShieldCheck className="w-3.5 h-3.5 text-[#3D4F40]" />
                              WHO/FAO JECFA Evaluation & ADI
                            </div>

                            <div className="text-[#221F1D] leading-relaxed">
                              <strong>Acceptable Daily Intake (ADI):</strong>{' '}
                              <span className="text-[#A8472A] font-semibold">
                                {adi?.text || 'Not specified / Safe at GMP'}
                              </span>
                            </div>

                            {scientific?.summary && (
                              <p className="text-[11px] text-[#67625B] leading-relaxed italic">
                                "{scientific.summary}"
                              </p>
                            )}

                            {scientific?.chronic_effects && (
                              <div className="text-[11px] text-[#50544E]">
                                <strong>Chronic Assessment:</strong> {scientific.chronic_effects}
                              </div>
                            )}

                            {scientific?.jecfa_url && (
                              <a
                                href={scientific.jecfa_url}
                                target="_blank"
                                rel="noreferrer"
                                className="inline-flex items-center gap-1 text-[11px] text-[#A8472A] font-bold hover:underline pt-1"
                              >
                                View JECFA Chemical Monograph <ExternalLink className="w-3 h-3" />
                              </a>
                            )}
                          </div>

                          {/* Right: Indian Regulatory Status (FSSAI) */}
                          <div className="bg-white p-3.5 rounded-lg border border-[#E2E6DF] space-y-2">
                            <div className="font-bold text-[11px] uppercase tracking-wider text-[#A8472A] flex items-center gap-1">
                              <Info className="w-3.5 h-3.5 text-[#A8472A]" />
                              FSSAI Standard & Permitted Limits
                            </div>

                            <div className="text-[#221F1D]">
                              <strong>Indian Regulatory Status:</strong>{' '}
                              <span className="text-emerald-700 font-semibold">
                                {regulatory?.fssai_permitted ? 'Permitted Food Additive' : 'Standard Pending'}
                              </span>
                            </div>

                            {regulatory?.conditions && (
                              <p className="text-[11px] text-[#50544E] leading-relaxed">
                                {regulatory.conditions}
                              </p>
                            )}

                            {scientific?.sensitivities && (
                              <div className="text-[11px] text-[#67625B]">
                                <strong>Sensitivities / Allergen Notice:</strong> {scientific.sensitivities}
                              </div>
                            )}

                            {regulatory?.source_url && (
                              <a
                                href={regulatory.source_url}
                                target="_blank"
                                rel="noreferrer"
                                className="inline-flex items-center gap-1 text-[11px] text-[#3D4F40] font-bold hover:underline pt-1"
                              >
                                FSSAI Food Additives Regulation (PDF) <ExternalLink className="w-3 h-3" />
                              </a>
                            )}
                          </div>
                        </div>

                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* SECTION 3: NUTRITIONAL PROFILE & EXPERIMENTAL SCORE */}
          {(activeSubTab === 'all' || activeSubTab === 'nutrition') && (
            <div className="bg-white rounded-2xl border border-[#E2E6DF] p-6 shadow-sm space-y-6">
              <div className="flex items-center justify-between pb-3 border-b border-[#E8E4DC]">
                <div>
                  <h4 className="font-serif-heading text-lg font-bold text-[#221F1D]">
                    Nutritional Table & Prototype Nutrition Indicator
                  </h4>
                  <p className="text-xs text-[#67625B]">
                    Extracted from label panels. Evaluated using transparent nutrient thresholds per 100g.
                  </p>
                </div>
                <span className="text-[11px] bg-[#EFECE5] px-3 py-1 rounded-full text-[#3D4F40] font-bold uppercase">
                  Experimental Indicator
                </span>
              </div>

              {result.nutrition?.detected ? (
                <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
                  {/* Left: Nutrients Grid */}
                  <div className="md:col-span-7 space-y-3">
                    <h5 className="font-bold text-xs uppercase tracking-wider text-[#3D4F40]">
                      Segmented Nutrients (Per 100g / 100ml)
                    </h5>
                    <div className="bg-[#F8F6F0] rounded-xl border border-[#E8E4DC] p-3 divide-y divide-[#E8E4DC] text-xs">
                      {Object.entries(result.nutrition.nutrients).map(([key, val]) => {
                        if (val === null) return null;
                        return (
                          <div key={key} className="flex justify-between py-1.5 px-2">
                            <span className="capitalize text-[#67625B]">{key.replace(/_/g, ' ')}:</span>
                            <span className="font-bold text-[#221F1D]">{val} {key.includes('kcal') ? 'kcal' : key.includes('mg') ? 'mg' : 'g'}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Right: Nutrition Score Card */}
                  <div className="md:col-span-5 bg-[#EFECE5] rounded-xl p-5 border border-[#E2E6DF] space-y-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="text-[10px] uppercase font-bold tracking-wider text-[#A8472A]">
                          Prototype Nutrition Score
                        </div>
                        <div className="font-serif-heading text-3xl font-bold text-[#221F1D] mt-1">
                          {result.nutrition.nutrition_score?.score ?? 'N/A'}{' '}
                          <span className="text-sm font-sans font-normal text-[#67625B]">/ 100</span>
                        </div>
                        <div className="text-xs font-semibold text-[#3D4F40] mt-0.5">
                          {result.nutrition.nutrition_score?.label || 'Insufficient Data'}
                        </div>
                      </div>
                    </div>

                    <div className="text-[11px] text-[#50544E] leading-relaxed border-t border-[#CBD3C6] pt-3">
                      {result.nutrition.nutrition_score?.methodology}
                    </div>

                    <div className="p-2.5 bg-amber-50 rounded-lg border border-amber-200 text-[10px] text-amber-900 leading-relaxed">
                      <strong>Important Notice:</strong> {result.nutrition.nutrition_score?.disclaimer}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-8 text-center text-xs text-[#67625B] bg-[#F8F6F0] rounded-xl space-y-2">
                  <div className="font-bold text-[#221F1D]">No Nutrition Table Detected in OCR Stream</div>
                  <p className="max-w-md mx-auto">
                    The uploaded image did not contain a readable nutritional panel per 100g. You can paste the nutrition facts in the text editor above and click <strong>"Re-Analyze Text"</strong> to generate the indicator.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* SECTION 4: DIETARY EXPOSURE GUIDANCE */}
          <div className="bg-[#3D4F40] text-white rounded-2xl p-6 sm:p-8 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <span className="text-[11px] font-bold uppercase tracking-widest text-[#F2B731]">
                  Quantitative Dietary Exposure Assessment
                </span>
                <h4 className="font-serif-heading text-xl font-bold mt-1">
                  Why Additive Exposure Cannot Be Guessed from Label Order
                </h4>
              </div>

              {onNavigateToExposure && (
                <button
                  onClick={() => onNavigateToExposure()}
                  className="bg-[#A8472A] hover:bg-[#933B20] text-white text-xs font-bold uppercase tracking-wider px-5 py-2.5 rounded-full transition-colors whitespace-nowrap self-start sm:self-auto"
                >
                  Open Exposure Calculator &rarr;
                </button>
              )}
            </div>

            <p className="text-xs text-[#CBD3C6] leading-relaxed">
              Under Indian food labeling regulations, ingredients are listed in descending order of incoming weight. However, manufacturers are <strong>not</strong> required to disclose precise additive concentrations (e.g. mg per kg of product). Inferring intake from ingredient position is scientifically invalid. Use our quantitative calculator to simulate exposure scenarios against verified JECFA ADI reference thresholds.
            </p>
          </div>

          {/* SECTION 5: TRANSPARENT LIMITATIONS */}
          <div className="bg-[#EFECE5] rounded-2xl p-6 border border-[#E2E6DF] space-y-3">
            <h5 className="font-bold text-xs uppercase tracking-wider text-[#221F1D] flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-[#A8472A]" />
              Scientific & Technology Limitations of this Prototype
            </h5>
            <ul className="text-xs text-[#50544E] space-y-1.5 list-disc list-inside">
              {result.limitations?.map((lim, i) => (
                <li key={i}>{lim}</li>
              ))}
            </ul>
          </div>

        </div>
      )}
    </div>
  );
}
