/* Purpose: Three-card introduction overlay on the landing page. Opens automatically on the first visit (remembered in localStorage) and again with the Intro button. X, Esc or a click outside just close it; "Open the simulator" closes it and starts the user guide. */

(function () {
  const STORAGE_KEY = 'neocaffeine-intro-done'
  const overlay = document.getElementById('intro-overlay')
  if (!overlay) {
    return
  }
  const panel = overlay.querySelector('.nc-intro-panel')
  const firstCard = document.getElementById('nc-1')
  let previousFocus = null

  function readDone() {
    try {
      return window.localStorage.getItem(STORAGE_KEY) === 'yes'
    } catch (error) {
      return false
    }
  }

  function storeDone() {
    try {
      window.localStorage.setItem(STORAGE_KEY, 'yes')
    } catch (error) {
      return
    }
  }

  function isOpen() {
    return !overlay.hidden
  }

  function onKeydown(event) {
    if (event.key === 'Escape') {
      event.preventDefault()
      close()
    }
  }

  function open() {
    if (isOpen()) {
      return
    }
    previousFocus = document.activeElement
    if (firstCard) {
      firstCard.checked = true
    }
    overlay.hidden = false
    panel.scrollTop = 0
    document.addEventListener('keydown', onKeydown, true)
    panel.focus()
  }

  function close() {
    if (!isOpen()) {
      return
    }
    storeDone()
    overlay.hidden = true
    document.removeEventListener('keydown', onKeydown, true)
    if (previousFocus && typeof previousFocus.focus === 'function') {
      previousFocus.focus()
    }
  }

  function startSimulator(event) {
    event.preventDefault()
    close()
    if (window.simulatorUserGuide) {
      window.simulatorUserGuide.open()
    }
  }

  overlay.addEventListener('click', (event) => {
    if (event.target === overlay) {
      close()
    }
  })
  overlay.querySelector('.nc-close')?.addEventListener('click', close)
  overlay.querySelectorAll('[data-intro-start]').forEach((link) => link.addEventListener('click', startSimulator))
  document.querySelectorAll('.intro-open-button').forEach((button) => button.addEventListener('click', open))

  window.simulatorIntro = { open, close, isOpen }

  if (!readDone()) {
    open()
  }
})()
