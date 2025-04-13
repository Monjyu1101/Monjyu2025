// index.js

// 処理中の状態を表す変数
let isReady = -1;
let isBusy = -1;

// 処理中の状態を取得する
function get_ready_count() {
    $.ajax({
        url: $('#core_endpoint0').val() + '/get_ready_count',
        method: 'GET',
        dataType: 'json',
        success: function(data) {
            // 処理可能な状態数を更新
            isReady = data.ready_count;
            // 処理中の状態数を更新
            isBusy = data.busy_count;
        },
        error: function(xhr, status, error) {
            console.error('get_ready_count error:', error);
            // エラー発生時は-1を設定
            isReady = -1;
            isBusy = -1;
        }
    });
}

// タイトルの下線のアニメーションを更新する関数
function updateTitleUnderline() {
    // 現在の時刻を取得
    var now = new Date().getTime() / 1000;
    var tm = now % 9;
    // 下線の明滅効果を計算
    var intensity = Math.abs(Math.sin((tm / 9) * Math.PI * 2));
    var c255 = Math.round(255 * intensity);
    var titleUnderline = document.querySelector('.title-underline');

    // 処理中の状態に基づいてタイトルの下線の色を変更
    switch (true) {
        case isReady === -1:
            // 未接続状態：黒
            titleUnderline.style.backgroundColor = `rgb(0, 0, 0)`;
            break;
        case isBusy > 0:
            // 処理中：赤
            titleUnderline.style.backgroundColor = `rgb(${c255}, 0, 0)`;
            break;
        case isReady > 0:
            // 処理可能：シアン
            titleUnderline.style.backgroundColor = `rgb(0, ${c255}, ${c255})`;
            break;
        default:
            // 待機中：グレー
            var c127 = Math.round(127 * intensity);
            titleUnderline.style.backgroundColor = `rgb(${c127}, ${c127}, ${c127})`;
    }
}



// ドキュメントが読み込まれた時に実行される処理
$(document).ready(function() {

    // 処理中の状態を取得
    setInterval(get_ready_count, 3000);

    // タイトル下線の色を更新
    setInterval(updateTitleUnderline, 50);

    // URLパラメータを取得
    const urlParams = new URLSearchParams(window.location.search);

    // メインフレームに表示するページを取得
    const innerPage = (urlParams.get('inner_page') || 'mainui');

    // メインフレームにページを設定
    $('#main-frame').attr('src', '/' + innerPage + '.html');

    // アクティブなタブを設定
    $('.tab[href="/index.html?inner_page=' + innerPage + '"]').addClass('active');

});
