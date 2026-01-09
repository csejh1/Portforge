
import React, { useState, useEffect, useCallback } from 'react';
import { useAuth, TestResult } from '../contexts/AuthContext';
import { GoogleGenAI, Type } from "@google/genai";
// Fix: Use STACK_CATEGORIES_BASE instead of non-existent STACK_CATEGORIES
import { STACK_CATEGORIES_BASE, getStackLogoUrl } from './HomePage';

// AI Studio API Key Selection helpers
// Augmenting global Window interface is removed as aistudio is already defined as AIStudio in the environment.

// Fix: Use STACK_CATEGORIES_BASE for categories lookup
const TEST_CATEGORIES = [
  { id: 'frontend', name: '프론트엔드', icon: '💻', stacks: STACK_CATEGORIES_BASE['프론트엔드'] },
  { id: 'backend', name: '백엔드', icon: '⚙️', stacks: STACK_CATEGORIES_BASE['백엔드'] },
  { id: 'db', name: 'DB', icon: '🗄️', stacks: STACK_CATEGORIES_BASE['DB'] },
  { id: 'infra', name: '인프라', icon: '☁️', stacks: STACK_CATEGORIES_BASE['인프라'] },
  { id: 'design', name: '디자인', icon: '🎨', stacks: STACK_CATEGORIES_BASE['디자인'] }
];

interface Question {
  question: string;
  options: string[];
  answer: number; 
  explanation: string;
}

