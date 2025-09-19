let intervalId;
// modal 用意
const modal = new bootstrap.Modal(document.getElementById("exampleModal"));
const addTaskModal = new bootstrap.Modal(
  document.getElementById("addTaskModal")
);
const editTaskModal = new bootstrap.Modal(
  document.getElementById("editTaskModal")
);
const deleteTaskModal = new bootstrap.Modal(
  document.getElementById("deleteTaskModal")
);
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
  return date_str.slice(3, 10) + result;
};

const convertDate2 = function (date_obj) {
  const converted_date_str = date_obj.toISOString().slice(0, 10);
  // console.log(converted_date_str);
  return converted_date_str;
};

const convertDate3 = function (date_str) {
  const converted_date_str = date_str.slice(2, 10).replaceAll("-", "/");
  return converted_date_str;
};
const convertDate4 = function (date_str) {
  const converted_date_str = date_str.slice(5, 10).replaceAll("-", "/");
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
    const isValid = isValidNewTask();
    if (!isValid) {
      console.log("入力エラーがあります");
      return;
    }
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
function deleteTaskRow(taskId) {
  const taskRow = document.querySelector(`tr[data-task-id="${taskId}"]`);
  taskRow.remove();
}
const deleteConfirmTask = document.getElementById("deleteConfirmTask");
if (deleteConfirmTask) {
  deleteConfirmTask.addEventListener("click", async function (e) {
    e.preventDefault();
    // const taskId = document.getElementById("deleteTaskModal").dataset.taskId;
    try {
      const deleteTaskDom = document.querySelector("#deleteTaskModal");
      const task_id = deleteTaskDom.dataset.taskId;
      const response = await fetch(`/api/delete_task/${task_id}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(task_id),
      });
      if (response.ok) {
        const result = await response.json();
        console.log("API応答", result);
        deleteTaskRow(task_id);
      } else {
        console.error("APIエラー");
      }
    } catch (error) {
      console.log("通信エラー発生", error);
    }
    deleteTaskModal.hide();
  });
}

const saveEditTask = document.getElementById("saveEditTask");
if (saveEditTask) {
  saveEditTask.addEventListener("click", async function (e) {
    e.preventDefault();
    const isValid = isValidEditForm();
    if (!isValid) {
      console.log("入力エラーがあります");
      return;
    }
    const editTitle = document.getElementById("editTitle").value;
    const editDeadDate = document.getElementById("editDeadDate").value;
    const editDeadTime = document.getElementById("editDeadTime").value;
    const editDeadLine = new Date(
      makeDeadLine(editDeadDate, editDeadTime)
    ).toLocaleString();
    const importances = document.getElementsByName("editImportance");
    let len = importances.length;
    let importance = "";
    for (let i = 0; i < len; i++) {
      if (importances.item(i).checked) importance = importances.item(i).value;
    }
    const data = {
      title: editTitle,
      deadline: format_deadLine(editDeadLine),
      dead_date: editDeadDate,
      dead_time: editDeadTime,
      importance: parseInt(importance),
    };
    try {
      // ここのtask_idをどこから持ってくるか？
      const editTaskDom = document.querySelector("#editTaskModal");
      const task_id = editTaskDom.dataset.taskId;
      const response = await fetch(`/api/task/update/${task_id}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });
      if (response.ok) {
        const result = await response.json();
        console.log("API応答", result);
        editTaskRow(result.updateTask);
      } else {
        console.error("APIエラー");
      }
    } catch (error) {
      console.log("通信エラー発生", error);
    }
    editTaskModal.hide();
  });
}
function editTaskRow(updateTask) {
  const taskId = updateTask.task_id;
  const taskRow = document.querySelector(`tr[data-task-id="${taskId}"]`);
  // const taskRow = document.querySelector(`tr[data-task-id="${taskId}"]`);
  if (!taskRow) {
    console.log(`タスクID ${taskId}の行が見つかりません`);
    return;
  }
  taskRow.querySelector(".taskname").textContent = updateTask.title;
  taskRow.querySelector(".deaddate").textContent = convertDate(
    convertDate3(new Date(updateTask.dead_line).toISOString()),
    new Date(updateTask.dead_line).getDay()
  );
  taskRow.querySelector(".deadtime").textContent = updateTask.dead_time;
  taskRow.querySelector(".importance").textContent = convertImportance(
    updateTask.importance
  );
}
async function showEditModal(taskId) {
  document.getElementById("editTitle").value = "";
  document.getElementById("editDeadDate").value = "";
  document.getElementById("editDeadTime").value = "";
  hideElement(editDeadDate, editDeadDateError);
  hideElement(editDeadTime, editDeadTimeError);

  try {
    const response = await fetch(`/api/get_task/${taskId}`);
    const data = await response.json();
    if (data.status === "success") {
      document.getElementById("editTitle").value = data.task.title;
      document.getElementById("editDeadDate").value = data.task.dead_date;
      document.getElementById("editDeadTime").value = data.task.dead_time;
      const editImportance = document.getElementsByName("editImportance");
      Array.from(editImportance).forEach((el, i) => {
        if (i === data.task.importance) el.checked = true;
      });
      const editTaskModalDom = document.querySelector("#editTaskModal");
      editTaskModalDom.dataset.taskId = taskId;
      editTaskModal.show();
    } else {
      console.log("APIエラー:", response.status);
    }
  } catch (error) {
    console.log("通信エラー:", error);
  }
}

