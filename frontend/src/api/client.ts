import axios from 'axios'

const client = axios.create({
    baseURL: 'http://localhost:8000',
})

// hardcoded token for frontend dev phase
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const TOKEN = localStorage.getItem('token') || ''

client.interceptors.request.use((config) => {
    const token = localStorage.getItem('token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

client.interceptors.response.use(
    res => res,
    err => {
        if (err.res?.status === 401) {
            localStorage.removeItem('token')
            window.location.reload()
        }
        return Promise.reject(err)
    }
)

export default client