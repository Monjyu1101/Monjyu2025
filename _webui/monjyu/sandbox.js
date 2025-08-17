// react.js

const CORE_ENDPOINT1 = 'http://localhost:8001';
const CORE_ENDPOINT2 = 'http://localhost:8002';
const CORE_ENDPOINT3 = 'http://localhost:8003';
const CORE_ENDPOINT4 = 'http://localhost:8004';
const CORE_ENDPOINT5 = 'http://localhost:8005';

// 最後の設定値を保持するオブジェクト
let last_sandbox_update = null;

// サーバーから設定値を取得する関数
function get_sandbox_update() {
    // 設定値をサーバーから受信
    $.ajax({
        url: '/get_sandbox_update',
        method: 'GET',
        success: function(data) {
            if (JSON.stringify(data) !== last_sandbox_update) {
                if (data.sandbox_update) {
                    $('#sandbox_file').text(data.sandbox_file || '');
                }
                last_sandbox_update = JSON.stringify(data);
            }    
        },
        error: function(xhr, status, error) {
            console.error('get_sandbox_update error:', error);
        }
    });
}

// コード表示
function post_sandbox_open() {
    $.ajax({
        url: '/post_sandbox_open',
        method: 'POST',
        contentType: 'application/json',
        success: function(response) {
            console.log('post_sandbox_open:', response);
        },
        error: function(xhr, status, error) {
            console.error('post_sandbox_open error:', error);
        }
    });
}

// Reactを差し替える関数
function post_set_react(filename) {
    var formData = {};
    formData = {
        filename: filename,
    }
    // 設定値をサーバーに送信
    $.ajax({
        url: '/post_set_react',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(response) {
            console.log('post_set_react:', response);
        },
        error: function(xhr, status, error) {
            console.error('post_set_react error:', error);
        }
    });
}

// ドキュメントが読み込まれた時に実行される処理
$(document).ready(function() {
   
    // 定期的に設定値を取得する処理
    setInterval(get_sandbox_update, 3000);

    $('#btn-sandbox-open').click(function() {
        post_sandbox_open();
    });

    $('#btn-react_sandbox').click(function() {
        post_set_react('react_sandbox.zip');
    });

});
