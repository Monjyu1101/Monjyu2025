// setting_engine.js

// サブAI設定のコンボボックスを取得する関数
function get_subai_info_all() {
    $.ajax({
        url: $('#core_endpoint0').val() + '/get_subai_info_all',
        method: 'GET',
        async: false, // 同期処理
        success: function(data) {
            var i = 0;
            $.each(data, function(port, info) {
                // サブAIのポート情報を追加
                i += 1;
                if (i <= 20) {
                    $('#parallel_max_ai_count').append(`<option value="${i}">${i}</option>`);
                }
            });
        },
        error: function(xhr, status, error) {
            console.error('get_subai_info_all error:', error);
        }
    });
}

// モデルの情報を取得してコンボボックスを設定する関数
function get_models() {
    // serial
    $.ajax({
        url: $('#core_endpoint0').val() + '/get_models',
        method: 'GET',
        data: { req_mode: 'serial' },
        dataType: 'json',
        async: false, // 同期処理
        success: function(data) {
            // 取得したモデルの選択肢を設定
            for (var [key, value] of Object.entries(data)) {
                $('#serial_req_engine').append(`<option value="${key}">${value}</option>`);
                $('#serial_before_engine').append(`<option value="${key}">${value}</option>`);
                $('#serial_after_engine').append(`<option value="${key}">${value}</option>`);
                $('#serial_check_engine').append(`<option value="${key}">${value}</option>`);
            }
        },
        error: function(xhr, status, error) {
            console.error('get_models (serial) error:', error);
        }
    });
    // parallel, session
    $.ajax({
        url: $('#core_endpoint0').val() + '/get_models',
        method: 'GET',
        data: { req_mode: 'parallel' },
        dataType: 'json',
        async: false, // 同期処理
        success: function(data) {
            // 取得したモデルの選択肢を設定
            for (var [key, value] of Object.entries(data)) {
                $('#parallel_req_engine').append(`<option value="${key}">${value}</option>`);
                $('#parallel_before_engine').append(`<option value="${key}">${value}</option>`);
                $('#parallel_after_engine').append(`<option value="${key}">${value}</option>`);
                $('#parallel_check_engine').append(`<option value="${key}">${value}</option>`);
                $('#session_req_engine').append(`<option value="${key}">${value}</option>`);
                $('#session_before_engine').append(`<option value="${key}">${value}</option>`);
                $('#session_after_engine').append(`<option value="${key}">${value}</option>`);
                $('#session_check_engine').append(`<option value="${key}">${value}</option>`);
            }
        },
        error: function(xhr, status, error) {
            console.error('get_models (parallel) error:', error);
        }
    });
    // chat, vision, websearch, clip, voice
    $.ajax({
        url: $('#core_endpoint0').val() + '/get_models',
        method: 'GET',
        data: { req_mode: 'chat' },
        dataType: 'json',
        async: false, // 同期処理
        success: function(data) {
            // 取得したモデルの選択肢を設定
            for (var [key, value] of Object.entries(data)) {
                $('#chat_req_engine').append(`<option value="${key}">${value}</option>`);
                $('#chat_before_engine').append(`<option value="${key}">${value}</option>`);
                $('#chat_after_engine').append(`<option value="${key}">${value}</option>`);
                $('#chat_check_engine').append(`<option value="${key}">${value}</option>`);
                $('#vision_req_engine').append(`<option value="${key}">${value}</option>`);
                $('#vision_before_engine').append(`<option value="${key}">${value}</option>`);
                $('#vision_after_engine').append(`<option value="${key}">${value}</option>`);
                $('#vision_check_engine').append(`<option value="${key}">${value}</option>`);
                $('#websearch_req_engine').append(`<option value="${key}">${value}</option>`);
                $('#websearch_before_engine').append(`<option value="${key}">${value}</option>`);
                $('#websearch_after_engine').append(`<option value="${key}">${value}</option>`);
                $('#websearch_check_engine').append(`<option value="${key}">${value}</option>`);
                $('#clip_req_engine').append(`<option value="${key}">${value}</option>`);
                $('#clip_before_engine').append(`<option value="${key}">${value}</option>`);
                $('#clip_after_engine').append(`<option value="${key}">${value}</option>`);
                $('#clip_check_engine').append(`<option value="${key}">${value}</option>`);
                $('#voice_req_engine').append(`<option value="${key}">${value}</option>`);
                $('#voice_before_engine').append(`<option value="${key}">${value}</option>`);
                $('#voice_after_engine').append(`<option value="${key}">${value}</option>`);
                $('#voice_check_engine').append(`<option value="${key}">${value}</option>`);
            }
        },
        error: function(xhr, status, error) {
            console.error('get_models (chat) error:', error);
        }
    });
}

