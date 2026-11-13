/* Purpose: Dashboard graphs with uPlot (proposal 06): heart rate, SpO2 and respiration trends from the browser vitals generator over the last 6 simulated hours, and the caffeine concentration curve from the server state. Animated at about 10 frames per second, independent of server calls. */

window.simulatorCharts = (function () {
  const VITALS_WINDOW_HOURS = 6
  const FRAME_INTERVAL_MS = 100
  const HOURS_PER_DAY = 24

  const hosts = {
    heartRate: document.getElementById('trace-heart-rate'),
    spo2: document.getElementById('trace-spo2'),
    respiration: document.getElementById('trace-resp'),
    caffeine: document.getElementById('trace-caffeine'),
  }
  const tiles = {
    heartRate: document.getElementById('tile-heart-rate'),
    spo2: document.getElementById('tile-spo2-value'),
    respiration: document.getElementById('tile-resp-value'),
  }
  if (!window.uPlot || Object.values(hosts).some((host) => !host)) {
    return { update() {} }
  }

  let plots = {}
  let envelope = null
  let receivedAt = 0
  let lastFrame = 0

  function token(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
  }

  function size(host) {
    return { width: Math.max(80, host.clientWidth), height: Math.max(50, host.clientHeight) }
  }

  function axes() {
    const stroke = token('--color-text-faint')
    const grid = { stroke: token('--color-grid-line'), width: 1 }
    return [
      { stroke, grid, ticks: { show: false }, size: 22, values: (u, values) => values.map((v) => `${Math.round(v)}h`) },
      { stroke, grid, ticks: { show: false }, size: 34 },
    ]
  }

  function vitalPlot(host, color, range) {
    return new window.uPlot({
      ...size(host),
      legend: { show: false },
      cursor: { show: false },
      scales: { x: { time: false }, y: { range } },
      axes: axes(),
      series: [{}, { stroke: color, width: 1.4, spanGaps: false, points: { show: false } }],
    }, [[0], [null]], host)
  }

  function caffeinePlot(host) {
    const amber = token('--color-amber')
    const faint = token('--color-text-faint')
    const truth = token('--color-text-strong')
    return new window.uPlot({
      ...size(host),
      legend: { show: false },
      cursor: { show: false },
      scales: { x: { time: false }, y: { range: (u, min, max) => [0, Math.max(20, Math.ceil((max || 0) * 1.15))] } },
      axes: axes(),
      series: [
        {},
        { label: 'estimate', stroke: amber, width: 1.6, points: { show: false } },
        { label: 'band low', stroke: faint, width: 1, dash: [4, 4], points: { show: false } },
        { label: 'band high', stroke: faint, width: 1, dash: [4, 4], points: { show: false } },
        { label: 'true', stroke: truth, width: 1, dash: [2, 3], points: { show: false } },
        { label: 'doses', stroke: amber, width: 0, paths: () => null, points: { show: true, size: 7, fill: amber, stroke: amber } },
      ],
    }, [[0], [null], [null], [null], [null], [null]], host)
  }

  function build() {
    Object.values(plots).forEach((plot) => plot.destroy())
    Object.values(hosts).forEach((host) => { host.innerHTML = '' })
    plots = {
      heartRate: vitalPlot(hosts.heartRate, token('--color-trace-heart-rate'), [80, 190]),
      spo2: vitalPlot(hosts.spo2, token('--color-trace-spo2'), [75, 100]),
      respiration: vitalPlot(hosts.respiration, token('--color-trace-respiration'), [0, 70]),
      caffeine: caffeinePlot(hosts.caffeine),
    }
    if (envelope) {
      drawCaffeine()
    }
  }

  function displayTime() {
    const state = envelope.state
    const serverTime = Number(state.time.sim_time_hours)
    const clock = window.simulatorClockController
    if (!clock || !clock.isRunning() || state.meta.phase !== 'playing') {
      return serverTime
    }
    const elapsedHours = (performance.now() - receivedAt) / 1000 / clock.speedSecondsPerHour
    const nextDayBoundary = (Math.floor(serverTime / HOURS_PER_DAY) + 1) * HOURS_PER_DAY
    return Math.min(serverTime + elapsedHours, nextDayBoundary)
  }

  function lastValue(values) {
    for (let index = values.length - 1; index >= 0; index -= 1) {
      if (values[index] !== null) return values[index]
    }
    return null
  }

  function setTile(node, value) {
    if (node) node.textContent = value === null ? '-' : value.toFixed(1)
  }

  function drawVitals() {
    const state = envelope.state
    const end = displayTime()
    const context = {
      monitoringOn: Boolean(state.context.monitoring_on),
      fio2: Number(state.context.fiO2_fraction),
      apneaRatePerHour: Number(state.monitor_panel.demo_apnea_rate_per_hour ?? 0),
      concentration: Number(state.monitor_panel.demo_true_concentration_mg_per_l ?? 0),
    }
    const data = window.simulatorVitals.series(Number(state.run.random_seed), end, VITALS_WINDOW_HOURS, context)
    const xRange = { min: Math.max(0, end - VITALS_WINDOW_HOURS), max: Math.max(end, VITALS_WINDOW_HOURS) }
    for (const key of ['heartRate', 'spo2', 'respiration']) {
      plots[key].batch(() => {
        plots[key].setData([data.time, data[key]], false)
        plots[key].setScale('x', xRange)
      })
      setTile(tiles[key], lastValue(data[key]))
    }
  }

  function drawCaffeine() {
    const panel = envelope.state.pharmacology_panel
    const estimate = panel.concentration_est_mg_per_l || []
    const truth = panel.true_concentration_mg_per_l || []
    const band = panel.concentration_band_mg_per_l || []
    const doseTimes = new Set((panel.dose_markers || []).map((marker) => Number(marker.t_sim_hours)))
    const time = estimate.map((point) => Number(point.t_sim_hours))
    const doseValues = estimate.map((point) => (doseTimes.has(Number(point.t_sim_hours)) ? Number(point.v) : null))
    const showTrue = Boolean(window.simulatorStateStore.showTrueValues)
    const plot = plots.caffeine
    plot.batch(() => {
      plot.setData([
        time,
        estimate.map((point) => Number(point.v)),
        band.map((point) => Number(point.lo)),
        band.map((point) => Number(point.hi)),
        truth.map((point) => (showTrue ? Number(point.v) : null)),
        doseValues,
      ], false)
      plot.setScale('x', { min: 0, max: Math.max(HOURS_PER_DAY, time.length ? time[time.length - 1] : 0) })
    })
  }

  function frame(now) {
    if (envelope && now - lastFrame >= FRAME_INTERVAL_MS) {
      lastFrame = now
      drawVitals()
    }
    window.requestAnimationFrame(frame)
  }

  function update(nextEnvelope) {
    envelope = nextEnvelope
    receivedAt = performance.now()
    drawCaffeine()
    drawVitals()
  }

  const resizeObserver = new ResizeObserver(() => {
    for (const [key, plot] of Object.entries(plots)) {
      plot.setSize(size(hosts[key]))
    }
  })
  Object.values(hosts).forEach((host) => resizeObserver.observe(host))
  window.addEventListener('neocaffeine:themechange', build)

  build()
  window.requestAnimationFrame(frame)
  return { update }
})()
