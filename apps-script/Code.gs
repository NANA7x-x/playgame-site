/**
 * PG イベント登録ページ（Google Apps Script）
 * スプレッドシート「イベント」タブに、改行つきでイベントを登録・編集するための専用ページです。
 *
 * ・ウェブアプリとして公開するときは「次のユーザーとして実行：ウェブアプリにアクセスしているユーザー」
 *   「アクセスできるユーザー：Google アカウントを持つ全員」にします。
 *   こうすると、そのシートを編集できる人だけが保存でき、ほかの人は保存できません。
 * ・「募集開始」「募集締切」の列は式で自動入力されるので、このページからは書き換えません。
 */
const SHEET_ID = '1LB24cc6LTDr2vjWspo_GD8tI6QsYJ1Y7x2V4LCLdo_0';
const TAB = 'イベント';
const HEADER_ROW = 2;
// このページから書く列（見出しの名前）。ここにない列（募集開始・募集締切など）は触りません。
const FIELDS = ['月', '日付', '日時', '種類', 'ゲーム', 'イベント名', '詳細', '確定', '募集状況', '募集期間', '定員',
  '応募条件', '参加方法', 'ルール', '備考', 'リンク名', 'リンクURL', '開始時刻', '配信URL', '参加サーバー'];
const AUTO = ['募集開始', '募集締切'];
const WEEK = ['日', '月', '火', '水', '木', '金', '土'];

function doGet() {
  return HtmlService.createHtmlOutputFromFile('Index')
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
    if (!row) row = emptyRow_(sh, col);
    else if (row <= HEADER_ROW) throw new Error('行の指定が正しくありません');
    FIELDS.forEach((k) => {
      const cell = sh.getRange(row, col[k]);
      cell.setNumberFormat('@'); // 日付や時刻が勝手に変換されないよう文字として入れる
      cell.setValue(e[k] || '');
    });
    SpreadsheetApp.flush();
    return { row: row, saved: listEvents().find((x) => x.row === row) };
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