// リトライの最大数を設定するコンボボックスを生成する関数
function set_max_retry() {
    for (var j = 1; j <= 3; j++) {
        $('#chat_max_retry').append(`<option value="${j}">${j}</option>`);
        $('#vision_max_retry').append(`<option value="${j}">${j}</option>`);
        $('#websearch_max_retry').append(`<option value="${j}">${j}</option>`);
        $('#serial_max_retry').append(`<option value="${j}">${j}</option>`);
        $('#parallel_max_retry').append(`<option value="${j}">${j}</option>`);
        $('#session_max_retry').append(`<option value="${j}">${j}</option>`);
        $('#clip_max_retry').append(`<option value="${j}">${j}</option>`);
        $('#voice_max_retry').append(`<option value="${j}">${j}</option>`);
    }
}

// 最後の設定値を保持するオブジェクト
let last_mode_setting = {
    chat: null,
    vision: null,
    websearch: null,
    serial: null,
    parallel: null,
    session: null,
    clip: null,
    voice: null
};

// サーバーから設定値を取得する関数
function get_mode_setting_all() {
    get_mode_setting('chat');
    get_mode_setting('vision');
    get_mode_setting('websearch');
    get_mode_setting('serial');
    get_mode_setting('parallel');
    get_mode_setting('session');
    get_mode_setting('clip');
    get_mode_setting('voice');
}

