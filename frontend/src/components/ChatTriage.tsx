import { useState, useRef, useEffect, useCallback } from 'react';
import { Mic, MicOff, ArrowRight, Activity, Heart, Thermometer, Wind, HelpCircle, Volume2, VolumeX } from 'lucide-react';
import type { Lang } from '../App';

const STRINGS: Record<Lang, {
    title: string; placeholder: string; send: string;
    listening: string; online: string; speakAlt: string; stopAlt: string;
    initialQ: string;
}> = {
    en: {
        title: 'Health Assessment',
        placeholder: 'Type your answer here...',
        send: 'Continue',
        listening: 'Listening...',
        online: '● Active',
        speakAlt: 'Speak question',
        stopAlt: 'Stop speaking',
        initialQ: 'Hello! What symptoms are you experiencing right now? (e.g. fever, cough, headache)',
    },
    te: {
        title: 'ఆరోగ్య మూల్యాంకనం',
        placeholder: 'మీ సమాధానం ఇక్కడ టైప్ చేయండి...',
        send: 'కొనసాగించు',
        listening: 'వింటున్నాను...',
        online: '● క్రియాశీలం',
        speakAlt: 'ప్రశ్న చదవండి',
        stopAlt: 'ఆపండి',
        initialQ: 'నమస్కారం! మీకు ఏ లక్షణాలు ఉన్నాయో చెప్పండి — ఉదాహరణకు జ్వరం, దగ్గు, తలనొప్పి వంటివి.',
    },
    hi: {
        title: 'स्वास्थ्य मूल्यांकन',
        placeholder: 'यहाँ अपना उत्तर टाइप करें...',
        send: 'जारी रखें',
        listening: 'सुन रहा हूँ...',
        online: '● सक्रिय',
        speakAlt: 'प्रश्न बोलें',
        stopAlt: 'रोकें',
        initialQ: 'नमस्ते! अभी आप कौन से लक्षण महसूस कर रहे हैं? (जैसे बुखार, खांसी, सिरदर्द)',
    },
};

// BCP-47 voice lang codes for Web Speech API
const VOICE_LANG: Record<Lang, string> = {
    en: 'en-US',
    te: 'te-IN',
    hi: 'hi-IN',
};

function getQuestionIcon(text: string) {
    const lower = text.toLowerCase();
    if (lower.includes('fever') || lower.includes('जुखाम') || lower.includes('बुखार') || lower.includes('జ్వరం') || lower.includes('pain'))
        return <Thermometer size={28} />;
    if (lower.includes('breath') || lower.includes('cough') || lower.includes('सांस') || lower.includes('खांसी') || lower.includes('శ్వాస'))
        return <Wind size={28} />;
    if (lower.includes('age') || lower.includes('वय') || lower.includes('उम्र') || lower.includes('condition') || lower.includes('diabetes'))
        return <Heart size={28} />;
    if (lower.includes('symptom') || lower.includes('लक్షణ') || lower.includes('लक्षण'))
        return <Activity size={28} />;
    return <HelpCircle size={28} />;
}

interface PatientData {
    symptoms: Array<{ name: string; severity?: string; days?: number }>;
    age?: number;
    existing_conditions: string[];
}

interface ChatTriageProps {
    onAssessmentReady: (data: PatientData) => void;
    language: Lang;
}

interface QA { question: string; answer: string; }

