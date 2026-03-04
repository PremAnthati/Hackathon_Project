import React from 'react';
import { AlertCircle, FileText, Activity } from 'lucide-react';
import { AnalyzeResponse } from '../api';

interface Props {
    result: AnalyzeResponse;
}

export function RecommendationCard({ result }: Props) {
    return (
        <div className="recommendation-card glass-panel fade-in">

            <div className="recommendation-section">
                <h3 className="section-title">
                    <Activity size={20} className="icon-mr" /> Detected Symptoms
                </h3>
                <div className="tags-container">
                    {result.detected_symptoms.length > 0 ? (
                        result.detected_symptoms.map((sym, idx) => (
                            <span key={idx} className="symptom-tag">{sym}</span>
                        ))
                    ) : (
                        <span className="text-muted">No specific severity-weighted symptoms detected.</span>
                    )}
                </div>
            </div>

            {result.predicted_condition && (
                <div className="recommendation-section">
                    <h3 className="section-title text-accent">
                        <Activity size={20} className="icon-mr" /> ML Prediction
                    </h3>
                    <div className="prediction-box">
                        <strong>Likely Condition: </strong>
                        <span className="prediction-text">{result.predicted_condition}</span>
                    </div>
                </div>
            )}

            <div className="recommendation-section">
                <h3 className="section-title">
                    <FileText size={20} className="icon-mr" /> Explanation
                </h3>
                <ul className="explanation-list">
                    {result.explanation.map((exp, idx) => (
                        <li key={idx}>{exp}</li>
                    ))}
                </ul>
            </div>

            <div className="recommendation-section primary-action-box">
                <h3 className="section-title text-primary">
                    <AlertCircle size={20} className="icon-mr" /> Recommendation
                </h3>
                <p className="recommendation-text">{result.recommendation}</p>
            </div>

        </div>
    );
}