// 指定されたモードの設定値を取得する関数
function get_mode_setting(req_mode) {
    // 設定値をサーバーから受信
    $.ajax({
        url: $('#core_endpoint4').val() + '/get_mode_setting',
        method: 'GET',
        data: { req_mode: req_mode },
        dataType: 'json',
        success: function(data) {

            // chat
            if (req_mode === 'chat') {
                if (JSON.stringify(data) !== last_mode_setting.chat) {
                    $('#chat_req_engine').val(data.req_engine || '');
                    $('#chat_req_functions').val(data.req_functions || '');
                    $('#chat_req_reset').val(data.req_reset || '');
                    $('#chat_max_retry').val(data.max_retry || '');
                    $('#chat_max_ai_count').val(data.max_ai_count || '');
                    $('#chat_before_proc').val(data.before_proc || '');
                    $('#chat_before_engine').val(data.before_engine || '');
                    $('#chat_after_proc').val(data.after_proc || '');
                    $('#chat_after_engine').val(data.after_engine || '');
                    $('#chat_check_proc').val(data.check_proc || '');
                    $('#chat_check_engine').val(data.check_engine || '');
                    last_mode_setting.chat = JSON.stringify(data);
                }    
            }

            // vision
            if (req_mode === 'vision') {
                if (JSON.stringify(data) !== last_mode_setting.vision) {
                    $('#vision_req_engine').val(data.req_engine || '');
                    $('#vision_req_functions').val(data.req_functions || '');
                    $('#vision_req_reset').val(data.req_reset || '');
                    $('#vision_max_retry').val(data.max_retry || '');
                    $('#vision_max_ai_count').val(data.max_ai_count || '');
                    $('#vision_before_proc').val(data.before_proc || '');
                    $('#vision_before_engine').val(data.before_engine || '');
                    $('#vision_after_proc').val(data.after_proc || '');
                    $('#vision_after_engine').val(data.after_engine || '');
                    $('#vision_check_proc').val(data.check_proc || '');
                    $('#vision_check_engine').val(data.check_engine || '');
                    last_mode_setting.vision = JSON.stringify(data);
                }    
            }

            // websearch
            if (req_mode === 'websearch') {
                if (JSON.stringify(data) !== last_mode_setting.websearch) {
                    $('#websearch_req_engine').val(data.req_engine || '');
                    $('#websearch_req_functions').val(data.req_functions || '');
                    $('#websearch_req_reset').val(data.req_reset || '');
                    $('#websearch_max_retry').val(data.max_retry || '');
                    $('#websearch_max_ai_count').val(data.max_ai_count || '');
                    $('#websearch_before_proc').val(data.before_proc || '');
                    $('#websearch_before_engine').val(data.before_engine || '');
                    $('#websearch_after_proc').val(data.after_proc || '');
                    $('#websearch_after_engine').val(data.after_engine || '');
                    $('#websearch_check_proc').val(data.check_proc || '');
                    $('#websearch_check_engine').val(data.check_engine || '');
                    last_mode_setting.websearch = JSON.stringify(data);
                }    
            }

            // serial
            if (req_mode === 'serial') {
                if (JSON.stringify(data) !== last_mode_setting.serial) {
                    $('#serial_req_engine').val(data.req_engine || '');
                    $('#serial_req_functions').val(data.req_functions || '');
                    $('#serial_req_reset').val(data.req_reset || '');
                    $('#serial_max_retry').val(data.max_retry || '');
                    $('#serial_max_ai_count').val(data.max_ai_count || '');
                    $('#serial_before_proc').val(data.before_proc || '');
                    $('#serial_before_engine').val(data.before_engine || '');
                    $('#serial_after_proc').val(data.after_proc || '');
                    $('#serial_after_engine').val(data.after_engine || '');
                    $('#serial_check_proc').val(data.check_proc || '');
                    $('#serial_check_engine').val(data.check_engine || '');
                    last_mode_setting.serial = JSON.stringify(data);
                }    
            }

            // parallel
            if (req_mode === 'parallel') {
                if (JSON.stringify(data) !== last_mode_setting.parallel) {
                    $('#parallel_req_engine').val(data.req_engine || '');
                    $('#parallel_req_functions').val(data.req_functions || '');
                    $('#parallel_req_reset').val(data.req_reset || '');
                    $('#parallel_max_retry').val(data.max_retry || '');
                    $('#parallel_max_ai_count').val(data.max_ai_count || '');
                    $('#parallel_before_proc').val(data.before_proc || '');
                    $('#parallel_before_engine').val(data.before_engine || '');
                    $('#parallel_after_proc').val(data.after_proc || '');
                    $('#parallel_after_engine').val(data.after_engine || '');
                    $('#parallel_check_proc').val(data.check_proc || '');
                    $('#parallel_check_engine').val(data.check_engine || '');
                    last_mode_setting.parallel = JSON.stringify(data);
                }    
            }

            // session
            if (req_mode === 'session') {
                if (JSON.stringify(data) !== last_mode_setting.session) {
                    $('#session_req_engine').val(data.req_engine || '');
                    $('#session_req_functions').val(data.req_functions || '');
                    $('#session_req_reset').val(data.req_reset || '');
                    $('#session_max_retry').val(data.max_retry || '');
                    $('#session_max_ai_count').val(data.max_ai_count || '');
                    $('#session_before_proc').val(data.before_proc || '');
                    $('#session_before_engine').val(data.before_engine || '');
                    $('#session_after_proc').val(data.after_proc || '');
                    $('#session_after_engine').val(data.after_engine || '');
                    $('#session_check_proc').val(data.check_proc || '');
                    $('#session_check_engine').val(data.check_engine || '');
                    last_mode_setting.session = JSON.stringify(data);
                }    
            }

            // clip
            if (req_mode === 'clip') {
                if (JSON.stringify(data) !== last_mode_setting.clip) {
                    $('#clip_req_engine').val(data.req_engine || '');
                    $('#clip_req_functions').val(data.req_functions || '');
                    $('#clip_req_reset').val(data.req_reset || '');
                    $('#clip_max_retry').val(data.max_retry || '');
                    $('#clip_max_ai_count').val(data.max_ai_count || '');
                    $('#clip_before_proc').val(data.before_proc || '');
                    $('#clip_before_engine').val(data.before_engine || '');
                    $('#clip_after_proc').val(data.after_proc || '');
                    $('#clip_after_engine').val(data.after_engine || '');
                    $('#clip_check_proc').val(data.check_proc || '');
                    $('#clip_check_engine').val(data.check_engine || '');
                    last_mode_setting.clip = JSON.stringify(data);
                }    
            }

            // voice
            if (req_mode === 'voice') {
                if (JSON.stringify(data) !== last_mode_setting.voice) {
                    $('#voice_req_engine').val(data.req_engine || '');
                    $('#voice_req_functions').val(data.req_functions || '');
                    $('#voice_req_reset').val(data.req_reset || '');
                    $('#voice_max_retry').val(data.max_retry || '');
                    $('#voice_max_ai_count').val(data.max_ai_count || '');
                    $('#voice_before_proc').val(data.before_proc || '');
                    $('#voice_before_engine').val(data.before_engine || '');
                    $('#voice_after_proc').val(data.after_proc || '');
                    $('#voice_after_engine').val(data.after_engine || '');
                    $('#voice_check_proc').val(data.check_proc || '');
                    $('#voice_check_engine').val(data.check_engine || '');
                    last_mode_setting.voice = JSON.stringify(data);
                }    
            }

        },
        error: function(xhr, status, error) {
            console.error('get_mode_setting error:', error);
        }
    });
}

