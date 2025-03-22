// chat.js

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

// 親ウィンドウにメッセージを送信する関数
function sendMessageToParent(action, method, data) {
    window.parent.postMessage({ action: action, method: method, data: data }, '*');
}

// 入力ファイルのリストを保持する配列
let currentInputFiles = []; 

// 日時文字列を時刻のみの文字列に変換する関数
function formatDateTime(dateTimeStr) {
    var date = new Date(dateTimeStr);
    var hours = date.getHours().toString().padStart(2, '0');
    var minutes = date.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
}

// チャット履歴を表示する関数
function displayChatHistory(histories) {
    const container = $('#message-container');
    container.empty();

    // 最新の10件を表示
    const sortedHistories = Object.entries(histories)
        .sort((a, b) => a[0] - b[0])
        .slice(-10);

    sortedHistories.forEach(([key, history]) => {
        // 出力時間の表示用
        const outTime = history.out_time ? history.out_time.split(' ')[1] : '';
        
        // ユーザーのリクエストメッセージ
        if (history.req_text) {
            const userMessage = $('<div>').addClass('message user-message');
            userMessage.html(escapeHtml(history.req_text).replace(/\n/g, '<br>'));
            
            const userTimestamp = $('<div>').addClass('timestamp');
            userTimestamp.text(outTime);
            userMessage.append(userTimestamp);
            
            container.append(userMessage);
        }
        
        // AIの応答メッセージ
        if (history.out_text) {
            const aiMessage = $('<div>').addClass('message ai-message');
            aiMessage.html(escapeHtml(history.out_text).replace(/\n/g, '<br>'));
            
            const aiTimestamp = $('<div>').addClass('timestamp');
            aiTimestamp.text(outTime);
            aiMessage.append(aiTimestamp);
            
            container.append(aiMessage);
        }
    });

    // スクロールを最下部に
    const historyContainer = $('.chat-history');
    historyContainer.scrollTop(historyContainer[0].scrollHeight);
}

// 履歴を取得して表示する関数
function getAndDisplayChatHistory() {
    $.ajax({
        url: $('#core_endpoint').val() + '/get_histories_all',
        type: 'GET',
        data: { user_id: $('#user_id').val() },
        success: function(data) {
            displayChatHistory(data);
        },
        error: function(xhr, status, error) {
            console.error('get_histories_all error:', error);
        }
    });
}

// リクエストをサーバーに送信する共通関数
function post_request(req_mode, system_text, request_text, input_text, result_savepath, result_schema) {
    // チェックボックスが選択されているファイル名を配列に格納
    var file_names = [];
    $('#input_files_list input[type="checkbox"]:checked').each(function() {
        file_names.push($(this).val());
    });
    
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
    
    // ユーザーメッセージをすぐに表示
    const userMessage = $('<div>').addClass('message user-message');
    userMessage.html(escapeHtml(request_text).replace(/\n/g, '<br>'));
    
    const userTimestamp = $('<div>').addClass('timestamp');
    const now = new Date();
    userTimestamp.text(`${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`);
    userMessage.append(userTimestamp);
    
    $('#message-container').append(userMessage);
    
    // 「処理中...」メッセージを表示
    const typingMessage = $('<div>').addClass('message ai-message').attr('id', 'typing-message');
    typingMessage.text('処理中...');
    $('#message-container').append(typingMessage);
    
    // スクロールを最下部に
    const historyContainer = $('.chat-history');
    historyContainer.scrollTop(historyContainer[0].scrollHeight);
    
    // サーバーにリクエストを送信
    $.ajax({
        url: $('#core_endpoint').val() + '/post_req',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(response) {
            console.log('post_req:', response);
            // 送信成功を親フレームに通知
            sendMessageToParent('output', 'updated', {});
            
            // 応答を取得するためのポーリングを開始
            pollForResponse();
        },
        error: function(xhr, status, error) {
            // 「入力中...」メッセージを削除
            $('#typing-message').remove();
            
            console.error('post_req error:', error);
            alert(error);
        }
    });
}

// サーバーから応答を取得するポーリング関数
function pollForResponse() {
    $.ajax({
        url: $('#core_endpoint').val() + '/get_output_log_user',
        method: 'GET',
        data: { user_id: $('#user_id').val() },
        success: function(data) {
            if (data && data.output_text) {
                // 「入力中...」メッセージを削除
                $('#typing-message').remove();
                
                // 履歴を再表示
                getAndDisplayChatHistory();
                
                // 入力エリアをクリア
                $('#request_text').val('');
            } else {
                // 応答がまだなければ再度ポーリング
                setTimeout(pollForResponse, 1000);
            }
        },
        error: function(xhr, status, error) {
            console.error('get_output_log_user error:', error);
            // エラー時も再度ポーリング
            setTimeout(pollForResponse, 1000);
        }
    });
}

