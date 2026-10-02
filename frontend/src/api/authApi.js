import api from './axios'

export async function registerAccount({ name, email, password }) {
  const response = await api.post('/auth/register', { name, email, password })
  return response.data
}

export async function loginAccount({ email, password }) {
  const response = await api.post('/auth/login', { email, password })
  return response.data
}

export async function getCurrentUser() {
  const response = await api.get('/auth/me')
  return response.data
}