// サーバーへ設定値を保存する関数
function post_mode_setting(req_mode) {
    var formData = {};

    // chat
    if (req_mode === 'chat') {
        formData = {
            req_mode: req_mode,
            req_engine: $('#chat_req_engine').val(),
            req_functions: $('#chat_req_functions').val(),
            req_reset: $('#chat_req_reset').val(),
            max_retry: $('#chat_max_retry').val(),
            max_ai_count: $('#chat_max_ai_count').val(),
            before_proc: $('#chat_before_proc').val(),
            before_engine: $('#chat_before_engine').val(),
            after_proc: $('#chat_after_proc').val(),
            after_engine: $('#chat_after_engine').val(),
            check_proc: $('#chat_check_proc').val(),
            check_engine: $('#chat_check_engine').val(),
        };
    }

    // vision
    if (req_mode === 'vision') {
        formData = {
            req_mode: req_mode,
            req_engine: $('#vision_req_engine').val(),
            req_functions: $('#vision_req_functions').val(),
            req_reset: $('#vision_req_reset').val(),
            max_retry: $('#vision_max_retry').val(),
            max_ai_count: $('#vision_max_ai_count').val(),
            before_proc: $('#vision_before_proc').val(),
            before_engine: $('#vision_before_engine').val(),
            after_proc: $('#vision_after_proc').val(),
            after_engine: $('#vision_after_engine').val(),
            check_proc: $('#vision_check_proc').val(),
            check_engine: $('#vision_check_engine').val(),
        };
    }

    // websearch
    if (req_mode === 'websearch') {
        formData = {
            req_mode: req_mode,
            req_engine: $('#websearch_req_engine').val(),
            req_functions: $('#websearch_req_functions').val(),
            req_reset: $('#websearch_req_reset').val(),
            max_retry: $('#websearch_max_retry').val(),
            max_ai_count: $('#websearch_max_ai_count').val(),
            before_proc: $('#websearch_before_proc').val(),
            before_engine: $('#websearch_before_engine').val(),
            after_proc: $('#websearch_after_proc').val(),
            after_engine: $('#websearch_after_engine').val(),
            check_proc: $('#websearch_check_proc').val(),
            check_engine: $('#websearch_check_engine').val(),
        };
    }

    // serial
    if (req_mode === 'serial') {
        formData = {
            req_mode: req_mode,
            req_engine: $('#serial_req_engine').val(),
            req_functions: $('#serial_req_functions').val(),
            req_reset: $('#serial_req_reset').val(),
            max_retry: $('#serial_max_retry').val(),
            max_ai_count: $('#serial_max_ai_count').val(),
            before_proc: $('#serial_before_proc').val(),
            before_engine: $('#serial_before_engine').val(),
            after_proc: $('#serial_after_proc').val(),
            after_engine: $('#serial_after_engine').val(),
            check_proc: $('#serial_check_proc').val(),
            check_engine: $('#serial_check_engine').val()
        };
    }

    // parallel
    if (req_mode === 'parallel') {
        formData = {
            req_mode: req_mode,
            req_engine: $('#parallel_req_engine').val(),
            req_functions: $('#parallel_req_functions').val(),
            req_reset: $('#parallel_req_reset').val(),
            max_retry: $('#parallel_max_retry').val(),
            max_ai_count: $('#parallel_max_ai_count').val(),
            before_proc: $('#parallel_before_proc').val(),
            before_engine: $('#parallel_before_engine').val(),
            after_proc: $('#parallel_after_proc').val(),
            after_engine: $('#parallel_after_engine').val(),
            check_proc: $('#parallel_check_proc').val(),
            check_engine: $('#parallel_check_engine').val()
        };
    }

    // session
    if (req_mode === 'session') {
        formData = {
            req_mode: req_mode,
            req_engine: $('#session_req_engine').val(),
            req_functions: $('#session_req_functions').val(),
            req_reset: $('#session_req_reset').val(),
            max_retry: $('#session_max_retry').val(),
            max_ai_count: $('#session_max_ai_count').val(),
            before_proc: $('#session_before_proc').val(),
            before_engine: $('#session_before_engine').val(),
            after_proc: $('#session_after_proc').val(),
            after_engine: $('#session_after_engine').val(),
            check_proc: $('#session_check_proc').val(),
            check_engine: $('#session_check_engine').val(),
        };
    }

    // clip
    if (req_mode === 'clip') {
        formData = {
            req_mode: req_mode,
            req_engine: $('#clip_req_engine').val(),
            req_functions: $('#clip_req_functions').val(),
            req_reset: $('#clip_req_reset').val(),
            max_retry: $('#clip_max_retry').val(),
            max_ai_count: $('#clip_max_ai_count').val(),
            before_proc: $('#clip_before_proc').val(),
            before_engine: $('#clip_before_engine').val(),
            after_proc: $('#clip_after_proc').val(),
            after_engine: $('#clip_after_engine').val(),
            check_proc: $('#clip_check_proc').val(),
            check_engine: $('#clip_check_engine').val(),
        };
    }

    // voice
    if (req_mode === 'voice') {
        formData = {
            req_mode: req_mode,
            req_engine: $('#voice_req_engine').val(),
            req_functions: $('#voice_req_functions').val(),
            req_reset: $('#voice_req_reset').val(),
            max_retry: $('#voice_max_retry').val(),
            max_ai_count: $('#voice_max_ai_count').val(),
            before_proc: $('#voice_before_proc').val(),
            before_engine: $('#voice_before_engine').val(),
            after_proc: $('#voice_after_proc').val(),
            after_engine: $('#voice_after_engine').val(),
            check_proc: $('#voice_check_proc').val(),
            check_engine: $('#voice_check_engine').val(),
        };
    }

    // 設定値をサーバーに送信
    $.ajax({
        url: $('#core_endpoint4').val() + '/post_mode_setting',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(response) {
            console.log('post_mode_setting:', response);
        },
        error: function(xhr, status, error) {
            console.error('post_mode_setting error:', error);
        }
    });
}

