// 섹터봇 - 메신저봇R (API2) 스크립트
// API_BASE를 배포된 앱 주소로 바꾸세요. 예: https://your-app.atoms.world
const API_BASE = "https://YOUR-APP-DOMAIN";
// 봇이 응답할 오픈채팅방 이름 (빈 배열이면 모든 방에서 응답)
const ROOMS = [];

const bot = BotManager.getCurrentBot();

bot.addListener(Event.MESSAGE, function (msg) {
  const text = (msg.content || "").trim();
  if (text.length < 2 || text.charAt(0) !== "/") return;
  if (ROOMS.length > 0 && ROOMS.indexOf(msg.room) === -1) return;
  try {
    const url = API_BASE + "/api/v1/kakao/search?q=" + encodeURIComponent(text);
    const body = org.jsoup.Jsoup.connect(url)
      .ignoreContentType(true)
      .timeout(5000)
      .execute()
      .body();
    msg.reply(JSON.parse(body).text);
  } catch (e) {
    msg.reply("조회 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.");
  }
});
