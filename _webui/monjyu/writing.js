// writing.js

// 親ウィンドウにメッセージを送信する関数
function sendMessageToParent(action, method, data) {
    window.parent.postMessage({ action: action, method: method, data: data }, '*');
}

// 処理中の状態を取得する
function get_ready_count() {
    var isReady = -1;
    var isBusy = -1;
    $.ajax({
        url: $('#core_endpoint0').val() + '/get_ready_count',
        method: 'GET',
        async: false, // 同期処理
        dataType: 'json',
        success: function(data) {
            isReady = data.ready_count;
            isBusy = data.busy_count;
        },
        error: function(xhr, status, error) {
            console.error('get_ready_count error:', error);
        }
    });
    return { isReady: isReady, isBusy: isBusy }; 
}

// スリープ処理
function sleep(milliSeconds) {
    return new Promise((resolve) => {
        setTimeout(() => resolve(), milliSeconds);
    });
}

// 起動確認(ビジー待機)
async function waitForBusy() {
    while (true) {
        var result = get_ready_count();
        if (result.isBusy > 0) {
            return;
        }
        await sleep(2000);
    }
}

// 終了確認(アイドル待機)
async function waitForIdol() {
    while (true) {
        var result = get_ready_count();
        if (result.isBusy === 0) {
            return;
        }
        await sleep(2000);
    }
}

// 【同期処理】ユーザーの出力履歴を取得する関数
function get_output_log_user() {
    // サーバーからユーザーの出力履歴を取得するAJAXリクエスト
    $.ajax({
        url: $('#core_endpoint2').val() + '/get_output_log_user',
        type: 'GET',
        async: false, // 同期処理
        data: { user_id: $('#user_id').val() },
        success: function(data) {
            // データが存在する場合
            if (data !== null) {

                // テキストエリアの内容を更新
                $('#last_text').val(data.output_data);

            }
        },
        error: function(xhr, status, error) { // パラメータを追加
            console.error('get_output_log_user error:', error); // コロンを追加
        }
    });
}

// 日付時刻文字列生成関数
function getYMDHMS() {
    var now = new Date();
    var yyyy = now.getFullYear();
    var mm = String(now.getMonth() + 1).padStart(2, '0');
    var dd = String(now.getDate()).padStart(2, '0');
    var hh = String(now.getHours()).padStart(2, '0');
    var mi = String(now.getMinutes()).padStart(2, '0');
    var ss = String(now.getSeconds()).padStart(2, '0');
    return `${yyyy}${mm}${dd}.${hh}${mi}${ss}`;
}

// 自動執筆（あらすじ）
async function arasuji_all() {
    var ymdhms = getYMDHMS();
    $('#summary_text').val('');
    $('#last_text').val('');

    // あらすじ要求
    var result_savepath = ymdhms + '.writing.00.txt'
    sendMessageToParent('requestRun', 'req_mode', result_savepath );

    // 実行待機
    await waitForBusy();
    await waitForIdol();
    await sleep(5000);
    sendMessageToParent('setInputText', 'set', '' );
    get_output_log_user();
    $('#summary_text').val( $('#last_text').val() );
    sendMessageToParent('setInputText', 'set', $('#last_text').val() );

    await sleep(1000);
    alert('あらすじ作成完了!')
}

// 自動執筆（小説）
async function novel_parallel() {
    if (confirm("全話の並列生成を実行しますか?")) {
        var ymdhms = getYMDHMS();
        $('#last_text').val('');
        var n_max = parseInt( $('#n_max').val() );
        for (var n = 1; n <= n_max; n++) {
            // 執筆要求
            var req_text = $('#req_doc2').val();
            req_text = req_text.replace("{ ***N*** }", n);
            sendMessageToParent('setRequestText', 'set', req_text);
            var result_savepath = ymdhms + '.writing.' + String(n).padStart(2, '0') + '.txt'
            sendMessageToParent('requestRun', 'req_mode', result_savepath );
            await sleep(1000);

            // ８件づつ処理
            if (n % 8 === 0 || n === n_max) {
                // 実行待機
                await waitForBusy();
                await waitForIdol();
            }
        }

        await sleep(1000);
        alert('執筆完了!')
    }
}

