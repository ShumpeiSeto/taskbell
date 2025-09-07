const loginForm = document.querySelector(".login_form");
const signupForm = document.querySelector(".signup_form");
const username = document.getElementById("username");
const usernameError = document.getElementById("usernameError");
const password = document.getElementById("password");
const passwordError = document.getElementById("passwordError");
const confpassword = document.getElementById("conf_password");
const confpasswordError = document.getElementById("conf_passwordError");

// Setting Page
const settingForm = document.querySelector(".setting_form");
const email = document.getElementById("email");
const emailError = document.getElementById("emailError");
const slack = document.getElementById("slack_url");
const slackError = document.getElementById("slackError");
const time = document.getElementById("morning_time");
const timeError = document.getElementById("timeError");

// 新規タスク追加ページ, タスク編集ページ
const addTaskForm = document.querySelector(".add_task_form");
const editTaskForm = document.querySelector(".edit_task_form");
const title = document.getElementById("title");
const titleError = document.getElementById("titleError");
const deadDate = document.getElementById("dead_date");
const deaddateError = document.getElementById("deaddateError");
const deadTime = document.getElementById("dead_time");
const deadtimeError = document.getElementById("deadtimeError");

// 要素の非表示関数(共通)
const showElement = function (inputElement, errorElement, message) {
  errorElement.textContent = message;
  errorElement.style.display = "block";
  inputElement.style.borderColor = "red";
};
const hideElement = function (inputElement, errorElement) {
  errorElement.textContent = "";
  errorElement.style.display = "none";
  inputElement.style.borderColor = null;
};

const validationMinRequired = function (value, minLength) {
  return value.trim() && value.trim().length >= minLength;
};
const validationMaxRequired = function (value, maxLength) {
  return value.trim() && value.trim().length < maxLength;
};

const validatePasswordMatch = function (password, confPassword) {
  return password.value.trim() === confPassword.value.trim();
};
if (username) {
  username.addEventListener("blur", function (e) {
    if (validateEmpty(username.value)) {
      showElement(username, usernameError, "ユーザー名が入力されていません");
    } else if (!validationMinRequired(username.value, 3)) {
      showElement(
        username,
        usernameError,
        "ユーザー名は3文字以上で入力して下さい"
      );
    } else {
      hideElement(username, usernameError);
    }
  });
}
if (password) {
  password.addEventListener("blur", function (e) {
    if (validateEmpty(password.value)) {
      showElement(password, passwordError, "パスワードが入力されていません");
    } else if (!validationMinRequired(password.value, 8)) {
      showElement(
        password,
        passwordError,
        "パスワードは８文字以上で入力して下さい"
      );
    } else {
      hideElement(password, passwordError);
    }
  });
}
if (confpassword) {
  confpassword.addEventListener("blur", function (e) {
    if (!confpassword.value.trim()) {
      showElement(
        confpassword,
        confpasswordError,
        "確認のパスワードを入力して下さい"
      );
    } else if (!validatePasswordMatch(password, confpassword)) {
      showElement(
        confpassword,
        confpasswordError,
        "入力したパスワードが一致していません"
      );
    } else {
      hideElement(confpassword, confpasswordError);
    }
  });
}
// 新規ユーザー登録画面
if (signupForm) {
  signupForm.addEventListener("submit", function (e) {
    let hasErrors = false;
    // defaultでリロードするのでそれを防止
    e.preventDefault();
    if (!validationMinRequired(username.value, 3)) {
      showElement(
        username,
        usernameError,
        "ユーザー名は3文字以上で入力して下さい"
      );
      hasErrors = true;
    }
    if (!validationMinRequired(password.value, 8)) {
      showElement(
        password,
        passwordError,
        "パスワードは８文字以上で入力して下さい"
      );
      hasErrors = true;
    } else if (!confpassword.value.trim()) {
      showElement(
        confpassword,
        confpasswordError,
        "確認のパスワードを入力して下さい"
      );
      hasErrors = true;
    } else if (!validatePasswordMatch(password, confpassword)) {
      showElement(
        confpassword,
        confpasswordError,
        "入力したパスワードが一致していません"
      );
      hasErrors = true;
    }
    if (!hasErrors) {
      signupForm.submit();
    }
  });
}

