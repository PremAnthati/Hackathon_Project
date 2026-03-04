import React, { useState } from 'react';
import { SymptomInput } from './components/SymptomInput';
import { RiskGauge } from './components/RiskGauge';
import { RecommendationCard } from './components/RecommendationCard';
import { analyzeSymptoms, AnalyzeResponse } from './api';
import './index.css';

function App() {
    const [result, setResult] = useState<AnalyzeResponse | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (text: string, language: string, context: { age?: number }) => {
        setIsLoading(true);
        setError(null);
        try {
            const resp = await analyzeSymptoms(text, language, context.age);
            setResult(resp);
        } catch (err: any) {
            setError(err.message || "An error occurred");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="app-container">
            <header className="app-header">
                <div className="logo-container">
                    <div className="pulse-dot"></div>
                    <h1>HealthTriage AI</h1>
                </div>
                <p className="subtitle">Early risk detection & intelligent medical recommendations</p>
            </header>

            <main className="main-content">
                <div className="left-panel">
                    <SymptomInput onSubmit={handleSubmit} isLoading={isLoading} />

                    {error && <div className="error-message fade-in">{error}</div>}
                </div>

                <div className="right-panel">
                    {result ? (
                        <div className="results-container fade-in">
                            <RiskGauge score={result.risk_score} level={result.risk_level} />
                            <RecommendationCard result={result} />
                        </div>
                    ) : (
                        <div className="empty-state glass-panel fade-in">
                            <div className="empty-icon">🩺</div>
                            <h3>Awaiting Input</h3>
                            <p>Describe your symptoms using text or voice to get an immediate AI risk assessment.</p>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
}

export default App;
