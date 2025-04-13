// debug_log.js

// HTMLエスケープ関数
function escapeHtml(unsafe) {
    if (unsafe === null || unsafe === undefined) {
        return '';
    }
    
    return String(unsafe)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// 結果を更新する関数
let lastMaxUpdTime = null;
function get_debug_log_all() {
    // サーバーから結果データを取得し、テーブルに表示する
    $.ajax({
        url: $('#core_endpoint5').val() + '/get_debug_log_all',
        type: 'GET',
        data: { user_id: $('#user_id').val() },
        success: function(data) {
            var currentMaxUpdTime = null;
            
            // 現在のデータセットの最大upd_timeを取得
            for (var key in data) {
                var updTime = data[key].upd_time;
                if (updTime && (!currentMaxUpdTime || updTime > currentMaxUpdTime)) {
                    currentMaxUpdTime = updTime;
                }
            }
            
            // 最大upd_timeが変化した場合のみ更新
            if (currentMaxUpdTime !== lastMaxUpdTime) {
                lastMaxUpdTime = currentMaxUpdTime;
                
                // 取得した結果データをテーブルのHTMLコードに変換する
                var tableHtml = '';
                
                for (var key in data) {
                    // 取得した各セッションデータに対して処理を行う
                    var dt = data[key];
                    // 出力時間の表示用
                    var outTime = dt.out_time ? dt.out_time.split(' ')[1] : '';
                    
                    tableHtml += `<tr>
                        <td class="key-col">${key}</td>
                        <td class="key-val">${ escapeHtml(dt.key_val) || '' }</td>
                        <td class="time-col">${outTime}</td>
                        <td class="req-col"><textarea readonly title="${ escapeHtml(dt.req_text) || '' }">${ escapeHtml(dt.req_text) || ''}</textarea></td>
                        <td class="inp-col"><textarea readonly title="${ escapeHtml(dt.inp_text) || '' }">${ escapeHtml(dt.inp_text) || ''}</textarea></td>
                        <td class="out-col"><textarea readonly title="${ escapeHtml(dt.out_text) || '' }">${ escapeHtml(dt.out_text) || ''}</textarea></td>
                        <td class="data-col"><textarea readonly title="${ escapeHtml(dt.out_data) || '' }">${ escapeHtml(dt.out_data) || ''}</textarea></td>
                    </tr>`;
                }
                
                // テーブルのHTMLコードをテーブル要素に設定する
                $('#debug_log').html(tableHtml);
                
                // ゼブラ配色を適用
                $('#debug_log tr').each(function(index) {
                    // テーブルの行に交互に背景色を設定する
                    if (index % 2 === 0) {
                        $(this).css({'background-color': '#ffffff'});
                    } else {
                        $(this).css({'background-color': '#f9f9f9'});
                    }
                });
                // すべてのテキストエリアにクリックイベントを追加
                $('textarea').on('click', function() {
                    // 行数10行に拡張
                    $(this).css('height', '12em');
                });

                // すべてのテキストエリアにダブルクリックイベントを追加
                $('textarea').on('dblclick', function() {
                    // クリップボードコピー
                    $(this).select(); // テキストを選択
                    var text = this.value;
                    navigator.clipboard.writeText(text) // クリップボードにコピー
                        .then(() => {
                            console.log('Copied to clipboard!'); // コピー成功のログ
                            alert('Copied to clipboard!'); // コピー成功メッセージ
                        })
                        .catch(err => {
                            console.error('Failed to copy: ', err); // コピー失敗のログ
                        });
                });

            }
        },
        error: function(xhr, status, error) {
            console.error('get_debug_log_all error:', error);
        }
    });
}
// ドキュメントが読み込まれた時に実行される処理
$(document).ready(function() {
    // 情報を取得する
    get_debug_log_all();
    setInterval(get_debug_log_all, 5000);

    // 各テキストエリアにダブルクリックイベントを追加
    const textAreas = document.querySelectorAll('textarea');
    for (const textarea of textAreas) {
        textarea.addEventListener('dblclick', function() {
            // ダブルクリックされたテキストエリアを選択
            $(this).select();

            // テキストエリアの値を取得
            var text = this.value;

            // クリップボードにコピー
            navigator.clipboard.writeText(text)
                .then(() => {
                    console.log('Copied to clipboard!');
                    alert('Copied to clipboard!');
                })
                .catch(err => {
                    console.error('Failed to copy: ', err);
                });
        });
    }

});
