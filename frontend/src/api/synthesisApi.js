import api from './axios'

export async function synthesizePapers(question) {
  const response = await api.post('/synthesis/', { question })
  return response.data
}