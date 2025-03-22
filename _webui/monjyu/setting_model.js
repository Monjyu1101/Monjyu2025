// setting_model.js

// 最後の設定値を保持するオブジェクト
let last_addins_setting = null;
let last_engine_models = {
    chatgpt: null,
    assist: null,
    respo: null,
    gemini: null,
    freeai: null,
    claude: null,
    openrt: null,
    perplexity: null,
    grok: null,
    groq: null,
    ollama: null,
};
let last_engine_setting = {
    chatgpt: null,
    assist: null,
    respo: null,
    gemini: null,
    freeai: null,
    claude: null,
    openrt: null,
    perplexity: null,
    grok: null,
    groq: null,
    ollama: null,
};

// max_wait_secを設定する関数
function add_wait_sec_all() {
    add_wait_sec("30", " 30秒");
    add_wait_sec("60", " 60秒");
    add_wait_sec("120", "120秒");
    add_wait_sec("180", "180秒");
    add_wait_sec("300", "300秒");
    add_wait_sec("600", "600秒");
    add_wait_sec("999", "999秒");
}
function add_wait_sec(key, value) {
    $('#gpt_max_wait_sec').append(`<option value="${key}">${value}</option>`);
    $('#asst_max_wait_sec').append(`<option value="${key}">${value}</option>`);
    $('#resp_max_wait_sec').append(`<option value="${key}">${value}</option>`);
    $('#gemn_max_wait_sec').append(`<option value="${key}">${value}</option>`);
    $('#free_max_wait_sec').append(`<option value="${key}">${value}</option>`);
    $('#clad_max_wait_sec').append(`<option value="${key}">${value}</option>`);
    $('#ort_max_wait_sec').append(`<option value="${key}">${value}</option>`);
    $('#pplx_max_wait_sec').append(`<option value="${key}">${value}</option>`);
    $('#grok_max_wait_sec').append(`<option value="${key}">${value}</option>`);
    $('#groq_max_wait_sec').append(`<option value="${key}">${value}</option>`);
    $('#olm_max_wait_sec').append(`<option value="${key}">${value}</option>`);
}

