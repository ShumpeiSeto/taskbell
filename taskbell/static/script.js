let intervalId;
// modal 用意
const modal = new bootstrap.Modal(document.getElementById("exampleModal"));
// modalのbody部
const modal_tasks = document.querySelector(".modal-tasks");

const close_modal = document.querySelector(".close_modal");

const addTaskModal = new bootstrap.Modal(
  document.getElementById("addTaskModal")
);
const deleteTaskModal = new bootstrap.Modal(
  document.getElementById("deleteTaskModal")
);
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
  yesterday.setDate(yesterday.getDate() - 1);
  yesterday = yesterday.toISOString().replaceAll("-", "/").slice(2, 10);
  let tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  tomorrow = tomorrow.toISOString().replaceAll("-", "/").slice(2, 10);
  console.log(date_str);
  console.log(today);
  if (date_str === today) return "今日";
  else if (date_str === yesterday) return "昨日";
  else if (date_str === tomorrow) return "明日";

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

const convertDate2 = function (date_obj) {
  const converted_date_str = date_obj.toISOString().slice(0, 10);
  console.log(converted_date_str);
  return converted_date_str;
};

const convertDate3 = function (date_str) {
  const converted_date_str = date_str.slice(2, 10).replaceAll("-", "/");
  return converted_date_str;
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
const makeDeadLine = function (deadDate, deadTime) {
  const deadLineStr = `${deadDate} ${deadTime}`;
  console.log(deadLineStr);
  return deadLineStr;
};

const format_deadLine = function (deadLineStr) {
  result = deadLineStr.replaceAll("/", "-");
  return result;
};

const saveNewTask = document.getElementById("saveNewTask");
if (saveNewTask) {
  saveNewTask.addEventListener("click", async function (e) {
    e.preventDefault();
    const newTitle = document.getElementById("title").value;
    const newDeadDate = document.getElementById("dead_date").value;
    const newDeadTime = document.getElementById("dead_time").value;
    const deadLine = new Date(
      makeDeadLine(newDeadDate, newDeadTime)
    ).toLocaleString();
    const importances = document.getElementsByName("importance");
    let len = importances.length;
    let importance = "";
    for (let i = 0; i < len; i++) {
      if (importances.item(i).checked) importance = importances.item(i).value;
    }
    const data = {
      title: newTitle,
      deadline: format_deadLine(deadLine),
      importance: parseInt(importance),
    };
    console.log(data);
    try {
      const response = await fetch("/api/task/create", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });
      if (response.ok) {
        const result = await response.json();
        console.log("API応答", result);
        addNewTaskRow(result.data);
      } else {
        console.error("APIエラー");
      }
    } catch (error) {
      console.log("通信エラー発生", error);
    }
    console.log("値を初期化します");

    // 値を初期化する
    document.querySelector("#title").value = "";
    document.querySelector("#dead_date").value = "";
    document.querySelector("#dead_time").value = "";
    // 重要度初期値は低にしておく
    Array.from(importances).forEach((el, i) => {
      if (i === 0) el.checked = true;
      else el.checked = false;
    });

    // Modalハイドする
    addTaskModal.hide();
  });
}

const ncTbody = document.getElementById("nc-tbody");
const checkPositionIndex = function (deadline) {
  let result = 0;
  const ncTaskTrs = document.querySelectorAll("tr.nc-task-item");
  const count = ncTaskTrs.length;
  for (let i = 0; i < count; i++) {
    const target_deadline = ncTaskTrs.item(i).dataset.deadline;
    if (new Date(deadline) > new Date(target_deadline)) result = i + 1;
  }
  console.log(result);
  return result;
};