// chat-engineのセット
function chat_set_engine(engine) {
    $('#chat_req_engine').val(engine);
    $('#chat_before_engine').val(engine);
    $('#chat_after_engine').val(engine);
    $('#chat_check_engine').val(engine);
    post_mode_setting('chat');
    $('#vision_req_engine').val(engine);
    $('#vision_before_engine').val(engine);
    $('#vision_after_engine').val(engine);
    $('#vision_check_engine').val(engine);
    post_mode_setting('vision');
    $('#websearch_req_engine').val(engine);
    $('#websearch_before_engine').val(engine);
    $('#websearch_after_engine').val(engine);
    $('#websearch_check_engine').val(engine);
    post_mode_setting('websearch');
    $('#clip_req_engine').val(engine);
    $('#clip_before_engine').val(engine);
    $('#clip_after_engine').val(engine);
    $('#clip_check_engine').val(engine);
    post_mode_setting('clip');
    $('#voice_req_engine').val(engine);
    $('#voice_before_engine').val(engine);
    $('#voice_after_engine').val(engine);
    $('#voice_check_engine').val(engine);
    post_mode_setting('voice');
}

// serial-engineのセット
function serial_set_engine(engine) {
        $('#serial_req_engine').val(engine);
        $('#serial_before_engine').val(engine);
        $('#serial_after_engine').val(engine);
        $('#serial_check_engine').val(engine);
        post_mode_setting('serial');
}

// parallel-engineのセット
function parallel_set_engine(engine) {
        $('#parallel_req_engine').val(engine);
        $('#parallel_before_engine').val(engine);
        $('#parallel_after_engine').val(engine);
        $('#parallel_check_engine').val(engine);
        post_mode_setting('parallel');
        $('#session_req_engine').val(engine);
        $('#session_before_engine').val(engine);
        $('#session_after_engine').val(engine);
        $('#session_check_engine').val(engine);
        post_mode_setting('session');
}