// エンジンのmodels情報を取得してコンボボックスを設定する関数
function get_engine_models(engine) {
    $.ajax({
        url: '/get_engine_models',
        method: 'GET',
        data: { engine: engine },
        dataType: 'json',
        async: false, // 同期処理
        success: function(data) {

            // オブジェクトの場合、エントリの配列に変換してソートする
            const sortedEntries = Object.entries(data).sort((a, b) => {
                return b[1].localeCompare(a[1]);
            });
            
            // chatgpt
            if (engine === 'chatgpt') {
                if (JSON.stringify(data) !== last_engine_models.chatgpt) {
                    // 既存の選択肢を削除
                    $('#gpt_a_model').empty();
                    $('#gpt_b_model').empty();
                    $('#gpt_v_model').empty();
                    $('#gpt_x_model').empty();
                    // 取得した選択肢を設定
                    $('#gpt_a_model').append(`<option value="">Auto (自動)</option>`);
                    $('#gpt_b_model').append(`<option value="">Auto (自動)</option>`);
                    $('#gpt_v_model').append(`<option value="">Auto (自動)</option>`);
                    $('#gpt_x_model').append(`<option value="">Auto (自動)</option>`);
                    //for (var [key, value] of Object.entries(data)) {
                    sortedEntries.forEach(([key, value]) => {
                        $('#gpt_a_model').append(`<option value="${key}">${value}</option>`);
                        $('#gpt_b_model').append(`<option value="${key}">${value}</option>`);
                        $('#gpt_v_model').append(`<option value="${key}">${value}</option>`);
                        $('#gpt_x_model').append(`<option value="${key}">${value}</option>`);
                    });
                    last_engine_models.chatgpt = JSON.stringify(data);
                }
            }

            // assist
            if (engine === 'assist') {
                if (JSON.stringify(data) !== last_engine_models.assist) {
                    // 既存の選択肢を削除
                    $('#asst_a_model').empty();
                    $('#asst_b_model').empty();
                    $('#asst_v_model').empty();
                    $('#asst_x_model').empty();
                    // 取得した選択肢を設定
                    $('#asst_a_model').append(`<option value="">Auto (自動)</option>`);
                    $('#asst_b_model').append(`<option value="">Auto (自動)</option>`);
                    $('#asst_v_model').append(`<option value="">Auto (自動)</option>`);
                    $('#asst_x_model').append(`<option value="">Auto (自動)</option>`);
                    //for (var [key, value] of Object.entries(data)) {
                    sortedEntries.forEach(([key, value]) => {
                        $('#asst_a_model').append(`<option value="${key}">${value}</option>`);
                        $('#asst_b_model').append(`<option value="${key}">${value}</option>`);
                        $('#asst_v_model').append(`<option value="${key}">${value}</option>`);
                        $('#asst_x_model').append(`<option value="${key}">${value}</option>`);
                    });
                    last_engine_models.assist = JSON.stringify(data);
                }
            }

            // respo
            if (engine === 'respo') {
                if (JSON.stringify(data) !== last_engine_models.respo) {
                    // 既存の選択肢を削除
                    $('#resp_a_model').empty();
                    $('#resp_b_model').empty();
                    $('#resp_v_model').empty();
                    $('#resp_x_model').empty();
                    // 取得した選択肢を設定
                    $('#resp_a_model').append(`<option value="">Auto (自動)</option>`);
                    $('#resp_b_model').append(`<option value="">Auto (自動)</option>`);
                    $('#resp_v_model').append(`<option value="">Auto (自動)</option>`);
                    $('#resp_x_model').append(`<option value="">Auto (自動)</option>`);
                    //for (var [key, value] of Object.entries(data)) {
                    sortedEntries.forEach(([key, value]) => {
                        $('#resp_a_model').append(`<option value="${key}">${value}</option>`);
                        $('#resp_b_model').append(`<option value="${key}">${value}</option>`);
                        $('#resp_v_model').append(`<option value="${key}">${value}</option>`);
                        $('#resp_x_model').append(`<option value="${key}">${value}</option>`);
                    });
                    last_engine_models.respo = JSON.stringify(data);
                }
            }

            // gemini
            if (engine === 'gemini') {
                if (JSON.stringify(data) !== last_engine_models.gemini) {
                    // 既存の選択肢を削除
                    $('#gemn_a_model').empty();
                    $('#gemn_b_model').empty();
                    $('#gemn_v_model').empty();
                    $('#gemn_x_model').empty();
                    // 取得した選択肢を設定
                    $('#gemn_a_model').append(`<option value="">Auto (自動)</option>`);
                    $('#gemn_b_model').append(`<option value="">Auto (自動)</option>`);
                    $('#gemn_v_model').append(`<option value="">Auto (自動)</option>`);
                    $('#gemn_x_model').append(`<option value="">Auto (自動)</option>`);
                    //for (var [key, value] of Object.entries(data)) {
                    sortedEntries.forEach(([key, value]) => {
                        $('#gemn_a_model').append(`<option value="${key}">${value}</option>`);
                        $('#gemn_b_model').append(`<option value="${key}">${value}</option>`);
                        $('#gemn_v_model').append(`<option value="${key}">${value}</option>`);
                        $('#gemn_x_model').append(`<option value="${key}">${value}</option>`);
                    });
                    last_engine_models.gemini = JSON.stringify(data);
                }
            }

            // freeai
            if (engine === 'freeai') {
                if (JSON.stringify(data) !== last_engine_models.freeai) {
                    // 既存の選択肢を削除
                    $('#free_a_model').empty();
                    $('#free_b_model').empty();
                    $('#free_v_model').empty();
                    $('#free_x_model').empty();
                    // 取得した選択肢を設定
                    $('#free_a_model').append(`<option value="">Auto (自動)</option>`);
                    $('#free_b_model').append(`<option value="">Auto (自動)</option>`);
                    $('#free_v_model').append(`<option value="">Auto (自動)</option>`);
                    $('#free_x_model').append(`<option value="">Auto (自動)</option>`);
                    //for (var [key, value] of Object.entries(data)) {
                    sortedEntries.forEach(([key, value]) => {
                        $('#free_a_model').append(`<option value="${key}">${value}</option>`);
                        $('#free_b_model').append(`<option value="${key}">${value}</option>`);
                        $('#free_v_model').append(`<option value="${key}">${value}</option>`);
                        $('#free_x_model').append(`<option value="${key}">${value}</option>`);
                    });
                    last_engine_models.freeai = JSON.stringify(data);
                }
            }

            // claude
            if (engine === 'claude') {
                if (JSON.stringify(data) !== last_engine_models.claude) {
                    // 既存の選択肢を削除
                    $('#clad_a_model').empty();
                    $('#clad_b_model').empty();
                    $('#clad_v_model').empty();
                    $('#clad_x_model').empty();
                    // 取得した選択肢を設定
                    $('#clad_a_model').append(`<option value="">Auto (自動)</option>`);
                    $('#clad_b_model').append(`<option value="">Auto (自動)</option>`);
                    $('#clad_v_model').append(`<option value="">Auto (自動)</option>`);
                    $('#clad_x_model').append(`<option value="">Auto (自動)</option>`);
                    //for (var [key, value] of Object.entries(data)) {
                    sortedEntries.forEach(([key, value]) => {
                        $('#clad_a_model').append(`<option value="${key}">${value}</option>`);
                        $('#clad_b_model').append(`<option value="${key}">${value}</option>`);
                        $('#clad_v_model').append(`<option value="${key}">${value}</option>`);
                        $('#clad_x_model').append(`<option value="${key}">${value}</option>`);
                    });
                    last_engine_models.claude = JSON.stringify(data);
                }
            }

            // openrt
            if (engine === 'openrt') {
                if (JSON.stringify(data) !== last_engine_models.openrt) {
                    // 既存の選択肢を削除
                    $('#ort_a_model').empty();
                    $('#ort_b_model').empty();
                    $('#ort_v_model').empty();
                    $('#ort_x_model').empty();
                    // 取得した選択肢を設定
                    $('#ort_a_model').append(`<option value="">Auto (自動)</option>`);
                    $('#ort_b_model').append(`<option value="">Auto (自動)</option>`);
                    $('#ort_v_model').append(`<option value="">Auto (自動)</option>`);
                    $('#ort_x_model').append(`<option value="">Auto (自動)</option>`);
                    //for (var [key, value] of Object.entries(data)) {
                    sortedEntries.forEach(([key, value]) => {
                        $('#ort_a_model').append(`<option value="${key}">${value}</option>`);
                        $('#ort_b_model').append(`<option value="${key}">${value}</option>`);
                        $('#ort_v_model').append(`<option value="${key}">${value}</option>`);
                        $('#ort_x_model').append(`<option value="${key}">${value}</option>`);
                    });
                    last_engine_models.openrt = JSON.stringify(data);
                }
            }

            // perplexity
            if (engine === 'perplexity') {
                if (JSON.stringify(data) !== last_engine_models.perplexity) {
                    // 既存の選択肢を削除
                    $('#pplx_a_model').empty();
                    $('#pplx_b_model').empty();
                    $('#pplx_v_model').empty();
                    $('#pplx_x_model').empty();
                    // 取得した選択肢を設定
                    $('#pplx_a_model').append(`<option value="">Auto (自動)</option>`);
                    $('#pplx_b_model').append(`<option value="">Auto (自動)</option>`);
                    $('#pplx_v_model').append(`<option value="">Auto (自動)</option>`);
                    $('#pplx_x_model').append(`<option value="">Auto (自動)</option>`);
                    //for (var [key, value] of Object.entries(data)) {
                    sortedEntries.forEach(([key, value]) => {
                        $('#pplx_a_model').append(`<option value="${key}">${value}</option>`);
                        $('#pplx_b_model').append(`<option value="${key}">${value}</option>`);
                        $('#pplx_v_model').append(`<option value="${key}">${value}</option>`);
                        $('#pplx_x_model').append(`<option value="${key}">${value}</option>`);
                    });
                    last_engine_models.perplexity = JSON.stringify(data);
                }
            }

            // grok
            if (engine === 'grok') {
                if (JSON.stringify(data) !== last_engine_models.grok) {
                    // 既存の選択肢を削除
                    $('#grok_a_model').empty();
                    $('#grok_b_model').empty();
                    $('#grok_v_model').empty();
                    $('#grok_x_model').empty();
                    // 取得した選択肢を設定
                    $('#grok_a_model').append(`<option value="">Auto (自動)</option>`);
                    $('#grok_b_model').append(`<option value="">Auto (自動)</option>`);
                    $('#grok_v_model').append(`<option value="">Auto (自動)</option>`);
                    $('#grok_x_model').append(`<option value="">Auto (自動)</option>`);
                    //for (var [key, value] of Object.entries(data)) {
                    sortedEntries.forEach(([key, value]) => {
                        $('#grok_a_model').append(`<option value="${key}">${value}</option>`);
                        $('#grok_b_model').append(`<option value="${key}">${value}</option>`);
                        $('#grok_v_model').append(`<option value="${key}">${value}</option>`);
                        $('#grok_x_model').append(`<option value="${key}">${value}</option>`);
                    });
                    last_engine_models.grok = JSON.stringify(data);
                }
            }

            // groq
            if (engine === 'groq') {
                if (JSON.stringify(data) !== last_engine_models.groq) {
                    // 既存の選択肢を削除
                    $('#groq_a_model').empty();
                    $('#groq_b_model').empty();
                    $('#groq_v_model').empty();
                    $('#groq_x_model').empty();
                    // 取得した選択肢を設定
                    $('#groq_a_model').append(`<option value="">Auto (自動)</option>`);
                    $('#groq_b_model').append(`<option value="">Auto (自動)</option>`);
                    $('#groq_v_model').append(`<option value="">Auto (自動)</option>`);
                    $('#groq_x_model').append(`<option value="">Auto (自動)</option>`);
                    //for (var [key, value] of Object.entries(data)) {
                    sortedEntries.forEach(([key, value]) => {
                        $('#groq_a_model').append(`<option value="${key}">${value}</option>`);
                        $('#groq_b_model').append(`<option value="${key}">${value}</option>`);
                        $('#groq_v_model').append(`<option value="${key}">${value}</option>`);
                        $('#groq_x_model').append(`<option value="${key}">${value}</option>`);
                    });
                    last_engine_models.groq = JSON.stringify(data);
                }
            }

            // ollama
            if (engine === 'ollama') {
                if (JSON.stringify(data) !== last_engine_models.ollama) {
                    // 既存の選択肢を削除
                    $('#olm_a_model').empty();
                    $('#olm_b_model').empty();
                    $('#olm_v_model').empty();
                    $('#olm_x_model').empty();
                    // 取得した選択肢を設定
                    $('#olm_a_model').append(`<option value="">Auto (自動)</option>`);
                    $('#olm_b_model').append(`<option value="">Auto (自動)</option>`);
                    $('#olm_v_model').append(`<option value="">Auto (自動)</option>`);
                    $('#olm_x_model').append(`<option value="">Auto (自動)</option>`);
                    //for (var [key, value] of Object.entries(data)) {
                    sortedEntries.forEach(([key, value]) => {
                        $('#olm_a_model').append(`<option value="${key}">${value}</option>`);
                        $('#olm_b_model').append(`<option value="${key}">${value}</option>`);
                        $('#olm_v_model').append(`<option value="${key}">${value}</option>`);
                        $('#olm_x_model').append(`<option value="${key}">${value}</option>`);
                    });
                    last_engine_models.ollama = JSON.stringify(data);
                }
            }

        },
        error: function(xhr, status, error) {
            console.error('get_engine_models error:', error);
        }
    });
}

