/* Purpose: Browser-owned simulation clock that calls advance at user-selected speed. */

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
    }, 150)
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
