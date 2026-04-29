async function fetchJSON(url) {
  const res = await fetch(url);
  return res.json();
}

async function loadStats() {
  const data = await fetchJSON('/api/jobs/stats');
  document.getElementById('stats-output').textContent =
    `Total jobs: ${data.total_jobs} | Output files: ${data.output_files}`;
}

async function loadLogs() {
  const data = await fetchJSON('/api/logs?limit=50');
  document.getElementById('log-output').textContent = data.join('\n');
}

async function trigger(source) {
  const res = await fetch(`/api/scraper/trigger?source=${source}`, { method: 'POST' });
  const data = await res.json();
  document.getElementById('trigger-output').textContent = JSON.stringify(data);
}

loadStats();
loadLogs();
setInterval(loadLogs, 10000);
