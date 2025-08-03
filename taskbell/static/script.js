let intervalId;

const slice_date_str = function (date_str) {
  const result = "20" + date_str.slice(0, 8);
  return result.replaceAll("/", "-");
};

intervalId ??= setInterval(checkdatetime, 30000);
function checkdatetime() {
  const now = new Date();
  const dates = document.querySelectorAll(".deaddate");
  const times = document.querySelectorAll(".deadtime");
  const nct_counts = dates.length;
  for (let i = 0; i < nct_counts; i++) {
    const datetime =
      slice_date_str(dates[i].innerText) + "T" + times[i].innerText;
    const diff = (new Date(datetime).getTime() - now.getTime()) / (60 * 1000);
    console.log(datetime, diff);
  }
}
