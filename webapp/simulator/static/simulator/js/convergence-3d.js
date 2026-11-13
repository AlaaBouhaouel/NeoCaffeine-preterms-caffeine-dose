/* Purpose: 3D convergence view with plotly (proposal 06): the day-by-day path of the two parameters chosen in the X and Y dropdowns (natural scale), Z = number of daily updates; the true point is shown only when "True values" is ticked. */

window.simulatorConvergence3d = (function () {
  const host = document.getElementById('convergence-plot-host')
  const xSelect = document.getElementById('conv-x-param')
  const ySelect = document.getElementById('conv-y-param')
  const resetButton = document.getElementById('conv-reset')
  if (!host || !window.Plotly || !xSelect || !ySelect) {
    return { update() {} }
  }

  const DEFAULT_CAMERA = { eye: { x: 1.6, y: 1.6, z: 0.9 } }
  let state = null
  let camera = DEFAULT_CAMERA
  let plotted = false

  function token(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
  }

  function rowFor(key) {
    return state.estimator_panel.theta.find((row) => row.key.toLowerCase() === key.toLowerCase())
  }

  function axisTitle(row) {
    return `${row.label.replace(/^(log|logit) /, '')} (${row.natural_unit})`
  }

  function axis(title) {
    return {
      title: { text: title, font: { size: 10, color: token('--color-text-muted') } },
      color: token('--color-text-faint'),
      gridcolor: token('--color-border'),
      zerolinecolor: token('--color-border'),
      backgroundcolor: token('--color-inset'),
      showbackground: true,
      tickfont: { size: 9 },
    }
  }

  function render() {
    if (!state) return
    const xRow = rowFor(xSelect.value)
    const yRow = rowFor(ySelect.value)
    const path = state.estimator_panel.trajectory || []
    if (!xRow || !yRow || path.length === 0) return

    const xs = path.map((point) => point.natural[xRow.key])
    const ys = path.map((point) => point.natural[yRow.key])
    const zs = path.map((point) => point.step)
    const amber = token('--color-amber')
    const traces = [
      {
        type: 'scatter3d', mode: 'lines+markers', name: 'estimate',
        x: xs, y: ys, z: zs,
        line: { color: amber, width: 4 },
        marker: { size: 3, color: amber },
        hovertemplate: 'day %{z}<br>x %{x:.4g}<br>y %{y:.4g}<extra></extra>',
      },
      {
        type: 'scatter3d', mode: 'markers', name: 'current',
        x: [xs[xs.length - 1]], y: [ys[ys.length - 1]], z: [zs[zs.length - 1]],
        marker: { size: 7, color: amber, line: { color: token('--color-text-strong'), width: 1 } },
        hoverinfo: 'skip',
      },
    ]
    if (window.simulatorStateStore.showTrueValues) {
      const lastStep = Math.max(1, zs[zs.length - 1])
      traces.push({
        type: 'scatter3d', mode: 'lines', name: 'true',
        x: [xRow.true_natural, xRow.true_natural], y: [yRow.true_natural, yRow.true_natural], z: [0, lastStep],
        line: { color: token('--color-positive'), width: 3, dash: 'dash' },
        hovertemplate: 'true<extra></extra>',
      })
    }
    const layout = {
      margin: { l: 0, r: 0, t: 0, b: 0 },
      paper_bgcolor: 'rgba(0,0,0,0)',
      showlegend: false,
      font: { family: 'IBM Plex Mono, monospace', color: token('--color-text') },
      scene: {
        xaxis: axis(axisTitle(xRow)),
        yaxis: axis(axisTitle(yRow)),
        zaxis: axis('day'),
        camera,
      },
    }
    const firstPlot = !plotted
    if (firstPlot) {
      host.textContent = ''
      plotted = true
    }
    window.Plotly.react(host, traces, layout, { displayModeBar: false, responsive: true })
    if (firstPlot) {
      host.on('plotly_relayout', rememberCamera)
    }
  }

  function rememberCamera(event) {
    if (event && event['scene.camera']) {
      camera = event['scene.camera']
    }
  }

  function update(nextState) {
    state = nextState
    render()
  }

  xSelect.addEventListener('change', render)
  ySelect.addEventListener('change', render)
  resetButton?.addEventListener('click', () => {
    camera = DEFAULT_CAMERA
    render()
  })
  window.addEventListener('neocaffeine:themechange', render)
  new ResizeObserver(() => {
    if (plotted) window.Plotly.Plots.resize(host)
  }).observe(host)

  return { update }
})()