// 入力ファイルリストを更新する関数
function updateInputFileList(files) {
    $('#input_files_list').empty();
    if (files.length === 0) {
        $('#input_files_list').hide();
        $('#input_files_empty').show();
    } else {
        $('#input_files_list').show();
        $('#input_files_empty').hide();
        
        files.forEach(file => {
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
        
        $('#input_files').addClass('blink-border');
        setTimeout(() => {
            $('#input_files').removeClass('blink-border');
        }, 2000);
    }
}

// ドロップされたファイルをサーバーに送信する関数
function post_drop_files(files) {
    var formData = new FormData();
    $.each(files, function(index, file) {
        formData.append('files', file);
    });
    
    $.ajax({
        url: '/post_drop_files',
        method: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(data) {
            updateInputFileList(data.files);
        },
        error: function(xhr, status, error) {
            console.error('post_drop_files error:', error);
        }
    });
}

// サーバーから入力ファイルリストを取得し、更新する関数
function get_input_list() {
    $.ajax({
        url: '/get_input_list',
        method: 'GET',
        success: function(data) {
            if (JSON.stringify(data.files) !== JSON.stringify(currentInputFiles)) {
                updateInputFileList(data.files);
            }
            currentInputFiles = data.files;
        },
        error: function(xhr, status, error) {
            console.error('get_input_list error:', error);
        }
    });
}

// ファイルをテキストとして読み込む関数
function post_text_files(files, dropArea) {
    const dropTarget = $(dropArea).data('drop-target');
    var formData = new FormData();
    
    for (var i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }
    
    formData.append('drop_target', dropTarget);
    
    $.ajax({
        url: '/post_text_files',
        method: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (dropTarget === 'request_text') {
                $(dropArea).val(response.drop_text);
            }
        },
        error: function(xhr, status, error) {
            console.error('post_text_files error:', error);
        }
    });
}

// subai コンボ設定
function get_subai_info_all() {
    $.ajax({
        url: $('#core_endpoint').val() + '/get_subai_info_all',
        method: 'GET',
        async: false,
        success: function(data) {
            $.each(data, function(port, info) {
                $('#to_port').append(`<option value="${port}">${port} (${info.nick_name})</option>`);
            });
        },
        error: function(xhr, status, error) {
            console.error('get_subai_info_all error:', error);
        }
    });
}

// チャット履歴をクリアする関数
function clearChat() {
    // メッセージコンテナをクリア
    $('#message-container').empty();
    
    // クリア通知をサーバーに送信
    $.ajax({
        url: $('#core_endpoint').val() + '/post_clear',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ user_id: $('#user_id').val() }),
        success: function(response) {
            console.log('post_clear:', response);
            // 入力フィールドをクリア
            $('#request_text').val('');
        },
        error: function(xhr, status, error) {
            console.error('post_clear error:', error);
        }
    });
}

// ドキュメントが読み込まれた時に実行される処理
$(document).ready(function() {
    // 初期表示設定
    $('#input_files_list').hide();
    $('#input_files_empty').show();

    // subai コンボ設定
    get_subai_info_all();

    // チャット履歴を表示
    getAndDisplayChatHistory();
    
    // 定期的に履歴を更新
    setInterval(getAndDisplayChatHistory, 5000);

    // ページ遷移時にlocalStorageから復元
    const storedData = JSON.parse(localStorage.getItem('chat_formData'));
    if (storedData) {
        $('#req_mode').val(storedData.req_mode || 'chat');
        $('#to_port').val(storedData.to_port || '');
        $('#request_text').val(storedData.request_text || '');
    }

    // ページ遷移時にlocalStorageに保存
    window.onbeforeunload = function() {
        var formData = {
            req_mode: $('#req_mode').val(),
            to_port: $('#to_port').val(),
            request_text: $('#request_text').val(),
        };
        localStorage.setItem('chat_formData', JSON.stringify(formData));
    };

    // 定期的な更新処理
    get_input_list();
    setInterval(get_input_list, 3000);

    // テキストエリアにダブルクリックイベントを追加
    const textAreas = document.querySelectorAll('textarea');
    for (const textarea of textAreas) {
        textarea.addEventListener('dblclick', function() {
            $(this).select();
            var text = this.value;
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

    // ドラッグ＆ドロップの処理
    $('#input_files').on('dragover', function(event) {
        event.preventDefault();
        $(this).addClass('hover');
    }).on('dragleave', function(event) {
        event.preventDefault();
        $(this).removeClass('hover');
    }).on('drop', function(event) {
        event.preventDefault();
        $(this).removeClass('hover');
        var files = event.originalEvent.dataTransfer.files;
        post_drop_files(files);
    });

    // ドラッグ＆ドロップエリアの設定
    const dropAreas = document.querySelectorAll('#request_text');

    dropAreas.forEach(dropArea => {
        dropArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropArea.style.backgroundColor = '#e1e7f0';
        });
        
        dropArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropArea.style.backgroundColor = '';
        });
        
        dropArea.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropArea.style.backgroundColor = '';
            
            var files = e.dataTransfer.files;
            
            if (files.length > 0) {
                post_text_files(files, dropArea);
            }
        });
    });

    // クリアボタンのクリックイベント
    $('#clear-button').click(function() {
        $('#request_text').val('');
        $('#input_text').val('');
        // クリア通知をサーバーに送信
        $.ajax({
            url: $('#core_endpoint').val() + '/post_clear',
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
        const req = $('#request_text').val().trim();
        if (req) {
            post_request($('#req_mode').val(), $('#system_text').val(), req, '', '', '');
        }
    });

});