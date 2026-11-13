/* Purpose: Thin fetch wrapper for simulator API endpoints. */

window.simulatorApiClient = {
  async getState(runId) {
    const response = await fetch(`/api/v1/runs/${runId}/state`)
    return response.json()
  },
  async getSummary(runId) {
    const response = await fetch(`/api/v1/runs/${runId}/summary`)
    return response.json()
  },
  async advance(runId, stateVersion, deltaSimHours) {
    const response = await fetch(`/api/v1/runs/${runId}/advance`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ state_version: stateVersion, delta_sim_hours: deltaSimHours })
    })
    return response.json()
  },
  async submitN(runId, dayIndex, stateVersion, observedN) {
    const response = await fetch(`/api/v1/runs/${runId}/days/${dayIndex}/n`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ state_version: stateVersion, observed_n: observedN })
    })
    return response.json()
  },
  async giveDose(runId, payload) {
    const response = await fetch(`/api/v1/runs/${runId}/interventions/dose`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    return response.json()
  },
  async acceptSuggestedDose(runId, stateVersion) {
    const response = await fetch(`/api/v1/runs/${runId}/interventions/dose/accept`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ state_version: stateVersion })
    })
    return response.json()
  },
  async setContext(runId, payload) {
    const response = await fetch(`/api/v1/runs/${runId}/interventions/context`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    return response.json()
  },
  async setMonitoring(runId, payload) {
    const response = await fetch(`/api/v1/runs/${runId}/interventions/monitoring`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    return response.json()
  },
  async addBloodLevel(runId, payload) {
    const response = await fetch(`/api/v1/runs/${runId}/interventions/blood-level`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    return response.json()
  },
  async createRun(payload) {
    const response = await fetch('/api/v1/runs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    return response.json()
  }
}
