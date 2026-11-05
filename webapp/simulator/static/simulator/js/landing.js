/* Purpose: Landing page behavior: scaling, animation, validation, run creation, and resume. */

(function () {
  const stage = document.getElementById('landing-stage')
  const canvasRoot = document.getElementById('landing-canvas')
  const form = document.getElementById('create-run-form')
  if (!stage || !canvasRoot || !form) {
    return
  }
  const gaWeeks = document.getElementById('ga-weeks')
  const gaDays = document.getElementById('ga-days')
  const birthWeight = document.getElementById('birth-weight')
  const sexHidden = document.getElementById('sex')
  const fio2Slider = document.getElementById('fio2-slider')
  const fio2Percent = document.getElementById('fio2-percent')
  const support = document.getElementById('breathing-support')
  const randomSeed = document.getElementById('random-seed')

  const gaError = document.getElementById('ga-error')
  const birthWeightError = document.getElementById('birth-weight-error')
  const sexError = document.getElementById('sex-error')
  const fio2Error = document.getElementById('fio2-error')
  const supportError = document.getElementById('support-error')
  const seedError = document.getElementById('seed-error')
  const landingError = document.getElementById('landing-error')

  const resumeToggle = document.getElementById('resume-toggle')
  const resumeControls = document.getElementById('resume-controls')
  const resumeInput = document.getElementById('resume-run-input')
  const resumeButton = document.getElementById('resume-run-button')
  const resumeError = document.getElementById('resume-error')

  function fitLandingToViewport () {
    canvasRoot.style.transform = 'none'
  }

  fitLandingToViewport()
  window.addEventListener('resize', fitLandingToViewport)

  function setSegmentControl(controlRoot, hiddenInput) {
    const buttons = controlRoot.querySelectorAll('.segment-option')
    buttons.forEach((button) => {
      button.addEventListener('click', () => {
        hiddenInput.value = button.dataset.value || ''
        buttons.forEach((node) => node.classList.remove('active'))
        button.classList.add('active')
      })
    })
  }

  document.querySelectorAll('.segment-control[data-target="sex"]').forEach((node) => {
    setSegmentControl(node, sexHidden)
  })

  function syncFio2FromSlider() {
    fio2Percent.value = fio2Slider.value
  }

  function syncFio2FromPercent() {
    let value = Number(fio2Percent.value)
    if (!Number.isFinite(value)) {
      return
    }
    value = Math.round(value)
    if (value < 21) value = 21
    if (value > 100) value = 100
    fio2Percent.value = String(value)
    fio2Slider.value = String(value)
  }

  fio2Slider.addEventListener('input', syncFio2FromSlider)
  fio2Percent.addEventListener('input', syncFio2FromPercent)
  fio2Percent.addEventListener('blur', syncFio2FromPercent)

  function clearErrors() {
    ;[gaError, birthWeightError, sexError, fio2Error, supportError, seedError, landingError, resumeError].forEach((node) => {
      if (node) {
        node.textContent = ''
      }
    })
  }

  function isInt(value) {
    return /^-?\d+$/.test(String(value).trim())
  }

  function validateForm() {
    clearErrors()
    let valid = true

    if (!isInt(gaWeeks.value)) {
      gaError.textContent = 'Gestational age weeks must be a whole number.'
      valid = false
    }

    if (!isInt(gaDays.value)) {
      gaError.textContent = 'Gestational age days must be a whole number from 0 to 6.'
      valid = false
    } else {
      const dayValue = Number(gaDays.value)
      if (dayValue < 0 || dayValue > 6) {
        gaError.textContent = 'Gestational age days must be between 0 and 6.'
        valid = false
      }
    }

    if (!isInt(birthWeight.value)) {
      birthWeightError.textContent = 'Birth weight must be a whole number in grams.'
      valid = false
    }

    if (!['male', 'female', 'unknown'].includes(sexHidden.value)) {
      sexError.textContent = 'Select one sex option.'
      valid = false
    }

    if (!isInt(fio2Percent.value)) {
      fio2Error.textContent = 'FiO2 must be a whole percent between 21 and 100.'
      valid = false
    } else {
      const fio2Value = Number(fio2Percent.value)
      if (fio2Value < 21 || fio2Value > 100) {
        fio2Error.textContent = 'FiO2 must stay between 21% and 100%.'
        valid = false
      }
    }

    if (!support.value) {
      supportError.textContent = 'Select a breathing support option.'
      valid = false
    }

    if (randomSeed.value !== '' && !isInt(randomSeed.value)) {
      seedError.textContent = 'Random seed must be a whole number or left empty.'
      valid = false
    }

    return valid
  }

  function mapCreateRunError(response) {
    const code = response?.error?.code
    if (code === 'missing_field') return 'Please complete all required fields before starting.'
    if (code === 'invalid_type') return 'One of the entered values is not in the correct format.'
    if (code === 'invalid_enum') return 'One selected option is not valid. Please reselect it.'
    if (code === 'out_of_definition') return 'One value is outside the allowed definition for this form.'
    if (code === 'invalid_json') return 'The request could not be prepared. Please try again.'
    return 'Could not start the simulation right now. Please try again.'
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault()
    if (!validateForm()) {
      return
    }

    const payload = {
      patient: {
        gestational_age_weeks: Number(gaWeeks.value),
        gestational_age_days_extra: Number(gaDays.value),
        birth_weight_g: Number(birthWeight.value),
        sex: sexHidden.value
      },
      initial_context: {
        fiO2_fraction: Number(fio2Percent.value) / 100,
        breathing_support: support.value,
        monitoring_on: true
      },
      random_seed: randomSeed.value === '' ? null : Number(randomSeed.value)
    }

    const response = await window.simulatorApiClient.createRun(payload)
    if (!response.ok) {
      landingError.textContent = mapCreateRunError(response)
      return
    }
    window.location.href = `/runs/${response.run_id}/`
  })

  function extractRunId(value) {
    const uuidRegex = /[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}/i
    const direct = value.match(uuidRegex)
    if (direct) {
      return direct[0]
    }

    try {
      const url = new URL(value)
      const pathMatch = url.pathname.match(/\/runs\/([0-9a-f-]{36})\/?/i)
      if (pathMatch) {
        const nested = pathMatch[1].match(uuidRegex)
        return nested ? nested[0] : null
      }
    } catch (_error) {
      return null
    }

    return null
  }

  resumeToggle.addEventListener('click', () => {
    resumeControls.classList.toggle('hidden')
    if (!resumeControls.classList.contains('hidden')) {
      resumeInput.focus()
    }
  })

  function openResumedRun() {
    resumeError.textContent = ''
    const raw = resumeInput.value.trim()
    if (!raw) {
      resumeError.textContent = 'Enter a run ID or run URL.'
      return
    }
    const runId = extractRunId(raw)
    if (!runId) {
      resumeError.textContent = 'Could not find a valid run ID in that text.'
      return
    }
    window.location.href = `/runs/${runId}/`
  }

  resumeButton.addEventListener('click', openResumedRun)
  resumeInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
      event.preventDefault()
      openResumedRun()
    }
  })

  function initMotif() {
    const canvas = document.getElementById('motif-canvas')
    if (!(canvas instanceof HTMLCanvasElement)) {
      return
    }
    const ctx = canvas.getContext('2d')
    if (!ctx) {
      return
    }

    const dpr = window.devicePixelRatio || 1
    const cssWidth = canvas.clientWidth
    const cssHeight = canvas.clientHeight
    canvas.width = Math.floor(cssWidth * dpr)
    canvas.height = Math.floor(cssHeight * dpr)
    ctx.scale(dpr, dpr)

    function draw(timeMs) {
      const t = timeMs * 0.00035
      ctx.clearRect(0, 0, cssWidth, cssHeight)

      ctx.fillStyle = '#07090c'
      ctx.fillRect(0, 0, cssWidth, cssHeight)

      ctx.strokeStyle = 'rgba(120, 135, 155, 0.16)'
      ctx.lineWidth = 1
      for (let x = 0; x <= cssWidth; x += 28) {
        ctx.beginPath()
        ctx.moveTo(x, 0)
        ctx.lineTo(x, cssHeight)
        ctx.stroke()
      }
      for (let y = 0; y <= cssHeight; y += 28) {
        ctx.beginPath()
        ctx.moveTo(0, y)
        ctx.lineTo(cssWidth, y)
        ctx.stroke()
      }

      const cx = cssWidth * 0.72
      const cy = cssHeight * 0.7
      const bowlW = cssWidth * 0.48
      const bowlH = cssHeight * 0.35
      ctx.strokeStyle = 'rgba(117, 137, 162, 0.22)'
      for (let i = 0; i < 8; i += 1) {
        const p = i / 7
        ctx.beginPath()
        for (let x = 0; x <= bowlW; x += 6) {
          const nx = x / bowlW
          const y = (Math.pow(nx - 0.5, 2) * 0.85 + p * 0.32) * bowlH
          if (x === 0) ctx.moveTo(cx - bowlW * 0.5 + x, cy - y)
          else ctx.lineTo(cx - bowlW * 0.5 + x, cy - y)
        }
        ctx.stroke()
      }

      const traces = [
        { color: '#6fae7a', base: cssHeight * 0.22, amp: 10, freq: 1.8 },
        { color: '#67b9cc', base: cssHeight * 0.35, amp: 8, freq: 1.35 },
        { color: '#e6e6e6', base: cssHeight * 0.48, amp: 7, freq: 1.05 },
        { color: '#e0a24a', base: cssHeight * 0.62, amp: 6, freq: 0.78 }
      ]

      traces.forEach((trace, index) => {
        ctx.strokeStyle = trace.color
        ctx.lineWidth = 1.6
        ctx.beginPath()
        for (let x = 0; x <= cssWidth; x += 2) {
          const wave = Math.sin((x * 0.02 * trace.freq) - t * (1.1 + index * 0.21))
          const wave2 = Math.sin((x * 0.012) + t * (0.55 + index * 0.09))
          const y = trace.base + wave * trace.amp + wave2 * (trace.amp * 0.35)
          if (x === 0) ctx.moveTo(x, y)
          else ctx.lineTo(x, y)
        }
        ctx.stroke()
      })

      requestAnimationFrame(draw)
    }

    requestAnimationFrame(draw)
  }

  initMotif()
})()

