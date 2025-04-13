// input.js

// 親ウィンドウにメッセージを送信する関数
function sendMessageToParent(action, method, data) {
    window.parent.postMessage({ action: action, method: method, data: data }, '*');
}

// 入力ファイルのリストを保持する配列
let currentInputFiles = []; 

// 日時文字列を時刻のみの文字列に変換する関数
function formatDateTime(dateTimeStr) {
    var date = new Date(dateTimeStr);
    var hours = date.getHours().toString().padStart(2, '0'); // 時間を2桁にフォーマット
    var minutes = date.getMinutes().toString().padStart(2, '0'); // 分を2桁にフォーマット
    return `${hours}:${minutes}`; // フォーマットされた時間を返す
}

// ユーザーの入力履歴を取得し、入力エリアを更新する関数
let lastInputData = {};
function get_input_log_user() {
    $.ajax({
        url: $('#core_endpoint1').val() + '/get_input_log_user',
        method: 'GET',
        data: { user_id: $('#user_id').val() },
        success: function(data) {
            if (data !== null) {
                // 受信データと前回データが異なる場合
                if(JSON.stringify(data) !== JSON.stringify(lastInputData)) {

                    // テキストエリアの内容を更新
                    if (data.system_text !== 'same,') {
                        $('#system_text').val(data.system_text);
                        $('#system_text').addClass('blink-border');
                    }
                    if (data.request_text !== 'same,') {
                        $('#request_text').val(data.request_text);
                        $('#request_text').addClass('blink-border');
                    }
                    if (data.input_text !== 'same,') {
                        $('#input_text').val(data.input_text);
                        $('#input_text').addClass('blink-border');
                    }
                    
                    // アニメーション終了後にクラスを削除
                    setTimeout(() => {
                        $('#system_text').removeClass('blink-border');
                        $('#request_text').removeClass('blink-border');
                        $('#input_text').removeClass('blink-border');
                    }, 2000); // アニメーション時間(2秒)

                }
                // 最新のデータを保持
                lastInputData = data;
            }
        },
        error: function(xhr, status, error) {
            console.error('get_input_log_user error:', error); // エラーログを出力
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
        url: $('#core_endpoint0').val() + '/post_req',
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

// 入力ファイルリストを更新する関数
function updateInputFileList(files) {
    $('#input_files_list').empty(); // 既存のリストをクリア
    if (files.length === 0) {
        // ファイルリストが空の場合、リストを非表示にして空メッセージを表示
        $('#input_files_list').hide();
        $('#input_files_empty').show(); // 空メッセージを表示
    } else {
        // ファイルリストが空でない場合、リストを表示して空メッセージを非表示
        $('#input_files_list').show();
        $('#input_files_empty').hide();
        
        // 各ファイルをリストに追加
        files.forEach(file => {
            // フォーマットされた日時を取得
            var formattedTime = formatDateTime(file.upd_time);
            var li = $('<li>');
            var checkbox = $('<input>').attr({
                type:    'checkbox',
                checked: file.checked,
                value:   file.file_name
            });
            li.append(checkbox).append(`${file.file_name} (${formattedTime})`);
            $('#input_files_list').append(li);
        });
        
        // ファイルリストが更新されたことを示すアニメーション
        $('#input_files').addClass('blink-border');
        setTimeout(() => {
            $('#input_files').removeClass('blink-border');
        }, 2000); // アニメーション時間(2秒)
    }
}

// ドロップされたファイルをサーバーに送信する関数
function post_drop_files(files) {
    var formData = new FormData(); // FormDataオブジェクトを作成
    $.each(files, function(index, file) {
        formData.append('files', file); // 各ファイルをFormDataに追加
    });
    
    $.ajax({
        url: '/post_drop_files', // ファイル送信のエンドポイント
        method: 'POST',
        data: formData,
        processData: false, // jQueryによるデータ処理を無効化
        contentType: false, // コンテンツタイプを無効化
        success: function(data) {
            updateInputFileList(data.files); // ファイルリストを更新
        },
        error: function(xhr, status, error) {
            console.error('post_drop_files error:', error); // エラーログを出力
        }
    });
}

// サーバーから入力ファイルリストを取得し、更新する関数
function get_input_list() {
    $.ajax({
        url: $('#core_endpoint0').val() + '/get_input_list', // ファイルリスト取得のエンドポイント
        method: 'GET',
        success: function(data) {
            // ファイルリストが更新された場合のみ、リストを更新
            if (JSON.stringify(data.files) !== JSON.stringify(currentInputFiles)) {
                updateInputFileList(data.files);
            }
            currentInputFiles = data.files; // 現在のファイルリストを更新
        },
        error: function(xhr, status, error) {
            console.error('get_input_list error:', error); // エラーログを出力
        }
    });
}

// 複数ファイルをサーバーに送信する関数 (dropAreaを追加)
function post_text_files(files, dropArea) {
    const dropTarget = $(dropArea).data('drop-target'); // ドロップターゲットを取得
    var formData = new FormData(); // FormDataオブジェクトを作成
    
    // 各ファイルをFormDataに追加
    for (var i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }
    
    formData.append('drop_target', dropTarget); // ドロップターゲットを追加
    
    // Ajax通信でサーバーに送信
    $.ajax({
        url: '/post_text_files', // ファイルアップロードのエンドポイント
        method: 'POST',
        data: formData,
        processData: false, // jQueryによるデータ処理を無効化
        contentType: false, // コンテンツタイプを無効化
        success: function(response) {
            // サーバーからのレスポンスを取得
            // レスポンスをinput_textエリアに追加
            if (dropTarget === 'system_text') {
                $(dropArea).val(response.drop_text); // system_textにテキストを設定
            } else if (dropTarget === 'request_text') {
                $(dropArea).val(response.drop_text); // request_textにテキストを設定
            } else if (dropTarget === 'input_text') {
                $(dropArea).val($(dropArea).val() + response.drop_text); // input_textにテキストを追加
            }
        },
        error: function(xhr, status, error) {
            console.error('post_text_files error:', error); // エラーログを出力
        }
    });
}

// subai コンボ設定
function get_subai_info_all() {
    $.ajax({
        url: $('#core_endpoint0').val() + '/get_subai_info_all',
        method: 'GET',
        async: false, // 同期処理
        success: function(data) {
            $.each(data, function(port, info) {
                // ポート情報をコンボボックスに追加
                $('#to_port').append(`<option value="${port}">${port} (${info.nick_name})</option>`);
            });
        },
        error: function(xhr, status, error) {
            console.error('get_subai_info_all error:', error); // エラーログを出力
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



// ドキュメントが読み込まれた時に実行される処理
$(document).ready(function() {

    // 初期表示設定
    $('#input_files_list').hide(); // 入力ファイルリストを非表示
    $('#input_files_empty').show(); // 空メッセージを表示

    // subai コンボ設定
    get_subai_info_all(); // subai情報を取得

    // ページ遷移時にlocalStorageから復元
    const storedData = JSON.parse(localStorage.getItem('input_formData'));
    if (storedData) {
        $('#req_mode').val(storedData.req_mode || 'chat'); // リクエストモードを設定
        $('#to_port').val(storedData.to_port || ''); // ポートを設定
        $('#system_text').val(storedData.system_text || 'あなたは美しい日本語を話す賢いアシスタントです。'); // 初期システムテキストを設定
        $('#request_text').val(storedData.request_text || ''); // リクエストテキストを設定
        $('#input_text').val(storedData.input_text || ''); // 入力テキストを設定
    }

    // ページ遷移時にlocalStorageに保存
    window.onbeforeunload = function() {
        var formData = {
            req_mode: $('#req_mode').val(), // リクエストモードを取得
            to_port: $('#to_port').val(), // ポートを取得
            system_text: $('#system_text').val(), // システムテキストを取得
            request_text: $('#request_text').val(), // リクエストテキストを取得
            input_text: $('#input_text').val(), // 入力テキストを取得
        };
        localStorage.setItem('input_formData', JSON.stringify(formData)); // localStorageに保存
    };

    // 定期的な更新処理
    get_input_log_user(); // 入力履歴を取得
    get_input_list(); // 入力ファイルリストを取得
    setInterval(get_input_log_user, 2000); // 2秒ごとに入力履歴を更新
    setInterval(get_input_list, 3000); // 3秒ごとに入力ファイルリストを更新

    // 各テキストエリアにダブルクリックイベントを追加
    const textAreas = document.querySelectorAll('textarea');
    for (const textarea of textAreas) {
        textarea.addEventListener('dblclick', function() {
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

    // ドラッグ＆ドロップの処理
    $('#input_files').on('dragover', function(event) {
        event.preventDefault(); // デフォルトの動作をキャンセル
        $(this).addClass('hover'); // ホバー効果を追加
    }).on('dragleave', function(event) {
        event.preventDefault(); // デフォルトの動作をキャンセル
        $(this).removeClass('hover'); // ホバー効果を削除
    }).on('drop', function(event) {
        event.preventDefault(); // デフォルトの動作をキャンセル
        $(this).removeClass('hover'); // ホバー効果を削除
        var files = event.originalEvent.dataTransfer.files; // ドロップされたファイルを取得
        post_drop_files(files); // ファイルをサーバーに送信
    });

    // ドラッグ＆ドロップエリアの設定 (共通化)
    const dropAreas = document.querySelectorAll('#system_text, #request_text, #input_text');

    // ドラッグオーバーイベントの処理 (共通化)
    dropAreas.forEach(dropArea => {
        dropArea.addEventListener('dragover', (e) => {
            e.preventDefault(); // デフォルトの動作をキャンセル
            e.stopPropagation(); // イベントのバブリングを停止
            dropArea.style.backgroundColor = '#e1e7f0'; // ドラッグオーバー時の背景色を設定
        });
        
        // ドラッグリーブイベントの処理 (共通化)
        dropArea.addEventListener('dragleave', (e) => {
            e.preventDefault(); // デフォルトの動作をキャンセル
            e.stopPropagation(); // イベントのバブリングを停止
            dropArea.style.backgroundColor = ''; // 背景色を元に戻す
        });
        
        // ドロップイベントのリスナー (共通化)
        dropArea.addEventListener('drop', (e) => {
            e.preventDefault(); // デフォルトの動作をキャンセル
            e.stopPropagation(); // イベントのバブリングを停止
            dropArea.style.backgroundColor = ''; // 背景色を元に戻す
            
            // ドロップされたファイルを取得
            var files = e.dataTransfer.files;
            
            // ファイルがドロップされた場合
            if (files.length > 0) {
                post_text_files(files, dropArea); // ファイルをサーバーに送信
            }
        });
    });

    // クリアボタンのクリックイベント
    $('#clear-button').click(function() {
        if ($('#input_text').val().trim() === '') {
            $('#request_text').val('');
        }
        $('#input_text').val('');
        // クリア通知をサーバーに送信
        $.ajax({
            url: $('#core_endpoint1').val() + '/post_clear',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ user_id: $('#user_id').val() }), // ユーザーIDを送信
            success: function(response) {
                console.log('post_clear:', response); // レスポンスをログに表示
            },
            error: function(xhr, status, error) {
                console.error('post_clear error:', error); // エラーログを出力
            }
        });
    });

    // 送信ボタンのクリックイベント
    $('#submit-button').click(function() {
        post_request($('#req_mode').val(), $('#system_text').val(), $('#request_text').val(), $('#input_text').val(), '', '');
    });

    // リセットボタンのクリックイベント
    $('#reset-button').click(function() {
        if (confirm("全ての設定をリセットしますか?")) {
            // 初期値にリセット
            $('#to_port').val('');
            
            // リセット通知をサーバーに送信
            $.ajax({
                url: $('#core_endpoint1').val() + '/post_reset',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ user_id: $('#user_id').val() }), // ユーザーIDを送信
                success: function(response) {
                    console.log('post_reset:', response); // レスポンスをログに表示
                },
                error: function(xhr, status, error) {
                    console.error('post_reset error:', error); // エラーログを出力
                }
            });
        }
    });

    // キャンセルボタンのクリックイベント
    $('#cancel-button').click(function() {
        if (confirm("実行中の要求を全てキャンセルしますか?")) {
            // キャンセル通知をサーバーに送信
            $.ajax({
                url: $('#core_endpoint1').val() + '/post_cancel',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ user_id: $('#user_id').val() }), // ユーザーIDを送信
                success: function(response) {
                    console.log('post_cancel:', response); // レスポンスをログに表示
                },
                error: function(xhr, status, error) {
                    console.error('post_cancel error:', error); // エラーログを出力
                }
            });
        }
    });

    // 入力欄からリクエスト欄へのクリックイベント
    $('#set-request-button').click(function() {
        $('#request_text').val( $('#request_text').val() + '\n' + $('#input_text').val() );
        $('#input_text').val('');
    });

    // 出力データ置換ボタンのクリックイベント
    $('#set-outData-button').click(function() {
        // 出力データを親ウィンドウに送信
        sendMessageToParent('setOutputData', 'set', $('#input_text').val() );
    });

    // 音声入力ボタンのクリックイベント
    $('#stt-req-button').click(function() {
        $.ajax({
            url: '/get_stt',
            method: 'GET',
            data: { input_field: 'request_text' },
            success: function(data) {
                $('#request_text').val(data.recognition_text);
                console.log('get_stt:', response); // レスポンスをログに表示
            },
            error: function(xhr, status, error) {
                console.error('get_stt error:', error); // エラーログを出力
            }
        });
    });
    $('#stt-inp-button').click(function() {
        $.ajax({
            url: '/get_stt',
            method: 'GET',
            data: { input_field: 'input_text' },
            success: function(data) {
                $('#input_text').val(data.recognition_text);
                console.log('get_stt:', response); // レスポンスをログに表示
            },
            error: function(xhr, status, error) {
                console.error('get_stt error:', error); // エラーログを出力
            }
        });
    });

    // 音声合成ボタンのクリックイベント
    $('#tts-req-button').click(function() {
        post_tts_text( $('#request_text').val() );
    });
    $('#tts-inp-button').click(function() {
        post_tts_text( $('#input_text').val() );
    });

});