export function ChatTriage({ onAssessmentReady, language }: ChatTriageProps) {
    const t = STRINGS[language];

    const [currentQuestion, setCurrentQuestion] = useState<string>(t.initialQ);
    const [history, setHistory] = useState<{ role: string; content: string }[]>([]);
    const [qaPairs, setQAPairs] = useState<QA[]>([]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [isListening, setIsListening] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [slideKey, setSlideKey] = useState(0);

    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        setTimeout(() => inputRef.current?.focus(), 400);
    }, [currentQuestion]);

    // Auto-stop TTS when language or question changes
    useEffect(() => {
        window.speechSynthesis?.cancel();
        setIsSpeaking(false);
    }, [language, currentQuestion]);

    // ── TTS Speaker ──
    const handleSpeak = useCallback(() => {
        const synth = window.speechSynthesis;
        if (!synth) {
            alert("Your browser does not support Text-to-Speech.");
            return;
        }

        if (isSpeaking) {
            synth.cancel();
            setIsSpeaking(false);
            return;
        }

        const speak = (voiceList: SpeechSynthesisVoice[]) => {
            const utterance = new SpeechSynthesisUtterance(currentQuestion);
            utterance.lang = VOICE_LANG[language];
            utterance.rate = 0.9;
            utterance.pitch = 1.0;
            utterance.volume = 1.0;

            // Find the best matching voice for the language
            const langPrefix = VOICE_LANG[language].split('-')[0]; // 'en', 'te', 'hi'
            const exactMatch = voiceList.find(v => v.lang === VOICE_LANG[language]);
            const prefixMatch = voiceList.find(v => v.lang.startsWith(langPrefix));
            utterance.voice = exactMatch || prefixMatch || null;

            utterance.onend = () => setIsSpeaking(false);
            utterance.onerror = () => setIsSpeaking(false);

            setIsSpeaking(true);
            synth.cancel(); // cancel any previous stuck utterance
            synth.speak(utterance);
        };

        // Chrome loads voices asynchronously — wait for them if not ready yet
        const voices = synth.getVoices();
        if (voices.length > 0) {
            speak(voices);
        } else {
            synth.onvoiceschanged = () => {
                speak(synth.getVoices());
                synth.onvoiceschanged = null;
            };
        }
    }, [currentQuestion, language, isSpeaking]);

    // ── Voice Input (Mic) ──
    const handleVoiceInput = () => {
        // @ts-ignore
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SR) { alert("Browser doesn't support speech recognition."); return; }
        const recognition = new SR();
        recognition.lang = VOICE_LANG[language];
        recognition.interimResults = false;
        recognition.onstart = () => setIsListening(true);
        recognition.onresult = (e: any) => setInput(e.results[0][0].transcript);
        recognition.onerror = () => setIsListening(false);
        recognition.onend = () => setIsListening(false);
        recognition.start();
    };

    // ── Send Answer ──
    const handleSend = async () => {
        const trimmed = input.trim();
        if (!trimmed || isTyping) return;

        window.speechSynthesis?.cancel();
        setIsSpeaking(false);

        const newQA: QA = { question: currentQuestion, answer: trimmed };
        setQAPairs(prev => [...prev, newQA]);
        setInput('');
        setIsTyping(true);

        const updatedHistory = [
            ...history,
            { role: 'model', content: currentQuestion },
            { role: 'user', content: trimmed },
        ];
        setHistory(updatedHistory);

        try {
            const response = await fetch('http://127.0.0.1:8000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    history: updatedHistory,
                    message: trimmed,
                    language,
                })
            });

            if (!response.ok) throw new Error("Failed");
            const data = await response.json();

            setSlideKey(k => k + 1);
            setCurrentQuestion(data.reply);

            if (data.is_complete) {
                setTimeout(() => onAssessmentReady(data.patient_data), 1400);
            }
        } catch {
            setCurrentQuestion(
                language === 'hi' ? 'क्षमा करें, कनेक्शन समस्या। कृपया पुनः प्रयास करें।'
                    : language === 'te' ? 'క్షమించండి, సంప్రదింపు సమస్య. తిరిగి ప్రయత్నించండి.'
                        : "Sorry, there was a connection issue. Please try again."
            );
            setSlideKey(k => k + 1);
        } finally {
            setIsTyping(false);
        }
    };

    const progressCount = Math.min(qaPairs.length, 6);

    return (
        <div className="intake-wizard glass-panel fade-in">

            {/* ── Header Strip ── */}
            <div className="wizard-header">
                <div className="wizard-brand">
                    <span className="wizard-brand-dot"></span>
                    <span className="wizard-brand-name">{t.title}</span>
                    <span className="wizard-status">{t.online}</span>
                </div>
                <div className="wizard-progress-dots">
                    {Array.from({ length: 6 }).map((_, i) => (
                        <span
                            key={i}
                            className={`progress-dot ${i < progressCount ? 'filled' : ''} ${i === progressCount ? 'current anim' : ''}`}
                        />
                    ))}
                </div>
            </div>

            {/* ── Body ── */}
            <div className="wizard-body">

                {/* Animated Icon */}
                <div className="question-icon-ring" key={`icon-${slideKey}`}>
                    {getQuestionIcon(currentQuestion)}
                </div>

                {/* Question Card + Speaker */}
                <div style={{ width: '100%', maxWidth: '640px', position: 'relative' }}>
                    <div className="question-card" key={`q-${slideKey}`}>
                        {isTyping
                            ? <span className="typing-skeleton">
                                {[0, 0.15, 0.3].map((d, i) => (
                                    <span key={i} className="typing-dot" style={{ animationDelay: `${d}s` }} />
                                ))}
                            </span>
                            : <p className="question-text">{currentQuestion}</p>
                        }
                    </div>

                    {/* Speaker button — top right of question card */}
                    {!isTyping && (
                        <button
                            onClick={handleSpeak}
                            className={`tts-btn ${isSpeaking ? 'speaking' : ''}`}
                            title={isSpeaking ? t.stopAlt : t.speakAlt}
                        >
                            {isSpeaking ? <VolumeX size={15} /> : <Volume2 size={15} />}
                        </button>
                    )}
                </div>

                {/* Q&A History Chips */}
                {qaPairs.length > 0 && (
                    <div className="qa-history">
                        {qaPairs.slice(-2).map((qa, i) => (
                            <div key={i} className="qa-chip">
                                <span className="qa-chip-q">
                                    {qa.question.slice(0, 42)}{qa.question.length > 42 ? '…' : ''}
                                </span>
                                <span className="qa-chip-a">
                                    ✓ {qa.answer.slice(0, 48)}{qa.answer.length > 48 ? '…' : ''}
                                </span>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* ── Input Panel ── */}
            <div className="wizard-input-panel">
                <div className={`wizard-input-wrap ${isListening ? 'listening' : ''}`}>
                    <input
                        ref={inputRef}
                        type="text"
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && handleSend()}
                        placeholder={isListening ? t.listening : t.placeholder}
                        disabled={isTyping}
                        className="wizard-input"
                    />
                    <button
                        onClick={handleVoiceInput}
                        className={`wizard-mic-btn ${isListening ? 'active' : ''}`}
                        disabled={isTyping}
                        title="Speak your answer"
                    >
                        {isListening ? <MicOff size={17} /> : <Mic size={17} />}
                    </button>
                </div>
                <button
                    onClick={handleSend}
                    disabled={isTyping || !input.trim()}
                    className="wizard-send-btn"
                >
                    {isTyping
                        ? <span className="btn-spinner" />
                        : <>{t.send} <ArrowRight size={17} style={{ marginLeft: 6 }} /></>
                    }
                </button>
            </div>
        </div>
    );
}
