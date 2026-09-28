import api from './axios'

export async function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post('/upload/', formData)
  return response.data
}