// サーバーからエンジンの設定値を取得する関数
function get_engine_setting_all(engine) {
    get_engine_setting('chatgpt');
    get_engine_setting('assist');
    get_engine_setting('respo');
    get_engine_setting('gemini');
    get_engine_setting('freeai');
    get_engine_setting('claude');
    get_engine_setting('openrt');
    get_engine_setting('perplexity');
    get_engine_setting('grok');
    get_engine_setting('groq');
    get_engine_models( 'ollama');
    get_engine_setting('ollama');
}
function get_engine_setting(engine) {
    // 設定値をサーバーから受信
    $.ajax({
        url: '/get_engine_setting',
        method: 'GET',
        data: { engine: engine },
        dataType: 'json',
        success: function(data) {

            // chatgpt
            if (engine === 'chatgpt') {
                if (JSON.stringify(data) !== last_engine_setting.chatgpt) {
                    $('#gpt_a_nick_name').text(data.a_nick_name || '');
                    $('#gpt_b_nick_name').text(data.b_nick_name || '');
                    $('#gpt_v_nick_name').text(data.v_nick_name || '');
                    $('#gpt_x_nick_name').text(data.x_nick_name || '');
                    $('#gpt_max_wait_sec').val(data.max_wait_sec || '');
                    $('#gpt_a_model').val(data.a_model || '');
                    $('#gpt_a_use_tools').val(data.a_use_tools || '');
                    $('#gpt_b_model').val(data.b_model || '');
                    $('#gpt_b_use_tools').val(data.b_use_tools || '');
                    $('#gpt_v_model').val(data.v_model || '');
                    $('#gpt_v_use_tools').val(data.v_use_tools || '');
                    $('#gpt_x_model').val(data.x_model || '');
                    $('#gpt_x_use_tools').val(data.x_use_tools || '');
                    last_engine_setting.chatgpt = JSON.stringify(data);
                }
            }

            // assist
            if (engine === 'assist') {
                if (JSON.stringify(data) !== last_engine_setting.assist) {
                    $('#asst_a_nick_name').text(data.a_nick_name || '');
                    $('#asst_b_nick_name').text(data.b_nick_name || '');
                    $('#asst_v_nick_name').text(data.v_nick_name || '');
                    $('#asst_x_nick_name').text(data.x_nick_name || '');
                    $('#asst_max_wait_sec').val(data.max_wait_sec || '');
                    $('#asst_a_model').val(data.a_model || '');
                    $('#asst_a_use_tools').val(data.a_use_tools || '');
                    $('#asst_b_model').val(data.b_model || '');
                    $('#asst_b_use_tools').val(data.b_use_tools || '');
                    $('#asst_v_model').val(data.v_model || '');
                    $('#asst_v_use_tools').val(data.v_use_tools || '');
                    $('#asst_x_model').val(data.x_model || '');
                    $('#asst_x_use_tools').val(data.x_use_tools || '');
                    last_engine_setting.assist = JSON.stringify(data);
                }
            }

            // respo
            if (engine === 'respo') {
                if (JSON.stringify(data) !== last_engine_setting.respo) {
                    $('#resp_a_nick_name').text(data.a_nick_name || '');
                    $('#resp_b_nick_name').text(data.b_nick_name || '');
                    $('#resp_v_nick_name').text(data.v_nick_name || '');
                    $('#resp_x_nick_name').text(data.x_nick_name || '');
                    $('#resp_max_wait_sec').val(data.max_wait_sec || '');
                    $('#resp_a_model').val(data.a_model || '');
                    $('#resp_a_use_tools').val(data.a_use_tools || '');
                    $('#resp_b_model').val(data.b_model || '');
                    $('#resp_b_use_tools').val(data.b_use_tools || '');
                    $('#resp_v_model').val(data.v_model || '');
                    $('#resp_v_use_tools').val(data.v_use_tools || '');
                    $('#resp_x_model').val(data.x_model || '');
                    $('#resp_x_use_tools').val(data.x_use_tools || '');
                    last_engine_setting.respo = JSON.stringify(data);
                }
            }

            // gemini
            if (engine === 'gemini') {
                if (JSON.stringify(data) !== last_engine_setting.gemini) {
                    $('#gemn_a_nick_name').text(data.a_nick_name || '');
                    $('#gemn_b_nick_name').text(data.b_nick_name || '');
                    $('#gemn_v_nick_name').text(data.v_nick_name || '');
                    $('#gemn_x_nick_name').text(data.x_nick_name || '');
                    $('#gemn_max_wait_sec').val(data.max_wait_sec || '');
                    $('#gemn_a_model').val(data.a_model || '');
                    $('#gemn_a_use_tools').val(data.a_use_tools || '');
                    $('#gemn_b_model').val(data.b_model || '');
                    $('#gemn_b_use_tools').val(data.b_use_tools || '');
                    $('#gemn_v_model').val(data.v_model || '');
                    $('#gemn_v_use_tools').val(data.v_use_tools || '');
                    $('#gemn_x_model').val(data.x_model || '');
                    $('#gemn_x_use_tools').val(data.x_use_tools || '');
                    last_engine_setting.gemini = JSON.stringify(data);
                }
            }

            // freeai
            if (engine === 'freeai') {
                if (JSON.stringify(data) !== last_engine_setting.freeai) {
                    $('#free_a_nick_name').text(data.a_nick_name || '');
                    $('#free_b_nick_name').text(data.b_nick_name || '');
                    $('#free_v_nick_name').text(data.v_nick_name || '');
                    $('#free_x_nick_name').text(data.x_nick_name || '');
                    $('#free_max_wait_sec').val(data.max_wait_sec || '');
                    $('#free_a_model').val(data.a_model || '');
                    $('#free_a_use_tools').val(data.a_use_tools || '');
                    $('#free_b_model').val(data.b_model || '');
                    $('#free_b_use_tools').val(data.b_use_tools || '');
                    $('#free_v_model').val(data.v_model || '');
                    $('#free_v_use_tools').val(data.v_use_tools || '');
                    $('#free_x_model').val(data.x_model || '');
                    $('#free_x_use_tools').val(data.x_use_tools || '');
                    last_engine_setting.freeai = JSON.stringify(data);
                }
            }

            // claude
            if (engine === 'claude') {
                if (JSON.stringify(data) !== last_engine_setting.claude) {
                    $('#clad_a_nick_name').text(data.a_nick_name || '');
                    $('#clad_b_nick_name').text(data.b_nick_name || '');
                    $('#clad_v_nick_name').text(data.v_nick_name || '');
                    $('#clad_x_nick_name').text(data.x_nick_name || '');
                    $('#clad_max_wait_sec').val(data.max_wait_sec || '');
                    $('#clad_a_model').val(data.a_model || '');
                    $('#clad_a_use_tools').val(data.a_use_tools || '');
                    $('#clad_b_model').val(data.b_model || '');
                    $('#clad_b_use_tools').val(data.b_use_tools || '');
                    $('#clad_v_model').val(data.v_model || '');
                    $('#clad_v_use_tools').val(data.v_use_tools || '');
                    $('#clad_x_model').val(data.x_model || '');
                    $('#clad_x_use_tools').val(data.x_use_tools || '');
                    last_engine_setting.claude = JSON.stringify(data);
                }
            }

            // openrt
            if (engine === 'openrt') {
                if (JSON.stringify(data) !== last_engine_setting.openrt) {
                    $('#ort_a_nick_name').text(data.a_nick_name || '');
                    $('#ort_b_nick_name').text(data.b_nick_name || '');
                    $('#ort_v_nick_name').text(data.v_nick_name || '');
                    $('#ort_x_nick_name').text(data.x_nick_name || '');
                    $('#ort_max_wait_sec').val(data.max_wait_sec || '');
                    $('#ort_a_model').val(data.a_model || '');
                    $('#ort_a_use_tools').val(data.a_use_tools || '');
                    $('#ort_b_model').val(data.b_model || '');
                    $('#ort_b_use_tools').val(data.b_use_tools || '');
                    $('#ort_v_model').val(data.v_model || '');
                    $('#ort_v_use_tools').val(data.v_use_tools || '');
                    $('#ort_x_model').val(data.x_model || '');
                    $('#ort_x_use_tools').val(data.x_use_tools || '');
                    last_engine_setting.openrt = JSON.stringify(data);
                }
            }

            // perplexity
            if (engine === 'perplexity') {
                if (JSON.stringify(data) !== last_engine_setting.perplexity) {
                    $('#pplx_a_nick_name').text(data.a_nick_name || '');
                    $('#pplx_b_nick_name').text(data.b_nick_name || '');
                    $('#pplx_v_nick_name').text(data.v_nick_name || '');
                    $('#pplx_x_nick_name').text(data.x_nick_name || '');
                    $('#pplx_max_wait_sec').val(data.max_wait_sec || '');
                    $('#pplx_a_model').val(data.a_model || '');
                    $('#pplx_a_use_tools').val(data.a_use_tools || '');
                    $('#pplx_b_model').val(data.b_model || '');
                    $('#pplx_b_use_tools').val(data.b_use_tools || '');
                    $('#pplx_v_model').val(data.v_model || '');
                    $('#pplx_v_use_tools').val(data.v_use_tools || '');
                    $('#pplx_x_model').val(data.x_model || '');
                    $('#pplx_x_use_tools').val(data.x_use_tools || '');
                    last_engine_setting.perplexity = JSON.stringify(data);
                }
            }

            // grok
            if (engine === 'grok') {
                if (JSON.stringify(data) !== last_engine_setting.grok) {
                    $('#grok_a_nick_name').text(data.a_nick_name || '');
                    $('#grok_b_nick_name').text(data.b_nick_name || '');
                    $('#grok_v_nick_name').text(data.v_nick_name || '');
                    $('#grok_x_nick_name').text(data.x_nick_name || '');
                    $('#grok_max_wait_sec').val(data.max_wait_sec || '');
                    $('#grok_a_model').val(data.a_model || '');
                    $('#grok_a_use_tools').val(data.a_use_tools || '');
                    $('#grok_b_model').val(data.b_model || '');
                    $('#grok_b_use_tools').val(data.b_use_tools || '');
                    $('#grok_v_model').val(data.v_model || '');
                    $('#grok_v_use_tools').val(data.v_use_tools || '');
                    $('#grok_x_model').val(data.x_model || '');
                    $('#grok_x_use_tools').val(data.x_use_tools || '');
                    last_engine_setting.grok = JSON.stringify(data);
                }
            }

            // groq
            if (engine === 'groq') {
                if (JSON.stringify(data) !== last_engine_setting.groq) {
                    $('#groq_a_nick_name').text(data.a_nick_name || '');
                    $('#groq_b_nick_name').text(data.b_nick_name || '');
                    $('#groq_v_nick_name').text(data.v_nick_name || '');
                    $('#groq_x_nick_name').text(data.x_nick_name || '');
                    $('#groq_max_wait_sec').val(data.max_wait_sec || '');
                    $('#groq_a_model').val(data.a_model || '');
                    $('#groq_a_use_tools').val(data.a_use_tools || '');
                    $('#groq_b_model').val(data.b_model || '');
                    $('#groq_b_use_tools').val(data.b_use_tools || '');
                    $('#groq_v_model').val(data.v_model || '');
                    $('#groq_v_use_tools').val(data.v_use_tools || '');
                    $('#groq_x_model').val(data.x_model || '');
                    $('#groq_x_use_tools').val(data.x_use_tools || '');
                    last_engine_setting.groq = JSON.stringify(data);
                }
            }

            // ollama
            if (engine === 'ollama') {
                if (JSON.stringify(data) !== last_engine_setting.ollama) {
                    $('#olm_a_nick_name').text(data.a_nick_name || '');
                    $('#olm_b_nick_name').text(data.b_nick_name || '');
                    $('#olm_v_nick_name').text(data.v_nick_name || '');
                    $('#olm_x_nick_name').text(data.x_nick_name || '');
                    $('#olm_max_wait_sec').val(data.max_wait_sec || '');
                    $('#olm_a_model').val(data.a_model || '');
                    $('#olm_a_use_tools').val(data.a_use_tools || '');
                    $('#olm_b_model').val(data.b_model || '');
                    $('#olm_b_use_tools').val(data.b_use_tools || '');
                    $('#olm_v_model').val(data.v_model || '');
                    $('#olm_v_use_tools').val(data.v_use_tools || '');
                    $('#olm_x_model').val(data.x_model || '');
                    $('#olm_x_use_tools').val(data.x_use_tools || '');
                    last_engine_setting.ollama = JSON.stringify(data);
                }
            }

        },
        error: function(xhr, status, error) {
            console.error('get_engine_setting error:', error);
        }
    });
}

