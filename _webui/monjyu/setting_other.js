// setting_other.js

// 最後の設定値を保持するオブジェクト
let last_addins_setting = null;

// サーバーから設定値を取得する関数
function get_addins_setting() {
    // 設定値をサーバーから受信
    $.ajax({
        url: '/get_addins_setting',
        method: 'GET',
        success: function(data) {
            if (JSON.stringify(data) !== last_addins_setting) {
                $('#result_text_save').val(data.result_text_save || '');
                $('#speech_stt_engine').val(data.speech_stt_engine || '');
                $('#speech_tts_engine').val(data.speech_tts_engine || '');
                $('#text_clip_input').val(data.text_clip_input || '');
                $('#text_url_execute').val(data.text_url_execute || '');
                $('#text_pdf_execute').val(data.text_pdf_execute || '');
                $('#image_ocr_execute').val(data.image_ocr_execute || '');
                $('#image_yolo_execute').val(data.image_yolo_execute || '');
                last_addins_setting = JSON.stringify(data);
            }    
        },
        error: function(xhr, status, error) {
            console.error('get_addins_setting error:', error);
        }
    });
}

// サーバーへ設定値を保存する関数
function post_addins_setting() {
    var formData = {};
    formData = {
        result_text_save: $('#result_text_save').val(),
        speech_stt_engine: $('#speech_stt_engine').val(),
        speech_tts_engine: $('#speech_tts_engine').val(),
        text_clip_input: $('#text_clip_input').val(),
        text_url_execute: $('#text_url_execute').val(),
        text_pdf_execute: $('#text_pdf_execute').val(),
        image_ocr_execute: $('#image_ocr_execute').val(),
        image_yolo_execute: $('#image_yolo_execute').val(),
    }
    // 設定値をサーバーに送信
    $.ajax({
        url: '/post_addins_setting',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(response) {
            console.log('post_addins_setting:', response);
        },
        error: function(xhr, status, error) {
            console.error('post_addins_setting error:', error);
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

    // ページ遷移時にlocalStorageから復元
    const storedData = JSON.parse(localStorage.getItem('setting_other_formData'));
    if (storedData) {
        // ページ開始時に保存されたタブを復元
        var activeTab = storedData.activeTab || 'reset';
        $('.tab-content').removeClass('active');
        $('.tab-header button').removeClass('active');
        $('#' + activeTab).addClass('active');
        $('.tab-header button[data-target="' + activeTab + '"]').addClass('active');
    }

    // ページ遷移時にlocalStorageに保存
    window.onbeforeunload = function() {
        var formData = {
            // ページ遷移時にlocalStorageに保存
            activeTab: $('.tab-header button.active').data('target')
        };
        localStorage.setItem('setting_other_formData', JSON.stringify(formData)); // localStorageに保存
    };

    // 定期的に設定値を取得する処理
    setInterval(get_addins_setting, 3000);

    $('#result_text_save, #speech_stt_engine, #speech_tts_engine, #text_clip_input, #text_url_execute, #text_pdf_execute, #image_ocr_execute, #image_yolo_execute').change(function() {
        post_addins_setting();
    });
    
    // リセットボタンのクリックイベント
    $('#reset-button').click(function() {
        if (confirm("全ての設定をリセットしますか?")) {
            // リセット処理を実行
            $.ajax({
                url: $('#core_endpoint').val() + '/post_reset',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ user_id: $('#user_id').val() }),
                success: function(response) {
                    console.log('post_reset:', response);
                },
                error: function(xhr, status, error) {
                    console.error('post_reset error:', error);
                }
            });
        }
    });
    
    $('#btn-react_sandbox').click(function() {
        post_set_react('react_sandbox.zip');
    });
    $('#btn-realtimeConsole-openai').click(function() {
        post_set_react('openai-realtime-console-main.zip');
    });
    $('#btn-realtimeConsole-google').click(function() {
        post_set_react('multimodal-live-api-web-console-main.zip');
    });

    // タブ切り替え処理
    $('.frame-tab .tab-header button').click(function() {
        var target = $(this).data('target');
        var frame = $(this).closest('.frame-tab');
        frame.find('.tab-header button').removeClass('active');
        $(this).addClass('active');
        frame.find('.tab-content').removeClass('active');
        frame.find('#' + target).addClass('active');
    });

});
