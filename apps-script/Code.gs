/**
 * PG イベント登録ページ（Google Apps Script）
 * スプレッドシート「イベント」タブに、改行つきでイベントを登録・編集するための専用ページです。
 *
 * ・ウェブアプリとして公開するときは「次のユーザーとして実行：ウェブアプリにアクセスしているユーザー」
 *   「アクセスできるユーザー：Google アカウントを持つ全員」にします。
 *   こうすると、そのシートを編集できる人だけが保存でき、ほかの人は保存できません。
 * ・「募集開始」「募集締切」の列は式で自動入力されるので、このページからは書き換えません。
 * ・画面（HTML）もこのファイルの最後に入っているので、貼り付けるのはこのファイル1つだけです。
 */
const SHEET_ID = '1LB24cc6LTDr2vjWspo_GD8tI6QsYJ1Y7x2V4LCLdo_0';
const TAB = 'イベント';
const HEADER_ROW = 2;
// このページから書く列（見出しの名前）。ここにない列（募集開始・募集締切など）は触りません。
const FIELDS = ['月', '日付', '日時', '種類', 'ゲーム', 'イベント名', '詳細', '確定', '募集状況', '募集期間', '定員',
  '応募条件', '参加方法', 'ルール', '備考', 'リンク名', 'リンクURL', '開始時刻', '配信URL', '参加サーバー'];
const AUTO = ['募集開始', '募集締切'];
const WEEK = ['日', '月', '火', '水', '木', '金', '土'];
const NEWS_TAB = 'お知らせ';

function doGet() {
  return HtmlService.createHtmlOutput(PAGE_HTML)
    .setTitle('PG イベント登録')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

function sheet_() {
  const sh = SpreadsheetApp.openById(SHEET_ID).getSheetByName(TAB);
  if (!sh) throw new Error('「' + TAB + '」シートが見つかりません');
  return sh;
}
function headers_(sh) {
  const head = sh.getRange(HEADER_ROW, 1, 1, sh.getLastColumn()).getDisplayValues()[0].map(String);
  const col = {};
  head.forEach((h, i) => { if (h.trim()) col[h.trim()] = i + 1; });
  const missing = FIELDS.concat(['イベント名']).filter((f) => !col[f]);
  if (missing.length) throw new Error('見出しが見つかりません：' + missing.join('、') + '（シートの見出しを変えていないか確認してください）');
  return col;
}

/** 登録済みのイベント一覧（編集用） */
function listEvents() {
  const sh = sheet_(), col = headers_(sh);
  const last = sh.getLastRow();
  if (last <= HEADER_ROW) return [];
  const values = sh.getRange(HEADER_ROW + 1, 1, last - HEADER_ROW, sh.getLastColumn()).getDisplayValues();
  const out = [];
  values.forEach((r, i) => {
    const get = (k) => (col[k] ? r[col[k] - 1] : '');
    if (!get('イベント名') && !get('月') && !get('日付')) return;
    const e = { row: HEADER_ROW + 1 + i };
    FIELDS.concat(AUTO).forEach((k) => { e[k] = get(k); });
    out.push(e);
  });
  return out;
}

/** 新しいイベントを足す、または row の行を書き換える。保存後の行（募集開始・締切の自動入力つき）を返す */
function saveEvent(input, row) {
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const sh = sheet_(), col = headers_(sh);
    const e = clean_(input);
    if (!e['イベント名']) throw new Error('イベント名を入れてください');
    if (!e['月']) throw new Error('日付か月を入れてください');
    const isNew = !row;
    if (!row) row = emptyRow_(sh, col);
    else if (row <= HEADER_ROW) throw new Error('行の指定が正しくありません');
    FIELDS.forEach((k) => {
      const cell = sh.getRange(row, col[k]);
      cell.setNumberFormat('@'); // 日付や時刻が勝手に変換されないよう文字として入れる
      cell.setValue(e[k] || '');
    });
    SpreadsheetApp.flush();
    // HPの「お知らせ」にも載せる（ページでチェックが入っているときだけ）
    let news = '';
    const want = String((input && input.__news) || '');
    if (want === 'new' || want === 'update') news = addNews_(e, want === 'new' && isNew ? '公開' : '更新');
    return { row: row, news: news, saved: listEvents().find((x) => x.row === row) };
  } catch (err) {
    throw new Error(friendly_(err));
  } finally {
    lock.releaseLock();
  }
}

