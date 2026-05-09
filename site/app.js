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

function metric(summary, group, key, fallback = null) {
  return summary?.[group]?.[key] ?? fallback;
}

async function init() {
  const summary = await loadJSON('./results/latest/summary.json');
  const conclusion = summary?.conclusion;
  const modelBenefit = summary?.model_benefit;
  const benefit = summary?.benefit;
  const falsePositive = summary?.false_positive;
  const adversarial = summary?.adversarial_gate;
  const probe = summary?.probe_utility;

  setField('conclusion', conclusion?.headline || 'Nog geen analyse geladen');
  setField(
    'baseline',
    fmt(metric(modelBenefit, 'summary', 'baseline_mean_gap_coverage', modelBenefit?.baseline_mean_gap_coverage))
  );
  setField(
    'with_ssl',
    fmt(metric(modelBenefit, 'summary', 'ssl_mean_gap_coverage', modelBenefit?.ssl_mean_gap_coverage))
  );
  setField('delta', fmt(metric(modelBenefit, 'summary', 'coverage_delta', modelBenefit?.coverage_delta)));

  const systemOk = Boolean(summary?.gap && falsePositive?.promoted_false_positive_rate === 0);
  setField('system', systemOk ? 'stabiel' : 'controle nodig');

  if (falsePositive?.promoted_false_positive_rate === 0) {
    setField('safety', 'schoon');
  } else {
    setField('safety', `fp ${fmt(falsePositive?.promoted_false_positive_rate)}`);
  }

  if (adversarial && probe) {
    setField('paper', 'adversarial + probe');
  } else if (adversarial) {
    setField('paper', 'adversarial zichtbaar');
  } else if (probe) {
    setField('paper', 'probe zichtbaar');
  } else if (benefit?.coverage_delta !== undefined) {
    setField('paper', `delta ${fmt(benefit.coverage_delta)}`);
  } else {
    setField('paper', 'nog beperkt');
  }
}

init();
