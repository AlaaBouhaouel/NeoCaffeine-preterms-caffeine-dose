/* Purpose: Landing form behavior for creating a run and redirecting to dashboard. */

(function () {
  const form = document.getElementById('create-run-form')
  if (!form) {
    return
  }

  const errorNode = document.getElementById('landing-error')

  form.addEventListener('submit', async (event) => {
    event.preventDefault()
    errorNode.textContent = ''

    const randomSeedRaw = document.getElementById('random-seed').value
    const payload = {
      patient: {
        gestational_age_weeks: Number(document.getElementById('ga-weeks').value),
        gestational_age_days_extra: Number(document.getElementById('ga-days').value),
        birth_weight_g: Number(document.getElementById('birth-weight').value),
        sex: document.getElementById('sex').value
      },
      initial_context: {
        fiO2_fraction: Number(document.getElementById('fio2').value),
        breathing_support: document.getElementById('breathing-support').value,
        monitoring_on: document.getElementById('monitoring-on').value === 'true'
      },
      random_seed: randomSeedRaw === '' ? null : Number(randomSeedRaw)
    }

    const response = await window.simulatorApiClient.createRun(payload)
    if (!response.ok) {
      errorNode.textContent = `${response.error.code}: ${response.error.message}`
      return
    }
    window.location.href = `/runs/${response.run_id}/`
  })
})()
