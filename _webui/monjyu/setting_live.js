// setting_live.js

const CORE_ENDPOINT1 = 'http://localhost:8001';
const CORE_ENDPOINT2 = 'http://localhost:8002';
const CORE_ENDPOINT3 = 'http://localhost:8003';
const CORE_ENDPOINT4 = 'http://localhost:8004';
const CORE_ENDPOINT5 = 'http://localhost:8005';

// 最後の設定値を保持するオブジェクト
let last_live_setting = {
    freeai: null,
    openai: null,
}

// Liveのmodel情報を取得してコンボボックスを設定する関数
function get_live_models(engine) {
    $.ajax({
        url: CORE_ENDPOINT4 + '/get_live_models',
        method: 'GET',
        data: { engine: engine },
        dataType: 'json',
        async: false, // 同期処理
        success: function(data) {

            // freeai
            if (engine === 'freeai') {
                // 取得した選択肢を設定
                for (var [key, value] of Object.entries(data)) {
                    $('#freeai_live_model').append(`<option value="${key}">${value}</option>`);
                }
                last_live_models.freeai = JSON.stringify(data);
            }

            // openai
            if (engine === 'openai') {
                // 取得した選択肢を設定
                for (var [key, value] of Object.entries(data)) {
                    $('#openai_live_model').append(`<option value="${key}">${value}</option>`);
                }
                last_live_models.openai = JSON.stringify(data);
            }

        },
        error: function(xhr, status, error) {
            console.error('get_live_models error:', error);
        }
    });
}

// Liveのvoice情報を取得してコンボボックスを設定する関数
function get_live_voices(engine) {
    $.ajax({
        url: CORE_ENDPOINT4 + '/get_live_voices',
        method: 'GET',
        data: { engine: engine },
        dataType: 'json',
        async: false, // 同期処理
        success: function(data) {

            // freeai
            if (engine === 'freeai') {
                // 取得した選択肢を設定
                for (var [key, value] of Object.entries(data)) {
                    $('#freeai_live_voice').append(`<option value="${key}">${value}</option>`);
                }
            }

            // openai
            if (engine === 'openai') {
                // 取得した選択肢を設定
                for (var [key, value] of Object.entries(data)) {
                    $('#openai_live_voice').append(`<option value="${key}">${value}</option>`);
                }
            }

        },
        error: function(xhr, status, error) {
            console.error('get_live_voices error:', error);
        }
    });
}

// サーバーからLive設定を取得する関数
function get_live_setting_all() {
    get_live_setting('freeai');
    get_live_setting('openai');
}
function get_live_setting(engine) {
    // Live設定をサーバーから受信
    $.ajax({
        url: CORE_ENDPOINT4 + '/get_live_setting',
        method: 'GET',
        data: { engine: engine },
        dataType: 'json',
        success: function(data) {

            // freeai
            if (engine === 'freeai') {
                if (JSON.stringify(data) !== last_live_setting.freeai) {
                    $('#freeai_live_model').val(data.live_model || '');
                    $('#freeai_live_voice').val(data.live_voice || '');
                    $('#freeai_shot_interval_sec').val(data.shot_interval_sec || '');
                    $('#freeai_clip_interval_sec').val(data.clip_interval_sec || '');
                    last_live_setting.freeai = JSON.stringify(data);
                }
            }

            // openai
            if (engine === 'openai') {
                if (JSON.stringify(data) !== last_live_setting.openai) {
                    $('#openai_live_model').val(data.live_model || '');
                    $('#openai_live_voice').val(data.live_voice || '');
                    $('#openai_shot_interval_sec').val(data.shot_interval_sec || '');
                    $('#openai_clip_interval_sec').val(data.clip_interval_sec || '');
                    last_live_setting.openai = JSON.stringify(data);
                }
            }

        },
        error: function(xhr, status, error) {
            console.error('get_live_setting error:', error);
        }
    });
}

// サーバーへLive設定を保存する関数
function post_live_setting(engine) {
    var formData = {};

    // freeai
    if (engine === 'freeai') {
        formData = {
            engine: engine,
            live_model: $('#freeai_live_model').val(),
            live_voice: $('#freeai_live_voice').val(),
            shot_interval_sec: $('#freeai_shot_interval_sec').val(),
            clip_interval_sec: $('#freeai_clip_interval_sec').val(),
        };
    }

    // openai
    if (engine === 'openai') {
        formData = {
            engine: engine,
            live_model: $('#openai_live_model').val(),
            live_voice: $('#openai_live_voice').val(),
            shot_interval_sec: $('#openai_shot_interval_sec').val(),
            clip_interval_sec: $('#openai_clip_interval_sec').val(),
        };
    }

    // Live設定をサーバーに送信
    $.ajax({
        url: CORE_ENDPOINT4 + '/post_live_setting',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(response) {
            console.log('post_live_setting:', response);
        },
        error: function(xhr, status, error) {
            console.error('post_live_setting error:', error);
        }
    });
}

// Live出力(text)
function post_live_request(live_req, live_text) {
    $.ajax({
        url: CORE_ENDPOINT5 + '/post_live_request',
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

    // ページ遷移時にlocalStorageから復元
    const storedData = JSON.parse(localStorage.getItem('setting_live_formData'));
    if (storedData) {
        // ページ開始時に保存されたタブを復元
        var activeTab = storedData.activeTab || 'reset';
        $('.tab-content').removeClass('active');
        $('.tab-header button').removeClass('active');
        $('#' + activeTab).addClass('active');
        $('.tab-header button[data-target="' + activeTab + '"]').addClass('active');
        // 入力欄
        $('#freeai_live_request').val(storedData.freeai_live_request || '');
        $('#openai_live_request').val(storedData.openai_live_request || '');
    }

    // ページ遷移時にlocalStorageに保存
    window.onbeforeunload = function() {
        var formData = {
            // ページ遷移時にlocalStorageに保存
            activeTab: $('.tab-header button.active').data('target'),
            // 入力欄
            freeai_live_request: $('#freeai_live_request').val(),
            openai_live_request: $('#openai_live_request').val(),
        };
        localStorage.setItem('setting_live_formData', JSON.stringify(formData));
    };

    // Liveのmodels設定を取得
    get_live_models('freeai');
    get_live_models('openai');

    // Liveのvoices設定を取得
    get_live_voices('freeai');
    get_live_voices('openai');

    // 定期的に設定値を取得する処理
    setInterval(get_live_setting_all, 3000);

    $('#freeai_live_model, #freeai_live_voice, #freeai_shot_interval_sec, #freeai_clip_interval_sec').change(function() {
        post_live_setting('freeai');
    });
    $('#openai_live_model, #openai_live_voice, #openai_shot_interval_sec, #openai_clip_interval_sec').change(function() {
        post_live_setting('openai');
    });

    $('#freeai-live-button').click(function() {
        post_live_request( '', $('#freeai_live_request').val() );
        // アニメーション(2秒)
        $('#freeai_live_request').addClass('blink-border');
        setTimeout(() => {
            $('#freeai_live_request').removeClass('blink-border');
        }, 2000);
    });
    $('#openai-live-button').click(function() {
        post_live_request( '', $('#openai_live_request').val() );
        // アニメーション(2秒)
        $('#openai_live_request').addClass('blink-border');
        setTimeout(() => {
            $('#openai_live_request').removeClass('blink-border');
        }, 2000);
    });
    
    // リセットボタンのクリックイベント
    $('#reset-button').click(function() {
        if (confirm("全ての設定をリセットしますか?")) {
            // リセット処理を実行
            $.ajax({
                url: CORE_ENDPOINT2 + '/post_reset',
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
