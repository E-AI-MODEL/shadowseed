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

// The A-G evidence table is static in index.html so the dashboard story can
// never silently drift from the wiki. This script only fills the small live
// fixture snapshot (layer B) and the conclusion line from the latest analyzer
// summary.
async function init() {
  const summary = await loadJSON('./results/latest/summary.json');
  if (!summary) return;

  const modelBenefit = summary.model_benefit || summary.benefit || {};
  setField('baseline', fmt(modelBenefit.baseline_mean_gap_coverage));
  setField('with_ssl', fmt(modelBenefit.ssl_mean_gap_coverage));
  setField('delta', fmt(modelBenefit.coverage_delta));

  const conclusion = summary.conclusion;
  if (conclusion?.headline) {
    const backend = conclusion.is_real_model ? 'echt model' : 'fixture-backend';
    setField('conclusion', `${conclusion.headline} (${backend})`);
  }
}

init();
