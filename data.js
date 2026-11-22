/* ============================================================
   PLAY GAME 公式サイト：内容データ
   イベント名・日程・結果・お知らせ・URLはここだけ書き換えればOK
   url が空 "" のものは「準備中」と表示されます
   ============================================================ */
window.SITE = {
  // ---- Googleシート連携（GitHub Pages で公開したとき使われます）----
  // id: シートURLの /d/ と /edit の間の文字列。空ならこのファイルの内容を表示
  sheet: { id: "1LB24cc6LTDr2vjWspo_GD8tI6QsYJ1Y7x2V4LCLdo_0", tabs: { events: "イベント", news: "お知らせ", archive: "過去のイベント" } },
  updated: "2026.11.22",
  about: [
    "PG（プレイゲーム / PLAY GAME）は、ゲームイベントの企画・運営・参加が気軽にできるコミュニティサーバーです。",
    "毎月のメインイベント（大会や企画）と、もっと気軽な小規模イベントを開催しています。告知はXから。"
  ],
  tags: ["VALORANT", "Overwatch 2", "Apex Legends", "Minecraft", "毎月イベント"],

  // ---- イベント情報（月ごとに表示）----
  // date: 日時 / name: 名前 / detail: 詳細 / note: 備考（ルールなど・空なら非表示）
  // links: 備考に出すボタン 例 [{ label: "くわしく", url: "https://..." }]
  // d: 日付（YYYY-MM-DD）を入れたイベントは NEXT の判定に使われます
  // confirmed: true にすると「確定前」の表示が消えます（未記入は確定前）
  // ↓ 詳細ページ用（あるものだけ表示）
  // status: 募集状況（募集前 / 募集中 / 締切 / 開催終了 / 調整中）
  // period: 募集期間 / capacity: 定員 / conditions: 応募条件（リスト）
  // apply: 参加方法 / rules: ルール（リスト）
  events: [
    { month: "2027-01", d: "2027-01-23", date: "2027/1/23（土）", type: "メイン", game: "", name: "イベント名未定", detail: "未定", note: "", status: "調整中", period: "未定", capacity: "未定", conditions: ["未定"], apply: "未定", links: [] },
    { month: "2027-01", d: "", date: "1月中（日程調整中）", type: "小規模", game: "", name: "イベント名未定", detail: "未定", note: "", status: "調整中", period: "未定", capacity: "未定", conditions: ["未定"], apply: "未定", links: [] },
    { month: "2027-02", d: "2027-02-27", date: "2027/2/27（土）", type: "メイン", game: "", name: "イベント名未定", detail: "未定", note: "", status: "調整中", period: "未定", capacity: "未定", conditions: ["未定"], apply: "未定", links: [] },
    { month: "2027-02", d: "", date: "2月中（日程調整中）", type: "小規模", game: "", name: "イベント名未定", detail: "未定", note: "", status: "調整中", period: "未定", capacity: "未定", conditions: ["未定"], apply: "未定", links: [] },
    { month: "2027-03", d: "2027-03-27", date: "2027/3/27（土）", type: "メイン", game: "", name: "イベント名未定", detail: "未定", note: "", status: "調整中", period: "未定", capacity: "未定", conditions: ["未定"], apply: "未定", links: [] },
    { month: "2027-03", d: "", date: "3月中（日程調整中）", type: "小規模", game: "", name: "イベント名未定", detail: "未定", note: "", status: "調整中", period: "未定", capacity: "未定", conditions: ["未定"], apply: "未定", links: [] },
    { month: "2027-04", d: "2027-04-24", date: "2027/4/24（土）", type: "メイン", game: "", name: "イベント名未定", detail: "未定", note: "", status: "調整中", period: "未定", capacity: "未定", conditions: ["未定"], apply: "未定", links: [] },
    { month: "2027-04", d: "", date: "4月中（日程調整中）", type: "小規模", game: "", name: "イベント名未定", detail: "未定", note: "", status: "調整中", period: "未定", capacity: "未定", conditions: ["未定"], apply: "未定", links: [] },
    { month: "2027-05", d: "2027-05-22", date: "2027/5/22（土）", type: "メイン", game: "", name: "イベント名未定", detail: "未定", note: "", status: "調整中", period: "未定", capacity: "未定", conditions: ["未定"], apply: "未定", links: [] },
    { month: "2027-05", d: "", date: "5月中（日程調整中）", type: "小規模", game: "", name: "イベント名未定", detail: "未定", note: "", status: "調整中", period: "未定", capacity: "未定", conditions: ["未定"], apply: "未定", links: [] },
    { month: "2027-06", d: "2027-06-26", date: "2027/6/26（土）", type: "メイン", game: "", name: "イベント名未定", detail: "未定", note: "", status: "調整中", period: "未定", capacity: "未定", conditions: ["未定"], apply: "未定", links: [] },
    { month: "2027-06", d: "", date: "6月中（日程調整中）", type: "小規模", game: "", name: "イベント名未定", detail: "未定", note: "", status: "調整中", period: "未定", capacity: "未定", conditions: ["未定"], apply: "未定", links: [] },
    { month: "2027-07", d: "2027-07-24", date: "2027/7/24（土）", type: "メイン", game: "", name: "イベント名未定", detail: "未定", note: "", status: "調整中", period: "未定", capacity: "未定", conditions: ["未定"], apply: "未定", links: [] },
    { month: "2027-07", d: "", date: "7月中（日程調整中）", type: "小規模", game: "", name: "イベント名未定", detail: "未定", note: "", status: "調整中", period: "未定", capacity: "未定", conditions: ["未定"], apply: "未定", links: [] },
    { month: "2027-08", d: "2027-08-28", date: "2027/8/28（土）", type: "メイン", game: "", name: "イベント名未定", detail: "未定", note: "", status: "調整中", period: "未定", capacity: "未定", conditions: ["未定"], apply: "未定", links: [] },
    { month: "2027-08", d: "", date: "8月中（日程調整中）", type: "小規模", game: "", name: "イベント名未定", detail: "未定", note: "", status: "調整中", period: "未定", capacity: "未定", conditions: ["未定"], apply: "未定", links: [] },
    { month: "2027-09", d: "2027-09-25", date: "2027/9/25（土）", type: "メイン", game: "", name: "イベント名未定", detail: "未定", note: "", status: "調整中", period: "未定", capacity: "未定", conditions: ["未定"], apply: "未定", links: [] },
    { month: "2027-09", d: "", date: "9月中（日程調整中）", type: "小規模", game: "", name: "イベント名未定", detail: "未定", note: "", status: "調整中", period: "未定", capacity: "未定", conditions: ["未定"], apply: "未定", links: [] },
    { month: "2027-10", d: "2027-10-23", date: "2027/10/23（土）", type: "メイン", game: "", name: "イベント名未定", detail: "未定", note: "", status: "調整中", period: "未定", capacity: "未定", conditions: ["未定"], apply: "未定", links: [] },
    { month: "2027-10", d: "", date: "10月中（日程調整中）", type: "小規模", game: "", name: "イベント名未定", detail: "未定", note: "", status: "調整中", period: "未定", capacity: "未定", conditions: ["未定"], apply: "未定", links: [] },
    { month: "2027-11", d: "2027-11-27", date: "2027/11/27（土）", type: "メイン", game: "", name: "イベント名未定", detail: "未定", note: "", status: "調整中", period: "未定", capacity: "未定", conditions: ["未定"], apply: "未定", links: [] },
    { month: "2027-11", d: "", date: "11月中（日程調整中）", type: "小規模", game: "", name: "イベント名未定", detail: "未定", note: "", status: "調整中", period: "未定", capacity: "未定", conditions: ["未定"], apply: "未定", links: [] },
    { month: "2027-12", d: "2027-12-18", date: "2027/12/18（土）", type: "メイン", game: "", name: "イベント名未定", detail: "未定", note: "", status: "調整中", period: "未定", capacity: "未定", conditions: ["未定"], apply: "未定", links: [] },
    { month: "2027-12", d: "", date: "12月中（日程調整中）", type: "小規模", game: "", name: "イベント名未定", detail: "未定", note: "", status: "調整中", period: "未定", capacity: "未定", conditions: ["未定"], apply: "未定", links: [] },
  ],

  // ---- 過去のイベント（終わったら足していく）----
  archive: [
    /* 例:
    { name: "PROFLUX CUP 01", date: "2027.01.23", game: "VALORANT",
      results: [["優勝","チーム名"],["準優勝","チーム名"],["3位","チーム名"]],
      note: "参加 8チーム", url: "" },
    */
  ],

  news: [
    { date: "2026.11.22", tag: "予定", title: "2027年のイベント日程（仮）を公開しました。内容は決まり次第お知らせします", url: "" },
    { date: "2026.11.22", tag: "サイト", title: "PLAY GAME 公式サイトを公開しました", url: "" }
  ],
  links: {
    discord: { title: "Discordサーバー", sub: "プレイゲームに参加する", url: "https://discord.gg/8S9cybdeA7" },
    x:       { title: "主催のX", sub: "@7x_x7x_x7・告知と最新情報", url: "https://x.com/7x_x7x_x7" }
  }
};