/** row の行の内容を消す（募集開始・締切の式は残す） */
function deleteEvent(row) {
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const sh = sheet_(), col = headers_(sh);
    if (!row || row <= HEADER_ROW) throw new Error('行の指定が正しくありません');
    FIELDS.forEach((k) => sh.getRange(row, col[k]).setValue(''));
    return true;
  } catch (err) {
    throw new Error(friendly_(err));
  } finally {
    lock.releaseLock();
  }
}

/** 「お知らせ」シートの一番上（見出しのすぐ下）に1行足す。足したタイトルを返す */
function addNews_(e, kind) {
  const sh = SpreadsheetApp.openById(SHEET_ID).getSheetByName(NEWS_TAB);
  if (!sh) return '';
  const date = Utilities.formatDate(new Date(), 'Asia/Tokyo', 'yyyy.MM.dd');
  const when = e['日時'] ? '（' + e['日時'] + (e['開始時刻'] ? ' ' + e['開始時刻'] + '〜' : '') + '）' : '';
  const title = kind === '公開'
    ? '「' + e['イベント名'] + '」' + when + 'の情報を公開しました'
    : '「' + e['イベント名'] + '」' + when + 'の情報を更新しました';
  sh.insertRowBefore(2);
  const cells = sh.getRange(2, 1, 1, 4);
  cells.setNumberFormat('@');
  cells.setValues([[date, 'イベント', title, '']]);
  return title;
}

function emptyRow_(sh, col) {
  const last = Math.max(sh.getLastRow(), HEADER_ROW + 1);
  const names = sh.getRange(HEADER_ROW + 1, col['イベント名'], last - HEADER_ROW, 1).getDisplayValues();
  const months = sh.getRange(HEADER_ROW + 1, col['月'], last - HEADER_ROW, 1).getDisplayValues();
  for (let i = 0; i < names.length; i++) if (!names[i][0] && !months[i][0]) return HEADER_ROW + 1 + i;
  return last + 1;
}

function clean_(input) {
  const e = {};
  FIELDS.forEach((k) => { e[k] = String((input && input[k]) || '').replace(/\r\n?/g, '\n').trim(); });
  // 日付（YYYY-MM-DD）があれば、月と表示用の日時を自動で埋める
  const d = /^(\d{4})-(\d{2})-(\d{2})$/.exec(e['日付']);
  if (d) {
    if (!e['月']) e['月'] = d[1] + '-' + d[2];
    if (!e['日時']) {
      const w = WEEK[new Date(+d[1], +d[2] - 1, +d[3]).getDay()];
      e['日時'] = d[1] + '/' + (+d[2]) + '/' + (+d[3]) + '（' + w + '）';
    }
  }
  e['確定'] = e['確定'] === '済' ? '済' : '';
  return e;
}

function friendly_(err) {
  const m = String(err && err.message || err);
  if (/permission|権限|access|アクセス/i.test(m)) return 'このシートを編集する権限がありません。シートの持ち主に編集者として追加してもらってください。';
  return m;
}

