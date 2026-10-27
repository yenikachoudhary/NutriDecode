import React, { useState } from 'react';
import { 
  Users, 
  Cpu, 
  Leaf, 
  Copy, 
  Check, 
  ShieldCheck, 
  ArrowRight,
  BookOpen
} from 'lucide-react';

export default function AnveshanaTab({ onNavigateToScanner }) {
  const [copiedSection, setCopiedSection] = useState(null);

  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedSection(id);
    setTimeout(() => setCopiedSection(null), 2500);
  };

  const sections = [
    {
      id: 'sec1',
      title: 'Project Title & Core Vision',
      content: 'NUTRIDECODE 2.0: AI-Assisted Citizen Science Food Safety & Label Intelligence Ecosystem connecting People, Machines, and the Planet.',
    },
    {
      id: 'sec2',
      title: 'The Problem Statement',
      content: 'Packaged foods on Indian grocery shelves increasingly use complex chemical aliases, obscure INS additive codes (e.g. INS 500ii, INS 635, INS 150d), and confusing front-of-pack wellness marketing. Commercial scanner apps often hallucinate binary "toxic / non-toxic" verdicts without scientific backing. Consumers lack an open, traceable, and evidence-linked food literacy system.',
    },
    {
      id: 'sec3',
      title: 'People: Student Citizen Scientists',
      content: 'School and college students are trained as active citizen scientists who photograph, transcribe, and inspect packaged foods in local kirana stores and home pantries. They provide the indispensable human-in-the-loop validation that prevents machine hallucinations.',
    },
    {
      id: 'sec4',
      title: 'Machines: AI & Computer Vision',
      content: 'Optical Character Recognition (OCR) with CLAHE adaptive contrast preprocessing extracts text from glossy or curved packaging. Natural language processing normalizes regional aliases (e.g. haldi, maida, uppu, methi) and queries WHO/FAO JECFA toxicological monographs and FSSAI standards.',
    },
    {
      id: 'sec5',
      title: 'Planet: Public Health & Sustainability',
      content: 'All findings populate an open, non-commercial public health repository. The platform logs packaging material types, resin identification codes (BOPP/PET/Tetra Pak), and single-use plastic footprints to foster environmental consciousness alongside dietary safety.',
    },
    {
      id: 'sec6',
      title: 'Prototype Budget (₹10,000 Allocation)',
      content: 'Field Photography & Packaging Samples: ₹3,500\nOptical Target Stand & Lighting Calibration: ₹2,000\nStudent Detective Handbook & Field Logbooks: ₹2,000\nCloud Deployment & Open API Registry: ₹2,500\nTotal Prototype Investment: ₹10,000',
    },
  ];

  return (
    <div className="max-w-6xl mx-auto px-6 py-10 space-y-12">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#E2E6DF] rounded-full text-xs font-semibold tracking-wider text-[#3D4F40] uppercase mb-3">
          Anveshana 2026 Student Science & Engineering Exhibition
        </div>
        <h2 className="font-serif-heading text-3xl sm:text-4xl font-semibold text-[#221F1D] uppercase">
          Citizen Science Food Safety Ecosystem
        </h2>
        <p className="text-xs sm:text-sm text-[#67625B] mt-2 max-w-2xl leading-relaxed">
          The complete academic and exhibition proposal uniting High School Citizen Detectives, Machine Vision, and Evidence-Based Public Health Literacy.
        </p>
      </div>

      {/* THREE PILLARS BANNER */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-[#EFECE5] rounded-2xl p-6 border border-[#E2E6DF] space-y-3">
          <div className="w-12 h-12 rounded-full bg-[#A8472A] text-white flex items-center justify-center">
            <Users className="w-6 h-6" />
          </div>
          <span className="text-[10px] uppercase font-bold tracking-wider text-[#A8472A]">Dimension 1</span>
          <h3 className="font-serif-heading text-lg font-bold text-[#221F1D]">PEOPLE: Citizen Scientists</h3>
          <p className="text-xs text-[#50544E] leading-relaxed">
            High school students turn everyday supermarket trips into genuine scientific investigations, transcribing labels and providing human-in-the-loop quality control.
          </p>
        </div>

        <div className="bg-[#EFECE5] rounded-2xl p-6 border border-[#E2E6DF] space-y-3">
          <div className="w-12 h-12 rounded-full bg-[#3D4F40] text-white flex items-center justify-center">
            <Cpu className="w-6 h-6" />
          </div>
          <span className="text-[10px] uppercase font-bold tracking-wider text-[#3D4F40]">Dimension 2</span>
          <h3 className="font-serif-heading text-lg font-bold text-[#221F1D]">MACHINES: Computer Vision & AI</h3>
          <p className="text-xs text-[#50544E] leading-relaxed">
            Tesseract OCR with adaptive contrast extracts micro-print text. NLP normalizes Indian regional aliases and automates WHO/FAO JECFA evidence matching.
          </p>
        </div>

        <div className="bg-[#EFECE5] rounded-2xl p-6 border border-[#E2E6DF] space-y-3">
          <div className="w-12 h-12 rounded-full bg-[#F2B731] text-[#221F1D] flex items-center justify-center">
            <Leaf className="w-6 h-6" />
          </div>
          <span className="text-[10px] uppercase font-bold tracking-wider text-[#9E6E00]">Dimension 3</span>
          <h3 className="font-serif-heading text-lg font-bold text-[#221F1D]">PLANET: Public Health Literacy</h3>
          <p className="text-xs text-[#50544E] leading-relaxed">
            Free from corporate sponsorship, the public gains transparent food safety intelligence and tracks single-use packaging recyclability across Indian cities.
          </p>
        </div>
      </div>

      {/* ANVESHANA PORTAL COMPLIANT APPLICATION SECTIONS */}
      <div className="bg-white rounded-2xl border border-[#E2E6DF] p-6 sm:p-8 shadow-sm space-y-6">
        <div className="flex items-center justify-between pb-4 border-b border-[#E8E4DC]">
          <div>
            <h3 className="font-serif-heading text-xl font-bold text-[#221F1D]">
              Exhibition Proposal & Application Dossier
            </h3>
            <p className="text-xs text-[#67625B]">
              Ready-to-export text sections matching Anveshana competition submission parameters.
            </p>
          </div>
          <span className="text-xs font-bold text-[#3D4F40] bg-[#E2E6DF] px-3 py-1 rounded-full">
            12 Sections Complete
          </span>
        </div>

        <div className="space-y-4">
          {sections.map((sec) => (
            <div key={sec.id} className="p-4 bg-[#F8F6F0] rounded-xl border border-[#E8E4DC] space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="font-bold text-xs uppercase tracking-wider text-[#A8472A]">
                  {sec.title}
                </h4>
                <button
                  onClick={() => copyToClipboard(sec.content, sec.id)}
                  className="text-[11px] text-[#67625B] hover:text-[#221F1D] flex items-center gap-1 font-semibold"
                >
                  {copiedSection === sec.id ? (
                    <><Check className="w-3.5 h-3.5 text-emerald-600" /> Copied</>
                  ) : (
                    <><Copy className="w-3.5 h-3.5" /> Copy</>
                  )}
                </button>
              </div>
              <p className="text-xs text-[#221F1D] whitespace-pre-line leading-relaxed font-sans">
                {sec.content}
              </p>
            </div>
          ))}
        </div>

        <div className="pt-4 border-t border-[#E8E4DC] flex justify-between items-center text-xs">
          <span className="text-[#67625B]">Prototype Demonstrated: Working Full-Stack System</span>
          <button
            onClick={onNavigateToScanner}
            className="bg-[#A8472A] hover:bg-[#933B20] text-white font-bold uppercase tracking-wider px-6 py-2.5 rounded-full flex items-center gap-1.5 transition-colors shadow-sm"
          >
            Launch Working Prototype <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
