
import React, { useState, useRef, useEffect } from 'react';
import { useAuth, User, TestResult } from '../contexts/AuthContext';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { STACK_CATEGORIES_BASE, getStackLogoUrl } from './HomePage';

const MyPage: React.FC = () => {
  const { user, projects, updateProfile, changePassword } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const queryParams = new URLSearchParams(location.search);
  const initialTab = (queryParams.get('tab') as any) || 'profile';
  const [activeTab, setActiveTab] = useState<'profile' | 'teams' | 'test' | 'security'>(initialTab);

  useEffect(() => {
    if (queryParams.get('tab')) {
      setActiveTab(queryParams.get('tab') as any);
    }
  }, [location.search]);

  if (!user) { navigate('/login'); return null; }

  const handleAvatarClick = () => fileInputRef.current?.click();
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => updateProfile({ avatarUrl: reader.result as string });
      reader.readAsDataURL(file);
    }
  };

  const avatarSrc = user.avatarUrl || `https://api.dicebear.com/7.x/avataaars/svg?seed=${user.id}`;

  return (
    <div className="max-w-6xl mx-auto py-8 flex flex-col lg:flex-row gap-8 animate-fadeIn">
      <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" />

      <aside className="lg:w-1/4 space-y-6">
        <div className="bg-white p-8 rounded-[3rem] shadow-sm border border-gray-100 text-center relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-2 bg-primary"></div>
          <div className="relative w-32 h-32 mx-auto mb-4 group cursor-pointer" onClick={handleAvatarClick}>
            <img src={avatarSrc} className="w-full h-full rounded-full border-4 border-primary/10 shadow-lg object-cover" alt="avatar" />
            <div className="absolute inset-0 bg-black/40 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
              <span className="text-white text-xs font-black">EDIT</span>
            </div>
          </div>
          <h2 className="text-2xl font-black">{user.name}</h2>
          <p className="text-primary text-[10px] font-black uppercase tracking-[0.2em] mt-1">{user.role}</p>
        </div>

        <nav className="bg-white p-4 rounded-[2.5rem] shadow-sm border border-gray-100 space-y-1">
          <MenuBtn active={activeTab === 'profile'} onClick={() => setActiveTab('profile')} label="내 프로필" icon="👤" />
          <MenuBtn active={activeTab === 'test'} onClick={() => setActiveTab('test')} label="테스트 결과" icon="🏆" />
          <MenuBtn active={activeTab === 'teams'} onClick={() => setActiveTab('teams')} label="참여 팀 / 지원현황" icon="🚀" />
          <MenuBtn active={activeTab === 'security'} onClick={() => setActiveTab('security')} label="계정 및 보안" icon="🔒" />
        </nav>
      </aside>

      <main className="flex-1">
        <div className="bg-white p-12 rounded-[3.5rem] shadow-sm border border-gray-100 min-h-[600px]">
          {activeTab === 'profile' && <ProfileEditor user={user} updateProfile={updateProfile} />}
          {activeTab === 'test' && <TestResultSection testResults={user.testResults || []} />}
          {activeTab === 'teams' && <TeamSection user={user} projects={projects} />}
          {activeTab === 'security' && <SecuritySection changePassword={changePassword} />}
        </div>
      </main>
    </div>
  );
};

