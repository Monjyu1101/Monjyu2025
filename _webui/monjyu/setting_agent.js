// setting_agent.js

const CORE_ENDPOINT1 = 'http://localhost:8001';
const CORE_ENDPOINT2 = 'http://localhost:8002';
const CORE_ENDPOINT3 = 'http://localhost:8003';
const CORE_ENDPOINT4 = 'http://localhost:8004';
const CORE_ENDPOINT5 = 'http://localhost:8005';

// ドキュメントが読み込まれた時に実行される処理
$(document).ready(function() {

    // ページ遷移時にlocalStorageから復元
    const storedData = JSON.parse(localStorage.getItem('setting_agent_formData'));
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
            activeTab: $('.tab-header button.active').data('target'),
        };
        localStorage.setItem('setting_agent_formData', JSON.stringify(formData));
    };

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
