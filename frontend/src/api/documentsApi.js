import api from './axios'

export async function getDocuments() {
  const response = await api.get('/documents/')
  return response.data
}

export async function deleteDocument(documentId) {
  await api.delete(`/documents/${documentId}`)
}
