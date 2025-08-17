// url.js

const CORE_ENDPOINT1 = 'http://localhost:8001';
const CORE_ENDPOINT2 = 'http://localhost:8002';
const CORE_ENDPOINT3 = 'http://localhost:8003';
const CORE_ENDPOINT4 = 'http://localhost:8004';
const CORE_ENDPOINT5 = 'http://localhost:8005';

// 親ウィンドウにメッセージを送信する関数
function sendMessageToParent(action, method, data) {
    window.parent.postMessage({ action: action, method: method, data: data }, '*');
}

// 処理中の状態を取得する
function get_ready_count() {
    var isReady = -1;
    var isBusy = -1;
    $.ajax({
        url: CORE_ENDPOINT1 + '/get_ready_count',
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
        url: CORE_ENDPOINT3 + '/get_output_log_user',
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

// リクエストをサーバーに送信する共通関数
function post_request(req_mode, system_text, request_text, input_text, result_savepath, result_schema) {
    // チェックボックスが選択されているファイル名を配列に格納
    var file_names = [];
    $('#input_files_list input[type="checkbox"]:checked').each(function() {
        file_names.push($(this).val()); // 選択されたファイル名を追加
    });
    // チェックボックスの選択状態を解除（必要に応じてコメントアウト）
    //$('#input_files_list input[type="checkbox"]').prop('checked', false);
    // フォームデータを作成
    var formData = {
        user_id: $('#user_id').val(),
        from_port: '',
        to_port: $('#to_port').val(),
        req_mode: req_mode,
        system_text: system_text,
        request_text: request_text,
        input_text: input_text,
        file_names: file_names,
        result_savepath: result_savepath,
        result_schema: result_schema
    };
    // サーバーにリクエストを送信
    $.ajax({
        url: CORE_ENDPOINT1 + '/post_req',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData), // フォームデータをJSON形式に変換
        success: function(response) {
            console.log('post_req:', response); // レスポンスをログに表示
        },
        error: function(xhr, status, error) {
            console.error('post_req error:', error); // エラーログを出力
            alert(error); // エラーメッセージを表示
        }
    });
}

// urlからテキスト抽出 実行
function url_to_text() {
    $.ajax({
        url: '/get_url_to_text',
        method: 'GET',
        async: false, // 同期処理
        data: { url_path: $('#url_path').val() },
        success: function(data) {
            $('#url_text').val(data.result_text);
            console.log('get_url_to_text:', response); // レスポンスをログに表示
        },
        error: function(xhr, status, error) {
            console.error('get_url_to_text error:', error); // エラーログを出力
        }
    });
}

// url ±１ 実行
function url_1_add() {
    var url = $('#url_path').val();
    var newUrl = url.replace(/\/\d+\//, function(match) {
        var numStr = match.match(/\d+/)[0];
        var newNum = parseInt(numStr) + 1;
        return "/" + newNum + "/";
    });
    $('#url_path').val(newUrl);
}
function url_1_sub() {
    var url = $('#url_path').val();
    var newUrl = url.replace(/\/\d+\//, function(match) {
        var numStr = match.match(/\d+/)[0];
        var newNum = parseInt(numStr) - 1;
        return "/" + newNum + "/";
    });
    $('#url_path').val(newUrl);
}

// リクエスト送信 実行
async function submit_execute(auto_speech) {
    $('#last_text').val('');
    $('#speech_text').val('');
    post_request('chat', $('#sys_text').val(), $('#req_text').val(), $('#url_text').val(), '', $('#res_json').val());

    // 実行待機
    await waitForBusy();
    await waitForIdol();
    await sleep(5000);
    get_output_log_user();

    await sleep(1000);
    if (auto_speech !== 'yes') {
        post_speech_json( $('#last_text').val(), 'no' );
        alert('完了!')    
    } else {
        post_speech_json( $('#last_text').val(), 'yes' );
        url_1_add();
        url_to_text();
    }
}

// TTS出力(text)
function post_tts_text(speech_text) {
    $.ajax({
        url: '/post_tts_text',
        method: 'POST',
        async: false, // 同期処理
        contentType: 'application/json',
        data: JSON.stringify({ speech_text: speech_text }),
        success: function(response) {
            console.log('post_tts_text:', response); // レスポンスをログに表示
        },
        error: function(xhr, status, error) {
            console.error('post_tts_text error:', error); // エラーログを出力
        }
    });
}

// TTS出力(csv)
function post_tts_csv(speech_text) {
    $.ajax({
        url: '/post_tts_csv',
        method: 'POST',
        async: false, // 同期処理
        contentType: 'application/json',
        data: JSON.stringify({ speech_text: speech_text }),
        success: function(response) {
            console.log('post_tts_csv:', response); // レスポンスをログに表示
        },
        error: function(xhr, status, error) {
            console.error('post_tts_csv error:', error); // エラーログを出力
        }
    });
}

