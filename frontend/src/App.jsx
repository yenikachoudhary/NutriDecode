import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import HomeTab from './components/HomeTab';
import AnalyzeWorkspace from './components/AnalyzeWorkspace';
import BarcodeLookup from './components/BarcodeLookup';
import ExposureCalculator from './components/ExposureCalculator';
import EvidenceCatalogue from './components/EvidenceCatalogue';
import AnveshanaTab from './components/AnveshanaTab';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  
  // State passed between tabs
  const [scannerInitialText, setScannerInitialText] = useState('');
  const [scannerInitialTitle, setScannerInitialTitle] = useState('');
  const [exposureInitialCode, setExposureInitialCode] = useState(null);
  const [exposureInitialAdi, setExposureInitialAdi] = useState(null);
  const [barcodeInitialQuery, setBarcodeInitialQuery] = useState('');

  // Navigate to scanner with pre-populated text (from Sample or Barcode)
  const handleNavigateToScanner = (text = '', title = '') => {
    setScannerInitialText(text);
    setScannerInitialTitle(title);
    setActiveTab('workspace');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Navigate to exposure calculator with an additive code & ADI
  const handleNavigateToExposure = (code = null, adi = null) => {
    setExposureInitialCode(code);
    setExposureInitialAdi(adi);
    setActiveTab('exposure');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Navigate to barcode/registry candidate discovery with pre-populated query
  const handleNavigateToBarcodeSearch = (query = '') => {
    setBarcodeInitialQuery(query);
    setActiveTab('barcode');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="w-full flex flex-col min-h-screen bg-[#F8F6F0] text-[#221F1D] font-sans selection:bg-[#A8472A] selection:text-white">
      {/* GLOBAL NAVBAR */}
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* MAIN BODY VIEW */}
      <main className="flex-1">
        {activeTab === 'overview' && (
          <HomeTab
            setActiveTab={setActiveTab}
            onSelectSample={handleNavigateToScanner}
          />
        )}

        {activeTab === 'workspace' && (
          <AnalyzeWorkspace
            initialText={scannerInitialText}
            initialTitle={scannerInitialTitle}
            onNavigateToExposure={handleNavigateToExposure}
            onNavigateToBarcodeSearch={handleNavigateToBarcodeSearch}
          />
        )}

        {activeTab === 'barcode' && (
          <BarcodeLookup
            onAnalyzeIngredients={handleNavigateToScanner}
            initialSearchQuery={barcodeInitialQuery}
          />
        )}

        {activeTab === 'exposure' && (
          <ExposureCalculator
            initialAdditiveCode={exposureInitialCode}
            initialAdi={exposureInitialAdi}
          />
        )}

        {activeTab === 'evidence' && (
          <EvidenceCatalogue
            onNavigateToExposure={handleNavigateToExposure}
          />
        )}

        {activeTab === 'anveshana' && (
          <AnveshanaTab
            onNavigateToScanner={() => setActiveTab('workspace')}
          />
        )}
      </main>

      {/* GLOBAL FOOTER */}
      <Footer setActiveTab={setActiveTab} />
    </div>
  );
}
