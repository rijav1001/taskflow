import client from './client'

export interface Card {
    id: string
    title: string
    description?: string
    list_id: string
    order: number
}

export interface List {
    id: string
    title: string
    board_id: string
    cards: Card[]
}

export interface Board {
    id: string
    title: string
    owner_id: string
    lists: List[]
}

export async function getBoards() {
    const res = await client.get('/boards')
    return res.data
}

export async function createBoard(title: string) {
    const res = await client.post('/boards', { title })
    return res.data
}

export async function getBoard(id: string): Promise<Board> {
    const res = await client.get(`/boards/${id}`)
    return res.data
}

export async function createList(title: string, board_id: string) {
    const res = await client.post('/lists', { title, board_id })
    return res.data
}

export async function createCard(title: string, list_id: string) {
    const res = await client.post('/cards', { title, list_id })
    return res.data
}

export async function moveCard(card_id: string, list_id: string, order: number) {
    const res = await client.put(`/cards/${card_id}/move`, { list_id, order })
    return res.data
}