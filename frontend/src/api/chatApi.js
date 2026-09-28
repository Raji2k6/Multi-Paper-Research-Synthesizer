import api from './axios'

export async function chatWithResearch(question) {
  const response = await api.post('/chat/', { question })
  return response.data
}