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
  if (!row?.merged_at) return false;
  const merged = Date.parse(row.merged_at);
  return Number.isFinite(merged) && merged >= start && merged <= end;
}).map((row) => ({
  number: row.number,
  title: String(row.title || '').slice(0, 180),
  mergedAt: row.merged_at,
  url: row.html_url,
}));

return [{ json: { kind: 'pulls', items } }];
