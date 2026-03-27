export const SUS_QUESTIONS = [
  { key: 'sus_q1', text: 'I think that I would like to use this system frequently.' },
  { key: 'sus_q2', text: 'I found the system unnecessarily complex.' },
  { key: 'sus_q3', text: 'I thought the system was easy to use.' },
  { key: 'sus_q4', text: 'I think that I would need the support of a technical person.' },
  { key: 'sus_q5', text: 'I found the various functions well integrated.' },
  { key: 'sus_q6', text: 'I thought there was too much inconsistency in this system.' },
  { key: 'sus_q7', text: 'I would imagine most people would learn to use this quickly.' },
  { key: 'sus_q8', text: 'I found the system very difficult to use.' },
  { key: 'sus_q9', text: 'I felt very confident using the system.' },
  { key: 'sus_q10', text: 'I needed to learn many things before I could get going.' },
]

export const ETHICS_QUESTIONS = [
  { key: 'q_fairness', text: 'The system handles different users without bias.' },
  { key: 'q_transparency', text: 'I understand how the AI arrives at its decisions.' },
  { key: 'q_privacy', text: 'I feel confident that personal data is protected.' },
  { key: 'q_accountability', text: 'It is clear who is responsible for errors.' },
  { key: 'q_trust', text: 'Overall, I trust the system to operate in my interest.' },
]

export const SCALE_LABELS = {
  1: 'Strongly Disagree',
  3: 'Neutral',
  5: 'Strongly Agree',
}

export function computeSus(sus) {
  const odd = ['sus_q1', 'sus_q3', 'sus_q5', 'sus_q7', 'sus_q9']
  const even = ['sus_q2', 'sus_q4', 'sus_q6', 'sus_q8', 'sus_q10']
  const allAnswered = [...odd, ...even].every((key) => sus[key] != null)
  if (!allAnswered) return null
  const sumOdd = odd.reduce((acc, key) => acc + sus[key], 0)
  const sumEven = even.reduce((acc, key) => acc + sus[key], 0)
  return ((sumOdd - 5) + (25 - sumEven)) * 2.5
}

export function makeAnonymousUserId() {
  const bytes = new Uint8Array(4)
  crypto.getRandomValues(bytes)
  const hex = Array.from(bytes, (byte) => byte.toString(16).padStart(2, '0')).join('')
  return `anon_${hex}`
}
