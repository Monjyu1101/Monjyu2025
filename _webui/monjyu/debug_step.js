// debug_step.js

// デバッグログを取得し、デバッグテキストエリアを更新する関数
let lastDebugData = {};
function get_debug_log_user() {

    // ajaxでデバッグログを取得
    $.ajax({
        url: $('#core_endpoint').val() + '/get_debug_log_user',
        type: 'GET',
        data: { user_id: $('#user_id').val() },
        success: function(data) {
            // データが存在する場合
            if (data !== null) {
                // 受信データと前回データが異なる場合
                if(JSON.stringify(data) !== JSON.stringify(lastDebugData)) {

                    // テキストエリアの内容を更新
                    $('#debug_text').val(data.debug_text);
                    $('#debug_data').val(data.debug_data);

                    // アニメーションを追加
                    $('#debug_text').addClass('blink-border');
                    $('#debug_data').addClass('blink-border');

                    // アニメーション終了後にクラスを削除
                    setTimeout(() => {
                        $('#debug_text').removeClass('blink-border');
                        $('#debug_data').removeClass('blink-border');
                    }, 2000); // アニメーション時間(2秒)

                }
                // 最新のデータを保持
                lastDebugData = data;
            }
        },
        error: function(xhr, status, error) {
            console.error('get_debug_log_user error:', error);
        }
    });
}



// ドキュメントが読み込まれた時に実行される処理
$(document).ready(function() {

    // ローカルストレージからデータ復元
    const storedData = JSON.parse(localStorage.getItem('debug_step_formData'));

    // データが存在する場合
    if (storedData) {
        // テキストエリアの内容を復元
        $('#debug_text').val(storedData.debug_text || '');
        $('#debug_data').val(storedData.debug_data || '');
    }

    // ページ遷移時にローカルストレージに保存
    window.onbeforeunload = function() {
        // フォームデータを取得
        var formData = {
            debug_text: $('#debug_text').val(),
            debug_data: $('#debug_data').val(),
        };
        // ローカルストレージに保存
        localStorage.setItem('debug_step_formData', JSON.stringify(formData));
    };


    // 定期的な更新処理
    get_debug_log_user();
    setInterval(get_debug_log_user, 2000);


    // 各テキストエリアにダブルクリックイベントを追加
    const textAreas = document.querySelectorAll('textarea');
    for (const textarea of textAreas) {

        // ダブルクリックイベントリスナー
        textarea.addEventListener('dblclick', function() {

            // テキストエリアを選択
            $(this).select();

            // テキストを取得
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
