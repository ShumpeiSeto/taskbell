let intervalId;
// modal 用意
const modal = new bootstrap.Modal(document.getElementById("exampleModal"));
// modalのbody部
const modal_body = document.querySelector(".modal-body");

// dateオブジェクトに変換用編集関数
const slice_date_str = function (date_str) {
  const result = "20" + date_str.slice(0, 8);
  return result.replaceAll("/", "-");
};

intervalId ??= setInterval(checkdatetime, 30000);
function checkdatetime() {
  // クライアントセッションから取得
  const dead_minutes = sessionStorage.getItem("dead_minutes");
  // 親要素で取得した方がアクセスしやすい
  const nctask_items = document.querySelectorAll(".nc-task-item");
  // 比較のため現座日時取得
  const now = new Date();

  nctask_items.forEach((item) => {
    const date = item.querySelector(".deaddate").innerHTML;
    const time = item.querySelector(".deadtime").innerHTML;
    const taskname = item.querySelector(".taskname").innerHTML;

    // modal表示用
    const tr = modal_body.appendChild(document.createElement("tr"));
    const td_taskname = tr.appendChild(document.createElement("td"));
    const td_deaddate = tr.appendChild(document.createElement("td"));
    const td_deadtime = tr.appendChild(document.createElement("td"));
    td_taskname.textContent = taskname;
    td_deaddate.textContent = date;
    td_deadtime.textContent = time;

    const datetime = slice_date_str(date) + "T" + time;
    const diff = (new Date(datetime).getTime() - now.getTime()) / (60 * 1000);
    console.log(datetime, diff);
    if (diff <= dead_minutes) {
      modal.show();
    }
  });
}
