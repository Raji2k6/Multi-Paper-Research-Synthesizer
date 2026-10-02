export function getFriendlyError(error) {
  if (!error.response) return 'Unable to connect to the research backend.'
  if (error.response.status === 429) return 'The AI service is temporarily rate-limited. Please try again shortly.'
  if (error.response.status === 502) return error.response.data?.detail || 'The language-model provider could not generate an answer. Please retry.'
  if (error.response.status >= 500) return 'The research backend is temporarily unavailable. Please try again.'
  if (error.response.status === 404) return error.response.data?.detail || 'No relevant research evidence was found.'
  const detail = error.response.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.map((issue) => issue.msg).filter(Boolean).join(' ')
  return 'Something went wrong while processing your request.'
}