// mainui.js

const CORE_ENDPOINT1 = 'http://localhost:8001';
const CORE_ENDPOINT2 = 'http://localhost:8002';
const CORE_ENDPOINT3 = 'http://localhost:8003';
const CORE_ENDPOINT4 = 'http://localhost:8004';
const CORE_ENDPOINT5 = 'http://localhost:8005';

// メッセージ受信のイベントリスナー
function add_event_listener() {
    window.addEventListener('message', function(event) {

        // リクエストテキスト設定
        if (event.data.action === 'setRequestText') {
            if (event.data.method !== 'add') {
                window.iframeInput.document.getElementById('request_text').value = event.data.data;
            } else {
                var currentText = window.iframeInput.document.getElementById('request_text').value;
                window.iframeInput.document.getElementById('request_text').value = currentText + '\n' + event.data.data;    
            }
        } 

        // 入力テキスト設定
        else if (event.data.action === 'setInputText') {
            if (event.data.method !== 'add') {
                window.iframeInput.document.getElementById('input_text').value = event.data.data;
            } else {
                var currentText = window.iframeInput.document.getElementById('input_text').value;
                window.iframeInput.document.getElementById('input_text').value = currentText + '\n' + event.data.data;    
            }
        } 

        // 出力データ設定
        else if (event.data.action === 'setOutputData') {
            if (event.data.method !== 'add') {
                window.iframeOutput.document.getElementById('output_data').value = event.data.data;
            } else {
                var currentText = window.iframeOutput.document.getElementById('output_data').value;
                window.iframeOutput.document.getElementById('output_data').value = currentText + '\n' + event.data.data;
            }
        }

        // リクエスト実行
        else if (event.data.action === 'requestRun') {
            var reqMode = event.data.method;
            if (reqMode === 'req_mode') {
                reqMode = window.iframeInput.document.getElementById('req_mode').value
            }
            var sysText = window.iframeInput.document.getElementById('system_text').value;
            var reqText = window.iframeInput.document.getElementById('request_text').value;
            var inpText = window.iframeInput.document.getElementById('input_text').value;
            window.iframeInput.post_request(reqMode, sysText, reqText, inpText, event.data.data, '');
        }

        // デバッグ実行
        else if (event.data.action === 'debugRun') {
            var reqMode = event.data.method;
            if (reqMode === 'req_mode') {
                reqMode = window.iframeInput.document.getElementById('req_mode').value
            }
            var sysText = window.iframeInput.document.getElementById('system_text').value;
            var reqText = window.iframeInput.document.getElementById('request_text').value;
            var inpText = window.iframeInput.document.getElementById('input_text').value;
            window.iframeInput.post_request(reqMode, sysText, "debug,\n" + reqText, inpText, '', '');
        }
       
    }, false);

}

// ドキュメント読み込み完了時の処理
$(document).ready(function() {

    // ページ遷移時にlocalStorageから復元
    const storedData = JSON.parse(localStorage.getItem('mainui_formData'));
    if (storedData) {
        // ページ開始時に保存されたタブを復元(左側)
        var activeTab_left = storedData.activeTab_left || 'input';
        $('.frame-left .tab-content').removeClass('active');
        $('.frame-left .tab-header button').removeClass('active');
        $('.frame-left #' + activeTab_left).addClass('active');
        $('.frame-left .tab-header button[data-target="' + activeTab_left + '"]').addClass('active');

        // ページ開始時に保存されたタブを復元(右側)
        var activeTab_right = storedData.activeTab_right || 'output';
        $('.frame-right .tab-content').removeClass('active');
        $('.frame-right .tab-header button').removeClass('active');
        $('.frame-right #' + activeTab_right).addClass('active');
        $('.frame-right .tab-header button[data-target="' + activeTab_right + '"]').addClass('active');
    }

    // ページ遷移時にlocalStorageに保存
    window.onbeforeunload = function() {
        var formData = {
            // ページ遷移時にlocalStorageに保存
            activeTab_left: $('.frame-left .tab-header button.active').data('target'),
            activeTab_right: $('.frame-right .tab-header button.active').data('target')
        };
        localStorage.setItem('mainui_formData', JSON.stringify(formData)); // localStorageに保存
    };

    // メッセージ受信のイベントリスナー
    add_event_listener();

    // iframeの読み込み完了時
    $('#iframe-input').on('load', function() {
        window.iframeInput = document.getElementById('iframe-input').contentWindow;
    });
    $('#iframe-output').on('load', function() {
        window.iframeOutput = document.getElementById('iframe-output').contentWindow;
    });
    $('#iframe-writing').on('load', function() {
        window.iframeWriting = document.getElementById('iframe-writing').contentWindow;
    });
    $('#iframe-url').on('load', function() {
        window.iframeUrl = document.getElementById('iframe-url').contentWindow;
    });

    // タブ切り替え機能
    $('.frame-left .tab-header button, .frame-right .tab-header button').click(function() {
        var target = $(this).data('target');
        var frame = $(this).closest('.frame-left, .frame-right');

        // アクティブなボタンとコンテンツを切り替え
        frame.find('.tab-header button').removeClass('active');
        $(this).addClass('active');
        frame.find('.tab-content').removeClass('active');
        frame.find('#' + target).addClass('active');
    });

});
