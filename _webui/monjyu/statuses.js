// statuses.js

// サブAIの情報を取得する関数
function getSubAiInfo() {
    // AJAXを使ってサブAIの情報を取得
    $.ajax({
        url: $('#core_endpoint0').val() + '/get_subai_info_all',
        type: 'GET',
        success: function(data) {
            // 取得したデータの各ポートに対して処理を行う
            for (var port in data) {
                let info = data[port];
                let subai = $(`#subai-${port}`);
                // ステータスに応じたクラスを追加
                subai.removeClass('READY CHAT SERIAL PARALLEL SESSION NONE CANCEL ERROR').addClass(info.status);
                // upd_time 属性の設定
                if (info.upd_time) {
                    subai.attr('data-upd-time', info.upd_time); 
                }
                // ニックネームがあれば設定
                if (info.nick_name) {
                    subai.contents().filter(function() {
                        return this.nodeType === 3;
                    }).first().replaceWith(info.nick_name);
                }
                // ツールチップに情報を設定
                subai.find('.tooltip').text(info.info_text || '');
            }
        },
        error: function(xhr, status, error) {
            console.error('get_subai_info_all error:', error);
        }
    });
}

// サブAIのステータスを更新する関数
function getSubAiStatuses() {

    // AJAXを使ってサブAIのステータスを取得
    $.ajax({
        url: $('#core_endpoint0').val() + '/get_subai_statuses_all',
        type: 'GET',
        success: function(data) {

            // 取得したデータの各ポートに対して処理を行う
            for (var port in data) {
                let info = data[port];
                let subai = $(`#subai-${port}`);

                // 現在のステータスを取得
                let currentStatus  = subai.attr('data-status');
                let currentUpdTime = subai.attr('data-upd-time');

                // ステータスが変更されていれば、クラスを変更し点滅アニメーションを適用
                if (currentStatus !== info.status) {
                    subai.removeClass('READY CHAT SERIAL PARALLEL SESSION NONE CANCEL ERROR').addClass(info.status);
                    
                    // upd_time 属性の設定
                    if (info.upd_time) {
                        subai.attr('data-upd-time', info.upd_time); 
                    }

                    subai.addClass('blinking');

                    // 2秒後に点滅アニメーションを解除
                    setTimeout(() => {
                        subai.removeClass('blinking');
                    }, 2000);

                } else {
                    if (currentUpdTime !== info.upd_time) {
                        // upd_time 属性の設定
                        if (info.upd_time) {
                            subai.attr('data-upd-time', info.upd_time); 
                        }

                        subai.addClass('blinking');

                        // 2秒後に点滅アニメーションを解除
                        setTimeout(() => {
                            subai.removeClass('blinking');
                        }, 2000);
                    }
                }

                // ステータスを更新
                subai.attr('data-status', info.status);

                // ニックネームがあれば設定
                if (info.nick_name) {
                    subai.contents().filter(function() {
                        return this.nodeType === 3;
                    }).first().replaceWith(info.nick_name);
                }
            }
        },
        error: function(xhr, status, error) {
            console.error('get_subai_statuses_all error:', error);
        }
    });
}



// ドキュメントが読み込まれた時に実行される処理
$(document).ready(function() {

    // サブAIの情報を取得
    getSubAiInfo();

    // サブAIのステータスを更新
    setInterval(getSubAiStatuses, 5000);

    // サブAI要素にマウスが移動した時の処理
    $('.subai').on('mousemove', function(event) {

        // ツールチップの位置を調整する
        var tooltip = $(this).find('.tooltip');
        var tooltipWidth = tooltip.outerWidth();
        var tooltipHeight = tooltip.outerHeight();
        var windowWidth = $(window).width();
        var windowHeight = $(window).height();
        var mouseX = event.pageX;
        var mouseY = event.pageY;
        var left = mouseX + 10;
        var top = mouseY + 10;

        // 右端に近い場合、左側に表示
        if (left + tooltipWidth > windowWidth) {
            left = mouseX - tooltipWidth - 10;
        }

        // 下端に近い場合、上側に表示
        if (top + tooltipHeight > windowHeight) {
            top = mouseY - tooltipHeight - 10;
        }

        // ツールチップの位置を設定
        tooltip.css({
            left: left,
            top: top
        });
    });

});
