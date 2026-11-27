/**
 * PG 参加記録の受け口（Google Apps Script）
 * NANA Support が、イベントが終わったら「だれが出席・欠席したか」をここに送ってきます。
 * スプレッドシートの「参加記録」タブに書き込み、「参加回数」タブで人ごとの出席回数を数えます。
 *
 * ・イベント登録ページ（もう1つの Apps Script）とは別のプロジェクトにしてください。
 * ・ウェブアプリとして公開するときは「次のユーザーとして実行：自分」「アクセスできるユーザー：全員」。
 *   合言葉（SECRET）が合わないと書き込まないので、URLを知られても大丈夫です。
 */
const SECRET = 'ここに合言葉';   // ← NANA Support の「参加記録 → スプレッドシート連携」で出る合言葉に書きかえる
const SHEET_ID = '1LB24cc6LTDr2vjWspo_GD8tI6QsYJ1Y7x2V4LCLdo_0';
const TAB = '参加記録';
const SUM_TAB = '参加回数';
const HEAD = ['キー', '日付', 'イベント名', 'イベントID', 'ユーザーID', '名前', '申込', 'チーム', 'VC（分）', 'チェックイン', '状態'];

/** 最初に1回だけ ▶実行：スプレッドシートを使う許可を出して、「参加記録」「参加回数」タブを作る */
function setup() {
  ensure_(SpreadsheetApp.openById(SHEET_ID), HEAD);
}

function doGet() {
  return ContentService.createTextOutput('PG 参加記録の受け口です（NANA Support から使います）');
}

function doPost(e) {
  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000);
    const body = JSON.parse(e.postData.contents);
    if (!SECRET || SECRET === 'ここに合言葉' || body.secret !== SECRET) return out_({ ok: false, error: '合言葉が違います（Apps Script の SECRET を確認して、新バージョンでデプロイしてください）' });
    const ss = SpreadsheetApp.openById(SHEET_ID);
    const sh = ensure_(ss, body.head);
    if ((body.days || []).length) save_(sh, body.head, body.rows || [], body.days);
    return out_({ ok: true, n: (body.rows || []).length });
  } catch (err) {
    return out_({ ok: false, error: String(err && err.message || err) });
  } finally {
    lock.releaseLock();
  }
}

/** 送られてきた日（イベントID|日付）の行を、まるごと新しい内容に入れかえる。何回送っても行は増えない。 */
function save_(sh, head, rows, days) {
  const last = sh.getLastRow();
  const old = last > 1 ? sh.getRange(2, 1, last - 1, head.length).getValues() : [];
  const drop = {};
  days.forEach(function (d) { drop[d] = true; });
  const keep = old.filter(function (r) { const k = String(r[0]).split('|'); return !drop[k[0] + '|' + k[1]]; });
  const all = keep.concat(rows).sort(function (a, b) {
    return String(b[1]).localeCompare(String(a[1])) || String(a[2]).localeCompare(String(b[2])) || (a[10] === '出席' ? 0 : 1) - (b[10] === '出席' ? 0 : 1);
  });
  if (last > 1) sh.getRange(2, 1, last - 1, head.length).clearContent();
  if (all.length) sh.getRange(2, 1, all.length, head.length).setNumberFormat('@').setValues(all.map(function (r) { return r.map(String); }));
}

function ensure_(ss, head) {
  let sh = ss.getSheetByName(TAB);
  if (!sh) {
    sh = ss.insertSheet(TAB);
    sh.getRange(1, 1, 1, head.length).setValues([head]).setFontWeight('bold').setBackground('#2a1f45').setFontColor('#ffffff');
    sh.setFrozenRows(1);
    sh.hideColumns(1); sh.hideColumns(4); // キー・イベントIDは隠す
  }
  if (!ss.getSheetByName(SUM_TAB)) {
    const s = ss.insertSheet(SUM_TAB);
    s.getRange('A1').setFormula("=QUERY('" + TAB + "'!A:K,\"select F, count(E) where K='出席' group by F order by count(E) desc label F '名前', count(E) '出席回数'\",1)");
    s.getRange('D1').setFormula("=QUERY('" + TAB + "'!A:K,\"select F, count(E) where K='欠席' group by F order by count(E) desc label F '名前', count(E) '欠席回数'\",1)");
    s.getRange('G1').setFormula("=QUERY('" + TAB + "'!A:K,\"select B, C, count(E) where K='出席' group by B, C order by B desc label B '日付', C 'イベント', count(E) '出席人数'\",1)");
    s.setFrozenRows(1);
  }
  return sh;
}

function out_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