// json text をサーバーに送信
function post_speech_json(speech_json, tts_yesno) {
    $('#speech_text').val('');
    // フォームデータを作成
    var formData = {
        speech_json: speech_json,
        speaker_male1: $('#speaker_male1').val(),
        speaker_male2: $('#speaker_male2').val(),
        speaker_female1: $('#speaker_female1').val(),
        speaker_female2: $('#speaker_female2').val(),
        speaker_etc: $('#speaker_etc').val(),
        tts_yesno: tts_yesno
    };
    $.ajax({
        url: '/post_speech_json',
        method: 'POST',
        async: false, // 同期処理
        contentType: 'application/json',
        data: JSON.stringify(formData), // フォームデータをJSON形式に変換
        success: function(response) {
            console.log('post_speech_json:', response); // レスポンスをログに表示
            // テキストエリアの内容を更新
            $('#speech_text').val(response.speech_text || '');
        },
        error: function(xhr, status, error) {
            console.error('post_speech_json error:', error); // エラーログを出力
            alert(error); // エラーメッセージを表示
        }
    });
}



// ドキュメントが読み込まれた時に実行される処理
$(document).ready(function() {

    // ローカルストレージからデータ復元
    const storedData = JSON.parse(localStorage.getItem('urlSpeech_formData'));

    // データが存在する場合
    if (storedData) {
        // テキストエリアの内容を復元
        $('#url_path').val(storedData.url_path || '');
        $('#url_text').val(storedData.url_text || '');
        $('#req_text').val(storedData.req_text || '');
        $('#res_json').val(storedData.res_json || '');
        $('#last_text').val(storedData.last_text || '');
        $('#speech_text').val(storedData.speech_text || '');
        $('#speaker_male1').val(storedData.speaker_male1 || '');
        $('#speaker_male2').val(storedData.speaker_male2 || '');
        $('#speaker_female1').val(storedData.speaker_female1 || '');
        $('#speaker_female2').val(storedData.speaker_female2 || '');
        $('#speaker_etc').val(storedData.speaker_etc || '');
    }

    // ページ遷移時にローカルストレージに保存
    window.onbeforeunload = function() {
        // フォームデータを取得
        var formData = {
            url_path: $('#url_path').val(),
            url_text: $('#url_text').val(),
            req_text: $('#req_text').val(),
            res_json: $('#res_json').val(),
            last_text: $('#last_text').val(),
            speech_text: $('#speech_text').val(),
            speaker_male1: $('#speaker_male1').val(),
            speaker_male2: $('#speaker_male2').val(),
            speaker_female1: $('#speaker_female1').val(),
            speaker_female2: $('#speaker_female2').val(),
            speaker_etc: $('#speaker_etc').val(),
        };
        // ローカルストレージに保存
        localStorage.setItem('urlSpeech_formData', JSON.stringify(formData));
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

    // 音声合成ボタンのクリックイベント
    $('#tts-url-button').click(function() {
        post_tts_text( $('#url_text').val() );
    });
    $('#tts-speech-button').click(function() {
        post_tts_csv( $('#speech_text').val() );
    });

    // 小説家になろう ボタンのクリックイベント
    $('#url-seijyo-1').click(function() {
        $('#url_path').val('https://ncode.syosetu.com/n8976gy/1/');
        $('#req_text').val( $('#req_doc').val() );
        $('#res_json').val( $('#schema_doc').val() );
        url_to_text();
    });
    $('#url-honzuki-1').click(function() {
        $('#url_path').val('https://ncode.syosetu.com/n4830bu/1/');
        $('#req_text').val( $('#req_doc').val() );
        $('#res_json').val( $('#schema_doc').val() );
        url_to_text();
    });
    $('#url-honzuki-594').click(function() {
        $('#url_path').val('https://ncode.syosetu.com/n4830bu/594/');
        $('#req_text').val( $('#req_doc').val() );
        $('#res_json').val( $('#schema_doc').val() );
        url_to_text();
    });
    $('#url-tensura-1').click(function() {
        $('#url_path').val('https://ncode.syosetu.com/n6316bn/1/');
        $('#req_text').val( $('#req_doc').val() );
        $('#res_json').val( $('#schema_doc').val() );
        url_to_text();
    });
    $('#url-tensura-283').click(function() {
        $('#url_path').val('https://ncode.syosetu.com/n6316bn/283/');
        $('#req_text').val( $('#req_doc').val() );
        $('#res_json').val( $('#schema_doc').val() );
        url_to_text();
    });
    $('#url1add-button').click(function() {
        url_1_add();
        url_to_text();
    });
    $('#url1sub-button').click(function() {
        url_1_sub();
        url_to_text();
    });

    // urlからテキスト抽出 ボタンのクリックイベント
    $('#url2text-button').click(function() {
        url_to_text();
    });
    $('#auto-url2speech-button').click(function() {
        url_to_text();
        submit_execute('yes');
    });

    // リクエスト送信 ボタンのクリックイベント
    $('#submit-button').click(function() {
        submit_execute('no');
    });

    // json text ボタンのクリックイベント
    $('#post-json-text-button').click(function() {
        post_speech_json( $('#last_text').val(), 'no' );
    });
    $('#post-json-tts-button').click(function() {
        post_speech_json( $('#last_text').val(), 'yes' );
    });

});
