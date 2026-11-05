/* Purpose: Client state holder for run payloads and derived UI toggles. */

window.simulatorStateStore = {
  stateEnvelope: null,
  showTrueValues: false,
  nMode: 'manual',
  isPlaying: false,
  setEnvelope(envelope) {
    this.stateEnvelope = envelope
  },
  getRunId() {
    return this.stateEnvelope?.run_id
  },
  getStateVersion() {
    return this.stateEnvelope?.state_version
  },
  getState() {
    return this.stateEnvelope?.state
  }
}