const PreTestPage: React.FC = () => {
  const { user, addTestResult } = useAuth();
  const [step, setStep] = useState<'category' | 'stack' | 'ready' | 'testing' | 'result'>('category');
  const [selectedCat, setSelectedCat] = useState<typeof TEST_CATEGORIES[0] | null>(null);
  const [selectedStack, setSelectedStack] = useState<string>('');
  
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [userAnswers, setUserAnswers] = useState<number[]>([]);
  const [correctCount, setCorrectCount] = useState(0);
  const [result, setResult] = useState<TestResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState('');
  
  const [timeLeft, setTimeLeft] = useState(20);
  const [timerActive, setTimerActive] = useState(false);

  // API 키 선택 확인 함수
  const ensureApiKey = async () => {
    try {
      // Cast window to any for flexible access to pre-configured aistudio helper
      const anyWindow = window as any;
      if (anyWindow.aistudio && !(await anyWindow.aistudio.hasSelectedApiKey())) {
        await anyWindow.aistudio.openSelectKey();
        // Assume key selection was successful to mitigate race conditions
        return true;
      }
      return true;
    } catch (e) {
      console.error("API Key selection failed", e);
      return true;
    }
  };

  const finishTest = useCallback(async (finalCorrectCount: number, totalQuestions: number) => {
    setTimerActive(false);
    setLoading(true);
    setLoadingMsg('AI가 전체 답변 데이터를 분석하여 최종 역량 리포트를 작성 중입니다...');
    
    const score = totalQuestions > 0 ? Math.round((finalCorrectCount / totalQuestions) * 100) : 0;
    const level = score >= 90 ? '고급 (Expert)' : score >= 65 ? '중급 (Advanced)' : score >= 35 ? '초급 (Beginner)' : '입문 (Novice)';

    try {
      await ensureApiKey();
      const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
      const response = await ai.models.generateContent({
        model: "gemini-3-flash-preview",
        contents: `${selectedStack} 기술 분야에 대해 총 ${totalQuestions}문제 중 ${finalCorrectCount}문제를 맞혔습니다 (점수: ${score}). 
        사용자의 정답률과 문제 수준을 고려하여 개발자 커리어 관점에서의 강점, 보완점, 그리고 향후 학습 로드맵을 3~4줄로 아주 구체적으로 조언해주세요.`,
      });
      
      const newResult: TestResult = { 
        skill: selectedStack, 
        score, 
        date: new Date().toLocaleDateString(), 
        feedback: response.text || "테스트를 완주하신 것을 축하드립니다! 실전 감각이 뛰어납니다.", 
        level 
      };
      
      setResult(newResult);
      addTestResult(newResult);
      setStep('result');
    } catch (e) { 
      console.error(e);
      alert("결과 분석 중 오류가 발생했습니다. 성적표는 마이페이지에서 확인 가능할 수 있습니다.");
      setStep('result'); 
    } finally { 
      setLoading(false); 
    }
  }, [selectedStack, addTestResult]);

  const fetchMoreQuestions = async (isInitial = false) => {
    if (!isInitial) {
      setLoadingMsg('실력 검증을 위해 AI가 다음 수준의 문제를 생성하고 있습니다...');
    } else {
      setLoadingMsg('AI가 당신을 위한 맞춤형 문제를 출제하고 있습니다...');
    }
    setLoading(true);
    
    try {
      await ensureApiKey();
      const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
      const difficulty = correctCount / (userAnswers.length || 1) > 0.7 ? "고급 실무 수준" : "기초 및 중급 핵심 개념";
      
      const response = await ai.models.generateContent({
        model: "gemini-3-flash-preview",
        contents: `${selectedStack} 분야에 대해 ${difficulty}의 변별력 있는 객관식 문제 5개를 생성해줘. 기존에 물어보지 않았던 새로운 유형이어야 함. JSON 형식: [{question, options, answer, explanation}]`,
        config: { 
          responseMimeType: "application/json", 
          responseSchema: { 
            type: Type.ARRAY, 
            items: { 
              type: Type.OBJECT, 
              properties: { 
                question: { type: Type.STRING }, 
                options: { type: Type.ARRAY, items: { type: Type.STRING } }, 
                answer: { type: Type.INTEGER }, 
                explanation: { type: Type.STRING } 
              }, 
              propertyOrdering: ["question", "options", "answer", "explanation"] 
            } 
          } 
        }
      });
      
      const newQuestions = JSON.parse(response.text || "[]");
      setQuestions(prev => [...prev, ...newQuestions]);
      if (isInitial) {
        setStep('testing');
        setTimerActive(true);
      }
    } catch (error) { 
      console.error("Gemini API Error:", error);
      alert("AI 문제 생성에 실패했습니다. API 키가 올바른지 확인하거나 잠시 후 다시 시도해주세요."); 
      if (isInitial) setStep('ready');
    } finally { 
      setLoading(false); 
    }
  };

  useEffect(() => {
    let timer: any;
    if (timerActive && timeLeft > 0) {
      timer = setInterval(() => {
        setTimeLeft(prev => prev - 1);
      }, 1000);
    } else if (timeLeft === 0 && timerActive) {
      handleAnswer(-1);
    }
    return () => clearInterval(timer);
  }, [timerActive, timeLeft]);

  const handleAnswer = (ansIdx: number) => {
    const isCorrect = ansIdx === questions[currentIdx].answer;
    if (isCorrect) setCorrectCount(prev => prev + 1);
    setUserAnswers(prev => [...prev, ansIdx]);
    
    if (currentIdx < questions.length - 1) {
      setCurrentIdx(prev => prev + 1);
      setTimeLeft(20);
    } else {
      fetchMoreQuestions();
      setCurrentIdx(prev => prev + 1);
      setTimeLeft(20);
    }
  };

  if (loading) return (
    <div className="flex flex-col items-center justify-center py-32 space-y-8 animate-fadeIn">
      <div className="relative w-24 h-24">
        <div className="absolute inset-0 border-4 border-primary/20 rounded-full"></div>
        <div className="absolute inset-0 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        <div className="absolute inset-0 flex items-center justify-center text-2xl animate-pulse">🤖</div>
      </div>
      <div className="text-center space-y-2">
        <p className="text-xl font-black text-text-main">AI 역량 분석 시스템</p>
        <p className="text-text-sub font-medium px-4">{loadingMsg}</p>
      </div>
    </div>
  );

  if (step === 'category') return (
    <div className="max-w-4xl mx-auto space-y-12 animate-fadeIn py-10">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-black text-text-main tracking-tight">AI 실시간 역량 검증</h1>
        <p className="text-text-sub font-medium text-lg">AI가 실시간으로 문제를 생성하며, 풀수록 정교한 리포트가 완성됩니다.</p>
      </div>
      <div className="grid sm:grid-cols-3 md:grid-cols-5 gap-6">
        {TEST_CATEGORIES.map(cat => (
          <button key={cat.id} onClick={() => {setSelectedCat(cat); setStep('stack');}} className="group bg-white p-8 rounded-[2.5rem] border-2 border-transparent hover:border-primary hover:shadow-2xl transition-all text-left shadow-sm flex flex-col items-center text-center">
            <div className="text-5xl mb-4 group-hover:scale-110 transition-transform drop-shadow-sm">{cat.icon}</div>
            <h3 className="text-lg font-black mb-1 text-text-main">{cat.name}</h3>
            <p className="text-text-sub text-[8px] font-bold uppercase tracking-widest">Select Category</p>
          </button>
        ))}
      </div>
    </div>
  );

  if (step === 'stack' && selectedCat) return (
    <div className="max-w-4xl mx-auto space-y-10 animate-fadeIn py-10">
      <div className="flex items-center gap-4">
        <button onClick={() => setStep('category')} className="p-3 bg-white rounded-2xl shadow-sm hover:text-primary transition-colors">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" /></svg>
        </button>
        <h2 className="text-3xl font-black text-text-main">{selectedCat.name} 스택 선택</h2>
      </div>
      <div className="bg-white p-10 rounded-[3rem] shadow-xl border border-gray-100 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
        {selectedCat.stacks.map(stack => (
          <button 
            key={stack} 
            onClick={() => { setSelectedStack(stack); setStep('ready'); }} 
            className="p-4 rounded-2xl border-2 border-gray-50 bg-gray-50/50 hover:border-primary hover:bg-primary/5 hover:text-primary transition-all font-black text-sm flex flex-col items-center gap-3"
          >
            <img src={getStackLogoUrl(stack)} className="w-10 h-10 object-contain rounded-md" alt={stack} />
            {stack}
          </button>
        ))}
      </div>
    </div>
  );

  if (step === 'ready') return (
    <div className="max-w-xl mx-auto space-y-10 animate-fadeIn py-10 text-center">
      <div className="bg-white p-12 rounded-[3.5rem] shadow-xl border border-gray-100 space-y-8">
        <div className="flex flex-col items-center gap-4 mb-4">
           <img src={getStackLogoUrl(selectedStack)} className="w-24 h-24 object-contain rounded-xl shadow-lg" alt={selectedStack} />
           <h2 className="text-3xl font-black text-text-main">{selectedStack} 무제한 챌린지</h2>
        </div>
        <div className="bg-gray-50 p-6 rounded-2xl text-left space-y-3 border border-gray-100">
          <p className="text-sm font-bold text-text-main flex items-center gap-2">⏱️ 문항당 시간: <span className="text-primary">20초</span></p>
          <p className="text-sm font-bold text-text-main flex items-center gap-2">♾️ 문항 수: <span className="text-primary">무제한 (최소 5문항 권장)</span></p>
          <p className="text-xs font-medium text-text-sub italic">많이 풀수록 AI가 당신의 실력을 더 정교하게 파악하여 '고급' 등급을 부여할 확률이 높아집니다.</p>
        </div>
        <button onClick={() => fetchMoreQuestions(true)} className="w-full bg-primary text-white py-6 rounded-3xl font-black text-xl shadow-xl shadow-primary/20 hover:scale-[1.02] transition-all">검증 시작하기</button>
      </div>
    </div>
  );

  if (step === 'testing' && questions.length > 0 && currentIdx < questions.length) {
    const q = questions[currentIdx];
    const timerProgress = (timeLeft / 20) * 100;

    return (
      <div className="max-w-3xl mx-auto space-y-8 animate-fadeIn py-10">
        <div className="flex justify-between items-center bg-white px-8 py-4 rounded-full border border-gray-100 shadow-sm">
           <div className="flex items-center gap-4">
              <span className="text-[10px] font-black text-text-sub uppercase tracking-widest">Progress</span>
              <span className="text-lg font-black text-primary">{currentIdx + 1}번째 문제</span>
           </div>
           <div className="flex items-center gap-4">
              <span className="text-[10px] font-black text-text-sub uppercase tracking-widest">Correct</span>
              <span className="text-lg font-black text-secondary">{correctCount}</span>
           </div>
           <button 
             onClick={() => finishTest(correctCount, userAnswers.length)} 
             className="px-6 py-2 bg-red-50 text-red-500 rounded-full text-xs font-black border border-red-100 hover:bg-red-500 hover:text-white transition-all"
           >
             종료 및 결과 보기
           </button>
        </div>

        <div className="space-y-3">
          <div className="flex justify-between items-end px-2">
            <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Time</span>
            <span className={`text-xl font-black ${timeLeft <= 5 ? 'text-red-500 animate-pulse' : 'text-primary'}`}>
              00:{timeLeft < 10 ? `0${timeLeft}` : timeLeft}
            </span>
          </div>
          <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
            <div className={`h-full transition-all duration-1000 ${timeLeft <= 5 ? 'bg-red-500' : 'bg-primary'}`} style={{ width: `${timerProgress}%` }}></div>
          </div>
        </div>

        <div className="bg-white p-12 rounded-[3.5rem] shadow-2xl border border-gray-100 space-y-10">
          <h3 className="text-2xl font-black text-text-main leading-tight">Q. {q.question}</h3>
          <div className="grid gap-4">
            {q.options.map((opt, idx) => (
              <button 
                key={idx} 
                onClick={() => handleAnswer(idx)} 
                className="group flex items-center justify-between p-6 rounded-[2rem] border-2 border-gray-50 bg-gray-50/30 hover:border-primary hover:bg-primary/5 transition-all text-left"
              >
                <span className="font-bold text-text-main group-hover:text-primary">{opt}</span>
                <div className="w-6 h-6 rounded-full border-2 border-gray-200 group-hover:border-primary group-hover:bg-primary/10 transition-colors"></div>
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (step === 'result' && result) return (
    <div className="max-w-3xl mx-auto space-y-10 animate-fadeIn text-center py-10">
      <div className="bg-white p-12 rounded-[4rem] shadow-2xl border border-gray-100 space-y-10 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-4 bg-primary"></div>
        <div className="space-y-4">
          <div className="inline-block p-4 bg-primary/10 rounded-3xl mb-2"><span className="text-5xl">🏆</span></div>
          <h2 className="text-4xl font-black text-text-main">{selectedStack} 역량 리포트</h2>
          <p className="text-text-sub font-medium">테스트 데이터를 분석하여 최종 등급이 산정되었습니다.</p>
        </div>
        <div className="grid grid-cols-2 gap-6">
          <div className="p-8 bg-gray-50 rounded-[2.5rem] border border-gray-100">
            <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Total Score</p>
            <p className="text-5xl font-black text-primary">{result.score}<span className="text-xl">점</span></p>
          </div>
          <div className="p-8 bg-gray-50 rounded-[2.5rem] border border-gray-100">
            <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Determined Level</p>
            <p className="text-2xl font-black text-secondary">{result.level}</p>
          </div>
        </div>
        <div className="text-left p-10 bg-primary/5 rounded-[3rem] border border-primary/10 space-y-4">
          <div className="flex items-center gap-3"><span className="text-xl">💡</span><h4 className="text-lg font-black text-primary">AI 분석 총평</h4></div>
          <p className="text-text-main font-medium leading-relaxed text-lg italic">"{result.feedback}"</p>
        </div>
        <div className="flex gap-4 pt-4">
          <button onClick={() => setStep('category')} className="flex-1 bg-gray-100 py-5 rounded-3xl font-black text-text-sub transition-all hover:bg-gray-200">다른 테스트 하기</button>
          <button 
            onClick={() => window.location.href='/#/mypage?tab=test'} 
            className="flex-1 bg-primary text-white py-5 rounded-3xl font-black text-lg shadow-xl shadow-primary/20 hover:scale-105 transition-all"
          >
            내 성적표 보기
          </button>
        </div>
      </div>
    </div>
  );
  return null;
};

export default PreTestPage;
