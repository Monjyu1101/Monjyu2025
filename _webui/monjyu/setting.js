// setting.js

// ドキュメント読み込み完了時の処理
$(document).ready(function() {

    // ページ遷移時にlocalStorageから復元
    const storedData = JSON.parse(localStorage.getItem('setting_formData'));
    if (storedData) {
        // ページ開始時に保存されたタブを復元(左側)
        var activeTab_left = storedData.activeTab_left || 'engine';
        $('.frame-left .tab-content').removeClass('active');
        $('.frame-left .tab-header button').removeClass('active');
        $('.frame-left #' + activeTab_left).addClass('active');
        $('.frame-left .tab-header button[data-target="' + activeTab_left + '"]').addClass('active');

        // ページ開始時に保存されたタブを復元(右側)
        var activeTab_right = storedData.activeTab_right || 'other';
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
        localStorage.setItem('setting_formData', JSON.stringify(formData));
    };

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