// サーバーへ設定値を保存する関数
function post_engine_setting(engine) {
    var formData = {};

    // chatgpt
    if (engine === 'chatgpt') {
        formData = {
            engine: 'chatgpt',
            max_wait_sec: $('#gpt_max_wait_sec').val(),
            a_model: $('#gpt_a_model').val(),
            a_use_tools: $('#gpt_a_use_tools').val(),
            b_model: $('#gpt_b_model').val(),
            b_use_tools: $('#gpt_b_use_tools').val(),
            v_model: $('#gpt_v_model').val(),
            v_use_tools: $('#gpt_v_use_tools').val(),
            x_model: $('#gpt_x_model').val(),
            x_use_tools: $('#gpt_x_use_tools').val(),
        }
    }

    // assist
    if (engine === 'assist') {
        formData = {
            engine: 'assist',
            max_wait_sec: $('#asst_max_wait_sec').val(),
            a_model: $('#asst_a_model').val(),
            a_use_tools: $('#asst_a_use_tools').val(),
            b_model: $('#asst_b_model').val(),
            b_use_tools: $('#asst_b_use_tools').val(),
            v_model: $('#asst_v_model').val(),
            v_use_tools: $('#asst_v_use_tools').val(),
            x_model: $('#asst_x_model').val(),
            x_use_tools: $('#asst_x_use_tools').val(),
        }
    }

    // respo
    if (engine === 'respo') {
        formData = {
            engine: 'respo',
            max_wait_sec: $('#resp_max_wait_sec').val(),
            a_model: $('#resp_a_model').val(),
            a_use_tools: $('#resp_a_use_tools').val(),
            b_model: $('#resp_b_model').val(),
            b_use_tools: $('#resp_b_use_tools').val(),
            v_model: $('#resp_v_model').val(),
            v_use_tools: $('#resp_v_use_tools').val(),
            x_model: $('#resp_x_model').val(),
            x_use_tools: $('#resp_x_use_tools').val(),
        }
    }

    // gemini
    if (engine === 'gemini') {
        formData = {
            engine: 'gemini',
            max_wait_sec: $('#gemn_max_wait_sec').val(),
            a_model: $('#gemn_a_model').val(),
            a_use_tools: $('#gemn_a_use_tools').val(),
            b_model: $('#gemn_b_model').val(),
            b_use_tools: $('#gemn_b_use_tools').val(),
            v_model: $('#gemn_v_model').val(),
            v_use_tools: $('#gemn_v_use_tools').val(),
            x_model: $('#gemn_x_model').val(),
            x_use_tools: $('#gemn_x_use_tools').val(),
        }
    }

    // freeai
    if (engine === 'freeai') {
        formData = {
            engine: 'freeai',
            max_wait_sec: $('#free_max_wait_sec').val(),
            a_model: $('#free_a_model').val(),
            a_use_tools: $('#free_a_use_tools').val(),
            b_model: $('#free_b_model').val(),
            b_use_tools: $('#free_b_use_tools').val(),
            v_model: $('#free_v_model').val(),
            v_use_tools: $('#free_v_use_tools').val(),
            x_model: $('#free_x_model').val(),
            x_use_tools: $('#free_x_use_tools').val(),
        }
    }

    // claude
    if (engine === 'claude') {
        formData = {
            engine: 'claude',
            max_wait_sec: $('#clad_max_wait_sec').val(),
            a_model: $('#clad_a_model').val(),
            a_use_tools: $('#clad_a_use_tools').val(),
            b_model: $('#clad_b_model').val(),
            b_use_tools: $('#clad_b_use_tools').val(),
            v_model: $('#clad_v_model').val(),
            v_use_tools: $('#clad_v_use_tools').val(),
            x_model: $('#clad_x_model').val(),
            x_use_tools: $('#clad_x_use_tools').val(),
        }
    }

    // openrt
    if (engine === 'openrt') {
        formData = {
            engine: 'openrt',
            max_wait_sec: $('#ort_max_wait_sec').val(),
            a_model: $('#ort_a_model').val(),
            a_use_tools: $('#ort_a_use_tools').val(),
            b_model: $('#ort_b_model').val(),
            b_use_tools: $('#ort_b_use_tools').val(),
            v_model: $('#ort_v_model').val(),
            v_use_tools: $('#ort_v_use_tools').val(),
            x_model: $('#ort_x_model').val(),
            x_use_tools: $('#ort_x_use_tools').val(),
        }
    }

    // perplexity
    if (engine === 'perplexity') {
        formData = {
            engine: 'perplexity',
            max_wait_sec: $('#pplx_max_wait_sec').val(),
            a_model: $('#pplx_a_model').val(),
            a_use_tools: $('#pplx_a_use_tools').val(),
            b_model: $('#pplx_b_model').val(),
            b_use_tools: $('#pplx_b_use_tools').val(),
            v_model: $('#pplx_v_model').val(),
            v_use_tools: $('#pplx_v_use_tools').val(),
            x_model: $('#pplx_x_model').val(),
            x_use_tools: $('#pplx_x_use_tools').val(),
        }
    }

    // grok
    if (engine === 'grok') {
        formData = {
            engine: 'grok',
            max_wait_sec: $('#grok_max_wait_sec').val(),
            a_model: $('#grok_a_model').val(),
            a_use_tools: $('#grok_a_use_tools').val(),
            b_model: $('#grok_b_model').val(),
            b_use_tools: $('#grok_b_use_tools').val(),
            v_model: $('#grok_v_model').val(),
            v_use_tools: $('#grok_v_use_tools').val(),
            x_model: $('#grok_x_model').val(),
            x_use_tools: $('#grok_x_use_tools').val(),
        }
    }

    // groq
    if (engine === 'groq') {
        formData = {
            engine: 'groq',
            max_wait_sec: $('#groq_max_wait_sec').val(),
            a_model: $('#groq_a_model').val(),
            a_use_tools: $('#groq_a_use_tools').val(),
            b_model: $('#groq_b_model').val(),
            b_use_tools: $('#groq_b_use_tools').val(),
            v_model: $('#groq_v_model').val(),
            v_use_tools: $('#groq_v_use_tools').val(),
            x_model: $('#groq_x_model').val(),
            x_use_tools: $('#groq_x_use_tools').val(),
        }
    }

    // ollama
    if (engine === 'ollama') {
        formData = {
            engine: 'ollama',
            max_wait_sec: $('#olm_max_wait_sec').val(),
            a_model: $('#olm_a_model').val(),
            a_use_tools: $('#olm_a_use_tools').val(),
            b_model: $('#olm_b_model').val(),
            b_use_tools: $('#olm_b_use_tools').val(),
            v_model: $('#olm_v_model').val(),
            v_use_tools: $('#olm_v_use_tools').val(),
            x_model: $('#olm_x_model').val(),
            x_use_tools: $('#olm_x_use_tools').val(),
        }
    }

    // 設定値をサーバーに送信
    $.ajax({
        url: '/post_engine_setting',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(response) {
            console.log('post_engine_setting:', response);
        },
        error: function(xhr, status, error) {
            console.error('post_engine_setting error:', error);
        }
    });
}

