import { useEffect, useRef, useState } from 'react';
import { createClient } from '@metagptx/web-sdk';
import { Copy, Send, TrendingUp } from 'lucide-react';
import { toast } from 'sonner';

const client = createClient();

type Msg = { from: 'user' | 'bot'; text: string; error?: boolean };

const SKILL_URL = `${window.location.origin}/api/v1/kakao/skill`;

const STEPS = [
  '카카오톡 채널을 만들고 카카오 i 오픈빌더(chatbot.kakao.com)에서 봇을 생성합니다.',
  '[스킬] 메뉴에서 새 스킬을 만들고 아래 URL을 입력합니다. (먼저 Publish로 배포한 뒤, 배포된 도메인 주소를 사용하세요.)',
  '[시나리오] → 폴백 블록(또는 "/"로 시작하는 발화를 받는 블록)의 봇 응답을 "스킬데이터 사용"으로 바꾸고, 위에서 만든 스킬을 연결합니다.',
  '[배포]를 누르고 봇을 카카오톡 채널에 연결하면, 채팅창에서 /삼성전자 처럼 검색할 수 있습니다.',
];

const OPEN_CHAT_STEPS = [
  '앱을 Publish로 배포합니다. 배포 후에는 배포된 주소에서 스크립트를 복사하세요.',
  '남는 안드로이드폰에 봇 전용 카카오 계정으로 로그인하고, 그 계정으로 오픈채팅방에 참여합니다.',
  '메신저봇R 앱을 설치한 뒤 알림 접근 권한을 허용하고, 새 봇(API2)을 만듭니다.',
  '아래 스크립트를 붙여 넣고 컴파일한 뒤 봇을 켭니다. 방에서 /삼성전자 를 입력하면 응답합니다.',
];

