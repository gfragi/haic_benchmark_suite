export function interpretSUS(mean: number, n: number) {
  // loose, readable mapping commonly used in UX practice
  let grade = 'F', adjective = 'Poor'
  if (mean >= 84) { grade = 'A', adjective = 'Excellent' }
  else if (mean >= 80) { grade = 'A-', adjective = 'Excellent' }
  else if (mean >= 74) { grade = 'B', adjective = 'Good' }
  else if (mean >= 68) { grade = 'C', adjective = 'OK' }
  else if (mean >= 62) { grade = 'D', adjective = 'Marginal' }
  else { grade = 'F', adjective = 'Poor' }

  const note = mean >= 68
    ? 'above the commonly cited SUS average (~68)'
    : 'below the commonly cited SUS average (~68)'

  return {
    grade, adjective,
    blurb: `Average SUS is ${mean.toFixed(1)} (${adjective}, ${grade}), ${note}. Based on ${n} responses.`
  }
}