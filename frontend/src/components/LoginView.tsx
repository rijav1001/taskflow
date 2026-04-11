import { useState } from 'react'
import { login, register } from '../api/auth'
import { Box, Button, TextField, Typography, Paper, Tab, Tabs } from '@mui/material'

interface Props {
    onLogin: () => void
}

export default function LoginView({ onLogin }: Props) {
    const [tab, setTab] = useState(0)
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')

    async function handleSubmit() {
        try {
            setError('')
            if (tab == 1) await register(email, password)
            const token = await login(email, password)
            localStorage.setItem('token', token)
            onLogin()
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (e: any) {
            setError(e.response?.data?.detail || "Something went wrong")
        }
    }

    return (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh" bgcolor="#0079bf">
            <Paper sx={{ p: 4, width: 360 }}>
                <Typography variant="h5" fontWeight="bold" mb={2} textAlign="center">
                    TaskFlow
                </Typography>
                <Tabs value={tab} onChange={(_, v) => setTab(v)} centered sx={{ mb: 3 }}>
                    <Tab label="Login"/>
                    <Tab label="Register"/>
                </Tabs>
                <TextField
                    fullWidth label="Email" value={email}
                    onChange={e => setEmail(e.target.value)} sx={{ mb: 2 }}
                />
                <TextField
                    fullWidth label="Password" value={password} type="password"
                    onChange={e => setPassword(e.target.value)} sx={{ mb: 2 }}
                />
                {error && <Typography color="error" mb={1}>{error}</Typography>}
                <Button fullWidth variant="contained" onClick={handleSubmit}>
                    {tab == 0 ? 'Login' : 'Register'}
                </Button>
            </Paper>
        </Box>
    )
}