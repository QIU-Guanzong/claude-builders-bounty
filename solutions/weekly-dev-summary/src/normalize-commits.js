const rows = $input.all().flatMap((item) => {
  const value = item.json;
  if (Array.isArray(value)) return value;
  if (Array.isArray(value?.data)) return value.data;
  if (Array.isArray(value?.body)) return value.body;
  return value && typeof value === 'object' ? [value] : [];
});

const items = rows.filter((row) => row && row.sha && row.commit?.author?.date)
  .map((row) => ({
    sha: String(row.sha).slice(0, 12),
    date: row.commit.author.date,
    author: row.author?.login || row.commit.author.name || 'unknown',
    title: String(row.commit.message || '').split('\n')[0].slice(0, 180),
    url: row.html_url,
  }));

return [{ json: { kind: 'commits', items } }];
