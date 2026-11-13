/* Purpose: Browser-owned simulation clock that calls advance at user-selected speed, once per real second (graphs interpolate in between). */

const CLOCK_TICK_MS = 1000

window.simulatorClockController = {
  timerHandle: null,
  speedSecondsPerHour: 1,
  setSpeed(value) {
    this.speedSecondsPerHour = value
  },
  start(tickCallback) {
    if (this.timerHandle !== null) {
      return
    }
    let lastTime = performance.now()
    this.timerHandle = window.setInterval(() => {
      const now = performance.now()
      const realSeconds = (now - lastTime) / 1000
      lastTime = now
      const deltaSimHours = realSeconds / this.speedSecondsPerHour
      tickCallback(deltaSimHours)
    }, CLOCK_TICK_MS)
  },
  stop() {
    if (this.timerHandle !== null) {
      window.clearInterval(this.timerHandle)
      this.timerHandle = null
    }
  },
  isRunning() {
    return this.timerHandle !== null
  }
}
