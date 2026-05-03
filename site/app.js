async function loadJSON(path){try{const r=await fetch(path);return await r.json()}catch(e){return null}}

async function init(){
  const system=await loadJSON('./results/latest/summary.json');
  const retrieval=await loadJSON('./results/latest/retrieval_model.json');
  const safety=await loadJSON('./results/latest/ssot_falsification.json');
  const paper=await loadJSON('./results/paper_scenario_suite.json');

  document.querySelector('[data-field="system"]').textContent=system?.summary?.passed?'OK':'?';
  document.querySelector('[data-field="model"]').textContent=retrieval?.summary?.ssl_mean_gap_coverage?.toFixed(2)||'?';
  document.querySelector('[data-field="safety"]').textContent=safety?.summary?.passed?'OK':'?';
  document.querySelector('[data-field="paper"]').textContent=paper?.summary?.coverage_delta?.toFixed(2)||'?';

  const table=document.getElementById('backend-table');
  if(retrieval?.backends){
    table.innerHTML='';
    for(const b of retrieval.backends){
      const row=`<tr>
        <td>${b.name}</td>
        <td>${b.vector}</td>
        <td>${b.ssot}</td>
        <td>${b.hit_at_k}</td>
        <td>${b.avg_rank}</td>
        <td>${b.retrieval_coverage}</td>
        <td>${b.delta}</td>
      </tr>`;
      table.insertAdjacentHTML('beforeend',row);
    }
  }
}

init();