const ProfileEditor = ({ user, updateProfile }: any) => {
  const { validateName } = useAuth();
  const [name, setName] = useState(user.name);
  const [myStacks, setMyStacks] = useState<string[]>(user.myStacks || []);
  const [stackInput, setStackInput] = useState('');
  const [nameError, setNameError] = useState('');

  const addStack = (stack: string) => {
    if (!myStacks.includes(stack)) {
      setMyStacks([...myStacks, stack]);
    }
    setStackInput('');
  };

  const removeStack = (stack: string) => {
    setMyStacks(myStacks.filter(s => s !== stack));
  };

  const allStacks = Object.values(STACK_CATEGORIES_BASE).flat() as string[];
  const filteredSuggestions = stackInput
    ? [...new Set(allStacks)].filter(s => s.toLowerCase().includes(stackInput.toLowerCase()) && !myStacks.includes(s)).slice(0, 5)
    : [];

  const handleSave = async () => {
    const v = validateName(name);
    if (!v.available) {
      setNameError(v.message);
      return;
    }
    try {
      await updateProfile({ name, myStacks });
      alert('프로필이 저장되었습니다.');
      setNameError('');
    } catch (e: any) {
      setNameError(e.message);
    }
  };

  return (
    <div className="space-y-10 animate-fadeIn">
      <h3 className="text-3xl font-black">기본 정보 편집</h3>
      <div className="space-y-8">
        <InputField label="활동 닉네임" value={name} onChange={(val: string) => { setName(val); setNameError(''); }} />
        <div className="space-y-4">
          <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">보유 기술 스택</label>
          <div className="flex flex-wrap gap-2">
            {myStacks.map((s: string) => (
              <span key={s} className="flex items-center gap-2 px-4 py-2 bg-primary/10 border border-primary/20 rounded-xl text-xs font-bold text-primary">
                {s}
                <button onClick={() => removeStack(s)}>✕</button>
              </span>
            ))}
          </div>
          <div className="relative">
            <input
              type="text"
              value={stackInput}
              onChange={(e) => setStackInput(e.target.value)}
              className="w-full bg-gray-50 p-5 rounded-2xl border-none outline-none focus:ring-2 focus:ring-primary/20 font-bold text-sm"
              placeholder="기술 스택 검색"
            />
            {filteredSuggestions.length > 0 && (
              <div className="absolute top-full left-0 w-full mt-2 bg-white border border-gray-100 rounded-2xl shadow-xl z-10 overflow-hidden">
                {filteredSuggestions.map(s => (
                  <button key={s} onClick={() => addStack(s)} className="w-full text-left px-6 py-3 hover:bg-gray-50 font-bold text-sm text-text-sub flex items-center gap-3">
                    <img src={getStackLogoUrl(s)} className="w-5 h-5 object-contain" alt={s} />
                    {s}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
      <button onClick={handleSave} className="bg-primary text-white px-10 py-4 rounded-2xl font-black shadow-lg shadow-primary/20 hover:scale-105 transition-all">저장하기</button>
    </div>
  );
};

const TeamSection = ({ user, projects }: { user: User, projects: any[] }) => {
  const [userProjects, setUserProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // 백엔드에서 사용자 프로젝트 목록 로드 (실패 시 정적 데이터 사용)
  useEffect(() => {
    // 로컬 데이터 사용 (fallback)
    const useLocalData = () => {
      console.log('📂 로컬 데이터 사용');
      // user.appliedProjects와 projects를 매칭하여 표시
      const appliedProjects = user.appliedProjects || [];
      console.log('📂 appliedProjects:', appliedProjects);

      // appliedProjects가 없으면 빈 배열로 표시
      if (appliedProjects.length === 0) {
        setUserProjects([]);
        setLoading(false);
        return;
      }

      const matchedProjects = appliedProjects.map((ap: any) => {
        // projects에서 찾거나, appliedProject 자체 데이터 사용
        const project = projects.find(p => p.id === ap.id);
        return {
          id: ap.id,
          title: project?.title || ap.projectTitle || `프로젝트 #${ap.id}`,
          userRole: ap.userRole,
          selectedPosition: ap.selectedPosition || (ap.userRole === 'Leader' ? '팀장 / PM' : '포지션 미정'),
          status: ap.status,
          tech_stacks: project?.tags || []
        };
      });

      setUserProjects(matchedProjects);
      setLoading(false);
    };

    const loadUserProjects = async () => {
      if (!user?.id) {
        setLoading(false);
        return;
      }

      try {
        console.log('🔄 사용자 프로젝트 목록 로드 중...');
        const response = await fetch(`/api/v1/integration/user-projects/${user.id}`);

        if (response.ok) {
          const result = await response.json();
          if (result.status === 'success' && result.data && result.data.length > 0) {
            console.log('✅ 사용자 프로젝트 목록 로드 성공:', result.data);

            // 백엔드 데이터를 프론트엔드 형식으로 변환
            const transformedProjects = result.data.map((project: any) => ({
              id: project.id,
              title: project.title,
              userRole: project.userRole === 'LEADER' ? 'Leader' : project.userRole === 'APPLICANT' ? 'Applicant' : 'Member',
              selectedPosition: project.position || (project.userRole === 'LEADER' ? '팀장' : '포지션 정보 없음'),
              status: project.status === '승인됨' ? 'accepted' :
                project.status === '거절됨' ? 'rejected' :
                  project.status === '심사중' ? 'pending' : 'accepted',
              tech_stacks: Array.isArray(project.tags) ? project.tags : [],
              applicationStatus: project.applicationStatus || null
            }));

            setUserProjects(transformedProjects);
            setLoading(false);
            return;
          }
        }

        // 백엔드 실패 시 로컬 데이터 사용
        console.log('⚠️ 백엔드 연결 실패, 로컬 데이터 사용');
        useLocalData();
      } catch (error) {
        console.error('❌ 사용자 프로젝트 로드 실패:', error);
        useLocalData();
      }
    };

    loadUserProjects();
  }, [user?.id, user?.appliedProjects, projects]);

  if (loading) {
    return (
      <div className="space-y-10 animate-fadeIn">
        <h3 className="text-3xl font-black">참여 중인 팀 및 지원 현황</h3>
        <div className="text-center py-20 text-gray-400">
          <p className="text-2xl mb-2">⏳</p>
          <p>프로젝트 목록을 불러오는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-10 animate-fadeIn">
      <h3 className="text-3xl font-black">참여 중인 팀 및 지원 현황</h3>
      <div className="grid gap-6">
        {userProjects.length > 0 ? userProjects.map(p => (
          <div key={p.id} className="p-8 border border-gray-100 rounded-[2.5rem] hover:bg-gray-50/50 transition-colors shadow-sm">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6">
              <div className="space-y-2">
                <div className="flex gap-2">
                  <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${p.userRole === 'Leader' ? 'bg-amber-100 text-amber-600' :
                    p.userRole === 'Applicant' ? 'bg-blue-100 text-blue-600' :
                      'bg-gray-100 text-gray-500'
                    }`}>
                    {p.userRole === 'Leader' ? '👑 리더' : p.userRole === 'Applicant' ? '📝 지원자' : '👤 멤버'}
                  </span>
                  <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${p.status === 'accepted' ? 'bg-primary/10 text-primary' :
                    p.status === 'rejected' ? 'bg-red-50 text-red-500' :
                      'bg-yellow-50 text-yellow-500'
                    }`}>
                    {p.status === 'accepted' ? '승인됨' : p.status === 'rejected' ? '거절됨' : '심사중'}
                  </span>
                </div>
                <h4 className="text-xl font-black text-text-main leading-tight">{p.title}</h4>
                <p className="text-xs text-text-sub font-bold">{p.selectedPosition || (p.userRole === 'Leader' ? '팀 관리' : '포지션 미정')}</p>
                {p.tech_stacks && p.tech_stacks.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {p.tech_stacks.slice(0, 3).map((tech: string, idx: number) => (
                      <span key={idx} className="text-[10px] bg-primary/5 text-primary px-2 py-0.5 rounded font-bold">
                        {tech}
                      </span>
                    ))}
                    {p.tech_stacks.length > 3 && (
                      <span className="text-[10px] text-gray-400 px-2 py-0.5">+{p.tech_stacks.length - 3}</span>
                    )}
                  </div>
                )}
              </div>
              <Link to={`/projects/${p.id}`} className="bg-primary text-white px-6 py-3 rounded-2xl text-xs font-black shadow-lg shadow-primary/10 whitespace-nowrap hover:scale-105 transition-all">
                프로젝트 보기 →
              </Link>
            </div>

            {/* 승인된 프로젝트에만 업무 현황 및 파일 공유 바로가기 표시 */}
            {p.status === 'accepted' && (
              <div className="mt-6 pt-6 border-t border-gray-100">
                <div className="flex flex-wrap gap-3">
                  <Link
                    to={`/team-space/${p.id}?tab=jira`}
                    className="flex items-center gap-2 px-4 py-2.5 bg-blue-50 text-blue-600 rounded-xl text-xs font-bold hover:bg-blue-100 transition-colors"
                  >
                    <span>📋</span> 업무 현황
                  </Link>
                  <Link
                    to={`/team-space/${p.id}?tab=files`}
                    className="flex items-center gap-2 px-4 py-2.5 bg-green-50 text-green-600 rounded-xl text-xs font-bold hover:bg-green-100 transition-colors"
                  >
                    <span>📁</span> 파일 공유
                  </Link>
                  <Link
                    to={`/team-space/${p.id}?tab=chat`}
                    className="flex items-center gap-2 px-4 py-2.5 bg-purple-50 text-purple-600 rounded-xl text-xs font-bold hover:bg-purple-100 transition-colors"
                  >
                    <span>💬</span> 팀 채팅
                  </Link>
                  <Link
                    to={`/team-space/${p.id}?tab=meetings`}
                    className="flex items-center gap-2 px-4 py-2.5 bg-amber-50 text-amber-600 rounded-xl text-xs font-bold hover:bg-amber-100 transition-colors"
                  >
                    <span>📄</span> 회의록
                  </Link>
                </div>
              </div>
            )}
          </div>
        )) : (
          <div className="py-20 text-center opacity-40">참여 중인 팀이 없습니다.</div>
        )}
      </div>
    </div>
  );
};

const TestResultSection = ({ testResults }: { testResults: TestResult[] }) => (
  <div className="space-y-10 animate-fadeIn">
    <h3 className="text-3xl font-black">AI 역량 테스트 결과</h3>
    <div className="grid gap-6">
      {testResults.length > 0 ? testResults.map((result, idx) => (
        <div key={idx} className="bg-gray-50/50 p-6 rounded-[2.5rem] border border-gray-100 flex flex-col gap-6">
          <div className="flex justify-between items-center border-b border-gray-100 pb-4">
            <div>
              <span className="text-xs font-black text-primary bg-primary/10 px-3 py-1 rounded-full">{result.skill}</span>
              <span className="ml-3 text-xs text-text-sub font-bold">{result.date}</span>
            </div>
            <div className="text-lg font-black text-text-main">
              {result.score}점 <span className="text-sm font-medium text-gray-400">({result.level})</span>
            </div>
          </div>

          <div className="space-y-4">
            {(() => {
              try {
                const data = JSON.parse(result.feedback);
                return (
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="bg-white p-5 rounded-2xl shadow-sm border border-indigo-50/50">
                      <strong className="block text-indigo-600 mb-2 flex items-center gap-2 text-sm">
                        <span>📊</span> 강점 및 보완점
                      </strong>
                      <p className="text-sm text-text-main leading-relaxed whitespace-pre-wrap">{data.summary}</p>
                    </div>
                    <div className="bg-white p-5 rounded-2xl shadow-sm border border-emerald-50/50">
                      <strong className="block text-emerald-600 mb-2 flex items-center gap-2 text-sm">
                        <span>🌱</span> 성장 가이드
                      </strong>
                      <p className="text-sm text-text-main leading-relaxed whitespace-pre-wrap">{data.growth_guide}</p>
                    </div>
                  </div>
                );
              } catch {
                return <p className="text-sm text-text-sub leading-relaxed whitespace-pre-wrap bg-white p-4 rounded-xl">"{result.feedback}"</p>;
              }
            })()}
          </div>
        </div>
      )) : <div className="py-20 text-center opacity-40">테스트 내역이 없습니다.</div>}
    </div>
  </div>
);

const SecuritySection = ({ changePassword }: any) => {
  const [oldPw, setOldPw] = useState('');
  const [newPw, setNewPw] = useState('');
  const handlePwChange = async () => {
    try {
      await changePassword(oldPw, newPw);
      alert('비밀번호가 변경되었습니다.');
      setOldPw(''); setNewPw('');
    } catch (e: any) {
      alert(e.message || '오류가 발생했습니다.');
    }
  };
  return (
    <div className="space-y-12 animate-fadeIn">
      <h3 className="text-3xl font-black">계정 및 보안</h3>
      <div className="max-w-md space-y-6">
        <InputField label="현재 비밀번호" type="password" value={oldPw} onChange={setOldPw} />
        <InputField label="새 비밀번호" type="password" value={newPw} onChange={setNewPw} />
        <button onClick={handlePwChange} className="w-full bg-text-main text-white py-4 rounded-2xl font-black shadow-xl">비밀번호 변경하기</button>
      </div>
    </div>
  );
};

const InputField = ({ label, value, onChange, type = "text" }: any) => (
  <div className="space-y-2">
    <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">{label}</label>
    <input type={type} value={value} onChange={e => onChange(e.target.value)} className="w-full bg-gray-50 p-5 rounded-2xl border-none outline-none focus:ring-2 focus:ring-primary/20 font-bold" />
  </div>
);

const MenuBtn = ({ active, onClick, label, icon }: any) => (
  <button onClick={onClick} className={`w-full text-left px-8 py-5 rounded-2xl font-bold transition-all flex items-center gap-4 ${active ? 'bg-primary text-white shadow-lg' : 'text-text-secondary hover:bg-gray-50'}`}>
    <span className="text-xl">{icon}</span> <span>{label}</span>
  </button>
);

export default MyPage;
