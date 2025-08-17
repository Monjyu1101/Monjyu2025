// output.js

const CORE_ENDPOINT1 = 'http://localhost:8001';
const CORE_ENDPOINT2 = 'http://localhost:8002';
const CORE_ENDPOINT3 = 'http://localhost:8003';
const CORE_ENDPOINT4 = 'http://localhost:8004';
const CORE_ENDPOINT5 = 'http://localhost:8005';

// 親ウィンドウにメッセージを送信する関数
function sendMessageToParent(action, method, data) {
    window.parent.postMessage({ action: action, method: method, data: data }, '*');
}

// 前回受信した画像データを保持する変数
let last_image_data = null; 

// 現在出力されているファイルの配列を保持する変数
let currentOutputFiles = [];

// デフォルト画像を取得する関数
function get_default_image() {
    // サーバーからデフォルト画像を取得するAJAXリクエスト
    $.ajax({
        url: CORE_ENDPOINT3 + '/get_default_image',
        method: 'GET',
        success: function(data) {
            // 画像情報を更新
            $('#image_img').attr('src', data.image_data);
            //if (data.image_ext === 'gif') {
                // gif 処理
            //}
        },
        error: function(xhr, status, error) {
            console.error('get_default_image error:', error);
        }
    });
}

// イメージ情報を取得する関数
function get_image_info() {
    // サーバーからイメージ情報を取得するAJAXリクエスト
    $.ajax({
        url: CORE_ENDPOINT3 + '/get_image_info',
        method: 'GET',
        success: function(data) {
            if (data.image_data !== last_image_data) {
                // 画像データが存在する場合
                if (data.image_data) {
                    // 画像情報を更新
                    $('#image_img').attr('src', data.image_data);
                    //if (data.image_ext === 'gif') {
                        // gif 処理
                    //}
                } else {
                    get_default_image();
                }

                // 最新の画像データを保持
                last_image_data = data.image_data;
            }
        },
        error: function(xhr, status, error) {
            console.error('get_image_info error:', error);
        }
    });
}

// 日時をフォーマットする関数
function formatDateTime(dateTimeStr) {
    // 日時文字列をDateオブジェクトに変換
    var date = new Date(dateTimeStr);
    // 時刻を取得し、2桁で表示
    var hours = date.getHours().toString().padStart(2, '0');
    var minutes = date.getMinutes().toString().padStart(2, '0');
    // フォーマットされた日時を返す
    return `${hours}:${minutes}`;
}

// ユーザーの出力履歴を取得し、出力テキストエリアを更新する関数
let lastOutputData = {};
function get_output_log_user() {
    // サーバーからユーザーの出力履歴を取得するAJAXリクエスト
    $.ajax({
        url: CORE_ENDPOINT3 + '/get_output_log_user',
        type: 'GET',
        data: { user_id: $('#user_id').val() },
        success: function(data) {
            // データが存在する場合
            if (data !== null) {
                // 受信データと前回データが異なる場合
                if(JSON.stringify(data) !== JSON.stringify(lastOutputData)) {

                    // テキストエリアの内容を更新
                    $('#output_text').val(data.output_text);
                    $('#output_data').val(data.output_data);

                    // アニメーションを追加
                    $('#output_text').addClass('blink-border');
                    $('#output_data').addClass('blink-border');

                    // アニメーション終了後にクラスを削除
                    setTimeout(() => {
                        $('#output_text').removeClass('blink-border');
                        $('#output_data').removeClass('blink-border');
                    }, 2000); // 2秒間アニメーション

                }
                // 最新のデータを保持
                lastOutputData = data;
            }
        },
        error: function(xhr, status, error) { // パラメータを追加
            console.error('get_output_log_user error:', error); // コロンを追加
        }
    });
}

// 出力ファイルリストを更新する関数
function updateOutputFileList(files) {
    // 出力ファイルリストをクリア
    $('#output_files_list').empty();

    // ファイルが存在しない場合
    if (files.length === 0) {
        // 出力ファイルリストを非表示
        $('#output_files_list').hide();
        // 空のメッセージを表示
        $('#output_files_empty').show();
    } else {
        // 出力ファイルリストを表示
        $('#output_files_list').show();
        // 空のメッセージを非表示
        $('#output_files_empty').hide();

        // 各ファイルに対して処理を行う
        files.forEach(file => {
            var formattedTime = formatDateTime(file.upd_time);
            var li = $('<li>');
            var checkbox = $('<input>').attr({
                type:    'checkbox',
                checked: file.checked,
                value:   file.file_name
            });
            var a = $('<a>').attr('href', '/get_output_file/' + file.file_name)
                              .text(`${file.file_name} (${formattedTime})`);
            li.append(checkbox).append(a);
            $('#output_files_list').append(li);
        });

        // アニメーションを追加
        $('#output_files').addClass('blink-border');

        // アニメーション終了後にクラスを削除
        setTimeout(() => {
            $('#output_files').removeClass('blink-border');
        }, 2000); // 2秒間アニメーション
    }
}

