async function loadJSON(path) {
  try {
    const response = await fetch(path, { cache: 'no-store' });
    if (!response.ok) return null;
    return await response.json();
  } catch (error) {
    return null;
  }
}

function setField(name, value) {
  const node = document.querySelector(`[data-field="${name}"]`);
  if (node) node.textContent = value ?? 'n/a';
}

function fmt(value) {
  if (value === null || value === undefined || Number.isNaN(value)) return 'n/a';
  if (typeof value === 'number') return value.toFixed(2);
  return String(value);
}

async function init() {
  const summary = await loadJSON('./results/latest/summary.json');
  const retrieval = await loadJSON('./results/latest/retrieval_model_benchmark.json')
    || await loadJSON('./results/latest/retrieval_model.json');
  const ssot = await loadJSON('./results/latest/ssot_smoke.json')
    || await loadJSON('./results/latest/ssot_falsification.json');
  const paper = await loadJSON('./results/latest/paper_scenario_suite.json')
    || await loadJSON('./results/paper_scenario_suite.json');

  const conclusion = summary?.conclusion;
  const modelBenefit = summary?.model_benefit;
  const benefit = summary?.benefit;
  const falsePositive = summary?.false_positive;

  setField('conclusion', conclusion?.headline || 'Nog geen analyse geladen');
  setField('baseline', fmt(modelBenefit?.baseline_mean_gap_coverage));
  setField('with_ssl', fmt(modelBenefit?.ssl_mean_gap_coverage));
  setField('delta', fmt(modelBenefit?.coverage_delta));

  const systemOk = Boolean(summary?.gap && falsePositive?.passed !== false);
  setField('system', systemOk ? 'OK' : '?');
  setField('safety', falsePositive?.promoted_false_positive_rate === 0 ? 'OK' : fmt(falsePositive?.promoted_false_positive_rate));
  setField('paper', fmt(paper?.summary?.coverage_delta ?? benefit?.coverage_delta));

  const table = document.getElementById('backend-table');
  if (!table) return;

  if (retrieval?.backends?.length) {
    table.innerHTML = '';
    for (const backend of retrieval.backends) {
      const row = `<tr>
        <td>${backend.name ?? 'n/a'}</td>
        <td>${backend.vector ?? 'n/a'}</td>
        <td>${backend.ssot ?? 'n/a'}</td>
        <td>${fmt(backend.hit_at_k)}</td>
        <td>${fmt(backend.avg_rank)}</td>
        <td>${fmt(backend.retrieval_coverage)}</td>
        <td>${fmt(backend.delta)}</td>
      </tr>`;
      table.insertAdjacentHTML('beforeend', row);
    }
  } else {
    table.innerHTML = `<tr>
      <td>Core SSL</td>
      <td>n/a</td>
      <td>${ssot?.summary?.passed ? 'OK' : 'n/a'}</td>
      <td>n/a</td>
      <td>n/a</td>
      <td>${fmt(modelBenefit?.ssl_mean_gap_coverage)}</td>
      <td>${fmt(modelBenefit?.coverage_delta)}</td>
    </tr>`;
  }
}

init();
