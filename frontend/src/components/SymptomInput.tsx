import React, { useState, useRef } from 'react';
import { Mic, Send, Square, Globe } from 'lucide-react';

interface Props {
    onSubmit: (text: string, language: string, context: { age?: number }) => void;
    isLoading: boolean;
}

export function SymptomInput({ onSubmit, isLoading }: Props) {
    const [text, setText] = useState("");
    const [isRecording, setIsRecording] = useState(false);
    const [language, setLanguage] = useState("en");
    const [age, setAge] = useState<string>("");

    const recognitionRef = useRef<any>(null);

    const handleStartRecording = () => {
        if (!('webkitSpeechRecognition' in window)) {
            alert("Speech recognition isn't supported in this browser.");
            return;
        }

        // @ts-ignore
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = true;
        recognitionRef.current.interimResults = true;
        recognitionRef.current.lang = language === "te" ? "te-IN" : "en-US";

        recognitionRef.current.onresult = (event: any) => {
            let finalTranscript = '';
            let interimTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }

            if (finalTranscript) {
                setText(prev => (prev + " " + finalTranscript).trim());
            }
        };

        recognitionRef.current.onerror = (event: any) => {
            console.error("Speech recognition error", event.error);
            setIsRecording(false);
        };

        recognitionRef.current.onend = () => {
            setIsRecording(false);
        };

        recognitionRef.current.start();
        setIsRecording(true);
    };

    const handleStopRecording = () => {
        if (recognitionRef.current) {
            recognitionRef.current.stop();
            setIsRecording(false);
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!text.trim()) return;
        onSubmit(text, language, { age: age ? parseInt(age) : undefined });
    };

    return (
        <div className="input-card glass-panel">
            <div className="settings-row">
                <label className="toggle-label">
                    <Globe size={16} /> Language:
                    <select value={language} onChange={e => setLanguage(e.target.value)} className="select-input">
                        <option value="en">English</option>
                        <option value="te">తెలుగు (Telugu)</option>
                    </select>
                </label>

                <label className="toggle-label">
                    Age (optional):
                    <input
                        type="number"
                        placeholder="e.g. 45"
                        value={age}
                        onChange={e => setAge(e.target.value)}
                        className="age-input"
                        min="0"
                        max="120"
                    />
                </label>
            </div>

            <form onSubmit={handleSubmit} className="input-form">
                <textarea
                    className="symptom-textarea"
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder={language === "en" ? "Describe your symptoms (e.g. I have fever and chest pain...)" : "మీ లక్షణాలను వివరించండి..."}
                    rows={4}
                />

                <div className="action-buttons">
                    {!isRecording ? (
                        <button
                            type="button"
                            className="btn btn-secondary voice-btn"
                            onClick={handleStartRecording}
                            disabled={isLoading}
                        >
                            <Mic size={20} /> {language === "te" ? "మాట్లాడండి" : "Record"}
                        </button>
                    ) : (
                        <button
                            type="button"
                            className="btn btn-danger voice-btn heartbeat"
                            onClick={handleStopRecording}
                        >
                            <Square size={20} /> Stop
                        </button>
                    )}

                    <button
                        type="submit"
                        className="btn btn-primary submit-btn"
                        disabled={isLoading || !text.trim()}
                    >
                        {isLoading ? <span className="loader"></span> : <><Send size={20} /> {language === "te" ? "పంపండి" : "Analyze"}</>}
                    </button>
                </div>
            </form>
        </div>
    );
}
