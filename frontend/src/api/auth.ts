import client from './client'

export async function login(email: string, password: string): Promise<string> {
    const res = await client.post('/auth/login', { email, password })
    return res.data.access_token
}

export async function register(email: string, password: string): Promise<void> {
    await client.post('/auth/register', { email, password })
}