if (loginForm) {
  loginForm.addEventListener("submit", function (e) {
    let hasErrors = false;
    e.preventDefault();
    // ユーザー名チェック
    if (validateEmpty(username.value)) {
      showElement(username, usernameError, "ユーザー名が入力されていません");
      hasErrors = true;
    } else if (!validationMinRequired(username.value, 3)) {
      showElement(
        username,
        usernameError,
        "ユーザー名は3文字以上で入力して下さい"
      );
      hasErrors = true;
    } else {
      hideElement(username, usernameError);
    }
    // パスワードチェック
    if (validateEmpty(password.value)) {
      showElement(password, passwordError, "パスワードが入力されていません");
      hasErrors = true;
    } else if (!validationMinRequired(password.value, 8)) {
      showElement(
        password,
        passwordError,
        "パスワードは８文字以上で入力して下さい"
      );
      hasErrors = true;
    } else {
      hideElement(password, passwordError);
    }
    if (!hasErrors) {
      loginForm.submit();
    }
  });
}
// Setting Page

// 要素の非表示関数(共通)
const showElement2 = function (inputElement, errorElement, message) {
  errorElement.textContent = message;
  errorElement.style.display = "block";
  errorElement.style.color = "red";
  inputElement.style.borderColor = "red";
};
const restoreElement = function (inputElement, errorElement, message) {
  errorElement.textContent = message;
  // errorElement.style.display = "none";
  errorElement.style.color = "gray";
  inputElement.style.borderColor = null;
};
// const validationRequired = function (value, minLength) {
//   return value.trim() && value.trim().length >= minLength;
// };

const validateEmpty = function (value) {
  return !value.trim();
};

const validateEmail = function (value) {
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return value.trim() && value.trim().match(pattern);
};

const check3input = function () {
  if (!slack.value.trim() && !email.value.trim()) {
    slack.style.borderColor = "red";
    email.style.borderColor = "red";
    timeError.style.color = "red";
    timeError.textContent =
      "通知を送るためにはSlackのURLかメールアドレスの入力が必要です";
  } else if (slack.value.trim() && !email.value.trim()) {
    slack.style.borderColor = "gray";
    email.style.borderColor = "gray";
    timeError.style.color = "green";
    timeError.textContent = "毎日この時間にSlack通知を送ります";
  } else if (!slack.value.trim() && email.value.trim()) {
    slack.style.borderColor = "gray";
    email.style.borderColor = "gray";
    timeError.style.color = "blue";
    timeError.textContent = "毎日この時間にメール通知を送ります";
  } else {
    slack.style.borderColor = "gray";
    email.style.borderColor = "gray";
    timeError.textContent = "毎日この時間にSlackとメールで通知します";
  }
};
// const validateTime = function (value) {
//   const pattern = /^[\d]{2}:[\d]{d}$/;
//   return value.trim() && value.trim().match(pattern);
// };

// 設定画面
if (email) {
  email.addEventListener("blur", function (e) {
    if (!validateEmail(email.value)) {
      showElement2(email, emailError, "正しいメール形式で入力して下さい");
    } else if (validateEmpty(email.value)) {
      restoreElement(email, emailError, "通知を受け取りたいメールアドレス");
    } else {
      restoreElement(email, emailError, "通知を受け取りたいメールアドレス");
      slack.style.borderColor = "var(--bs-border-color)";
    }
    check3input();
  });
}
if (time) {
  time.addEventListener("blur", function (e) {
    check3input();
  });
}

// 新規タスク追加ページ, タスク編集ページ
if (title) {
  title.addEventListener("blur", function () {
    if (validateEmpty(title.value)) {
      showElement(deadDate, deaddateError, "日付が入力されていません");
    } else if (!validationMaxRequired(title.value, 30)) {
      showElement(title, titleError, "タスク名は30文字以内で入力してください");
    } else {
      hideElement(title, titleError);
    }
  });
}
if (deadDate) {
  deadDate.addEventListener("blur", function () {
    const now = new Date();
    const nowDate = new Date(
      `${now.getFullYear()}/${now.getMonth() + 1}/${now.getDay()}`
    );
    const target_date = new Date(
      `${deadDate.value.trim().replaceAll("-", "/")}`
    );
    if (validateEmpty(deadDate.value)) {
      showElement(deadDate, deaddateError, "日付が入力されていません");
    } else if (target_date < nowDate) {
      showElement(deadDate, deaddateError, "過去の日付は入力できません");
    } else {
      hideElement(deadDate, deaddateError);
    }
  });
}

