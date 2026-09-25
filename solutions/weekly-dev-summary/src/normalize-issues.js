const settings = $('Build Settings').first().json;
const start = Date.parse(settings.since);
const end = Date.parse(settings.until);
const rows = $input.all().flatMap((item) => {
  const value = item.json;
  if (Array.isArray(value)) return value;
  if (Array.isArray(value?.data)) return value.data;
  if (Array.isArray(value?.body)) return value.body;
  return value && typeof value === 'object' ? [value] : [];
});

const items = rows.filter((row) => {
  if (!row || row.pull_request || row.state !== 'closed' || !row.closed_at) return false;
  const closed = Date.parse(row.closed_at);
  return Number.isFinite(closed) && closed >= start && closed <= end;
}).map((row) => ({
  number: row.number,
  title: String(row.title || '').slice(0, 180),
  closedAt: row.closed_at,
  url: row.html_url,
}));

return [{ json: { kind: 'issues', items } }];
