/* Purpose: Beginner guided tour (proposal 07) for the landing page and the dashboard. Opens automatically on the first visit to each page, can always be skipped, and is reopened with the ? button. Front end only; the finished/skipped choice is kept in localStorage. */

(function () {
  const GUIDES = {
    landing: {
      pageSelector: '#landing-canvas',
      storageKey: 'neocaffeine-guide-done-landing',
      steps: [
        { targets: [], title: 'Welcome', text: 'Create a virtual preterm baby and watch the model learn. Skip any time.' },
        { targets: ['#create-run-form .field-row', '.segment-control', '#birth-time'], title: 'Describe the baby', text: 'Enter gestational age, birth weight, sex and birth time.' },
        { targets: ['.initial-care'], title: 'Initial care', text: 'Set the oxygen (FiO2) and breathing support.' },
        { targets: ['#start-simulation'], title: 'Start', text: 'Press Start simulation to open the dashboard.' },
        { targets: ['.resume-box'], title: 'Come back later', text: 'Paste a run ID to reopen a saved run.' },
        { targets: ['.guide-open-button'], title: 'Done', text: 'Reopen this guide with the ? button.' },
      ],
    },
    dashboard: {
      pageSelector: '#dashboard-canvas',
      storageKey: 'neocaffeine-guide-done-dashboard',
      steps: [
        { targets: [], title: 'Welcome', text: 'A quick tour of the simulator. Skip any time.' },
        { targets: ['#play-pause-button', '#speed-select'], title: 'Start the clock', text: 'Press Play to start the simulator. At speed 1, one second is one hour.' },
        { targets: ['.monitor-panel'], title: 'Watch the baby', text: 'Live vital signs of the baby.' },
        { targets: ['#dose-card-panel'], title: 'Suggested caffeine dose', text: 'The suggestion updates as the model learns. It is always in the therapeutic range.' },
        { targets: ['#dose-form .dose-entry'], title: 'Give caffeine', text: 'Enter a dose and press Submit. It does not have to be the suggested amount; the system still learns.' },
        { targets: ['#n-card-panel'], title: 'Report each day', text: "Every 24 h, submit the day's apnea event count." },
        { targets: ['.estimator-panel', '.convergence-panel', '#show-true-toggle'], title: 'See it learn', text: 'Estimates move toward the true values. Tick "True values" to see the hidden states and compare.' },
        { targets: ['.guide-open-button'], title: 'Done', text: 'Reopen this guide with the ? button.' },
      ],
    },
  }

  const SVG_NS = 'http://www.w3.org/2000/svg'
  const HIGHLIGHT_PADDING_PX = 6
  const CARD_GAP_PX = 14
  const VIEWPORT_MARGIN_PX = 16
  const AUTO_OPEN_DELAY_MS = 400

  function findGuide() {
    return Object.values(GUIDES).find((guide) => document.querySelector(guide.pageSelector)) || null
  }

  function readDone(key) {
    try {
      return window.localStorage.getItem(key) === 'yes'
    } catch (error) {
      return false
    }
  }

  function storeDone(key) {
    try {
      window.localStorage.setItem(key, 'yes')
    } catch (error) {
      return
    }
  }

  function pauseDashboardClock() {
    const clock = window.simulatorClockController
    const playButton = document.getElementById('play-pause-button')
    if (clock && clock.isRunning() && playButton) {
      playButton.click()
    }
  }

  function visibleElements(selectors) {
    return selectors
      .map((selector) => document.querySelector(selector))
      .filter((element) => element && element.getClientRects().length > 0)
  }

  function paddedRect(element) {
    const rect = element.getBoundingClientRect()
    return {
      left: rect.left - HIGHLIGHT_PADDING_PX,
      top: rect.top - HIGHLIGHT_PADDING_PX,
      width: rect.width + HIGHLIGHT_PADDING_PX * 2,
      height: rect.height + HIGHLIGHT_PADDING_PX * 2,
    }
  }

  function unionRect(rects) {
    const left = Math.min(...rects.map((rect) => rect.left))
    const top = Math.min(...rects.map((rect) => rect.top))
    const right = Math.max(...rects.map((rect) => rect.left + rect.width))
    const bottom = Math.max(...rects.map((rect) => rect.top + rect.height))
    return { left, top, width: right - left, height: bottom - top }
  }

  function svgElement(name, attributes) {
    const element = document.createElementNS(SVG_NS, name)
    Object.entries(attributes).forEach(([key, value]) => element.setAttribute(key, String(value)))
    return element
  }

  function buildOverlay() {
    const root = document.createElement('div')
    root.className = 'guide-root'
    root.innerHTML = `
      <svg class="guide-shade" aria-hidden="true" focusable="false">
        <defs><mask id="guide-shade-mask"><rect class="guide-mask-base" x="0" y="0" width="100%" height="100%" fill="white"></rect><g class="guide-mask-holes"></g></mask></defs>
        <rect class="guide-shade-fill" x="0" y="0" width="100%" height="100%" mask="url(#guide-shade-mask)"></rect>
        <g class="guide-rings"></g>
      </svg>
      <section class="guide-card" role="dialog" aria-modal="true" aria-labelledby="guide-title" aria-describedby="guide-text">
        <p class="guide-progress"></p>
        <h2 id="guide-title" class="guide-title"></h2>
        <p id="guide-text" class="guide-text"></p>
        <div class="guide-buttons">
          <button type="button" class="guide-skip">Skip</button>
          <span class="guide-nav">
            <button type="button" class="guide-back">Back</button>
            <button type="button" class="guide-next">Next</button>
          </span>
        </div>
      </section>`
    document.body.appendChild(root)
    return root
  }

  function placeCard(card, highlight) {
    card.style.left = ''
    card.style.top = ''
    if (window.matchMedia('(max-width: 640px)').matches) {
      card.classList.add('guide-card-docked')
      return
    }
    card.classList.remove('guide-card-docked')
    const cardWidth = card.offsetWidth
    const cardHeight = card.offsetHeight
    const viewportWidth = window.innerWidth
    const viewportHeight = window.innerHeight
    if (!highlight) {
      card.style.left = `${Math.max(VIEWPORT_MARGIN_PX, (viewportWidth - cardWidth) / 2)}px`
      card.style.top = `${Math.max(VIEWPORT_MARGIN_PX, (viewportHeight - cardHeight) / 2)}px`
      return
    }
    const spaceBelow = viewportHeight - (highlight.top + highlight.height)
    const spaceAbove = highlight.top
    let top
    if (spaceBelow >= cardHeight + CARD_GAP_PX + VIEWPORT_MARGIN_PX) {
      top = highlight.top + highlight.height + CARD_GAP_PX
    } else if (spaceAbove >= cardHeight + CARD_GAP_PX + VIEWPORT_MARGIN_PX) {
      top = highlight.top - cardHeight - CARD_GAP_PX
    } else {
      top = viewportHeight - cardHeight - VIEWPORT_MARGIN_PX
    }
    const centeredLeft = highlight.left + highlight.width / 2 - cardWidth / 2
    const left = Math.min(Math.max(VIEWPORT_MARGIN_PX, centeredLeft), viewportWidth - cardWidth - VIEWPORT_MARGIN_PX)
    card.style.left = `${Math.max(VIEWPORT_MARGIN_PX, left)}px`
    card.style.top = `${Math.max(VIEWPORT_MARGIN_PX, top)}px`
  }

  function createTour(guide) {
    let root = null
    let stepIndex = 0
    let previousFocus = null

    function currentElements() {
      return visibleElements(guide.steps[stepIndex].targets)
    }

    function draw() {
      if (!root) {
        return
      }
      const holes = root.querySelector('.guide-mask-holes')
      const rings = root.querySelector('.guide-rings')
      holes.replaceChildren()
      rings.replaceChildren()
      const rects = currentElements().map(paddedRect)
      rects.forEach((rect) => {
        const shape = { x: rect.left, y: rect.top, width: rect.width, height: rect.height, rx: 8, ry: 8 }
        holes.appendChild(svgElement('rect', { ...shape, fill: 'black' }))
        rings.appendChild(svgElement('rect', { ...shape, class: 'guide-ring' }))
      })
      placeCard(root.querySelector('.guide-card'), rects.length ? unionRect(rects) : null)
    }

    function showStep(index) {
      stepIndex = index
      const step = guide.steps[stepIndex]
      const isLast = stepIndex === guide.steps.length - 1
      root.querySelector('.guide-progress').textContent = `${stepIndex + 1} / ${guide.steps.length}`
      root.querySelector('.guide-title').textContent = step.title
      root.querySelector('.guide-text').textContent = step.text
      root.querySelector('.guide-back').disabled = stepIndex === 0
      root.querySelector('.guide-next').textContent = isLast ? 'Finish' : 'Next'
      root.querySelector('.guide-skip').hidden = isLast
      const elements = currentElements()
      if (elements.length) {
        elements[0].scrollIntoView({ block: 'center', inline: 'nearest' })
      }
      draw()
      root.querySelector('.guide-next').focus()
    }

    function close() {
      if (!root) {
        return
      }
      storeDone(guide.storageKey)
      window.removeEventListener('resize', draw)
      window.removeEventListener('scroll', draw, true)
      document.removeEventListener('keydown', onKeydown, true)
      root.remove()
      root = null
      if (previousFocus && typeof previousFocus.focus === 'function') {
        previousFocus.focus()
      }
    }

    function next() {
      if (stepIndex >= guide.steps.length - 1) {
        close()
        return
      }
      showStep(stepIndex + 1)
    }

    function back() {
      if (stepIndex > 0) {
        showStep(stepIndex - 1)
      }
    }

    function onKeydown(event) {
      if (event.key === 'Escape') {
        event.preventDefault()
        close()
      } else if (event.key === 'ArrowRight') {
        event.preventDefault()
        next()
      } else if (event.key === 'ArrowLeft') {
        event.preventDefault()
        back()
      } else if (event.key === 'Tab') {
        const buttons = Array.from(root.querySelectorAll('.guide-card button')).filter((button) => !button.disabled && !button.hidden)
        const position = buttons.indexOf(document.activeElement)
        event.preventDefault()
        const step = event.shiftKey ? -1 : 1
        buttons[(position + step + buttons.length) % buttons.length].focus()
      }
    }

    function open() {
      if (root) {
        return
      }
      pauseDashboardClock()
      previousFocus = document.activeElement
      root = buildOverlay()
      root.querySelector('.guide-skip').addEventListener('click', close)
      root.querySelector('.guide-back').addEventListener('click', back)
      root.querySelector('.guide-next').addEventListener('click', next)
      window.addEventListener('resize', draw)
      window.addEventListener('scroll', draw, true)
      document.addEventListener('keydown', onKeydown, true)
      showStep(0)
    }

    return { open }
  }

  const guide = findGuide()
  if (!guide) {
    return
  }
  const tour = createTour(guide)
  document.querySelectorAll('.guide-open-button').forEach((button) => {
    button.addEventListener('click', tour.open)
  })
  window.simulatorUserGuide = { open: tour.open }
  if (!readDone(guide.storageKey)) {
    window.setTimeout(tour.open, AUTO_OPEN_DELAY_MS)
  }
})()