export default function Index() {
  const [msgs, setMsgs] = useState<Msg[]>([
    { from: 'bot', text: '안녕하세요! /종목명 을 입력하면 업종과 섹터를 알려드려요.\n예: /삼성전자, /에코프로, /005930' },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => endRef.current?.scrollIntoView({ behavior: 'smooth' }), [msgs, loading]);

  const send = async () => {
    const q = input.trim();
    if (!q || loading) return;
    setMsgs((m) => [...m, { from: 'user', text: q }]);
    setInput('');
    setLoading(true);
    try {
      const res = await client.apiCall.invoke({ url: '/api/v1/kakao/search', method: 'GET', data: { q } });
      setMsgs((m) => [...m, { from: 'bot', text: res.data.text }]);
    } catch (e: any) {
      setMsgs((m) => [...m, { from: 'bot', text: e?.data?.detail || e?.message || '조회에 실패했습니다.', error: true }]);
    } finally {
      setLoading(false);
    }
  };

  const copy = () => {
    navigator.clipboard.writeText(SKILL_URL).then(() => toast.success('스킬 URL을 복사했습니다.'));
  };

  const copyScript = async () => {
    try {
      const text = await (await fetch('/messengerbot.js')).text();
      await navigator.clipboard.writeText(text.replace('https://YOUR-APP-DOMAIN', window.location.origin));
      toast.success('현재 주소가 들어간 스크립트를 복사했습니다.');
    } catch {
      toast.error('복사하지 못했습니다. 스크립트를 다운로드해 주세요.');
    }
  };

  return (
    <div className="min-h-screen bg-[#F4F5F7] text-[#191919]" style={{ fontFamily: 'Pretendard, system-ui, sans-serif' }}>
      <header className="mx-auto flex max-w-[1120px] items-center gap-2 px-5 py-6">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#FEE500]">
          <TrendingUp className="h-5 w-5" />
        </div>
        <div>
          <h1 className="text-[28px] font-bold leading-tight">섹터봇</h1>
          <p className="text-sm text-[#5F6368]">카카오톡에서 /종목명 으로 업종·섹터 조회</p>
        </div>
      </header>

      <main className="mx-auto grid max-w-[1120px] gap-6 px-5 pb-10 lg:grid-cols-[3fr_2fr]">
        <section aria-label="봇 테스트" className="flex h-[600px] flex-col overflow-hidden rounded-2xl bg-[#B2C7D9] shadow-sm">
          <div className="bg-[#A9BDCE] px-4 py-3 text-sm font-semibold">섹터봇 테스트 채팅</div>
          <div className="flex-1 space-y-3 overflow-y-auto p-4">
            {msgs.map((m, i) => (
              <div key={i} className={`flex ${m.from === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-[80%] whitespace-pre-line rounded-[14px] px-3.5 py-2.5 text-[15px] leading-normal shadow-sm ${
                    m.from === 'user' ? 'bg-[#FEE500]' : m.error ? 'bg-white text-[#D93025]' : 'bg-white'
                  }`}
                >
                  {m.text}
                </div>
              </div>
            ))}
            {loading && <div className="w-fit rounded-[14px] bg-white px-3.5 py-2.5">…</div>}
            <div ref={endRef} />
          </div>
          <form
            className="flex gap-2 bg-white p-3"
            onSubmit={(e) => {
              e.preventDefault();
              send();
            }}
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="/삼성전자"
              className="h-10 flex-1 rounded-full bg-[#F4F5F7] px-4 outline-none focus:ring-2 focus:ring-[#191919]"
            />
            <button
              type="submit"
              aria-label="전송"
              disabled={loading || !input.trim()}
              className="flex h-10 w-10 items-center justify-center rounded-full bg-[#FEE500] text-[#191919] disabled:opacity-50"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </section>

        <section className="rounded-2xl bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-bold">카카오톡 채널 연결 방법</h2>
          <ol className="space-y-3 text-[15px] leading-normal">
            {STEPS.map((s, i) => (
              <li key={i} className="flex gap-3">
                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[#FEE500] text-xs font-bold">{i + 1}</span>
                <span>{s}</span>
              </li>
            ))}
          </ol>
          <div className="mt-5">
            <p className="mb-1 text-sm font-semibold">스킬 서버 URL (POST)</p>
            <div className="flex items-center gap-2 rounded-xl bg-[#F4F5F7] p-3">
              <code className="flex-1 break-all text-xs">{SKILL_URL}</code>
              <button onClick={copy} aria-label="URL 복사" className="flex h-10 w-10 items-center justify-center rounded-full bg-[#191919] text-white">
                <Copy className="h-4 w-4" />
              </button>
            </div>
          </div>

          <h2 className="mb-3 mt-8 text-lg font-bold">오픈채팅방에서 쓰기 (메신저봇R)</h2>
          <p className="mb-3 text-sm text-[#5F6368]">
            오픈빌더 공식 챗봇은 오픈채팅방에 초대할 수 없습니다. 대신 봇 전용 카카오 계정을 안드로이드폰에 로그인하고, 메신저봇R 앱으로 자동응답을 설정합니다.
          </p>
          <ol className="space-y-3 text-[15px] leading-normal">
            {OPEN_CHAT_STEPS.map((s, i) => (
              <li key={i} className="flex gap-3">
                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[#FEE500] text-xs font-bold">{i + 1}</span>
                <span>{s}</span>
              </li>
            ))}
          </ol>
          <div className="mt-4 flex gap-2">
            <a href="/messengerbot.js" download className="flex h-10 items-center rounded-full bg-[#FEE500] px-4 text-sm font-semibold text-[#191919]">
              스크립트 다운로드
            </a>
            <button onClick={copyScript} className="h-10 rounded-full bg-[#191919] px-4 text-sm font-semibold text-white">
              스크립트 복사
            </button>
          </div>
          <p className="mt-3 text-xs text-[#D93025]">
            ※ 메신저봇R은 비공식 방식이라 카카오 계정이 제재될 수 있습니다. 반드시 봇 전용 계정을 사용하세요.
          </p>
        </section>
      </main>
    </div>
  );
}