// ドキュメントが読み込まれた時に実行される処理
$(document).ready(function() {

    // ページ遷移時にlocalStorageから復元
    const storedData = JSON.parse(localStorage.getItem('setting_model_formData'));
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
        localStorage.setItem('setting_model_formData', JSON.stringify(formData)); // localStorageに保存
    };

    // max_wait_secを設定する関数
    add_wait_sec_all();

    // エンジンのmodels設定を取得
    get_engine_models('chatgpt');
    get_engine_models('assist');
    get_engine_models('respo');
    get_engine_models('gemini');
    get_engine_models('freeai');
    get_engine_models('claude');
    get_engine_models('openrt');
    get_engine_models('perplexity');
    get_engine_models('grok');
    get_engine_models('groq');
    get_engine_models('ollama');

    // 定期的に設定値を取得する処理
    setInterval(get_engine_setting_all, 3100);

    $('#gpt_max_wait_sec, #gpt_a_model, #gpt_a_use_tools, #gpt_b_model, #gpt_b_use_tools, #gpt_v_model, #gpt_v_use_tools, #gpt_x_model, #gpt_x_use_tools').change(function() {
        post_engine_setting('chatgpt');
    });
    $('#gpt-a2bvx-button').click(function() {
        $('#gpt_b_model').val( $('#gpt_a_model').val() );
        $('#gpt_b_use_tools').val( $('#gpt_a_use_tools').val() );
        $('#gpt_v_model').val( $('#gpt_a_model').val() );
        $('#gpt_v_use_tools').val( $('#gpt_a_use_tools').val() );
        $('#gpt_x_model').val( $('#gpt_a_model').val() );
        $('#gpt_x_use_tools').val( $('#gpt_a_use_tools').val() );
        post_engine_setting('chatgpt');
    });

    $('#asst_max_wait_sec, #asst_a_model, #asst_a_use_tools, #asst_b_model, #asst_b_use_tools, #asst_v_model, #asst_v_use_tools, #asst_x_model, #asst_x_use_tools').change(function() {
        post_engine_setting('assist');
    });
    $('#asst-a2bvx-button').click(function() {
        $('#asst_b_model').val( $('#asst_a_model').val() );
        $('#asst_b_use_tools').val( $('#asst_a_use_tools').val() );
        $('#asst_v_model').val( $('#asst_a_model').val() );
        $('#asst_v_use_tools').val( $('#asst_a_use_tools').val() );
        $('#asst_x_model').val( $('#asst_a_model').val() );
        $('#asst_x_use_tools').val( $('#asst_a_use_tools').val() );
        post_engine_setting('assist');
    });

    $('#resp_max_wait_sec, #resp_a_model, #resp_a_use_tools, #resp_b_model, #resp_b_use_tools, #resp_v_model, #resp_v_use_tools, #resp_x_model, #resp_x_use_tools').change(function() {
        post_engine_setting('respo');
    });
    $('#resp-a2bvx-button').click(function() {
        $('#resp_b_model').val( $('#resp_a_model').val() );
        $('#resp_b_use_tools').val( $('#resp_a_use_tools').val() );
        $('#resp_v_model').val( $('#resp_a_model').val() );
        $('#resp_v_use_tools').val( $('#resp_a_use_tools').val() );
        $('#resp_x_model').val( $('#resp_a_model').val() );
        $('#resp_x_use_tools').val( $('#resp_a_use_tools').val() );
        post_engine_setting('respo');
    });

    $('#gemn_max_wait_sec, #gemn_a_model, #gemn_a_use_tools, #gemn_b_model, #gemn_b_use_tools, #gemn_v_model, #gemn_v_use_tools, #gemn_x_model, #gemn_x_use_tools').change(function() {
        post_engine_setting('gemini');
    });
    $('#gemn-a2bvx-button').click(function() {
        $('#gemn_b_model').val( $('#gemn_a_model').val() );
        $('#gemn_b_use_tools').val( $('#gemn_a_use_tools').val() );
        $('#gemn_v_model').val( $('#gemn_a_model').val() );
        $('#gemn_v_use_tools').val( $('#gemn_a_use_tools').val() );
        $('#gemn_x_model').val( $('#gemn_a_model').val() );
        $('#gemn_x_use_tools').val( $('#gemn_a_use_tools').val() );
        post_engine_setting('gemini');
    });

    $('#free_max_wait_sec, #free_a_model, #free_a_use_tools, #free_b_model, #free_b_use_tools, #free_v_model, #free_v_use_tools, #free_x_model, #free_x_use_tools').change(function() {
        post_engine_setting('freeai');
    });
    $('#free-a2bvx-button').click(function() {
        $('#free_b_model').val( $('#free_a_model').val() );
        $('#free_b_use_tools').val( $('#free_a_use_tools').val() );
        $('#free_v_model').val( $('#free_a_model').val() );
        $('#free_v_use_tools').val( $('#free_a_use_tools').val() );
        $('#free_x_model').val( $('#free_a_model').val() );
        $('#free_x_use_tools').val( $('#free_a_use_tools').val() );
        post_engine_setting('freeai');
    });

    $('#clad_max_wait_sec, #clad_a_model, #clad_a_use_tools, #clad_b_model, #clad_b_use_tools, #clad_v_model, #clad_v_use_tools, #clad_x_model, #clad_x_use_tools').change(function() {
        post_engine_setting('claude');
    });
    $('#clad-a2bvx-button').click(function() {
        $('#clad_b_model').val( $('#clad_a_model').val() );
        $('#clad_b_use_tools').val( $('#clad_a_use_tools').val() );
        $('#clad_v_model').val( $('#clad_a_model').val() );
        $('#clad_v_use_tools').val( $('#clad_a_use_tools').val() );
        $('#clad_x_model').val( $('#clad_a_model').val() );
        $('#clad_x_use_tools').val( $('#clad_a_use_tools').val() );
        post_engine_setting('claude');
    });

    $('#ort_max_wait_sec, #ort_a_model, #ort_a_use_tools, #ort_b_model, #ort_b_use_tools, #ort_v_model, #ort_v_use_tools, #ort_x_model, #ort_x_use_tools').change(function() {
        post_engine_setting('openrt');
    });
    $('#ort-a2bvx-button').click(function() {
        $('#ort_b_model').val( $('#ort_a_model').val() );
        $('#ort_b_use_tools').val( $('#ort_a_use_tools').val() );
        $('#ort_v_model').val( $('#ort_a_model').val() );
        $('#ort_v_use_tools').val( $('#ort_a_use_tools').val() );
        $('#ort_x_model').val( $('#ort_a_model').val() );
        $('#ort_x_use_tools').val( $('#ort_a_use_tools').val() );
        post_engine_setting('openrt');
    });

    $('#pplx_max_wait_sec, #pplx_a_model, #pplx_a_use_tools, #pplx_b_model, #pplx_b_use_tools, #pplx_v_model, #pplx_v_use_tools, #pplx_x_model, #pplx_x_use_tools').change(function() {
        post_engine_setting('perplexity');
    });
    $('#pplx-a2bvx-button').click(function() {
        $('#pplx_b_model').val( $('#pplx_a_model').val() );
        $('#pplx_b_use_tools').val( $('#pplx_a_use_tools').val() );
        $('#pplx_v_model').val( $('#pplx_a_model').val() );
        $('#pplx_v_use_tools').val( $('#pplx_a_use_tools').val() );
        $('#pplx_x_model').val( $('#pplx_a_model').val() );
        $('#pplx_x_use_tools').val( $('#pplx_a_use_tools').val() );
        post_engine_setting('perplexity');
    });

    $('#grok_max_wait_sec, #grok_a_model, #grok_a_use_tools, #grok_b_model, #grok_b_use_tools, #grok_v_model, #grok_v_use_tools, #grok_x_model, #grok_x_use_tools').change(function() {
        post_engine_setting('grok');
    });
    $('#grok-a2bvx-button').click(function() {
        $('#grok_b_model').val( $('#grok_a_model').val() );
        $('#grok_b_use_tools').val( $('#grok_a_use_tools').val() );
        $('#grok_v_model').val( $('#grok_a_model').val() );
        $('#grok_v_use_tools').val( $('#grok_a_use_tools').val() );
        $('#grok_x_model').val( $('#grok_a_model').val() );
        $('#grok_x_use_tools').val( $('#grok_a_use_tools').val() );
        post_engine_setting('grok');
    });

    $('#groq_max_wait_sec, #groq_a_model, #groq_a_use_tools, #groq_b_model, #groq_b_use_tools, #groq_v_model, #groq_v_use_tools, #groq_x_model, #groq_x_use_tools').change(function() {
        post_engine_setting('groq');
    });
    $('#groq-a2bvx-button').click(function() {
        $('#groq_b_model').val( $('#groq_a_model').val() );
        $('#groq_b_use_tools').val( $('#groq_a_use_tools').val() );
        $('#groq_v_model').val( $('#groq_a_model').val() );
        $('#groq_v_use_tools').val( $('#groq_a_use_tools').val() );
        $('#groq_x_model').val( $('#groq_a_model').val() );
        $('#groq_x_use_tools').val( $('#groq_a_use_tools').val() );
        post_engine_setting('groq');
    });

    $('#olm_max_wait_sec, #olm_a_model, #olm_a_use_tools, #olm_b_model, #olm_b_use_tools, #olm_v_model, #olm_v_use_tools, #olm_x_model, #olm_x_use_tools').change(function() {
        post_engine_setting('ollama');
    });
    $('#olm-a2bvx-button').click(function() {
        $('#olm_b_model').val( $('#olm_a_model').val() );
        $('#olm_b_use_tools').val( $('#olm_a_use_tools').val() );
        $('#olm_v_model').val( $('#olm_a_model').val() );
        $('#olm_v_use_tools').val( $('#olm_a_use_tools').val() );
        $('#olm_x_model').val( $('#olm_a_model').val() );
        $('#olm_x_use_tools').val( $('#olm_a_use_tools').val() );
        post_engine_setting('ollama');
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
