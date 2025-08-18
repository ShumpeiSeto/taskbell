let intervalId;
// modal 用意
const modal = new bootstrap.Modal(document.getElementById("exampleModal"));
// modalのbody部
const modal_tasks = document.querySelector(".modal-tasks");

const close_modal = document.querySelector(".close_modal");

//
let limity_tasks_arr = [];

// 3分ごとにチェックしている（3分180,000ms）
intervalId ??= setInterval(checkdatetime, 180000);
function checkdatetime() {
  // クライアントセッションから取得
  const dl_time = sessionStorage.getItem("dl_time");
  // 親要素で取得した方がアクセスしやすい
  const nctask_items = document.querySelectorAll(".nc-task-item");
  // 比較のため現座日時取得
  const now = new Date();

  // modal tasks内容を初期化する
  modal_tasks.innerHTML = "";

  // 通知用期限保持をクリアする
  limity_tasks_arr.splice(0);

  nctask_items.forEach((item) => {
    const date = item.querySelector(".deaddate").innerHTML;
    const time = item.querySelector(".deadtime").innerHTML;
    const taskname = item.querySelector(".taskname").innerHTML;
    const importance = item.querySelector(".importance").innerHTML;

    const limity_date = item.dataset.deadline;
    const the_task_id = item.dataset.taskId;

    // slack通知用タスク
    // const post_tasks = [];

    // 現在時との差異チェック
    // const datetime = slice_date_str(date) + "T" + time;
    // const datetime = new Date(limity_date);
    const diff =
      (new Date(limity_date).getTime() - now.getTime()) / (60 * 1000);

    // console.log(limity_date, diff);
    if (diff <= dl_time) {
      const tr = modal_tasks.appendChild(document.createElement("tr"));
      tr.classList.add("limity_task");
      const td_taskname = tr.appendChild(document.createElement("td"));
      const td_deaddate = tr.appendChild(document.createElement("td"));
      const td_deadtime = tr.appendChild(document.createElement("td"));
      const td_importance = tr.appendChild(document.createElement("td"));
      const td_status = tr.appendChild(document.createElement("td"));
      td_taskname.textContent = taskname;
      td_deaddate.textContent = date;
      td_deadtime.textContent = time;
      td_importance.textContent = importance;
      status_result = diff <= 0 ? "期限切れ" : `${diff.toFixed(0)}分前`;
      td_status.textContent = status_result;

      // slack通知用オブジェクト作る
      const post_obj = {
        the_task_id,
        taskname,
        limity_date,
        importance,
        status_result,
      };
      limity_tasks_arr.push(post_obj);

      modal.show();
      if (diff <= 0) {
        td_status.classList.add("text-danger", "fw-bold");
      }
    }
    // modal表示用
  });
  console.log(limity_tasks_arr);
}

// close_modal.addEventListener("click", function () {
//   const limity_tasks = document.querySelectorAll(".limity_task");
//   limity_tasks.remove();
// });
