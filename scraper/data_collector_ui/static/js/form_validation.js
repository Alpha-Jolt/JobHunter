document.getElementById('prefs-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const keywords = document.getElementById('keywords').value.split(',').map(s => s.trim()).filter(Boolean);
  const locations = document.getElementById('locations').value.split(',').map(s => s.trim()).filter(Boolean);
  const experience = document.getElementById('experience').value || undefined;
  const remote_preference = document.getElementById('remote').value || undefined;

  const payload = { keywords, locations, experience, remote_preference };

  const res = await fetch('/api/submit_preferences', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  const result = document.getElementById('result');
  result.style.display = 'block';
  result.textContent = `Search started for: ${data.keywords.join(', ')} in ${data.locations.join(', ')}`;
});
