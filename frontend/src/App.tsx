import { useState } from 'react';
import { ChatTriage } from './components/ChatTriage';
import { RiskGauge } from './components/RiskGauge';
import { RecommendationCard } from './components/RecommendationCard';
import { AnalyzeResponse } from './api';
import './index.css';

export type Lang = 'en' | 'te' | 'hi';

const LANGUAGES: { code: Lang; label: string; flag: string }[] = [
    { code: 'en', label: 'English', flag: '🇬🇧' },
    { code: 'te', label: 'తెలుగు', flag: '🇮🇳' },
    { code: 'hi', label: 'हिंदी', flag: '🇮🇳' },
];

// Backend codes for translation (google-translate compatible)
export const LANG_CODE: Record<Lang, string> = {
    en: 'en',
    te: 'te',
    hi: 'hi',
};

const UI_STRINGS: Record<Lang, { title: string; subtitle: string; processing: string }> = {
    en: {
        title: 'HealthTriage AI',
        subtitle: 'Early risk detection & conversational medical intake',
        processing: 'Processing final risk assessment...',
    },
    te: {
        title: 'HealthTriage AI',
        subtitle: 'ప్రారంభ ప్రమాద గుర్తింపు & వైద్య ఇన్‌టేక్ సిస్టమ్',
        processing: 'ప్రమాద అంచనా ప్రాసెస్ చేయబడుతోంది...',
    },
    hi: {
        title: 'HealthTriage AI',
        subtitle: 'प्रारंभिक जोखिम पहचान और चिकित्सा सेवन प्रणाली',
        processing: 'जोखिम मूल्यांकन प्रक्रिया में है...',
    },
};

function App() {
    const [result, setResult] = useState<AnalyzeResponse | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [lang, setLang] = useState<Lang>('en');

    const t = UI_STRINGS[lang];

    const handleLangChange = (newLang: Lang) => {
        setLang(newLang);
        setResult(null);
        setError(null);
    };

    const handleAssessmentReady = async (patientData: any) => {
        setIsLoading(true);
        setError(null);
        try {
            const cleanedData = {
                ...patientData,
                age: patientData.age || 30,
                symptoms: (patientData.symptoms || []).map((s: any) => ({
                    name: s.name,
                    severity: s.severity || 'moderate',
                    days: s.days || 1
                })),
                existing_conditions: patientData.existing_conditions || []
            };

            const response = await fetch('http://127.0.0.1:8000/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: "Extracted via Chat UI",
                    language: LANG_CODE[lang],
                    user_age: cleanedData.age,
                    patient_data: cleanedData
                })
            });

            if (!response.ok) throw new Error("Failed to analyze");
            const data = await response.json();
            setResult(data);
        } catch (err: any) {
            setError(err.message || "An error occurred");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="app-container">
            <header className="app-header">
                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '16px', marginBottom: '8px', flexWrap: 'wrap' }}>
                    <div className="logo-container" style={{ marginBottom: 0 }}>
                        <div className="pulse-dot"></div>
                        <h1>{t.title}</h1>
                    </div>

                    {/* ── 3-Language Selector ── */}
                    <div className="lang-selector">
                        {LANGUAGES.map(({ code, label, flag }) => (
                            <button
                                key={code}
                                onClick={() => handleLangChange(code)}
                                className={`lang-btn ${lang === code ? 'active' : ''}`}
                            >
                                {flag} {label}
                            </button>
                        ))}
                    </div>
                </div>
                <p className="subtitle">{t.subtitle}</p>
            </header>

            <main style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
                <div style={{ width: '100%' }}>
                    <ChatTriage
                        key={lang}   /* remount component on lang change to reset questions */
                        onAssessmentReady={handleAssessmentReady}
                        language={lang}
                    />
                    {error && <div className="error-message fade-in">{error}</div>}
                    {isLoading && (
                        <p style={{ color: '#94a3b8', textAlign: 'center', marginTop: '12px', fontSize: '0.9rem' }}>
                            {t.processing}
                        </p>
                    )}
                </div>

                {result && (
                    <div className="fade-in" style={{ display: 'flex', gap: '20px', width: '100%', flexWrap: 'wrap' }}>
                        <RiskGauge score={result.risk_score} level={result.risk_level} />
                        <RecommendationCard result={result} />
                    </div>
                )}
            </main>
        </div>
    );
}

export default App;
