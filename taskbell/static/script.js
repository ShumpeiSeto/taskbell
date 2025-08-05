let intervalId;
// modal 用意
const modal = new bootstrap.Modal(document.getElementById("exampleModal"));
// modalのbody部
const modal_tasks = document.querySelector(".modal-tasks");

const close_modal = document.querySelector(".close_modal");

// dateオブジェクトに変換用編集関数
// const slice_date_str = function (date_str) {
//   const result = "20" + date_str.slice(0, 8);
//   return result.replaceAll("/", "-");
// };

intervalId ??= setInterval(checkdatetime, 180000);
function checkdatetime() {
  // クライアントセッションから取得
  const dead_minutes = sessionStorage.getItem("dead_minutes");
  // 親要素で取得した方がアクセスしやすい
  const nctask_items = document.querySelectorAll(".nc-task-item");
  // 比較のため現座日時取得
  const now = new Date();

  // modal tasks内容を初期化する
  modal_tasks.innerHTML = "";

  nctask_items.forEach((item) => {
    const date = item.querySelector(".deaddate").innerHTML;
    const time = item.querySelector(".deadtime").innerHTML;
    const taskname = item.querySelector(".taskname").innerHTML;

    const limity_date = item.dataset.deadline;
    const the_task_id = item.dataset.taskId;

    // 現在時との差異チェック
    // const datetime = slice_date_str(date) + "T" + time;
    // const datetime = new Date(limity_date);
    const diff =
      (new Date(limity_date).getTime() - now.getTime()) / (60 * 1000);

    // console.log(limity_date, diff);
    if (diff <= dead_minutes) {
      const tr = modal_tasks.appendChild(document.createElement("tr"));
      tr.classList.add("limity_task");
      const td_taskname = tr.appendChild(document.createElement("td"));
      const td_deaddate = tr.appendChild(document.createElement("td"));
      const td_deadtime = tr.appendChild(document.createElement("td"));
      const td_status = tr.appendChild(document.createElement("td"));
      td_taskname.textContent = taskname;
      td_deaddate.textContent = date;
      td_deadtime.textContent = time;
      td_status.textContent = diff <= 0 ? "期限切れ" : `${diff.toFixed(0)}分前`;
      modal.show();
    }
    // modal表示用
  });
}

// close_modal.addEventListener("click", function () {
//   const limity_tasks = document.querySelectorAll(".limity_task");
//   limity_tasks.remove();
// });