// 出力ファイルリストを取得する関数
function get_output_list() {
    // サーバーから出力ファイルリストを取得するAJAXリクエスト
    $.ajax({
        url: CORE_ENDPOINT3 + '/get_output_list',
        method: 'GET',
        success: function(data) {
            // ファイルリストが更新された場合
            if (JSON.stringify(data.files) !== JSON.stringify(currentOutputFiles)) {
                // 出力ファイルリストを更新
                updateOutputFileList(data.files);
            }
            // 最新の出力ファイルリストを保持
            currentOutputFiles = data.files;
        },
        error: function(xhr, status, error) {
            console.error('get_output_list error:', error);
        }
    });
}

// TTS出力(text)
function post_tts_text(speech_text) {
    $.ajax({
        url: '/post_tts_text',
        method: 'POST',
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

// files_out2inp処理
function post_files_out2inp() {
    $.ajax({
        url: '/post_files_out2inp',
        method: 'POST',
        success: function(response) {
            console.log('post_files_out2inp:', response); // レスポンスをログに表示
        },
        error: function(xhr, status, error) {
            console.error('post_files_out2inp error:', error); // エラーログを出力
        }
    });
}

// Live出力(text)
function post_live_request(live_req, live_text) {
    $.ajax({
        url: '/post_live_request',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ live_req: live_req, live_text: live_text }),
        success: function(response) {
            console.log('post_live_request:', response); // レスポンスをログに表示
        },
        error: function(xhr, status, error) {
            console.error('post_live_request error:', error); // エラーログを出力
        }
    });
}

// ドキュメントが読み込まれた時に実行される処理
$(document).ready(function() {

    // 初期表示設定
    $('#output_files_list').hide();
    $('#output_files_empty').show();

    // デフォルト画像を取得する
    get_default_image();
    get_image_info();

    // localStorageからデータ復元
    const storedData = JSON.parse(localStorage.getItem('output_formData'));

    // データが存在する場合
    if (storedData) {
        // テキストエリアの内容を復元
        $('#output_text').val(storedData.output_text || '');
        $('#output_data').val(storedData.output_data || '');
    }

    // ページ遷移時にlocalStorageに保存
    window.onbeforeunload = function() {
        // フォームデータを取得
        var formData = {
            output_text: $('#output_text').val(),
            output_data: $('#output_data').val(),
        };

        // localStorageに保存
        localStorage.setItem('output_formData', JSON.stringify(formData));
    };

    // 定期的な更新処理
    get_output_log_user();
    get_output_list();
    setInterval(get_image_info,  3000); // 3秒ごとにイメージ情報を更新
    setInterval(get_output_log_user, 2000); // 2秒ごとに出力履歴を更新
    setInterval(get_output_list, 3000); // 3秒ごとに出力ファイルリストを更新

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

    // 入力置換ボタンのクリックイベント
    $('#set-input-button').click(function() {
        // 出力データを親ウィンドウに送信
        sendMessageToParent('setInputText', 'set', $('#output_data').val() );
    });

    // 入力追加ボタンのクリックイベント
    $('#add-input-button').click(function() {
        // 出力データを親ウィンドウに送信
        sendMessageToParent('setInputText', 'add', $('#output_data').val() );
    });

    // 音声合成ボタンのクリックイベント
    $('#tts-text-button').click(function() {
        post_tts_text( $('#output_text').val() );
    });
    $('#tts-data-button').click(function() {
        post_tts_text( $('#output_data').val() );
    });
    $('#set-files-button').click(function() {
        post_files_out2inp();
    });
    $('#live-data-button').click(function() {
        post_live_request( '', $('#output_data').val() );
    });
    $('#live-data-youyaku').click(function() {
        post_live_request( '以下を要約して、音声で教えてください。', $('#output_data').val() );
    });
    $('#live-data-roudoku').click(function() {
        post_live_request( '以下の小説を、感情豊かに朗読してください。', $('#output_data').val() );
    });
    $('#live-data-honyaku').click(function() {
        post_live_request( '以下を日本語に翻訳し要約して、音声で教えてください。', $('#output_data').val() );
    });

});
