/* Purpose: Dashboard flow wiring without polling, with compact clinician-action UX. */

(function () {
  const root = document.querySelector('.dashboard-root')
  if (!root) {
    return
  }

  const runId = root.dataset.runId

  const topBar = document.querySelector('.top-bar')
  const mainGrid = document.getElementById('dashboard-main-grid')
  const footerNotice = document.querySelector('.footer-notice')
  const runMissingPanel = document.getElementById('run-missing-panel')
  const runMissingClose = document.getElementById('run-missing-close')

  const phaseTop = document.getElementById('top-phase-badge')
  const phaseSide = document.getElementById('side-phase-badge')
  const simTimeText = document.getElementById('sim-time-text')
  const hourIndexText = document.getElementById('hour-index-text')
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

  const nCard = document.getElementById('n-submission-row')
  const awaitingHourText = document.getElementById('awaiting-hour-text')
  const nHourEndedText = document.getElementById('n-hour-ended-text')
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
  const doseUnitSelect = document.getElementById('dose-unit')
  const doseRouteInput = document.getElementById('dose-route')
  const doseFormInput = document.getElementById('dose-form-select')
  const acceptSuggestedDoseButton = document.getElementById('accept-suggested-dose')

  const fio2Slider = document.getElementById('context-fio2-slider')
  const fio2PercentInput = document.getElementById('context-fio2-percent')
  const supportSelect = document.getElementById('context-support')
  const monitoringValueInput = document.getElementById('monitoring-value')

  const bloodConcentrationInput = document.getElementById('blood-concentration')
  const bloodBelowDlCheckbox = document.getElementById('blood-below-dl')
  const bloodDlInput = document.getElementById('blood-dl')
  const bloodDlRow = document.getElementById('blood-dl-row')

  const tileHr = document.getElementById('tile-heart-rate')
  const tileSpo2 = document.getElementById('tile-spo2-value')
  const tileResp = document.getElementById('tile-resp-value')
  const hrMarkerCount = document.getElementById('hr-marker-count')
  const spo2MarkerCount = document.getElementById('spo2-marker-count')
  const respMarkerCount = document.getElementById('resp-marker-count')

  const concEstLatest = document.getElementById('conc-est-latest')
  const doseMarkerCount = document.getElementById('dose-marker-count')

  const thetaPreview = document.getElementById('theta-preview')
  const lastHourN = document.getElementById('last-hour-n')
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
  const disableRunMissingOverlayForEditing = true
  const suppressRunMissingErrorsForEditing = true

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

  function formatRoute(value) {
    if (value === 'intravenous') return 'IV'
    if (value === 'oral') return 'Oral'
    return value
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
    if (code === 'hour_index_mismatch') return 'The submitted hour does not match the pending hour.'
    if (code === 'phase_awaiting_n_locked') return 'Interventions are locked while awaiting N.'
    if (code === 'run_converged_locked') return 'Run is converged and controls are locked.'
    if (code === 'run_not_found') return 'This run no longer exists.'
    return fallback || 'Action failed. Please try again.'
  }

  function showRunMissingState() {
    window.simulatorClockController.stop()
    setClockVisualState(false)
    runMissingPanel.hidden = false
  }

  function handleApiError(response, errorNode, fallbackMessage) {
    if (response.ok) {
      return false
    }
    if (response?.error?.code === 'run_not_found') {
      if (suppressRunMissingErrorsForEditing) {
        return true
      }
      if (disableRunMissingOverlayForEditing) {
        showTimedError(errorNode, 'This run no longer exists. Start a new run to continue.')
      } else {
        showRunMissingState()
      }
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

  function setBloodFieldsState() {
    const belowDl = bloodBelowDlCheckbox.checked
    bloodConcentrationInput.disabled = belowDl
    bloodConcentrationInput.required = !belowDl
    bloodDlInput.required = belowDl
    bloodDlRow.hidden = !belowDl
  }

  function updateNCardState(state) {
    const simHourIndex = Number(state.time.sim_hour_index)
    const currentProgress = Number(state.time.hour_progress_01)
    const awaitingHour = state.hour_gate.awaiting_n_for_hour_index
    const prefill = state.hour_gate.n_prefill_value
    const awaiting = state.meta.phase === 'awaiting_n'

    if (nSubmitInFlight) {
      nCard.classList.remove('n-state-idle', 'n-state-awaiting')
      nCard.classList.add('n-state-updating')
    } else if (awaiting) {
      nCard.classList.remove('n-state-idle', 'n-state-updating')
      nCard.classList.add('n-state-awaiting')
    } else {
      nCard.classList.remove('n-state-awaiting', 'n-state-updating')
      nCard.classList.add('n-state-idle')
    }

    const nextHour = awaiting ? awaitingHour + 1 : simHourIndex + 1
    const timeRemaining = awaiting ? 0 : Math.max(0, 1 - currentProgress)

    awaitingHourText.textContent = String(nextHour)
    nHourEndedText.textContent = awaitingHour === null ? '-' : String(awaitingHour)
    nTimeRemainingText.textContent = formatNumber(timeRemaining, 2)
    prefillNText.textContent = prefill === null ? '-' : String(prefill)

    observedNInput.disabled = !awaiting || nSubmitInFlight
    submitNButton.disabled = !awaiting || nSubmitInFlight

    if (awaiting) {
      observedNInput.value = prefill ?? ''
      if (!wasAwaiting) {
        observedNInput.focus()
        nCard.classList.remove('pulse')
        void nCard.offsetWidth
        nCard.classList.add('pulse')
      }
    }
    wasAwaiting = awaiting
  }

  function renderState(envelope) {
    window.simulatorStateStore.setEnvelope(envelope)
    const state = envelope.state

    const uiPhase = displayPhaseForUi(state.meta.phase)
    setPhaseBadge(phaseTop, uiPhase)
    setPhaseBadge(phaseSide, uiPhase)
    simTimeText.textContent = formatNumber(state.time.sim_time_hours, 3)
    hourIndexText.textContent = String(state.time.sim_hour_index)
    versionText.textContent = String(envelope.state_version)
    convergenceStatusText.textContent = state.convergence.is_converged ? 'converged' : 'running'

    runIdShort.textContent = shortRunId(envelope.run_id)
    runIdShort.title = envelope.run_id

    patientSex.textContent = state.patient.covariates.sex
    const gaDays = Number(state.patient.covariates.gestational_age_days)
    const gaWeeks = Math.floor(gaDays / 7)
    const gaDaysExtra = gaDays % 7
    patientGaWeeksDays.textContent = `${gaWeeks}w + ${gaDaysExtra}d`
    patientBw.textContent = String(state.patient.covariates.birth_weight_g)
    patientCurrentWeight.textContent = String(latest(state.patient.weight_log, 'weight_g') ?? '-')
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
    setBloodFieldsState()
    isHydrating = false

    updateNCardState(state)

    tileHr.textContent = formatNumber(state.monitor_panel.tiles.heart_rate_bpm, 1)
    tileSpo2.textContent = formatNumber(state.monitor_panel.tiles.spo2_pct, 1)
    tileResp.textContent = formatNumber(state.monitor_panel.tiles.resp_rate_bpm, 1)

    const events = state.monitor_panel.events || []
    hrMarkerCount.textContent = String(events.filter((entry) => entry.type === 'bradycardia').length)
    spo2MarkerCount.textContent = String(events.filter((entry) => entry.type === 'desaturation').length)
    respMarkerCount.textContent = String(events.filter((entry) => entry.type === 'apnea').length)

    concEstLatest.textContent = formatNumber(latest(state.pharmacology_panel.concentration_est_mg_per_l, 'v'), 3)
    doseMarkerCount.textContent = String(state.pharmacology_panel.dose_markers.length)

    const thetaLines = state.estimator_panel.theta.map((row) => {
      const trueNatural = window.simulatorStateStore.showTrueValues ? formatSignificant(row.true_natural, 3) : 'hidden'
      return `${row.label}: nat=${formatSignificant(row.natural_estimate, 3)} ${row.natural_unit}, 90%=[${formatSignificant(row.natural_interval_90.lo, 3)}, ${formatSignificant(row.natural_interval_90.hi, 3)}], tr=${formatSignificant(row.transformed_estimate, 4)}, true=${trueNatural}`
    })
    thetaPreview.textContent = thetaLines.join('\n')

    lastHourN.textContent = `${formatNumber(state.estimator_panel.last_hour.predicted_n, 2)} / ${state.estimator_panel.last_hour.observed_n ?? '-'}`
    lossLatest.textContent = formatNumber(latest(state.estimator_panel.diagnostics.loss_negative_log_likelihood, 'value'), 4)
    newtonIter.textContent = String(state.estimator_panel.diagnostics.newton_iterations_last_update)
    gradNorm.textContent = formatNumber(state.estimator_panel.diagnostics.gradient_norm_last_update, 4)

    const decision = state.decision_panel
    targetConc.textContent = formatNumber(decision.target_concentration_mg_per_l, 3)
    suggestedDose.textContent = `${formatNumber(decision.suggested_dose.amount, 3)} ${decision.suggested_dose.amount_unit}, ${formatRoute(decision.suggested_dose.route)}, ${formatForm(decision.suggested_dose.form)}`
    safetyShare.textContent = formatNumber(decision.safety_share_vs_limit, 4)
    confidenceGate.textContent = decision.confidence_gate.open ? `open (${decision.confidence_gate.reason})` : `closed (${decision.confidence_gate.reason})`
    acceptSuggestedDoseButton.textContent = `Accept: ${formatNumber(decision.suggested_dose.amount, 3)} ${decision.suggested_dose.amount_unit} ${formatRoute(decision.suggested_dose.route)} ${formatForm(decision.suggested_dose.form)}`

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
    const hourIndex = state.hour_gate.awaiting_n_for_hour_index
    if (hourIndex === null) {
      return
    }

    nSubmitInFlight = true
    updateNCardState(state)

    const observedN = Number(observedNInput.value)
    const response = await window.simulatorApiClient.submitN(runId, hourIndex, envelope.state_version, observedN)
    nSubmitInFlight = false
    if (handleApiError(response, nError, 'Could not submit N.')) {
      updateNCardState(state)
      return
    }
    clearError(nError)
    renderState(response)
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
        if (window.simulatorStateStore.stateEnvelope?.state?.meta?.phase === 'playing') {
          playPauseButton.click()
        }
      }
    }
  }

  function currentContextPayload() {
    return {
      fiO2_fraction: Number(fio2PercentInput.value) / 100,
      breathing_support: supportSelect.value,
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
      ...currentContextPayload(),
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
      amount_unit: doseUnitSelect.value,
      route: doseRouteInput.value,
      form: doseFormInput.value,
      source: 'manual',
    }
    const response = await window.simulatorApiClient.giveDose(runId, payload)
    if (handleApiError(response, doseError, 'Could not apply dose.')) {
      return
    }
    clearError(doseError)
    renderState(response)
  })

  acceptSuggestedDoseButton.addEventListener('click', async () => {
    const envelope = window.simulatorStateStore.stateEnvelope
    if (!envelope) {
      return
    }
    const response = await window.simulatorApiClient.acceptSuggestedDose(runId, envelope.state_version)
    if (handleApiError(response, doseError, 'Could not accept suggested dose.')) {
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

  bloodBelowDlCheckbox.addEventListener('change', () => {
    setBloodFieldsState()
  })

  document.getElementById('blood-form').addEventListener('submit', async (event) => {
    event.preventDefault()
    const envelope = window.simulatorStateStore.stateEnvelope
    if (!envelope) {
      return
    }
    const belowDl = bloodBelowDlCheckbox.checked
    const payload = {
      state_version: envelope.state_version,
      below_detection_limit: belowDl,
      detection_limit_mg_per_l: Number(bloodDlInput.value),
      concentration_mg_per_l: belowDl ? null : Number(bloodConcentrationInput.value),
    }
    const response = await window.simulatorApiClient.addBloodLevel(runId, payload)
    if (handleApiError(response, bloodError, 'Could not add blood level.')) {
      return
    }
    clearError(bloodError)
    renderState(response)
  })

  initializeSegmentControls()
  setBloodFieldsState()

  if (runMissingClose) {
    runMissingClose.addEventListener('click', () => {
      window.location.href = '/'
    })
  }

  window.simulatorClockController.setSpeed(Number(speedSelect.value))
  window.simulatorStateStore.nMode = nModeSelect.value
  setClockVisualState(false)
  refreshInitialState()
})()