// ---- 画面（ここは触らなくてOK）----
const PAGE_HTML = "<!DOCTYPE html>\n<html lang=\"ja\">\n<head>\n<base target=\"_top\">\n<meta charset=\"utf-8\">\n<style>\n:root{--bg:#0b0814;--panel:#16121f;--panel2:#1f1a2c;--line:#3a3050;--ink:#f3eefc;--sub:#b9add0;--pink:#ff3fd0;--cyan:#2fd8ff;--mint:#3dffb0}\n*{box-sizing:border-box}\n[hidden]{display:none!important}\nbody{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 system-ui,-apple-system,\"Hiragino Sans\",\"Noto Sans JP\",sans-serif}\nmain{max-width:860px;margin:0 auto;padding:20px 16px 80px}\nh1{font-size:22px;margin:0 0 4px}\n.sub{color:var(--sub);margin:0 0 16px;font-size:13px}\n.bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px;margin-bottom:16px}\n.bar select{flex:1 1 280px}\nfieldset{border:1px solid var(--line);border-radius:12px;padding:14px;margin:0 0 14px;background:var(--panel)}\nlegend{padding:0 6px;color:var(--cyan);font-weight:700}\n.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}\nlabel{display:flex;flex-direction:column;gap:4px;font-size:13px;color:var(--sub)}\nlabel.full{grid-column:1/-1}\n.req::after{content:\" *\";color:var(--pink)}\ninput,select,textarea{font:inherit;color:var(--ink);background:var(--panel2);border:1px solid var(--line);border-radius:8px;padding:9px 10px;min-height:42px;width:100%}\ntextarea{min-height:96px;resize:vertical}\ninput:focus,select:focus,textarea:focus{outline:2px solid var(--cyan);border-color:transparent}\ninput[type=date],input[type=time],input[type=month]{color-scheme:dark}\n.hint{font-size:12px;color:var(--sub);opacity:.85}\n.check{flex-direction:row;align-items:center;gap:8px;color:var(--ink)}\n.check input{width:20px;min-height:20px}\n.auto{display:flex;flex-wrap:wrap;gap:8px 18px;font-size:13px;color:var(--sub)}\n.auto b{color:var(--mint);font-weight:600}\nbutton{font:inherit;border-radius:10px;padding:10px 18px;min-height:44px;border:1px solid var(--line);background:var(--panel2);color:var(--ink);cursor:pointer}\nbutton.primary{background:var(--pink);border-color:var(--pink);color:#1a0718;font-weight:700}\nbutton.danger{border-color:#ff6b6b;color:#ff9b9b}\nbutton:disabled{opacity:.5;cursor:wait}\n.actions{position:sticky;bottom:0;display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:flex-end;background:linear-gradient(transparent,var(--bg) 30%);padding:18px 0 8px}\n#msg{flex:1 1 240px;font-size:14px}\n#msg.ok{color:var(--mint)}#msg.ng{color:#ff9b9b}\n.newsck{flex:1 1 100%;justify-content:flex-end;font-size:14px}\n.err{flex:1 1 100%;background:#3a1020;border:2px solid #ff6b6b;color:#ffd0d0;border-radius:10px;padding:12px 14px;font-size:15px;white-space:pre-line}\n.done{background:var(--panel);border:2px solid var(--mint);border-radius:16px;padding:28px 20px;text-align:center;margin:10px 0 20px}\n.done h2{margin:0 0 6px;font-size:24px;color:var(--mint)}\n.done .nm{font-size:18px;font-weight:700;margin:6px 0 4px;word-break:break-word}\n.done .info{color:var(--sub);font-size:14px;margin:0 0 4px}\n.done .btns{display:flex;flex-direction:column;gap:10px;max-width:360px;margin:20px auto 0}\n.done a.btnlink{display:block;text-align:center;text-decoration:none;font:inherit;border-radius:10px;padding:10px 18px;border:1px solid var(--line);background:var(--panel2);color:var(--cyan)}\n</style>\n</head>\n<body>\n<main>\n  <h1>PG イベント登録</h1>\n  <p class=\"sub\">保存すると、スプレッドシートの「イベント」に入ります。HPとDiscordの告知（NANA Support）にもそのまま反映されます。詳細やルールの欄は、そのまま改行できます。</p>\n\n  <div class=\"done\" id=\"done\" hidden>\n    <h2>✅ 保存しました！</h2>\n    <p class=\"nm\" id=\"doneName\"></p>\n    <p class=\"info\" id=\"doneInfo\"></p>\n    <p class=\"info\" id=\"doneNews\"></p>\n    <p class=\"info\">HPとDiscordの告知に反映されます（HPは開き直すと出ます）。</p>\n    <div class=\"btns\">\n      <button type=\"button\" class=\"primary\" id=\"again\">＋ 続けて別のイベントを登録する</button>\n      <button type=\"button\" id=\"editMore\">このイベントをもう少し直す</button>\n      <a class=\"btnlink\" href=\"https://nana7x-x.github.io/playgame-site/#events\" target=\"_blank\" rel=\"noopener\">HPで確認する ↗</a>\n    </div>\n  </div>\n\n  <div id=\"editor\">\n  <div class=\"bar\">\n    <select id=\"pick\" aria-label=\"編集するイベント\"><option value=\"\">＋ 新しいイベントを登録する</option></select>\n    <button type=\"button\" id=\"reload\">一覧を読み直す</button>\n  </div>\n\n  <form id=\"f\" autocomplete=\"off\" novalidate onsubmit=\"return false\">\n    <fieldset><legend>基本</legend>\n      <div class=\"grid\">\n        <label class=\"full\"><span class=\"req\">イベント名</span><input name=\"イベント名\" maxlength=\"100\" placeholder=\"PROFLUX CUP 01\"><span class=\"hint\">「イベント名未定」のあいだは Discord の告知は出ません</span></label>\n        <label>種類<select name=\"種類\"><option>メイン</option><option>小規模</option><option>Nexus Server</option></select></label>\n        <label>ゲーム<input name=\"ゲーム\" list=\"games\" placeholder=\"VALORANT\"></label>\n        <label class=\"check\"><input type=\"checkbox\" name=\"確定\" value=\"済\">内容が確定した（「確定前」の表示が消えます）</label>\n      </div>\n    </fieldset>\n\n    <fieldset><legend>日程</legend>\n      <div class=\"grid\">\n        <label>実施日<input type=\"date\" name=\"日付\"><span class=\"hint\">まだ決まっていなければ空でOK</span></label>\n        <label>開始時刻<input type=\"time\" name=\"開始時刻\"><span class=\"hint\">入れると当日の朝と30分前に告知します</span></label>\n        <label id=\"monthBox\">実施予定の月（実施日が未定のとき）<input type=\"month\" name=\"月\"><span class=\"hint\">実施日を入れたら不要です</span></label>\n        <label class=\"full\">募集期間<input name=\"募集期間\" placeholder=\"1/5〜1/20 23:59\"><span class=\"hint\">ここから募集開始・募集締切が自動で決まり、その日に告知します</span></label>\n        <label class=\"full\">HPに出す日にちの書き方（ふだんは空でOK）<input name=\"日時\" placeholder=\"空なら実施日から自動で「2026/11/22（日）」\"><span class=\"hint\">「1月中（日程調整中）」のように書きたいときだけ使います</span></label>\n      </div>\n    </fieldset>\n\n    <fieldset><legend>内容</legend>\n      <div class=\"grid\">\n        <label class=\"full\">詳細<textarea name=\"詳細\" placeholder=\"どんなイベントか\"></textarea></label>\n        <label class=\"full\">ルール<textarea name=\"ルール\" placeholder=\"1行に1つ書くと、HPで箇条書きになります\"></textarea></label>\n        <label class=\"full\">備考<textarea name=\"備考\"></textarea></label>\n      </div>\n    </fieldset>\n\n    <fieldset><legend>募集</legend>\n      <div class=\"grid\">\n        <label>募集状況<select name=\"募集状況\"><option>調整中</option><option>募集前</option><option>募集中</option><option>締切</option><option>開催終了</option></select></label>\n        <label>定員<input name=\"定員\" placeholder=\"8チーム\"></label>\n        <label class=\"full\">応募条件<textarea name=\"応募条件\" placeholder=\"1行に1つ書くと、HPで箇条書きになります\"></textarea></label>\n        <label class=\"full\">参加方法<textarea name=\"参加方法\" placeholder=\"Discordのエントリーチャンネルで申請\"></textarea></label>\n        <div class=\"auto full\" id=\"auto\"></div>\n      </div>\n    </fieldset>\n\n    <fieldset><legend>リンク</legend>\n      <div class=\"grid\">\n        <label>リンク名<input name=\"リンク名\" placeholder=\"エントリー\"></label>\n        <label>リンクURL<input name=\"リンクURL\" type=\"url\" placeholder=\"https://...\"></label>\n        <label>配信URL<input name=\"配信URL\" type=\"url\" placeholder=\"https://youtube.com/...\"><span class=\"hint\">当日朝・30分前の告知に載ります</span></label>\n        <label>参加サーバー<input name=\"参加サーバー\" type=\"url\" placeholder=\"https://discord.gg/...\"><span class=\"hint\">募集開始・締切・当日朝の告知に載ります</span></label>\n      </div>\n    </fieldset>\n\n    <div class=\"actions\">\n      <label class=\"check newsck\"><input type=\"checkbox\" id=\"news\" checked><span id=\"newsLabel\">HPのお知らせに「情報を公開しました」を載せる</span></label>\n      <div id=\"err\" class=\"err\" role=\"alert\" hidden></div>\n      <span id=\"msg\" role=\"status\"></span>\n      <button type=\"button\" class=\"danger\" id=\"del\" hidden>このイベントを消す</button>\n      <button type=\"button\" class=\"primary\" id=\"save\">保存する</button>\n    </div>\n  </form>\n  </div>\n  <datalist id=\"games\"><option>VALORANT</option><option>OW2</option><option>Apex</option><option>Minecraft</option><option>複数タイトル</option></datalist>\n</main>\n<script>\nconst $ = (s) => document.querySelector(s);\nconst form = $('#f');\nlet events = [], current = null;\nconst run = (fn, ...args) => new Promise((ok, ng) => {\n  const slow = setTimeout(() => { $('#msg').textContent = 'Googleからの返事を待っています…（30秒以上かかるときは、ページを開き直してください）'; }, 8000);\n  google.script.run.withSuccessHandler((r) => { clearTimeout(slow); ok(r); }).withFailureHandler((e) => { clearTimeout(slow); ng(e); })[fn](...args);\n});\nconst msg = (t, cls) => {\n  const err = cls === 'ng';\n  $('#err').hidden = !err; $('#err').textContent = err ? '⚠ 保存できませんでした\\n' + t : '';\n  $('#msg').textContent = err ? '' : t; $('#msg').className = err ? '' : (cls || '');\n  if (err) $('#err').scrollIntoView({ block: 'center', behavior: 'smooth' });\n};\nconst busy = (on) => { $('#save').disabled = $('#del').disabled = on; };\n\n/* シートの表示（2027/01/23 や 2027-01-23、20:00:00）を入力欄の形にそろえる */\nconst toDate = (v) => { const m = /(\\d{4})\\D(\\d{1,2})\\D(\\d{1,2})/.exec(v || ''); return m ? `${m[1]}-${m[2].padStart(2, '0')}-${m[3].padStart(2, '0')}` : ''; };\nconst toMonth = (v) => { const m = /(\\d{4})\\D(\\d{1,2})/.exec(v || ''); return m ? `${m[1]}-${m[2].padStart(2, '0')}` : ''; };\nconst toTime = (v) => { const m = /(\\d{1,2}):(\\d{2})/.exec(v || ''); return m ? `${m[1].padStart(2, '0')}:${m[2]}` : ''; };\n\nfunction fill(e) {\n  current = e;\n  form.reset();\n  if (e) for (const el of form.elements) {\n    if (!el.name) continue;\n    const v = e[el.name] || '';\n    if (el.type === 'checkbox') el.checked = /^(済|確定|○|◯|TRUE|true|yes|1)$/.test(v);\n    else if (el.name === '日付') el.value = toDate(v);\n    else if (el.name === '月') el.value = toMonth(v);\n    else if (el.name === '開始時刻') el.value = toTime(v);\n    else if (el.tagName === 'SELECT') { if (![...el.options].some((o) => o.value === v) && v) el.add(new Option(v)); el.value = v || el.options[0].value; }\n    else el.value = v;\n  }\n  $('#del').hidden = !e;\n  $('#news').checked = !e;\n  $('#newsLabel').textContent = e ? 'HPのお知らせに「情報を更新しました」を載せる' : 'HPのお知らせに「情報を公開しました」を載せる';\n  syncMonth();\n  $('#save').textContent = e ? '変更を保存する' : '登録する';\n  showAuto(e);\n}\nfunction showAuto(e) {\n  $('#auto').innerHTML = e && (e['募集開始'] || e['募集締切'])\n    ? `募集開始（自動）<b>${e['募集開始'] || '—'}</b>　募集締切（自動）<b>${e['募集締切'] || '—'}</b>`\n    : '保存すると、募集期間から募集開始・募集締切が自動で入ります。';\n}\nfunction label(e) { return `${e['日付'] || e['日時'] || e['月'] || ''}　${e['イベント名'] || '（名前なし）'}`; }\nasync function load(selectRow) {\n  msg('読み込み中…');\n  try {\n    events = await run('listEvents');\n    const pick = $('#pick');\n    pick.length = 1;\n    for (const e of events) pick.add(new Option(label(e), e.row));\n    pick.value = selectRow ? String(selectRow) : '';\n    fill(events.find((e) => e.row === +pick.value) || null);\n    msg('');\n  } catch (err) { msg(err.message, 'ng'); }\n}\n$('#pick').addEventListener('change', (ev) => { fill(events.find((e) => e.row === +ev.target.value) || null); msg(''); });\n$('#reload').addEventListener('click', () => load(current && current.row));\nconst syncMonth = () => { const d = form.elements['日付'].value; if (d) form.elements['月'].value = d.slice(0, 7); $('#monthBox').hidden = !!d; };\nform.elements['日付'].addEventListener('change', syncMonth);\nform.elements['日付'].addEventListener('input', syncMonth);\n\n/* Enter キーなどでページが読み込み直されないよう、フォームの送信は使わずボタンで保存する */\nform.addEventListener('submit', (ev) => { ev.preventDefault(); save(); });\n$('#save').addEventListener('click', save);\nlet saving = false;\nfunction showDone(e) {\n  $('#doneName').textContent = e ? e['イベント名'] : '';\n  const parts = [];\n  if (e && (e['日時'] || e['日付'])) parts.push('日時：' + (e['日時'] || e['日付']) + (e['開始時刻'] ? ' ' + e['開始時刻'] + '〜' : ''));\n  if (e && (e['募集開始'] || e['募集締切'])) parts.push('募集開始：' + (e['募集開始'] || '—') + '　募集締切：' + (e['募集締切'] || '—'));\n  $('#doneInfo').textContent = parts.join('\\n');\n  $('#doneInfo').style.whiteSpace = 'pre-line';\n  $('#editor').hidden = true; $('#done').hidden = false;\n  window.scrollTo(0, 0);\n}\nfunction showEditor() { $('#done').hidden = true; $('#editor').hidden = false; window.scrollTo(0, 0); }\n$('#again').addEventListener('click', () => { $('#pick').value = ''; fill(null); msg(''); showEditor(); });\n$('#editMore').addEventListener('click', () => { msg(''); showEditor(); });\nasync function save() {\n  if (saving) return;\n  const data = {};\n  for (const el of form.elements) if (el.name) data[el.name] = el.type === 'checkbox' ? (el.checked ? '済' : '') : el.value;\n  if (!data['イベント名'].trim()) { msg('イベント名を入れてください', 'ng'); return; }\n  if (!data['日付'] && !data['月']) { msg('実施日（未定なら実施予定の月）を入れてください', 'ng'); return; }\n  for (const k of ['リンクURL', '配信URL', '参加サーバー']) if (data[k] && !/^https?:\\x2f\\x2f/.test(data[k])) { msg(`${k} は https: で始まるURLを書いてください`, 'ng'); return; }\n  /* 「日付」と「日時」の日にちが食い違っていたら止める（年の選び間違いを防ぐ） */\n  const shown = /(\\d{4})\\D(\\d{1,2})\\D(\\d{1,2})/.exec(data['日時'] || '');\n  if (data['日付'] && shown && toDate(shown[0]) !== data['日付']) {\n    msg(`「実施日」(${data['日付'].replace(/-/g, '/')}) と「HPに出す日にちの書き方」(${shown[0]}) の日にちが違います。どちらかを直すか、「HPに出す日にちの書き方」を空にしてください（実施日から自動で入ります）。`, 'ng'); return;\n  }\n  data.__news = $('#news').checked ? (current ? 'update' : 'new') : '';\n  saving = true; busy(true); msg('保存中…');\n  try {\n    const res = await run('saveEvent', data, current ? current.row : 0);\n    await load(res.row);\n    msg('');\n    showDone(res.saved || current);\n    $('#doneNews').textContent = res.news ? '📰 HPのお知らせにも載せました：' + res.news : '';\n  } catch (err) { msg((err && err.message) || String(err), 'ng'); console.error(err); }\n  saving = false; busy(false);\n}\n$('#del').addEventListener('click', async () => {\n  if (!current || !confirm(`「${current['イベント名']}」を消しますか？（HPと告知からも消えます）`)) return;\n  busy(true); msg('消しています…');\n  try { await run('deleteEvent', current.row); await load(); msg('消しました。', 'ok'); }\n  catch (err) { msg(err.message, 'ng'); }\n  busy(false);\n});\nload();\n</script>\n</body>\n</html>\n";
