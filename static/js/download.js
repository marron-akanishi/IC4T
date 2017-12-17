// ファイルをダウンロード
var downloadFile = function (url) {
    var xhr = new XMLHttpRequest(),
    deferred = new $.Deferred();

    // ダウンロードが完了したら実行されるよ
    xhr.addEventListener('load', function() {
        xhr.response; // ダウンロードしたデータ
        deferred.resolve(xhr);
    });

    xhr.open('GET', url, true);
    xhr.responseType = 'arraybuffer'; //ここでarraybufferを設定
    xhr.send();

    return deferred.promise();
}

// 複数ファイルを一括ダウンロード
var batchDownload = function(urlList) {
    // 初期化
    dispLoading("準備中...");
    $(".btn").attr('disabled', true);

    var zip = new JSZip(),
    deferreds = [];

    for (var i = 0; i < urlList.length; i += 1) {
        //拡張子取得
        var f = urlList[i].split('.');
        var ext = f[f.length-1].split(':')[0];
        let filename = i+"."+ext;
        var deferred = downloadFile(urlList[i]).done(function(xhr) {
            zip.file(filename, xhr.response); //zipに追加
        })
        deferreds.push(deferred);
    }

    $.when.apply($, deferreds).done(function() {
        // すべてのダウンロードが完了したら実行されるよ！
        zip.generateAsync({type:"blob"}).then(function (content) {
            saveAs(content, _formatDate(new Date(), "YYYYMMDD-hhmmss") + ".zip");
        });
        $(".btn").attr('disabled', false);
        removeLoading();
    });
};

/**
 * ZIPファイルを生成する
 */
function DownloadZip() {
    // 選択した画像分ループ
    var $images = $("img");
    var list = [];
    $images.each(function(i) {
        var thumbUrl = $(this).data("original");
        var originalUrl = thumbUrl.replace(/:thumb/, ":orig");
        list.push(originalUrl);
    });
    batchDownload(list);
}

/**
 * 日付をフォーマットする
 */
function _formatDate(date, format) {
    if (!format) format = 'YYYY-MM-DD hh:mm:ss.SSS';
    format = format.replace(/YYYY/g, date.getFullYear());
    format = format.replace(/MM/g, ('0' + (date.getMonth() + 1)).slice(-2));
    format = format.replace(/DD/g, ('0' + date.getDate()).slice(-2));
    format = format.replace(/hh/g, ('0' + date.getHours()).slice(-2));
    format = format.replace(/mm/g, ('0' + date.getMinutes()).slice(-2));
    format = format.replace(/ss/g, ('0' + date.getSeconds()).slice(-2));
    if (format.match(/S/g)) {
        var milliSeconds = ('00' + date.getMilliseconds()).slice(-3);
        var length = format.match(/S/g).length;
        for (var i = 0; i < length; i++) format = format.replace(/S/, milliSeconds.substring(i, i + 1));
    }
    return format;
};


// Loadingイメージ表示関数
function dispLoading(msg){
    // 画面表示メッセージ
    var dispMsg = "";
 
    // 引数が空の場合は画像のみ
    if( msg != "" ){
        dispMsg = "<div class='loadingMsg'>" + msg + "</div>";
    }
    // ローディング画像が表示されていない場合のみ表示
    if($("#loading").size() == 0){
        $("body").append("<div id='loading'>" + dispMsg + "</div>");
    } 
}
 
// Loadingイメージ削除関数
function removeLoading(){
    $("#loading").remove();
}