document.addEventListener("click", function (e) {
  if (e.target.classList.contains("edit-task-btn")) {
    const task_id = e.target.dataset.taskId;
    showEditModal(task_id);
  }
});
document.addEventListener("click", function (e) {
  if (e.target.classList.contains("delete-task-btn")) {
    const task_id = e.target.dataset.taskId;
    // console.log(task_id);
    deleteViewTask(task_id);
  }
});

const ncTbody = document.getElementById("nc-tbody");
const ncCheckPositionIndex = function (deadline) {
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

const cTbody = document.getElementById("c-tbody");
const cCheckPositionIndex = function (deadline) {
  let result = 0;
  const cTaskTrs = document.querySelectorAll("tr.c-task-item");
  const count = cTaskTrs.length;
  for (let i = 0; i < count; i++) {
    const target_deadline = cTaskTrs.item(i).dataset.deadline;
    if (new Date(deadline) > new Date(target_deadline)) result = i + 1;
  }
  console.log(result);
  return result;
};

async function deleteViewTask(taskId) {
  try {
    const response = await fetch(`/api/get_task/${taskId}`);
    const data = await response.json();
    if (data.status === "success") {
      const deleteTaskName = document.querySelector("#delete_task_title");
      deleteTaskName.textContent = data.task.title;
      const deleteTaskDate = document.querySelector("#delete_task_date");
      deleteTaskDate.textContent = data.task.dead_date;
      const deleteTaskTime = document.querySelector("#delete_task_time");
      deleteTaskTime.textContent = data.task.dead_time;
      const deleteTaskModalDom = document.querySelector("#deleteTaskModal");
      deleteTaskModalDom.dataset.taskId = taskId;
      deleteTaskModal.show();
    } else {
      console.log("APIエラー:", response.status);
    }
  } catch (error) {
    console.error("API通信エラー", error);
  }
  // modal表示
}

function addNewTaskRow(task) {
  const positionIndex = ncCheckPositionIndex(task.deadline);
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
                  <label class="taskname form-check-label my-auto">${
                    task.title
                  }</label>
                </td>
                <td width="15%" class="px-0 p-md-0 text-center align-middle">
                  <label class="deaddate my-auto">${convertDate(
                    convertDate3(new Date(task.deadline).toISOString()),
                    new Date(task.deadline).getDay()
                  )}</label>
                </td>
                <td width="10%" class="px-0 p-md-0 text-center align-middle">
                  <label class="deadtime my-auto">${new Date(
                    task.deadline
                  ).getHours()}:${new Date(task.deadline).getMinutes()}</label>
                </td>
                <td width="10%" class="px-0 p-md-0 text-center align-middle">
                  <label class="importance my-auto">${convertImportance(
                    task.importance
                  )}</label>
                </td>
                <td width="15%" class="px-0 p-md-0 text-center align-middle">
                  <div class="handle_buttons d-flex flex-row px-0 py-auto p-md-2 text-center justify-content-evenly align-middle gap-3 flex-grow">
                    <button type="button" class="btn btn-primary py-2 px-1 edit-task-btn" data-task-id=${
                      task.task_id
                    }>編集</button>
                    <button type="button" class="btn btn-danger py-2 px-1 delete-task-btn" data-task-id=${
                      task.task_id
                    }>削除</button>
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

async function moveTaskRow(taskId) {
  const taskRow = document.querySelector(`tr[data-task-id="${taskId}"]`);
  if (!taskRow) {
    console.log(`タスクID ${taskId}の行が見つかりません`);
    return;
  }

  // nodeごとコピーしておき原本ノードは削除
  const copyRow = taskRow.cloneNode(true);
  taskRow.remove();

  // 表形式に合うようにノードを編集
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

  // この際にソート情報をセッションから取り出して、適切な位置に入れ込む必要あり
  // const response = await fetch("/api/get_session");
  // const result = await response.json();
  console.log("完了済みテーブルのtbody:", completedTableBody);
  if (completedTableBody) {
    console.log(result.session);

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

  // 操作ボタンを「編集」を「戻す」に変更
  const handleButtonsDiv = row.querySelector(".handle_buttons");
  if (handleButtonsDiv) {
    handleButtonsDiv.innerHTML = `
            <a href="/checked/${taskId}" class="mb-1">
                <button type="button" class="btn btn-gray text-light py-2 px-1">戻す</button>
            </a>
            <button type="button" class="btn btn-danger py-2 px-1 delete-task-btn" data-task-id="${taskId}">削除</button>
        `;
  }
}
document.addEventListener("DOMContentLoaded", function () {
  document.removeEventListener("click", handleCheckboxClick);
  document.addEventListener("click", handleCheckboxClick);
});

async function returnTaskRow(taskId) {
  const taskRow = document.querySelector(`tr[data-task-id="${taskId}"]`);
  if (!taskRow) {
    console.log(`タスクID ${taskId}の行が見つかりません`);
    return;
  }
  // nodeごとコピーしておき原本ノードは削除
  const copyRow = taskRow.cloneNode(true);
  taskRow.remove();
  // 未完了表形式に合うようにノードを編集
  reverseAdjustRowForCompletedTable(copyRow, taskId);

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
  const nonCompletedTableBody = allTables[0]?.querySelector("tbody");
  console.log("未完了テーブルのtbody:", nonCompletedTableBody);
  if (nonCompletedTableBody) {
    console.log(result.session);

    nonCompletedTableBody.appendChild(copyRow);
    console.log(`タスク ${taskId}を未完了テーブルに移動しました`);
  } else {
    console.error("未完了テーブルが見つかりません");
  }
}

// 戻るボタンを押した時の整形関数
function reverseAdjustRowForCompletedTable(row, taskId) {
  // 最初のth要素（チェックボックス列）を追加
  const element = `
                <th width="10%" scope="row" class="px-0 p-md-2 text-center align-middle">
                  <input type="checkbox" class="check_box_fin rounded-circle px-1 py-2" data-task-id="${taskId}">
                </th>
  `;

  row.append(element);

  // タスク名のクラスを変更
  const taskNameLabel = row.querySelector(".comp_task_name");
  if (taskNameLabel) {
    taskNameLabel.className = "taskname";
  }

  // 期限のクラス調整
  const deadlineCells = row.querySelectorAll(".deaddate, .deadtime");
  deadlineCells.forEach((cell) => {
    const label = cell.querySelector("comp_task_deadline");
    if (label) {
      label.className = "label";
    }
  });

  // 最初のtdをwidth="50%"に変更（タスク名の幅調整）
  const firstTd = row.querySelector("td");
  if (firstTd) {
    firstTd.setAttribute("width", "40%");
  }

  // 操作ボタンを「戻す」を「編集」に変更
  const handleButtonsDiv = row.querySelector(".handle_buttons");
  if (handleButtonsDiv) {
    handleButtonsDiv.innerHTML = `
            <button type="button" class="btn btn-primary py-2 px-1 edit-task-btn" data-task-id="${taskId}">編集</button>
            <button type="button" class="btn btn-danger py-2 px-1 delete-task-btn" data-task-id="${taskId}">削除</button>
        `;
  }
}
document.addEventListener("DOMContentLoaded", function () {
  // document.removeEventListener("click", handleCheckboxClick);
  // document.addEventListener("click", handleCheckboxClick);
});
async function handleCheckboxClick(e) {
  if (e.target.classList.contains("check_box_fin")) {
    e.preventDefault();
    e.stopPropagation();
    // 最も近くにある.nc-task-itemのRow
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
  // console.log(sorted_nctasks);
  sorted_nctasks.forEach((task) => {
    const deadline_obj = new Date(task.deadline);
    const deaddate = formatDateStr(deadline_obj);
    const deadtime = `${String(deadline_obj.getHours()).padStart(
      2,
      "0"
    )}:${String(deadline_obj.getMinutes()).padStart(2, "0")}`;
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
  // console.log(limity_tasks_arr);
}

// test 用に
window.testSlack = checkdatetime;
