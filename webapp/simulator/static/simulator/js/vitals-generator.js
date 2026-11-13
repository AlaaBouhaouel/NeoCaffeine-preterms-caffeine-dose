/* Purpose: Browser-side DEMO vital signs (proposal 06). Deterministic from the run seed and simulated time; never stored. Trends are sampled once per simulated minute; apnea episodes are placed per simulated hour at the demo apnea rate sent by the server. */

window.simulatorVitals = (function () {
  const MINUTES_PER_HOUR = 60
  const HOURS_PER_DAY = 24
  const HEART_RATE_BASELINE = 145
  const HEART_RATE_CAFFEINE_PER_MG_PER_L = 0.4
  const HEART_RATE_DURING_BRADYCARDIA = 98
  const SPO2_BASELINE = 95
  const SPO2_PER_FIO2_ABOVE_ROOM_AIR = 10
  const SPO2_CEILING = 99
  const SPO2_DURING_DESATURATION = 82
  const RESPIRATION_BASELINE = 42
  const RECOVERY_MINUTES = 3

  const rateByHour = new Map()

  function hash(seed, a, b) {
    let h = (seed ^ Math.imul(a + 0x9e3779b9, 0x85ebca6b) ^ Math.imul(b + 0x7f4a7c15, 0xc2b2ae35)) >>> 0
    h = Math.imul(h ^ (h >>> 16), 0x7feb352d) >>> 0
    h = Math.imul(h ^ (h >>> 15), 0x846ca68b) >>> 0
    return ((h ^ (h >>> 16)) >>> 0) / 4294967296
  }

  function noise(seed, channel, minute) {
    return (hash(seed, channel, minute) + hash(seed, channel + 7, minute) + hash(seed, channel + 13, minute)) - 1.5
  }

  function rememberRate(hour, rate) {
    if (!rateByHour.has(hour)) {
      rateByHour.set(hour, rate)
    }
  }

  function rateForHour(hour, currentRate) {
    return rateByHour.has(hour) ? rateByHour.get(hour) : currentRate
  }

  function poisson(seed, hour, mean) {
    const limit = Math.exp(-mean)
    let count = 0
    let product = hash(seed, 101, hour)
    while (product > limit && count < 30) {
      count += 1
      product *= hash(seed, 101 + count, hour)
    }
    return count
  }

  function apneaMinutesOfHour(seed, hour, rate) {
    const starts = []
    const count = poisson(seed, hour, rate)
    for (let index = 0; index < count; index += 1) {
      starts.push(hour * MINUTES_PER_HOUR + Math.floor(hash(seed, 211 + index, hour) * MINUTES_PER_HOUR))
    }
    return starts
  }

  function minutesSinceApnea(seed, minute, currentRate) {
    const hour = Math.floor(minute / MINUTES_PER_HOUR)
    let closest = Infinity
    for (const candidateHour of [hour - 1, hour]) {
      if (candidateHour < 0) continue
      for (const start of apneaMinutesOfHour(seed, candidateHour, rateForHour(candidateHour, currentRate))) {
        const since = minute - start
        if (since >= 0 && since < closest) closest = since
      }
    }
    return closest
  }

  function sampleAt(seed, minute, context) {
    if (!context.monitoringOn) {
      return { heartRate: null, spo2: null, respiration: null }
    }
    const since = minutesSinceApnea(seed, minute, context.apneaRatePerHour)
    const circadian = Math.sin((2 * Math.PI * minute) / (HOURS_PER_DAY * MINUTES_PER_HOUR))
    const recovery = since <= RECOVERY_MINUTES ? 1 - since / (RECOVERY_MINUTES + 1) : 0

    const baseHeartRate = HEART_RATE_BASELINE + 4 * circadian + HEART_RATE_CAFFEINE_PER_MG_PER_L * context.concentration + 2 * noise(seed, 1, minute)
    const bradycardia = since >= 1 && since <= RECOVERY_MINUTES
    const heartRate = bradycardia ? baseHeartRate - (baseHeartRate - HEART_RATE_DURING_BRADYCARDIA) * recovery : baseHeartRate

    const baseSpo2 = Math.min(SPO2_CEILING, SPO2_BASELINE + SPO2_PER_FIO2_ABOVE_ROOM_AIR * (context.fio2 - 0.21) + 0.6 * noise(seed, 2, minute))
    const desaturation = since >= 1 && since <= RECOVERY_MINUTES
    const spo2 = desaturation ? baseSpo2 - (baseSpo2 - SPO2_DURING_DESATURATION) * recovery : baseSpo2

    const respiration = since === 0 ? 0 : RESPIRATION_BASELINE + 2 * circadian + 2.5 * noise(seed, 3, minute)

    return { heartRate, spo2, respiration }
  }

  function series(seed, endHours, windowHours, context) {
    const endMinute = Math.floor(endHours * MINUTES_PER_HOUR)
    const startMinute = Math.max(0, endMinute - Math.round(windowHours * MINUTES_PER_HOUR))
    rememberRate(Math.floor(endHours), context.apneaRatePerHour)
    const time = []
    const heartRate = []
    const spo2 = []
    const respiration = []
    for (let minute = startMinute; minute <= endMinute; minute += 1) {
      const sample = sampleAt(seed, minute, context)
      time.push(minute / MINUTES_PER_HOUR)
      heartRate.push(sample.heartRate)
      spo2.push(sample.spo2)
      respiration.push(sample.respiration)
    }
    return { time, heartRate, spo2, respiration }
  }

  return { series }
})()