// ドキュメントが読み込まれた時に実行される処理
$(document).ready(function() {

    // ページ遷移時にlocalStorageから復元
    const storedData = JSON.parse(localStorage.getItem('setting_engine_formData'));
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
        localStorage.setItem('setting_engine_formData', JSON.stringify(formData)); // localStorageに保存
    };

    // サブAI設定を取得
    get_subai_info_all();

    // モデルの設定を取得
    get_models();

    // リトライの設定を行う
    set_max_retry();

    // 定期的に設定値を取得する処理
    get_mode_setting_all();
    setInterval(get_mode_setting_all, 3000);

    // 設定項目が変更された際に保存
    $('#chat_req_engine, #chat_req_functions, #chat_req_reset, #chat_max_retry, #chat_max_ai_count').change(function() {
        post_mode_setting('chat');
    });
    $('#chat_before_proc, #chat_before_engine, #chat_after_proc, #chat_after_engine, #chat_check_proc, #chat_check_engine').change(function() {
        post_mode_setting('chat');
    });
    $('#vision_req_engine, #vision_req_functions, #vision_req_reset, #vision_max_retry, #vision_max_ai_count').change(function() {
        post_mode_setting('vision');
    });
    $('#vision_before_proc, #vision_before_engine, #vision_after_proc, #vision_after_engine, #vision_check_proc, #vision_check_engine').change(function() {
        post_mode_setting('vision');
    });
    $('#websearch_req_engine, #websearch_req_functions, #websearch_req_reset, #websearch_max_retry, #websearch_max_ai_count').change(function() {
        post_mode_setting('websearch');
    });
    $('#websearch_before_proc, #websearch_before_engine, #websearch_after_proc, #websearch_after_engine, #websearch_check_proc, #websearch_check_engine').change(function() {
        post_mode_setting('websearch');
    });
    $('#serial_req_engine, #serial_req_functions, #serial_req_reset, #serial_max_retry, #serial_max_ai_count').change(function() {
        post_mode_setting('serial');
    });
    $('#serial_before_proc, #serial_before_engine, #serial_after_proc, #serial_after_engine, #serial_check_proc, #serial_check_engine').change(function() {
        post_mode_setting('serial');
    });
    $('#parallel_req_engine, #parallel_req_functions, #parallel_req_reset, #parallel_max_retry, #parallel_max_ai_count').change(function() {
        post_mode_setting('parallel');
    });
    $('#parallel_before_proc, #parallel_before_engine, #parallel_after_proc, #parallel_after_engine, #parallel_check_proc, #parallel_check_engine').change(function() {
        post_mode_setting('parallel');
    });
    $('#session_req_engine, #session_req_functions, #session_req_reset, #session_max_retry, #session_max_ai_count').change(function() {
        post_mode_setting('session');
    });
    $('#session_before_proc, #session_before_engine, #session_after_proc, #session_after_engine, #session_check_proc, #session_check_engine').change(function() {
        post_mode_setting('session');
    });
    $('#clip_req_engine, #clip_req_functions, #clip_req_reset, #clip_max_retry, #clip_max_ai_count').change(function() {
        post_mode_setting('clip');
    });
    $('#clip_before_proc, #clip_before_engine, #clip_after_proc, #clip_after_engine, #clip_check_proc, #clip_check_engine').change(function() {
        post_mode_setting('clip');
    });
    $('#voice_req_engine, #voice_req_functions, #voice_req_reset, #voice_max_retry, #voice_max_ai_count').change(function() {
        post_mode_setting('voice');
    });
    $('#voice_before_proc, #voice_before_engine, #voice_after_proc, #voice_after_engine, #voice_check_proc, #voice_check_engine').change(function() {
        post_mode_setting('voice');
    });
    
    // リセットボタンのクリックイベント
    $('#reset-button').click(function() {
        if (confirm("全ての設定をリセットしますか?")) {
            // リセット処理を実行
            $.ajax({
                url: $('#core_endpoint1').val() + '/post_reset',
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

    // chat-engineボタンのクリックイベント
    $('#chat-auto').click(function() {
        chat_set_engine('');
    });
    $('#chat-freeai').click(function() {
        chat_set_engine('[freeai]');
    });
    $('#chat-openrt').click(function() {
        chat_set_engine('[openrt]');
    });
    $('#chat-openai').click(function() {
        chat_set_engine('[openai]');
    });
    $('#chat-grok').click(function() {
        chat_set_engine('[grok]');
    });

    // serial-engineボタンのクリックイベント
    $('#serial-auto').click(function() {
        serial_set_engine('');
    });
    $('#serial-freeai').click(function() {
        serial_set_engine('[freeai]');
    });
    $('#serial-openrt').click(function() {
        serial_set_engine('[openrt]');
    });

    // parallel-engineボタンのクリックイベント
    $('#parallel-auto').click(function() {
        parallel_set_engine('');
    });
    $('#parallel-freeai').click(function() {
        parallel_set_engine('[freeai]');
    });
    $('#parallel-openrt').click(function() {
        parallel_set_engine('[openrt]');
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
