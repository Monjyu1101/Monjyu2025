// development.js

const CORE_ENDPOINT1 = 'http://localhost:8001';
const CORE_ENDPOINT2 = 'http://localhost:8002';
const CORE_ENDPOINT3 = 'http://localhost:8003';
const CORE_ENDPOINT4 = 'http://localhost:8004';
const CORE_ENDPOINT5 = 'http://localhost:8005';

// 親ウィンドウにメッセージを送信する関数
function sendMessageToParent(action, method, data) {
    window.parent.postMessage({ action: action, method: method, data: data }, '*');
}

// ソースコードをサーバーから取得し、親ウィンドウに送信する関数
function get_source_input(sourceName) {
    $.ajax({
        url: '/get_source',
        method: 'GET',
        data: { source_name: sourceName },
        dataType: 'json',
        success: function(data) {
            // 取得したソースコードを親ウィンドウに送信
            sendMessageToParent('setInputText', 'add', data.source_text);
        },
        error: function(xhr, status, error) {
            console.error('get_source (input) error:', error);
        }
    });
}

// ソースコードをサーバーから取得し、親ウィンドウに送信し、処理を要求する関数
function get_source_request(sourceName) {
    $.ajax({
        url: '/get_source',
        method: 'GET',
        data: { source_name: sourceName },
        dataType: 'json',
        success: function(data) {
            // 取得したソースコードを親ウィンドウに要求
            sendMessageToParent('setInputText', 'set', data.source_text);
            sendMessageToParent('requestRun', 'req_mode', '');
        },
        error: function(xhr, status, error) {
            console.error('get_source (request) error:', error);
        }
    });
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

async function allPyRequest() {
    get_source_request('RiKi_Monjyu.py');
    get_source_request('RiKi_Monjyu__conf.py');
    get_source_request('RiKi_Monjyu__data.py');
    get_source_request('RiKi_Monjyu__addin.py');
    get_source_request('RiKi_Monjyu__coreai0.py');
    get_source_request('RiKi_Monjyu__coreai1.py');
    get_source_request('RiKi_Monjyu__coreai2.py');
    get_source_request('RiKi_Monjyu__coreai4.py');
    get_source_request('RiKi_Monjyu__coreai5.py');
    get_source_request('RiKi_Monjyu__subai.py');
    get_source_request('RiKi_Monjyu__subbot.py');
    get_source_request('RiKi_Monjyu__llm.py');
    get_source_request('RiKi_Monjyu__webui.py');

    // 実行待機
    await waitForBusy();
    await waitForIdol();

    alert('py処理完了!')
}

async function allHtmlRequest() {
    get_source_request('_webui/monjyu/index.html');
    get_source_request('_webui/monjyu/mainui.html');
    get_source_request('_webui/monjyu/setting.html');
    get_source_request('_webui/monjyu/setting_engine.html');
    get_source_request('_webui/monjyu/setting_model.html');
    get_source_request('_webui/monjyu/setting_live.html');
    get_source_request('_webui/monjyu/setting_agent.html');
    get_source_request('_webui/monjyu/setting_other.html');
    get_source_request('_webui/monjyu/chat.html');
    get_source_request('_webui/monjyu/input.html');
    get_source_request('_webui/monjyu/vision.html');
    get_source_request('_webui/monjyu/statuses.html');
    get_source_request('_webui/monjyu/output.html');
    get_source_request('_webui/monjyu/histories.html');
    get_source_request('_webui/monjyu/sessions.html');

    // 実行待機
    await waitForBusy();
    await waitForIdol();

    get_source_request('_webui/monjyu/debug_step.html');
    get_source_request('_webui/monjyu/debug_log.html');
    get_source_request('_webui/monjyu/react.html');
    get_source_request('_webui/monjyu/writing.html');
    get_source_request('_webui/monjyu/development.html');
    get_source_request('_webui/monjyu/links.html');

    // 実行待機
    await waitForBusy();
    await waitForIdol();

    alert('html処理完了!')
}

async function allJsRequest() {
    get_source_request('_webui/monjyu/index.js');
    get_source_request('_webui/monjyu/mainui.js');
    get_source_request('_webui/monjyu/setting.js');
    get_source_request('_webui/monjyu/setting_engine.js');
    get_source_request('_webui/monjyu/setting_model.js');
    get_source_request('_webui/monjyu/setting_live.js');
    get_source_request('_webui/monjyu/setting_agent.js');
    get_source_request('_webui/monjyu/setting_other.js');
    get_source_request('_webui/monjyu/chat.js');
    get_source_request('_webui/monjyu/input.js');
    get_source_request('_webui/monjyu/vision.js');
    get_source_request('_webui/monjyu/statuses.js');
    get_source_request('_webui/monjyu/output.js');
    get_source_request('_webui/monjyu/histories.js');
    get_source_request('_webui/monjyu/sessions.js');

    // 実行待機
    await waitForBusy();
    await waitForIdol();

    get_source_request('_webui/monjyu/debug_step.js');
    get_source_request('_webui/monjyu/debug_log.js');
    get_source_request('_webui/monjyu/react.js');
    get_source_request('_webui/monjyu/writing.js');
    get_source_request('_webui/monjyu/development.js');

    // 実行待機
    await waitForBusy();
    await waitForIdol();

    alert('js処理完了!')
}



// ドキュメントが読み込まれた時に実行される処理
$(document).ready(function() {

    // デバッグアシスタントボタンのクリックイベント
    $('#btnDebugParallel').click(function() {
        sendMessageToParent('debugRun', 'parallel', '' );
    });
    $('#btnDebugSerial').click(function() {
        sendMessageToParent('debugRun', 'serial', '' );
    });
    $('#btnDebugChat').click(function() {
        sendMessageToParent('debugRun', 'chat', '' );
    });

    // Py,jsリクエストボタンのクリックイベント
    $('#btnReq_pyjs1').click(function() {
        sendMessageToParent('setRequestText', 'set', $('#req_pyjs1').val() );
    });
    $('#btnReq_pyjs2').click(function() {
        sendMessageToParent('setRequestText', 'set', $('#req_pyjs2').val() );
    });
    $('#btnReq_pyjs3').click(function() {
        sendMessageToParent('setRequestText', 'set', $('#req_pyjs3').val() );
    });

    // HTMLリクエストボタンのクリックイベント
    $('#btnReq_html1').click(function() {
        sendMessageToParent('setRequestText', 'set', $('#req_html1').val() );
    });
    $('#btnReq_html2').click(function() {
        sendMessageToParent('setRequestText', 'set', $('#req_html2').val() );
    });
    $('#btnReq_html3').click(function() {
        sendMessageToParent('setRequestText', 'set', $('#req_html3').val() );
    });
    $('#btnReq_index').click(function() {
        sendMessageToParent('setRequestText', 'set', $('#req_index').val() );
    });
    $('#btnReq_react').click(function() {
        sendMessageToParent('setRequestText', 'set', $('#req_react').val() );
    });

    // 全Pythonソースコードリクエストボタンのクリックイベント
    $('#btnSource_allPy2Text').click(function() {
        get_source_input('RiKi_Monjyu.py');
        get_source_input('RiKi_Monjyu__conf.py');
        get_source_input('RiKi_Monjyu__data.py');
        get_source_input('RiKi_Monjyu__addin.py');
        get_source_input('RiKi_Monjyu__coreai0.py');
        get_source_input('RiKi_Monjyu__coreai1.py');
        get_source_input('RiKi_Monjyu__coreai2.py');
        get_source_input('RiKi_Monjyu__coreai4.py');
        get_source_input('RiKi_Monjyu__coreai5.py');
        get_source_input('RiKi_Monjyu__subai.py');
        get_source_input('RiKi_Monjyu__subbot.py');
        get_source_input('RiKi_Monjyu__llm.py');
        get_source_input('RiKi_Monjyu__webui.py');
    });
    $('#btnSource_allPyRequest').click(function() {
        if (confirm("全てのpythonソースで実行しますか?")) {
            allPyRequest();
        }
    });

    // 全HTMLソースコードリクエストボタンのクリックイベント
    $('#btnSource_allHtml2Text').click(function() {
        get_source_input('_webui/monjyu/index.html');
        get_source_input('_webui/monjyu/mainui.html');
        get_source_input('_webui/monjyu/setting.html');
        get_source_input('_webui/monjyu/setting_engine.html');
        get_source_input('_webui/monjyu/setting_model.html');
        get_source_input('_webui/monjyu/setting_live.html');
        get_source_input('_webui/monjyu/setting_agent.html');
        get_source_input('_webui/monjyu/setting_other.html');
        get_source_input('_webui/monjyu/chat.html');
        get_source_input('_webui/monjyu/input.html');
        get_source_input('_webui/monjyu/vision.html');
        get_source_input('_webui/monjyu/statuses.html');
        get_source_input('_webui/monjyu/output.html');
        get_source_input('_webui/monjyu/histories.html');
        get_source_input('_webui/monjyu/sessions.html');
        get_source_input('_webui/monjyu/debug_step.html');
        get_source_input('_webui/monjyu/debug_log.html');
        get_source_input('_webui/monjyu/react.html');
        get_source_input('_webui/monjyu/writing.html');
        get_source_input('_webui/monjyu/development.html');
        get_source_input('_webui/monjyu/links.html');
    });
    $('#btnSource_allHtmlRequest').click(function() {
        if (confirm("全てのhtmlソースで実行しますか?")) {
            allHtmlRequest();
        }
    });

    // 全JavaScriptソースコードリクエストボタンのクリックイベント
    $('#btnSource_allJs2Text').click(function() {
        get_source_input('_webui/monjyu/index.js');
        get_source_input('_webui/monjyu/mainui.js');
        get_source_input('_webui/monjyu/setting.js');
        get_source_input('_webui/monjyu/setting_engine.js');
        get_source_input('_webui/monjyu/setting_model.js');
        get_source_input('_webui/monjyu/setting_live.js');
        get_source_input('_webui/monjyu/setting_agent.js');
        get_source_input('_webui/monjyu/setting_other.js');
        get_source_input('_webui/monjyu/chat.js');
        get_source_input('_webui/monjyu/input.js');
        get_source_input('_webui/monjyu/vision.js');
        get_source_input('_webui/monjyu/statuses.js');
        get_source_input('_webui/monjyu/output.js');
        get_source_input('_webui/monjyu/histories.js');
        get_source_input('_webui/monjyu/sessions.js');
        get_source_input('_webui/monjyu/debug_step.js');
        get_source_input('_webui/monjyu/debug_log.js');
        get_source_input('_webui/monjyu/react.js');
        get_source_input('_webui/monjyu/writing.js');
        get_source_input('_webui/monjyu/development.js');
    });
    $('#btnSource_allJsRequest').click(function() {
        if (confirm("全てのjsソースで実行しますか?")) {
            allJsRequest();
        }
    });

    // 各Pythonソースコードボタンのクリックイベント
    $('#btnSource_Monjyu').click(function() {
        get_source_input('RiKi_Monjyu.py');
    });
    $('#btnSource_conf').click(function() {
        get_source_input('RiKi_Monjyu__conf.py');
    });
    $('#btnSource_data').click(function() {
        get_source_input('RiKi_Monjyu__data.py');
    });
    $('#btnSource_addin').click(function() {
        get_source_input('RiKi_Monjyu__addin.py');
    });
    $('#btnSource_coreai0').click(function() {
        get_source_input('RiKi_Monjyu__coreai0.py');
    });
    $('#btnSource_coreai1').click(function() {
        get_source_input('RiKi_Monjyu__coreai1.py');
    });
    $('#btnSource_coreai2').click(function() {
        get_source_input('RiKi_Monjyu__coreai2.py');
    });
    $('#btnSource_coreai4').click(function() {
        get_source_input('RiKi_Monjyu__coreai4.py');
    });
    $('#btnSource_coreai5').click(function() {
        get_source_input('RiKi_Monjyu__coreai5.py');
    });
    $('#btnSource_subai').click(function() {
        get_source_input('RiKi_Monjyu__subai.py');
    });
    $('#btnSource_subbot').click(function() {
        get_source_input('RiKi_Monjyu__subbot.py');
    });
    $('#btnSource_llm').click(function() {
        get_source_input('RiKi_Monjyu__llm.py');
    });
    $('#btnSource_webui').click(function() {
        get_source_input('RiKi_Monjyu__webui.py');
    });

    // 各HTMLソースコードボタンのクリックイベント
    $('#btnSource_index').click(function() {
        get_source_input('_webui/monjyu/index.html');
    });
    $('#btnSource_mainui').click(function() {
        get_source_input('_webui/monjyu/mainui.html');
    });
    $('#btnSource_setting').click(function() {
        get_source_input('_webui/monjyu/setting.html');
    });
    $('#btnSource_setting_engine').click(function() {
        get_source_input('_webui/monjyu/setting_engine.html');
    });
    $('#btnSource_setting_model').click(function() {
        get_source_input('_webui/monjyu/setting_model.html');
    });
    $('#btnSource_setting_live').click(function() {
        get_source_input('_webui/monjyu/setting_live.html');
    });
    $('#btnSource_setting_agent').click(function() {
        get_source_input('_webui/monjyu/setting_agent.html');
    });
    $('#btnSource_setting_other').click(function() {
        get_source_input('_webui/monjyu/setting_other.html');
    });
    $('#btnSource_chat').click(function() {
        get_source_input('_webui/monjyu/chat.html');
    });
    $('#btnSource_input').click(function() {
        get_source_input('_webui/monjyu/input.html');
    });
    $('#btnSource_vision').click(function() {
        get_source_input('_webui/monjyu/vision.html');
    });
    $('#btnSource_statuses').click(function() {
        get_source_input('_webui/monjyu/statuses.html');
    });
    $('#btnSource_output').click(function() {
        get_source_input('_webui/monjyu/output.html');
    });
    $('#btnSource_histories').click(function() {
        get_source_input('_webui/monjyu/histories.html');
    });
    $('#btnSource_sessions').click(function() {
        get_source_input('_webui/monjyu/sessions.html');
    });
    $('#btnSource_debug_step').click(function() {
        get_source_input('_webui/monjyu/debug_step.html');
    });
    $('#btnSource_debug_log').click(function() {
        get_source_input('_webui/monjyu/debug_log.html');
    });
    $('#btnSource_react').click(function() {
        get_source_input('_webui/monjyu/react.html');
    });
    $('#btnSource_writing').click(function() {
        get_source_input('_webui/monjyu/writing.html');
    });
    $('#btnSource_development').click(function() {
        get_source_input('_webui/monjyu/development.html');
    });
    $('#btnSource_react').click(function() {
        get_source_input('_webui/monjyu/react.html');
    });
    $('#btnSource_links').click(function() {
        get_source_input('_webui/monjyu/links.html');
    });

    // 各JavaScriptソースコードボタンのクリックイベント
    $('#btnSource_index_js').click(function() {
        get_source_input('_webui/monjyu/index.js');
    });
    $('#btnSource_mainui_js').click(function() {
        get_source_input('_webui/monjyu/mainui.js');
    });
    $('#btnSource_setting_js').click(function() {
        get_source_input('_webui/monjyu/setting.js');
    });
    $('#btnSource_setting_engine_js').click(function() {
        get_source_input('_webui/monjyu/setting_engine.js');
    });
    $('#btnSource_setting_model_js').click(function() {
        get_source_input('_webui/monjyu/setting_model.js');
    });
    $('#btnSource_setting_live_js').click(function() {
        get_source_input('_webui/monjyu/setting_live.js');
    });
    $('#btnSource_setting_agent_js').click(function() {
        get_source_input('_webui/monjyu/setting_agent.js');
    });
    $('#btnSource_setting_other_js').click(function() {
        get_source_input('_webui/monjyu/setting_other.js');
    });
    $('#btnSource_chat_js').click(function() {
        get_source_input('_webui/monjyu/chat.js');
    });
    $('#btnSource_input_js').click(function() {
        get_source_input('_webui/monjyu/input.js');
    });
    $('#btnSource_vision_js').click(function() {
        get_source_input('_webui/monjyu/vision.js');
    });
    $('#btnSource_statuses_js').click(function() {
        get_source_input('_webui/monjyu/statuses.js');
    });
    $('#btnSource_output_js').click(function() {
        get_source_input('_webui/monjyu/output.js');
    });
    $('#btnSource_histories_js').click(function() {
        get_source_input('_webui/monjyu/histories.js');
    });
    $('#btnSource_sessions_js').click(function() {
        get_source_input('_webui/monjyu/sessions.js');
    });
    $('#btnSource_debug_step_js').click(function() {
        get_source_input('_webui/monjyu/debug_step.js');
    });
    $('#btnSource_debug_log_js').click(function() {
        get_source_input('_webui/monjyu/debug_log.js');
    });
    $('#btnSource_react_js').click(function() {
        get_source_input('_webui/monjyu/react.js');
    });
    $('#btnSource_writing_js').click(function() {
        get_source_input('_webui/monjyu/writing.js');
    });
    $('#btnSource_development_js').click(function() {
        get_source_input('_webui/monjyu/development.js');
    });

    // 各テストPythonソースコードボタンのクリックイベント
    $('#btnSource_test1_py').click(function() {
        get_source_input('RiKi_Monjyu_test1.py');
    });
    $('#btnSource_test2_py').click(function() {
        get_source_input('RiKi_Monjyu_test2.py');
    });
    $('#btnSource_test3_py').click(function() {
        get_source_input('RiKi_Monjyu_test3.py');
    });
    $('#btnSource_test4_py').click(function() {
        get_source_input('RiKi_Monjyu_test4.py');
    });
    $('#btnSource_test5_py').click(function() {
        get_source_input('RiKi_Monjyu_test5.py');
    });

});
