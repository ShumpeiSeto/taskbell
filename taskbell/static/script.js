let intervalId;
// modal 用意
const modal = new bootstrap.Modal(document.getElementById("exampleModal"));
// modalのbody部
const modal_tasks = document.querySelector(".modal-tasks");

const close_modal = document.querySelector(".close_modal");

let limity_tasks_arr = [];

// 重要度から星表現に変換
const convertImportance = function (importance) {
  const importanceStars = ["★", "★★", "★★★"];
  return importanceStars[importance];
};

// Day()の数字を引数に文字列に曜日を付加して返す関数
const convertDate = function (date_str, dayNum) {
  // 期限切れもしくは期限接近タスク日時は今日昨日表示がある
  // それ以外の日付は"25/09/09"などの表示をする
  const today = new Date().toISOString().replaceAll("-", "/").slice(2, 10);
  let yesterday = new Date();
  yesterday.setDate(yesterday.getDate() + 1);
  yesterday = yesterday.toISOString().replaceAll("-", "/").slice(2, 10);
  console.log(date_str);
  console.log(today);
  if (date_str === today) return "今日";
  if (date_str === yesterday) return "昨日";

  result = "";

  if (dayNum === 0) {
    result = "(日)";
  } else if (dayNum === 1) {
    result = "(月)";
  } else if (dayNum === 2) {
    result = "(火)";
  } else if (dayNum === 3) {
    result = "(水)";
  } else if (dayNum === 4) {
    result = "(木)";
  } else if (dayNum === 5) {
    result = "(金)";
  } else if (dayNum === 6) {
    result = "(土)";
  }
  return date_str + result;
};

const formatDateStr = function (deadline_obj) {
  const result =
    `${deadline_obj.getFullYear()}`.slice(2, 4) +
    "/" +
    `${deadline_obj.getMonth() + 1}`.padStart(2, "0") +
    "/" +
    `${deadline_obj.getDate()}`.padStart(2, "0");
  return result;
};

// 3分ごとにチェックしている（3分180,000ms）
intervalId ??= setInterval(checkdatetime, 60000);
async function checkdatetime() {
  // クライアントセッションからユーザーが設定したタスク通知時間を取得
  const dl_time = sessionStorage.getItem("dl_time");
  // const nctask_items = document.querySelectorAll(".nc-task-item");
  const response = await fetch("/api/tasks/limity");
  const result = await response.json();
  const nctaks = result.data;
  const now = new Date();

  // modal tasks内容を初期化しておく
  modal_tasks.innerHTML = "";

  // 通知用期限タスク配列をクリアする
  limity_tasks_arr.splice(0);

  nctaks.forEach((task) => {
    const deadline_obj = new Date(task.deadline);
    const deaddate = formatDateStr(deadline_obj);
    const deadtime = `${deadline_obj.getHours()}:${deadline_obj.getMinutes()}`;
    const deadline = task.format_deadline;
    const title = task.title;
    const importance = task.importance;
    const taskId = task.id;
    const deadday = deadline_obj.getDay();
    // const date = item.querySelector(".deaddate").innerHTML;
    // const time = item.querySelector(".deadtime").innerHTML;
    // const taskname = item.querySelector(".taskname").innerHTML;
    // const importance = item.querySelector(".importance").innerHTML;

    // const limity_date = item.dataset.deadline;
    // const the_task_id = item.dataset.taskId;

    // 現在日時との差を計算
    const diff = (deadline_obj.getTime() - now.getTime()) / (60 * 1000);

    // 設定された通知時間以内の場合は表を埋めてモーダル表示する
    if (diff <= dl_time) {
      const tr = modal_tasks.appendChild(document.createElement("tr"));
      tr.classList.add("limity_task");
      const td_taskname = tr.appendChild(document.createElement("td"));
      const td_deaddate = tr.appendChild(document.createElement("td"));
      const td_deadtime = tr.appendChild(document.createElement("td"));
      const td_importance = tr.appendChild(document.createElement("td"));
      const td_status = tr.appendChild(document.createElement("td"));
      td_taskname.textContent = title;
      td_taskname.classList.add("text-center", "align-middle");
      td_deaddate.textContent = convertDate(deaddate, deadday);
      td_deaddate.classList.add("text-center", "align-middle");
      td_deadtime.textContent = deadtime;
      td_deadtime.classList.add("text-center", "align-middle");
      td_importance.textContent = convertImportance(importance);
      td_importance.classList.add("text-center", "align-middle");
      td_importance.style.color = "red";
      status_result = diff <= 0 ? "期限切れ" : `${diff.toFixed(0)}分前`;
      td_status.textContent = status_result;
      td_status.classList.add("text-center", "align-middle");

      // コンソールでテスト出力用
      const test_limity_task = {
        taskId,
        title,
        deadline,
        importance,
        status_result,
      };
      limity_tasks_arr.push(test_limity_task);

      modal.show();
      if (diff <= 0) {
        td_status.classList.add("text-danger", "fw-bold");
      }
    }
  });
  console.log(limity_tasks_arr);
}

// async function noticeLimityTasks() {
//   const response = await fetch("/api/tasks/limity");
//   const result = await response.json();
//   // slackの返り値の判定を後ほど書く
//   const slackResponse = await fetch("/api/slack/notify_limit", {
//     method: "POST",
//     headers: {
//       "Content-Type": "application/json",
//     },
//     body: JSON.stringify({
//       limity_tasks: result.data,
//     }),
//   });
// }

// // 初回実行
// // my_task.html読み込み時に毎回実行されている
// if (sessionStorage.getItem("is_first_slack") === "1") {
//   console.log(sessionStorage.getItem("is_first_slack"));
//   noticeLimityTasks();
//   sessionStorage.setItem("is_first_slack", "0");
//   console.log(sessionStorage.getItem("is_first_slack"));
// }
// // 30分ごとに自動実行
// intervalId ??= setInterval(noticeLimityTasks, 10 * 60 * 1000);

// // test 用に
// window.testSlack = noticeLimityTasks;
