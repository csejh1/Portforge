
export interface QuestionItem {
    question: string;
    options: string[];
    answer: number;
}

export interface QuestionResponse {
    questions: QuestionItem[];
}

export interface TestResultAnalysis {
    score: number;
    stack: string;
    level: string;
    feedback: string;
    date: string;
}

export const fetchQuestions = async (stack: string, difficulty: string = '초급'): Promise<QuestionItem[]> => {
    try {
        const response = await fetch('/ai/test/questions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ stack, difficulty, count: 5 })
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || 'Failed to fetch questions');
        }

        const data: QuestionResponse = await response.json();
        return data.questions;
    } catch (error) {
        console.error("AI API Error:", error);
        throw error;
    }
};

export const analyzeResults = async (userId: string, stack: string, total: number, correct: number, score: number, wrong_answers: string[] = []): Promise<TestResultAnalysis> => {
    try {
        const response = await fetch('/ai/test/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, stack, total_questions: total, correct_count: correct, score, wrong_answers })
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || 'Failed to analyze results');
        }

        return await response.json();
    } catch (error) {
        console.error("AI Analysis Error:", error);
        throw error;
    }
};

export const fetchUserTestResult = async (userId: string): Promise<TestResultAnalysis | null> => {
    try {
        const response = await fetch(`/ai/test/result/${userId}`);
        if (response.status === 404) return null;
        if (!response.ok) throw new Error('Failed to fetch user test result');
        return await response.json();
    } catch (e) {
        console.error("AI Fetch Error:", e);
        return null;
    }
};

// 사용자의 모든 테스트 결과 조회
export const fetchUserTestResults = async (userId: string): Promise<TestResultAnalysis[]> => {
    try {
        const response = await fetch(`/ai/data/test-results/user/${userId}`);
        if (response.status === 404) return [];
        if (!response.ok) throw new Error('Failed to fetch user test results');
        const data = await response.json();
        return data.map((r: any) => ({
            score: r.score,
            stack: r.test_type || 'Unknown',
            level: r.score >= 80 ? '고급' : r.score >= 60 ? '중급' : '초급',
            feedback: r.feedback || '',
            date: r.created_at ? new Date(r.created_at).toLocaleDateString() : new Date().toLocaleDateString()
        }));
    } catch (e) {
        console.error("AI Fetch Error:", e);
        return [];
    }
};

export interface ApplicantData {
    name: string;
    position: string;
    message: string;
    score?: number;
    feedback?: string;
}

export const analyzeApplicants = async (applicants: ApplicantData[]): Promise<string> => {
    try {
        const response = await fetch('/ai/recruit/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ applicants })
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Failed to analyze applicants');
        }
        const data = await response.json();
        return data.analysis;
    } catch (e) {
        console.error("AI Applicant Analysis Error:", e);
        throw e;
    }
};
export interface PortfolioResult {
    role: string;
    period: string;
    stack: string;
    contributions: { category: string; text: string }[];
    aiAnalysis: string;
}

export const generatePortfolio = async (userId: string, projectId: number): Promise<PortfolioResult> => {
    try {
        const response = await fetch('/ai/portfolio/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, project_id: projectId })
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Failed to generate portfolio');
        }
        const data = await response.json();
        return data.result;
    } catch (e) {
        console.error("Portfolio Generation Error:", e);
        throw e;
    }
};
