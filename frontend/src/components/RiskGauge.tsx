import React from 'react';

interface Props {
    score: number;
    level: string;
}

export function RiskGauge({ score, level }: Props) {
    // Determine color based on level
    let colorClass = "risk-low";
    if (level === "MODERATE") colorClass = "risk-moderate";
    if (level === "HIGH") colorClass = "risk-high";
    if (level === "CRITICAL") colorClass = "risk-critical";

    const percentage = Math.min(100, Math.max(0, score));

    return (
        <div className="risk-gauge-container glass-panel">
            <h3 className="section-title">Risk Assessment</h3>

            <div className="gauge-wrapper">
                <svg viewBox="0 0 36 36" className={`circular-chart ${colorClass}`}>
                    <path
                        className="circle-bg"
                        d="M18 2.0845
              a 15.9155 15.9155 0 0 1 0 31.831
              a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                    <path
                        className="circle"
                        strokeDasharray={`${percentage}, 100`}
                        d="M18 2.0845
              a 15.9155 15.9155 0 0 1 0 31.831
              a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                    <text x="18" y="20.35" className="percentage">{score}</text>
                </svg>
            </div>

            <div className={`risk-badge ${colorClass}`}>
                {level} RISK
            </div>
        </div>
    );
}
