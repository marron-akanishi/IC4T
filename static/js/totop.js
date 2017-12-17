$(function() {
  // 「TOPに戻る」ボタンがクリックされた時の動きを指定します。
  $("#scroll_to_top").click(function() {
    window.scrollTo(0,0);
  });

  // 「一番下へ」ボタンがクリックされた時の動きを指定します。
  $("#scroll_to_bottom").click(function() {
    window.scrollTo(0,document.body.scrollHeight);
  });

  // 関数を変数「changeButtonState」に入れておきます。
  var changeButtonState = function() {
    // 「TOPに戻る」ボタンを取得します。
    var $toTopButton = $('#scroll_to_top');

    // 縦にどれだけスクロールしたかを取得します。
    var scrollTop = $(window).scrollTop();

    if (scrollTop != 0) {
      // ウィンドウの縦幅以上にスクロールしていた、
      // またはページの下端に達していた場合、
      // 「TOPに戻る」ボタンを表示します。
      $toTopButton.show();
    } else {
      // ウィンドウの縦幅以上にスクロールしていない場合、
      // 「TOPに戻る」ボタンを隠します。
      $toTopButton.hide();
    }
  }

  // ウィンドウをスクロール・ロード・リサイズしたときを契機に、
  // 「TOPに戻る】ボタンの表示・非表示を変更します。
  $(window).scroll(changeButtonState)
           .load(changeButtonState)
           .resize(changeButtonState);
  
  $(document).ready(changeButtonState);
});