if (deadTime) {
  deadTime.addEventListener("blur", function () {
    const now = new Date();
    const target_datetime = new Date(
      `${deadDate.value.trim().replaceAll("-", "/")} ${deadTime.value.trim()}`
    );
    console.log(target_datetime);
    if (validateEmpty(deadTime.value)) {
      showElement(deadTime, deadtimeError, "時刻が入力されていません");
    } else if (target_datetime < now) {
      showElement(deadTime, deadtimeError, "過去の日時は登録できません");
    } else {
      hideElement(deadTime, deadtimeError);
    }
  });
}
if (addTaskForm) {
  addTaskForm.addEventListener("submit", function (e) {
    let hasErrors = false;
    e.preventDefault();
    // title のチェック
    console.log(title.value, deadDate.value, deadTime.value);
    if (validateEmpty(title.value)) {
      showElement(title, titleError, "タスク名が入力されていません");
    } else if (!validationMaxRequired(title.value, 30)) {
      showElement(title, titleError, "タスク名は30文字以内で入力してください");
      hasErrors = true;
    } else {
      hideElement(title, titleError);
    }

    // 日にちチェック
    const now = new Date();
    const nowDate = new Date(
      `${now.getFullYear()}/${now.getMonth() + 1}/${now.getDay()}`
    );
    const target_date = new Date(
      `${deadDate.value.trim().replaceAll("-", "/")}`
    );
    if (validateEmpty(deadDate.value)) {
      showElement(deadDate, deaddateError, "日付が入力されていません");
      hasErrors = true;
    } else if (target_date < nowDate) {
      showElement(deadDate, deaddateError, "過去の日付は入力できません");
      hasErrors = true;
    } else {
      hideElement(deadDate, deaddateError);
    }
    const target_datetime = new Date(
      `${deadDate.value.trim()?.replaceAll("-", "/")} ${deadTime.value.trim()}`
    );
    // console.log(target_datetime);
    if (validateEmpty(deadTime.value)) {
      showElement(deadTime, deadtimeError, "時刻が入力されていません");
      hasErrors = true;
    } else if (target_datetime < now) {
      showElement(deadTime, deadtimeError, "過去の日時は登録できません");
      hasErrors = true;
    } else {
      hideElement(deadTime, deadtimeError);
    }
    if (!hasErrors) {
      addTaskForm.submit();
    }
  });
}

if (editTaskForm) {
  editTaskForm.addEventListener("submit", function (e) {
    let hasErrors = false;
    e.preventDefault();
    // title のチェック
    if (validateEmpty(title.value)) {
      showElement(title, titleError, "タスク名が入力されていません");
      hasErrors = true;
    } else if (!validationMaxRequired(title.value, 30)) {
      showElement(title, titleError, "タスク名は30文字以内で入力してください");
      hasErrors = true;
    } else {
      hideElement(title, titleError);
    }

    // 日にちチェック
    const now = new Date();
    const nowDate = new Date(
      `${now.getFullYear()}/${now.getMonth() + 1}/${now.getDay()}`
    );
    const target_date = new Date(
      `${deadDate.value.trim().replaceAll("-", "/")}`
    );
    if (validateEmpty(deadDate.value)) {
      showElement(deadDate, deaddateError, "日付が入力されていません");
      hasErrors = true;
    } else if (target_date < nowDate) {
      showElement(deadDate, deaddateError, "過去の日付は入力できません");
      hasErrors = true;
    } else {
      hideElement(deadDate, deaddateError);
    }
    const target_datetime = new Date(
      `${deadDate.value.trim().replaceAll("-", "/")} ${deadTime.value.trim()}`
    );
    console.log(target_datetime);
    if (validateEmpty(deadTime.value)) {
      showElement(deadTime, deadtimeError, "時刻が入力されていません");
      hasErrors = true;
    } else if (target_datetime < now) {
      showElement(deadTime, deadtimeError, "過去の日時は登録できません");
      hasErrors = true;
    } else {
      hideElement(deadTime, deadtimeError);
    }
    if (!hasErrors) {
      editTaskForm.submit();
    }
  });
}
