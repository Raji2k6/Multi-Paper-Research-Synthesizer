import api from './axios'

export async function synthesizePapers(question) {
  const response = await api.post('/synthesis/', { question })
  return response.data
}

export async function getSynthesisHistory() {
  const response = await api.get('/synthesis/history')
  return response.data
}