// 自動執筆（小説）
async function novel_serial1(tts) {
    if (confirm("全話の順次生成を実行しますか?")) {
        var ymdhms = getYMDHMS();
        $('#last_text').val('');
        var n_max = parseInt( $('#n_max').val() );
        for (var n = 1; n <= n_max; n++) {
            // あらすじ、前話設定
            sendMessageToParent('setInputText', 'set', $('#summary_text').val() );
            sendMessageToParent('setInputText', 'add', $('#last_text').val() );

            // 執筆要求
            var req_text = $('#req_doc2').val();
            req_text = req_text.replace("{ ***N*** }", n);
            sendMessageToParent('setRequestText', 'set', req_text);
            var result_savepath = ymdhms + '.writing.' + String(n).padStart(2, '0') + '.txt'
            sendMessageToParent('requestRun', 'req_mode', result_savepath );
            await sleep(1000);

            // 実行待機
            await waitForBusy();
            await waitForIdol();
            await sleep(5000);
            get_output_log_user();
            sendMessageToParent('setInputText', 'add', $('#last_text').val() );
            await sleep(1000);

            if (tts === 'yes') {
                sendMessageToParent('data2TTS', '', '' );
            }
        }
        sendMessageToParent('setInputText', 'set', $('#summary_text').val() );
        await sleep(1000);
        if (tts !== 'yes') {
            alert('執筆完了!')
        }
    }
}

// 自動執筆（小説）
async function novel_serial2(tts) {
    if (confirm("（★開発中★全話実行するので注意！）１話の生成を実行しますか?")) {
        var ymdhms = getYMDHMS();
        $('#last_text').val('');
        var n_max = parseInt( $('#n_max').val() );
        for (var n = 1; n <= n_max; n++) {
            // 執筆要求
            var req_text = $('#req_doc2').val();
            req_text = req_text.replace("{ ***N*** }", n);
            sendMessageToParent('setRequestText', 'set', req_text);
            var result_savepath = ymdhms + '.writing.' + String(n).padStart(2, '0') + '.txt'
            sendMessageToParent('requestRun', 'req_mode', result_savepath );

            // 実行待機
            await waitForBusy();
            await waitForIdol();
            await sleep(5000);
            get_output_log_user();
            sendMessageToParent('setInputText', 'add', $('#last_text').val() );
            await sleep(1000);

            if (tts === 'yes') {
                sendMessageToParent('data2TTS', '', '' );
            }
        }
        sendMessageToParent('setInputText', 'set', $('#summary_text').val() );
        await sleep(1000);
        if (tts !== 'yes') {
            alert('執筆完了!')
        }
    }
}



// ドキュメントが読み込まれた時に実行される処理
$(document).ready(function() {

    // ローカルストレージからデータ復元
    const storedData = JSON.parse(localStorage.getItem('writing_formData'));

    // データが存在する場合
    if (storedData) {
        // テキストエリアの内容を復元
        $('#n_max').val(storedData.n_max || '6');
        $('#plot_text').val(storedData.plot_text || '');
        $('#summary_text').val(storedData.summary_text || '');
        $('#last_text').val(storedData.last_text || '');
    }

    // ページ遷移時にローカルストレージに保存
    window.onbeforeunload = function() {
        // フォームデータを取得
        var formData = {
            n_max: $('#n_max').val(),
            plot_text: $('#plot_text').val(),
            summary_text: $('#summary_text').val(),
            last_text: $('#last_text').val(),
        };
        // ローカルストレージに保存
        localStorage.setItem('writing_formData', JSON.stringify(formData));
    };
    
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

    // docリクエストボタンのクリックイベント
    $('#btnReq_doc1').click(function() {
        var req_text = $('#req_doc1').val();
        req_text = req_text.replace("{ ***N_MAX*** }", $('#n_max').val() );
        req_text = req_text.replace("{ ***N_MAX*** }", $('#n_max').val() );
        req_text = req_text.replace("{ ***PLOT_TEXT*** }", $('#plot_text').val() );
        sendMessageToParent('setRequestText', 'set', req_text );
        sendMessageToParent('setInputText', 'set', '' );
    });
    $('#btnReq_doc2').click(function() {
        sendMessageToParent('setRequestText', 'set', $('#req_doc2').val() );
    });
    $('#btnReq_doc3').click(function() {
        sendMessageToParent('setRequestText', 'set', $('#req_doc3').val() );
    });

    // 実行ボタンのクリックイベント
    $('#btnArasuji_all').click(function() {
        arasuji_all();
    });
    $('#btnNovel_parallel').click(function() {
        novel_parallel();
    });
    $('#btnNovel_serial1').click(function() {
        novel_serial1('no');
    });
    $('#btnNovel_serial1_TTS').click(function() {
        novel_serial1('yes');
    });
    $('#btnNovel_serial2').click(function() {
        novel_serial2('no');
    });
    $('#btnNovel_serial2_TTS').click(function() {
        novel_serial2('yes');
    });

});
