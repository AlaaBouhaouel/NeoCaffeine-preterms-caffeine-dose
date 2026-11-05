/* Purpose: Hover and tap tooltip behavior for info icons in dashboard controls and panels. */

(function () {
  function createTooltipLayer() {
    const node = document.createElement('div')
    node.className = 'tooltip-layer'
    node.hidden = true
    document.body.appendChild(node)
    return node
  }

  const tooltip = createTooltipLayer()
  let activeButton = null

  function positionTooltip(button) {
    const rect = button.getBoundingClientRect()
    const tooltipRect = tooltip.getBoundingClientRect()
    const top = Math.max(8, rect.top - tooltipRect.height - 8)
    const left = Math.min(window.innerWidth - tooltipRect.width - 8, Math.max(8, rect.left))
    tooltip.style.top = `${top}px`
    tooltip.style.left = `${left}px`
  }

  function showTooltip(button) {
    const text = button.getAttribute('data-tooltip')
    if (!text) {
      return
    }
    tooltip.textContent = text
    tooltip.hidden = false
    positionTooltip(button)
    activeButton = button
  }

  function hideTooltip() {
    tooltip.hidden = true
    activeButton = null
  }

  function registerButton(button) {
    button.addEventListener('mouseenter', () => showTooltip(button))
    button.addEventListener('mouseleave', hideTooltip)
    button.addEventListener('focus', () => showTooltip(button))
    button.addEventListener('blur', hideTooltip)
    button.addEventListener('click', (event) => {
      event.preventDefault()
      if (activeButton === button && !tooltip.hidden) {
        hideTooltip()
        return
      }
      showTooltip(button)
    })
  }

  document.querySelectorAll('.info-icon[data-tooltip]').forEach(registerButton)
  document.addEventListener('click', (event) => {
    const target = event.target
    if (!(target instanceof HTMLElement)) {
      return
    }
    if (!target.closest('.info-icon')) {
      hideTooltip()
    }
  })
  window.addEventListener('resize', () => {
    if (activeButton && !tooltip.hidden) {
      positionTooltip(activeButton)
    }
  })
})()