function deleteViewTask(task_id) {
  try {
    const response = await fetch("/api/delete_task/", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
  
  }
  // modal表示
}

function addNewTaskRow(task) {
  const deleteTaskUrl = `/delete_task/${task.task_id}`;
  const editTaskUrl = `/edit_task/${task.task_id}`;
  const positionIndex = checkPositionIndex(task.deadline);
  const ncTaskTrs = document.querySelectorAll("tr.nc-task-item");
  const targetTr = ncTaskTrs.item(positionIndex);
  const element = `
              <tr class="nc-task-item" data-deadline="${
                task.deadline
              }" data-task-id="${task.task_id}">
                <th width="10%" scope="row" class="px-0 p-md-2 text-center align-middle">
                  <!-- aタグを削除、直接チェックボックスのみ -->
                  <input type="checkbox" class="check_box_fin rounded-circle px-1 py-2" data-task-id="${
                    task.task_id
                  }">
                </th>
                <td width="40%" class="px-0 p-md-0 text-center align-middle">
                  <label class="taskname form-check-label my-auto" for="firstCheckbox">${
                    task.title
                  }</label>
                </td>
                <td width="15%" class="px-0 p-md-0 text-center align-middle">
                  <label class="deaddate my-auto" for="deadline">${convertDate(
                    convertDate3(new Date(task.deadline).toISOString()),
                    new Date(task.deadline).getDay()
                  )}</label>
                </td>
                <td width="10%" class="px-0 p-md-0 text-center align-middle">
                  <label class="deadtime my-auto" for="deadline">${new Date(
                    task.deadline
                  ).getHours()}:${new Date(task.deadline).getMinutes()}</label>
                </td>
                <td width="10%" class="px-0 p-md-0 text-center align-middle">
                  <label class="importance my-auto" for="importance">${
                    task.importance
                  }</label>
                </td>
                <td width="15%" class="px-0 p-md-0 text-center align-middle">
                  <div class="handle_buttons d-flex flex-row px-0 py-auto p-md-2 text-center justify-content-evenly align-middle gap-3 flex-grow">
                    <a href="${editTaskUrl}" class="mb-1"><button type="button" class="btn btn-primary py-2 px-1">編集</button></a>
                    <a href="${deleteTaskUrl}"><button type="button" class="btn btn-danger py-2 px-1">削除</button></a>
                  </div>
                </td>
              </tr>
  `;
  if (targetTr) {
    targetTr.insertAdjacentHTML("beforebegin", element);
  } else {
    ncTbody.insertAdjacentHTML("beforeend", element);
  }

  // ncTbody.insertBefore(element, targetTr);
}

function moveTaskRow(taskId) {
  const taskRow = document.querySelector(`tr[data-task-id="${taskId}"]`);
  if (!taskRow) {
    console.log(`タスクID ${taskId}の行が見つかりません`);
    return;
  }

  const copyRow = taskRow.cloneNode(true);
  taskRow.remove();

  adjustRowForCompletedTable(copyRow, taskId);

  // より安全な方法でテーブルを特定
  const allTables = document.querySelectorAll(".table");
  console.log("見つかったテーブル数:", allTables.length);

  // 各テーブルをログ出力して確認
  allTables.forEach((table, index) => {
    console.log(
      `テーブル${index}:`,
      table.closest(".row, .modal")?.querySelector("h4, h1")?.textContent ||
        "モーダル内"
    );
  });

  // 最後のテーブル（完了済み）を使用
  const completedTableBody =
    allTables[allTables.length - 1]?.querySelector("tbody");

  console.log("完了済みテーブルのtbody:", completedTableBody);
  if (completedTableBody) {
    completedTableBody.appendChild(copyRow);
    console.log(`タスク ${taskId}を完了済みテーブルに移動しました`);
  } else {
    console.error("完了済みテーブルが見つかりません");
  }
}
function adjustRowForCompletedTable(row, taskId) {
  // 最初のth要素（チェックボックス列）を削除
  const checkboxCell = row.querySelector("th");
  if (checkboxCell) {
    checkboxCell.remove();
  }

  // タスク名のクラスを変更
  const taskNameLabel = row.querySelector(".taskname");
  if (taskNameLabel) {
    taskNameLabel.className = "comp_task_name";
  }

  // 期限のクラス調整
  const deadlineCells = row.querySelectorAll(".deaddate, .deadtime");
  deadlineCells.forEach((cell) => {
    const label = cell.querySelector("label");
    if (label) {
      label.className = "comp_task_deadline";
    }
  });

  // 最初のtdをwidth="50%"に変更（タスク名の幅調整）
  const firstTd = row.querySelector("td");
  if (firstTd) {
    firstTd.setAttribute("width", "50%");
  }

  // 操作ボタンを「戻す」「削除」に変更
  const handleButtonsDiv = row.querySelector(".handle_buttons");
  if (handleButtonsDiv) {
    handleButtonsDiv.innerHTML = `
            <a href="/checked/${taskId}" class="mb-1">
                <button type="button" class="btn btn-gray text-light py-2 px-1">戻す</button>
            </a>
            <a href="/delete_task/${taskId}">
                <button type="button" class="btn btn-danger py-2 px-1">削除</button>
            </a>
        `;
  }
}
document.addEventListener("DOMContentLoaded", function () {
  document.removeEventListener("click", handleCheckboxClick);
  document.addEventListener("click", handleCheckboxClick);
});

async function handleCheckboxClick(e) {
  if (e.target.classList.contains("check_box_fin")) {
    e.preventDefault();
    e.stopPropagation();
    const taskRow = e.target.closest("tr");
    const taskId = taskRow.dataset.taskId;
    e.target.disabled = true;
    try {
      const response = await fetch(`/api/checked/${taskId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });
      if (response.ok) {
        const result = await response.json();
        console.log("API応答:", result);
        moveTaskRow(taskId);
      } else {
        console.error("APIエラー:", response.status);
        e.target.disabled = false;
      }
    } catch (error) {
      console.log("通信エラー:", error);
      e.target.disabled = false;
    }
  }
}

// 3分ごとにチェックしている（3分180,000ms）
intervalId ??= setInterval(checkdatetime, 60000);
async function checkdatetime() {
  // クライアントセッションからユーザーが設定したタスク通知時間を取得
  const dl_time = sessionStorage.getItem("dl_time");
  // const nctask_items = document.querySelectorAll(".nc-task-item");
  const response = await fetch("/api/tasks/limity");
  const result = await response.json();
  const nctasks = result.data;
  const now = new Date();

  // modal tasks内容を初期化しておく
  modal_tasks.innerHTML = "";

  // 通知用期限タスク配列をクリアする
  limity_tasks_arr.splice(0);

  const sorted_nctasks = nctasks.toSorted(
    (a, b) => new Date(a.deadline) - new Date(b.deadline)
  );
  console.log(sorted_nctasks);
  sorted_nctasks.forEach((task) => {
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
      const td_dateinput = td_deaddate.appendChild(
        document.createElement("input")
      );
      td_dateinput.setAttribute("type", "date");
      // td_dateinput.value = "12/1";
      // td_dateinput.value = `${
      //   task.deadline.getMonth() + 1
      // }/${task.deadline.getDay()}`;
      const td_deadtime = tr.appendChild(document.createElement("td"));
      const td_timeinput = td_deadtime.appendChild(
        document.createElement("input")
      );
      td_timeinput.setAttribute("type", "time");
      // td_timeinput.value = "08:00";
      // td_timeinput.value = `${task.deadline.getHours()}:${
      //   task.deadline.getMinutes
      // }`;
      const td_importance = tr.appendChild(document.createElement("td"));
      const td_status = tr.appendChild(document.createElement("td"));
      td_taskname.textContent = title;
      td_taskname.classList.add("text-center", "align-middle");
      // td_deaddate.textContent = convertDate(deaddate, deadday);
      td_dateinput.value = convertDate2(deadline_obj);
      td_deaddate.classList.add("text-center", "align-middle");
      // td_deadtime.textContent = deadtime;
      td_timeinput.value = deadtime;
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
