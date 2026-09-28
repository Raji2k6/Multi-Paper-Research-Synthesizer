export function getFriendlyError(error) {
  if (!error.response) return 'Unable to connect to the research backend.'
  if (error.response.status === 404) return 'No relevant research evidence was found.'
  if (error.response.status === 429) return 'The AI service is temporarily rate-limited. Please try again shortly.'
  if (error.response.status >= 500) return 'The research backend is temporarily unavailable. Please try again.'
  if (error.response.status === 400) return error.response.data?.detail || 'Please check the request and try again.'
  return 'Something went wrong while processing your request.'
}