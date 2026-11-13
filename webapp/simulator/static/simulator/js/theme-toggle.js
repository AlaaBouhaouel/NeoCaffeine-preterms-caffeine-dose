/* Purpose: Light/dark theme switch shared by every page. The first visit follows the OS setting; a button press is remembered in this browser. */

(function () {
  const STORAGE_KEY = 'neocaffeine-theme'
  const THEMES = ['dark', 'light']
  const osPrefersLight = window.matchMedia ? window.matchMedia('(prefers-color-scheme: light)') : null

  function readStoredTheme() {
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY)
      return THEMES.includes(stored) ? stored : null
    } catch (error) {
      return null
    }
  }

  function storeTheme(theme) {
    try {
      window.localStorage.setItem(STORAGE_KEY, theme)
    } catch (error) {
      return
    }
  }

  function osTheme() {
    return osPrefersLight && osPrefersLight.matches ? 'light' : 'dark'
  }

  function currentTheme() {
    const applied = document.documentElement.getAttribute('data-theme')
    return THEMES.includes(applied) ? applied : 'dark'
  }

  function otherTheme(theme) {
    return theme === 'dark' ? 'light' : 'dark'
  }

  const ICONS = {
    light: '<svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>',
    dark: '<svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
  }

  function updateButtons(theme) {
    const target = otherTheme(theme)
    document.querySelectorAll('.theme-toggle').forEach((button) => {
      button.innerHTML = ICONS[target]
      button.setAttribute('aria-label', `Switch to ${target} theme`)
      button.setAttribute('title', `Switch to ${target} theme`)
    })
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme)
    updateButtons(theme)
    window.dispatchEvent(new CustomEvent('neocaffeine:themechange', { detail: { theme } }))
  }

  document.querySelectorAll('.theme-toggle').forEach((button) => {
    button.addEventListener('click', () => {
      const next = otherTheme(currentTheme())
      storeTheme(next)
      applyTheme(next)
    })
  })

  if (osPrefersLight && typeof osPrefersLight.addEventListener === 'function') {
    osPrefersLight.addEventListener('change', () => {
      if (readStoredTheme() === null) {
        applyTheme(osTheme())
      }
    })
  }

  applyTheme(readStoredTheme() || osTheme())
})()
