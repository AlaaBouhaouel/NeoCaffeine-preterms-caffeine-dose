/* Purpose: Dashboard flow wiring without polling, adapted for v3 layout. */

(function () {
  const root = document.getElementById('dashboard-canvas')
  if (!root) {
    return
  }

  const runId = root.dataset.runId

  const phaseTop = document.getElementById('top-phase-badge')
  const phaseSide = document.getElementById('side-phase-badge')
  const simTimeText = document.getElementById('sim-time-text')
  const hourIndexText = document.getElementById('hour-index-text')
  const dayIndexText = document.getElementById('day-index-text')
  const versionText = document.getElementById('state-version-text')
  const convergenceStatusText = document.getElementById('convergence-status-text')

  const runIdShort = document.getElementById('run-id-short')
  const flagsCount = document.getElementById('flags-count')
  const flagsInfo = document.getElementById('flags-info')

  const patientSex = document.getElementById('patient-sex')
  const patientGaWeeksDays = document.getElementById('patient-ga-weeks-days')
  const patientBw = document.getElementById('patient-bw')
  const patientCurrentWeight = document.getElementById('patient-current-weight')
  const patientPnaDisplay = document.getElementById('patient-pna-display')
  const patientPmaDisplay = document.getElementById('patient-pma-display')

  const doseLogCount = document.getElementById('dose-log-count')
  const bloodLogCount = document.getElementById('blood-log-count')
  const contextLogCount = document.getElementById('context-log-count')

  const nCardPanel = document.getElementById('n-card-panel')
  const nInfo = document.getElementById('n-info')
  const nStatusText = document.getElementById('n-status-text')
  const nextDayText = document.getElementById('next-day-text')
  const nDayEndedText = document.getElementById('n-day-ended-text')
  const HOURS_PER_DAY = 24
  const nTimeRemainingText = document.getElementById('n-time-remaining-text')
  const prefillNText = document.getElementById('prefill-n-text')
  const observedNInput = document.getElementById('observed-n-input')
  const submitNButton = document.getElementById('submit-n-button')

  const nError = document.getElementById('n-error')
  const doseError = document.getElementById('dose-error')
  const contextError = document.getElementById('context-error')
  const monitoringError = document.getElementById('monitoring-error')
  const bloodError = document.getElementById('blood-error')

  const contextFeedback = document.getElementById('context-feedback')
  const monitoringFeedback = document.getElementById('monitoring-feedback')

  const playPauseButton = document.getElementById('play-pause-button')
  const speedSelect = document.getElementById('speed-select')
  const nModeSelect = document.getElementById('n-mode-select')
  const showTrueToggle = document.getElementById('show-true-toggle')

  const doseAmountInput = document.getElementById('dose-amount')
  const DOSE_ROUTE = 'iv'
  const DOSE_FORM = 'citrate'

  const fio2Slider = document.getElementById('context-fio2-slider')
  const fio2PercentInput = document.getElementById('context-fio2-percent')
  const supportSelect = document.getElementById('context-support')
  const monitoringValueInput = document.getElementById('monitoring-value')

  const bloodConcentrationInput = document.getElementById('blood-concentration')

  const concEstLatest = document.getElementById('conc-est-latest')

  const thetaTableBody = document.getElementById('theta-table-body')
  const lastDayN = document.getElementById('last-day-n')
  const lossLatest = document.getElementById('loss-latest')
  const newtonIter = document.getElementById('newton-iter')
  const gradNorm = document.getElementById('grad-norm')

  const targetConc = document.getElementById('target-conc')
  const suggestedDose = document.getElementById('suggested-dose')
  const safetyShare = document.getElementById('safety-share')
  const confidenceGate = document.getElementById('confidence-gate')

  let advanceInFlight = false
  let nSubmitInFlight = false
  let hasPlayed = false
  let isHydrating = false
  let wasAwaiting = false
  let contextApplyTimer = null
  let feedbackClearTimer = null

  const errorTimers = new Map()

  function formatNumber(value, decimals) {
    if (value === null || value === undefined) {
      return '-'
    }
    const numberValue = Number(value)
    if (Number.isNaN(numberValue)) {
      return '-'
    }
    return numberValue.toFixed(decimals)
  }

  function formatSignificant(value, sig) {
    if (value === null || value === undefined) {
      return '-'
    }
    const numberValue = Number(value)
    if (Number.isNaN(numberValue)) {
      return '-'
    }
    return numberValue.toPrecision(sig)
  }

  function shortRunId(fullRunId) {
    if (!fullRunId || fullRunId.length < 13) {
      return fullRunId
    }
    return `${fullRunId.slice(0, 8)}…${fullRunId.slice(-4)}`
  }

  function displayPhaseForUi(serverPhase) {
    if (serverPhase === 'awaiting_n' || serverPhase === 'converged') {
      return serverPhase
    }
    if (window.simulatorClockController.isRunning()) {
      return 'playing'
    }
    return hasPlayed ? 'paused' : 'ready'
  }

  function setPhaseBadge(node, phase) {
    node.textContent = phase
    node.className = `phase-chip phase-${phase}`
  }

  function setClockVisualState(running) {
    playPauseButton.textContent = running ? 'Pause' : 'Play'
  }

  function formatPna(hours) {
    if (hours < 48) {
      return `${formatNumber(hours, 2)} h`
    }
    const wholeHours = Math.floor(hours)
    const days = Math.floor(wholeHours / 24)
    const remHours = wholeHours % 24
    return `${days}d + ${remHours}h`
  }

  function formatWeeksDays(totalDays) {
    const wholeDays = Math.floor(totalDays)
    const weeks = Math.floor(wholeDays / 7)
    const days = wholeDays % 7
    return `${weeks}w + ${days}d`
  }

  function latest(array, key) {
    if (!Array.isArray(array) || array.length === 0) {
      return null
    }
    return array[array.length - 1][key]
  }

  function formatForm(value) {
    if (value === 'citrate') return 'citrate'
    if (value === 'base') return 'base'
    return value
  }

  function clearError(node) {
    if (!node) {
      return
    }
    node.textContent = ''
    const existing = errorTimers.get(node)
    if (existing) {
      window.clearTimeout(existing)
      errorTimers.delete(node)
    }
  }

  function showTimedError(node, message) {
    if (!node) {
      return
    }
    node.textContent = message
    const existing = errorTimers.get(node)
    if (existing) {
      window.clearTimeout(existing)
    }
    const timer = window.setTimeout(() => {
      node.textContent = ''
      errorTimers.delete(node)
    }, 4500)
    errorTimers.set(node, timer)
  }

  function clearFeedbackSoon() {
    if (feedbackClearTimer !== null) {
      window.clearTimeout(feedbackClearTimer)
    }
    feedbackClearTimer = window.setTimeout(() => {
      contextFeedback.textContent = ''
      monitoringFeedback.textContent = ''
      feedbackClearTimer = null
    }, 2800)
  }

  function plainErrorMessage(response, fallback) {
    const code = response?.error?.code
    if (code === 'invalid_json') return 'Could not read request data.'
    if (code === 'invalid_request') return 'Request data is invalid.'
    if (code === 'missing_field') return 'Please fill in all required fields.'
    if (code === 'invalid_type') return 'Please enter values in the correct format.'
    if (code === 'invalid_enum') return 'Please choose one of the allowed options.'
    if (code === 'out_of_definition') return 'Value is outside the allowed definition.'
    if (code === 'stale_state_version') return 'State changed. Please retry.'
    if (code === 'phase_awaiting_n_requires_submission') return 'Submit N before advancing time.'
    if (code === 'phase_not_awaiting_n') return 'N can be submitted only when waiting for N.'
    if (code === 'day_index_mismatch') return 'The submitted day does not match the pending day.'
    if (code === 'phase_awaiting_n_locked') return 'Interventions are locked while awaiting N.'
    if (code === 'run_converged_locked') return 'Run is converged and controls are locked.'
    if (code === 'run_not_found') return 'This run no longer exists.'
    return fallback || 'Action failed. Please try again.'
  }

  function showRunMissingState() {
    return
  }

  function handleApiError(response, errorNode, fallbackMessage) {
    if (response.ok) {
      return false
    }
    if (response?.error?.code === 'run_not_found') {
      return true
    }
    showTimedError(errorNode, plainErrorMessage(response, fallbackMessage))
    return true
  }

  function setSegmentValue(hiddenInput, value) {
    hiddenInput.value = value
    const control = hiddenInput.closest('.segment-control')
    if (!control) {
      return
    }
    const buttons = control.querySelectorAll('.segment-option')
    buttons.forEach((button) => {
      button.classList.toggle('active', button.dataset.value === value)
    })
  }

  function initializeSegmentControls() {
    const controls = document.querySelectorAll('.segment-control')
    controls.forEach((control) => {
      const targetId = control.dataset.target
      const hiddenInput = document.getElementById(targetId)
      if (!hiddenInput) {
        return
      }
      control.querySelectorAll('.segment-option').forEach((button) => {
        button.addEventListener('click', async () => {
          setSegmentValue(hiddenInput, button.dataset.value)
          if (targetId === 'monitoring-value' && !isHydrating) {
            await submitMonitoringChange()
          }
        })
      })
    })
  }

  function updateNCardState(state) {
    const simDayIndex = Number(state.time.sim_day_index)
    const dayProgress = Number(state.time.day_progress_01)
    const awaitingDay = state.n_gate.awaiting_n_for_day_index
    const prefill = state.n_gate.n_prefill_value
    const awaiting = state.meta.phase === 'awaiting_n'

    const pendingDay = awaiting ? awaitingDay : simDayIndex
    const hoursRemaining = awaiting ? 0 : Math.max(0, HOURS_PER_DAY * (1 - dayProgress))

    nextDayText.value = String(pendingDay)
    nDayEndedText.value = awaitingDay === null ? '-' : String(awaitingDay)
    nTimeRemainingText.value = formatNumber(hoursRemaining, 1)
    prefillNText.value = prefill === null ? '-' : String(prefill)

    observedNInput.disabled = !awaiting || nSubmitInFlight
    submitNButton.disabled = !awaiting || nSubmitInFlight
    nCardPanel.classList.toggle('n-awaiting-active', awaiting)

    if (nSubmitInFlight) {
      nStatusText.textContent = 'updating...'
    } else if (awaiting) {
      nStatusText.textContent = `day ${awaitingDay}`
    } else {
      nStatusText.textContent = `day ${pendingDay} N in ${formatNumber(hoursRemaining, 1)}h`
    }

    nInfo.setAttribute('data-tooltip', awaiting
      ? `Observed event count for day ${awaitingDay} (24 h).`
      : `N is the event count of one 24 h day, submitted at each day boundary. Next submission is for day ${pendingDay}.`)

    if (awaiting) {
      observedNInput.value = prefill ?? ''
      if (!wasAwaiting) {
        observedNInput.focus()
      }
    }
    wasAwaiting = awaiting
  }

  function renderThetaTable(thetaRows) {
    const showTrue = window.simulatorStateStore.showTrueValues
    const rowsHtml = thetaRows.map((row) => {
      const transformed = `transformed=${formatSignificant(row.transformed_estimate, 4)}, sd=${formatSignificant(row.transformed_sd, 4)}`
      const estimate = `<span class="estimate-value">${formatSignificant(row.natural_estimate, 3)}</span> <span class="unit-blue">${row.natural_unit}</span>`
      const interval = `[${formatSignificant(row.natural_interval_90.lo, 3)}, ${formatSignificant(row.natural_interval_90.hi, 3)}]`
      const sparklineText = row.sparkline_transformed.slice(-8).map((entry) => formatSignificant(entry.v, 3)).join(' · ')
      const trueText = showTrue ? `${formatSignificant(row.true_natural, 3)}` : 'hidden'
      return `<tr>
        <td title="${transformed}">${row.label}</td>
        <td>${estimate}</td>
        <td>${interval}</td>
        <td class="sparkline-cell">${sparklineText || '-'}</td>
        <td>${trueText}</td>
      </tr>`
    }).join('')
    thetaTableBody.innerHTML = rowsHtml
  }

  function renderState(envelope) {
    window.simulatorStateStore.setEnvelope(envelope)
    const state = envelope.state

    const uiPhase = displayPhaseForUi(state.meta.phase)
    setPhaseBadge(phaseTop, uiPhase)
    setPhaseBadge(phaseSide, uiPhase)
    simTimeText.textContent = formatNumber(state.time.sim_time_hours, 3)
    hourIndexText.textContent = String(state.time.sim_hour_index)
    dayIndexText.textContent = String(state.time.sim_day_index)
    versionText.textContent = String(envelope.state_version)
    convergenceStatusText.textContent = state.convergence.is_converged ? 'converged' : 'running'

    runIdShort.textContent = shortRunId(envelope.run_id)
    runIdShort.title = envelope.run_id

    patientSex.textContent = state.patient.covariates.sex
    const gaDays = Number(state.patient.covariates.gestational_age_days)
    patientGaWeeksDays.textContent = `${Math.floor(gaDays / 7)}w + ${gaDays % 7}d`
    patientBw.textContent = String(state.patient.covariates.birth_weight_g)
    patientCurrentWeight.textContent = String(state.patient.current_weight_g ?? latest(state.patient.weight_log, 'weight_g') ?? '-')
    patientPnaDisplay.textContent = formatPna(Number(state.patient.postnatal_age_hours))
    patientPmaDisplay.textContent = formatWeeksDays(Number(state.patient.postmenstrual_age_days))

    const flags = state.patient.flags || []
    flagsCount.textContent = String(flags.length)
    flagsInfo.setAttribute('data-tooltip', flags.length === 0 ? 'No flags' : flags.join(', '))

    doseLogCount.textContent = String(state.patient_file_panel.dose_log.length)
    bloodLogCount.textContent = String(state.patient_file_panel.blood_levels.length)
    contextLogCount.textContent = String(state.patient_file_panel.context_log.length)

    isHydrating = true
    fio2Slider.value = String(Math.round(Number(state.context.fiO2_fraction) * 100))
    fio2PercentInput.value = fio2Slider.value
    supportSelect.value = state.context.breathing_support
    setSegmentValue(monitoringValueInput, state.context.monitoring_on ? 'true' : 'false')
    isHydrating = false

    updateNCardState(state)

    concEstLatest.textContent = formatNumber(latest(state.pharmacology_panel.concentration_est_mg_per_l, 'v'), 3)
    window.simulatorCharts.update(envelope)
    window.simulatorConvergence3d.update(state)

    renderThetaTable(state.estimator_panel.theta)

    lastDayN.textContent = `${formatNumber(state.estimator_panel.last_day.predicted_n, 2)} / ${state.estimator_panel.last_day.observed_n ?? '-'}`
    lossLatest.textContent = formatNumber(latest(state.estimator_panel.diagnostics.loss_negative_log_likelihood, 'value'), 4)
    newtonIter.textContent = String(state.estimator_panel.diagnostics.newton_iterations_last_update)
    gradNorm.textContent = formatNumber(state.estimator_panel.diagnostics.gradient_norm_last_update, 4)

    const decision = state.decision_panel
    targetConc.textContent = formatNumber(decision.target_concentration_mg_per_l, 3)
    suggestedDose.textContent = `${formatNumber(decision.suggested_dose.amount, 1)} mg/kg ${formatForm(decision.suggested_dose.form)}`
    safetyShare.textContent = formatNumber(decision.safety_share_vs_limit, 4)
    confidenceGate.textContent = decision.confidence_gate.open ? `open (${decision.confidence_gate.reason})` : `closed (${decision.confidence_gate.reason})`

    if (state.meta.phase === 'converged') {
      window.simulatorClockController.stop()
      setClockVisualState(false)
    }
  }

  async function refreshInitialState() {
    const response = await window.simulatorApiClient.getState(runId)
    if (handleApiError(response, nError, 'Could not load run state.')) {
      return
    }
    renderState(response)
  }

  async function submitObservedN() {
    const envelope = window.simulatorStateStore.stateEnvelope
    if (!envelope) {
      return
    }
    const state = envelope.state
    const dayIndex = state.n_gate.awaiting_n_for_day_index
    if (dayIndex === null) {
      return
    }

    nSubmitInFlight = true
    updateNCardState(state)

    const observedN = Number(observedNInput.value)
    const response = await window.simulatorApiClient.submitN(runId, dayIndex, envelope.state_version, observedN)
    nSubmitInFlight = false
    if (handleApiError(response, nError, 'Could not submit N.')) {
      updateNCardState(state)
      return
    }
    clearError(nError)
    renderState(response)
    if (response.state.meta.phase === 'playing' && !window.simulatorClockController.isRunning()) {
      hasPlayed = true
      window.simulatorClockController.start(clockTick)
      setClockVisualState(true)
    }
  }

  async function clockTick(deltaSimHours) {
    if (advanceInFlight) {
      return
    }
    const envelope = window.simulatorStateStore.stateEnvelope
    if (!envelope) {
      return
    }
    if (envelope.state.meta.phase !== 'playing') {
      window.simulatorClockController.stop()
      setClockVisualState(false)
      return
    }

    advanceInFlight = true
    const response = await window.simulatorApiClient.advance(runId, envelope.state_version, deltaSimHours)
    advanceInFlight = false

    if (handleApiError(response, nError, 'Could not advance simulation.')) {
      window.simulatorClockController.stop()
      setClockVisualState(false)
      return
    }

    clearError(nError)
    renderState(response)
    if (response.state.meta.phase === 'awaiting_n') {
      window.simulatorClockController.stop()
      setClockVisualState(false)
      if (window.simulatorStateStore.nMode === 'auto') {
        await submitObservedN()

      }
    }
  }

  async function submitContextChange() {
    if (isHydrating) {
      return
    }
    const envelope = window.simulatorStateStore.stateEnvelope
    if (!envelope) {
      return
    }
    const payload = {
      state_version: envelope.state_version,
      fiO2_fraction: Number(fio2PercentInput.value) / 100,
      breathing_support: supportSelect.value,
    }
    const response = await window.simulatorApiClient.setContext(runId, payload)
    if (handleApiError(response, contextError, 'Could not apply care settings.')) {
      return
    }
    clearError(contextError)
    contextFeedback.textContent = `Applied at ${formatNumber(response.state.time.sim_time_hours, 1)} h`
    clearFeedbackSoon()
    renderState(response)
  }

  async function submitMonitoringChange() {
    if (isHydrating) {
      return
    }
    const envelope = window.simulatorStateStore.stateEnvelope
    if (!envelope) {
      return
    }
    const payload = {
      state_version: envelope.state_version,
      monitoring_on: monitoringValueInput.value === 'true',
    }
    const response = await window.simulatorApiClient.setMonitoring(runId, payload)
    if (handleApiError(response, monitoringError, 'Could not apply monitoring setting.')) {
      return
    }
    clearError(monitoringError)
    monitoringFeedback.textContent = `Applied at ${formatNumber(response.state.time.sim_time_hours, 1)} h`
    clearFeedbackSoon()
    renderState(response)
  }

  function queueContextApply() {
    if (contextApplyTimer !== null) {
      window.clearTimeout(contextApplyTimer)
    }
    contextApplyTimer = window.setTimeout(async () => {
      contextApplyTimer = null
      await submitContextChange()
    }, 180)
  }

  playPauseButton.addEventListener('click', () => {
    if (window.simulatorClockController.isRunning()) {
      window.simulatorClockController.stop()
      setClockVisualState(false)
      if (window.simulatorStateStore.stateEnvelope) {
        renderState(window.simulatorStateStore.stateEnvelope)
      }
      return
    }
    hasPlayed = true
    window.simulatorClockController.start(clockTick)
    setClockVisualState(true)
    if (window.simulatorStateStore.stateEnvelope) {
      renderState(window.simulatorStateStore.stateEnvelope)
    }
  })

  speedSelect.addEventListener('change', () => {
    window.simulatorClockController.setSpeed(Number(speedSelect.value))
  })

  nModeSelect.addEventListener('change', () => {
    window.simulatorStateStore.nMode = nModeSelect.value
  })

  showTrueToggle.addEventListener('change', () => {
    window.simulatorStateStore.showTrueValues = showTrueToggle.checked
    if (window.simulatorStateStore.stateEnvelope) {
      renderState(window.simulatorStateStore.stateEnvelope)
    }
  })

  submitNButton.addEventListener('click', async () => {
    await submitObservedN()
  })

  observedNInput.addEventListener('keydown', async (event) => {
    if (event.key === 'Enter') {
      event.preventDefault()
      await submitObservedN()
    }
  })

  document.getElementById('dose-form').addEventListener('submit', async (event) => {
    event.preventDefault()
    const envelope = window.simulatorStateStore.stateEnvelope
    if (!envelope) {
      return
    }
    const payload = {
      state_version: envelope.state_version,
      amount: Number(doseAmountInput.value),
      amount_unit: 'mg_per_kg',
      route: DOSE_ROUTE,
      form: DOSE_FORM,
      source: 'manual',
    }
    const response = await window.simulatorApiClient.giveDose(runId, payload)
    if (handleApiError(response, doseError, 'Could not apply dose.')) {
      return
    }
    clearError(doseError)
    renderState(response)
  })

  fio2Slider.addEventListener('input', () => {
    fio2PercentInput.value = fio2Slider.value
  })
  fio2Slider.addEventListener('change', () => {
    queueContextApply()
  })

  fio2PercentInput.addEventListener('change', () => {
    const next = Math.min(100, Math.max(21, Number(fio2PercentInput.value) || 21))
    fio2PercentInput.value = String(next)
    fio2Slider.value = String(next)
    queueContextApply()
  })

  supportSelect.addEventListener('change', () => {
    queueContextApply()
  })

  document.getElementById('blood-form').addEventListener('submit', async (event) => {
    event.preventDefault()
    const envelope = window.simulatorStateStore.stateEnvelope
    if (!envelope) {
      return
    }
    const concentration = Number(bloodConcentrationInput.value)
    const payload = {
      state_version: envelope.state_version,
      below_detection_limit: false,
      detection_limit_mg_per_l: 0,
      concentration_mg_per_l: concentration,
    }
    const response = await window.simulatorApiClient.addBloodLevel(runId, payload)
    if (handleApiError(response, bloodError, 'Could not add blood level.')) {
      return
    }
    clearError(bloodError)
    renderState(response)
  })

  initializeSegmentControls()

  window.simulatorClockController.setSpeed(Number(speedSelect.value))
  window.simulatorStateStore.nMode = nModeSelect.value
  const sidebarToggle = document.getElementById('sidebar-toggle')
  const mainGrid = document.getElementById('dashboard-main-grid')
  sidebarToggle?.addEventListener('click', () => {
    const open = mainGrid.classList.toggle('sidebar-open')
    sidebarToggle.setAttribute('aria-expanded', open ? 'true' : 'false')
  })

  setClockVisualState(false)
  refreshInitialState()
})()










