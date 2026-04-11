import { useEffect, useState } from 'react'
import { Box, Typography, Button, TextField, CircularProgress } from '@mui/material'
import { DndContext, PointerSensor, useSensor, useSensors, closestCorners } from '@dnd-kit/core'
import type { DragEndEvent } from '@dnd-kit/core'
import { getBoards, getBoard, createBoard, createList, moveCard } from '../api/boards'
import type { Board, Card } from '../api/boards'
import ListColumn from './ListColumn'
import LoginView from './LoginView'

export default function BoardView() {
    const [authed, setAuthed] = useState(!!localStorage.getItem('token'))
    const [board, setBoard] = useState<Board | null>(null)
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const [boards, setBoards] = useState<any[]>([])
    const [newBoardTitle, setNewBoardTitle] = useState('')
    const [newListTitle, setNewListTitle] = useState('')
    const [loading, setLoading] = useState(false)

    const sensors = useSensors(useSensor(PointerSensor))

    async function fetchBoard(id: string) {
        setLoading(true)
        const data = await getBoard(id)
        setBoard(data)
        setLoading(false)
    }

    async function fetchBoards() {
        const data = await getBoards()
        setBoards(data)
        if (data.length > 0) fetchBoard(data[0].id)
    }

    useEffect(() => {
        if (!authed) return
        async function load() {
            const data = await getBoards()
            setBoards(data)
            if (data.length > 0) {
            const board = await getBoard(data[0].id)
            setBoard(board)
            }
        }
        
        load()
    }, [authed])

    async function handleCreateBoard() {
        if (!newBoardTitle.trim()) return
        const b = await createBoard(newBoardTitle)
        setNewBoardTitle('')
        await fetchBoards()
        fetchBoard(b.id)
    }

    async function handleCreateList() {
        if (!newListTitle.trim() || !board) return
        await createList(newListTitle, board.id)
        setNewListTitle('')
        fetchBoard(board.id)
    }

    function handleCardAdded(listId: string, card: Card) {
        if (!board) return
        setBoard(prev => {
            if (!prev) return prev
            return {
                ...prev,
                lists: prev.lists.map(l =>
                    l.id === listId ? { ...l, cards: [...l.cards, card] } : l
                )
            }
        })
    }

    async function handleDragEnd(event: DragEndEvent) {
        const { active, over } = event
        if (!over || !board) return

        const cardId = active.id as string
        const targetListId = (over.data.current?.listId || over.data.current?.card?.list_id) as string
        if (!targetListId) return

        const targetList = board.lists.find(l => l.id === targetListId)
        if (!targetList) return

        const sortedCards = [...targetList.cards].sort((a, b) => a.order - b.order)
        const overCard = sortedCards.find(c => c.id === over.id)
        const overIndex = overCard ? sortedCards.indexOf(overCard) : sortedCards.length

        const before = sortedCards[overIndex - 1]?.order ?? null
        const after = sortedCards[overIndex]?.order ?? null
        let newOrder: number

        if (before === null && after === null) newOrder = 1000
        else if (before === null) newOrder = after! - 1000
        else if (after === null) newOrder = before + 1000
        else newOrder = (before + after) / 2

        // optimistic update
        const previousBoard = board
        setBoard(prev => {
            if (!prev) return prev
            return {
                ...prev,
                lists: prev.lists.map(l => ({
                    ...l,
                    cards: l.id === targetListId
                    ? [...l.cards.filter(c => c.id !== cardId), { ...active.data.current!.card, list_id: targetListId, order: newOrder }]
                    : l.cards.filter(c => c.id !== cardId)
                }))
            }
        })

        // API call with rollback on failure
        try {
            await moveCard(cardId, targetListId, newOrder)
        } catch {
            setBoard(previousBoard)
        }
    }

    if (!authed) return <LoginView onLogin={() => setAuthed(true)}/>

    return (
        <Box minHeight="100vh" bgcolor="#0079bf" p={2}>
            {/* Header */}
            <Box display="flex" alignItems="center" gap={2} mb={3}>
                <Typography variant="h5" color="white" fontWeight="bold">TaskFlow</Typography>
                <TextField
                    size="small" placeholder="New board..." value={newBoardTitle}
                    onChange={e => setNewBoardTitle(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleCreateBoard()}
                    sx={{ bgcolor: 'white', borderRadius: 1 }}
                />
                <Button variant="contained" color="success" onClick={handleCreateBoard}>Create Board</Button>
                {boards.map(b => (
                    <Button key={b.id} variant={board?.id === b.id ? 'contained' : 'outlined'}
                        onClick={() => fetchBoard(b.id)}
                        sx={{ color: 'white', borderColor: 'white' }}>
                        {b.title}
                    </Button>
                ))}
            </Box>

            {loading && <CircularProgress sx={{ color: 'white' }}/>}

            {board && (
                <>
                    <Typography variant="h6" color="white" fontWeight="bold" mb={2}>{board.title}</Typography>

                    {/* Add list */}
                    <Box display="flex" gap={1} mb={2}>
                        <TextField
                            size="small" placeholder="New list..." value={newListTitle}
                            onChange={e => setNewListTitle(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && handleCreateList()}
                            sx={{ bgcolor: 'white', borderRadius: 1 }}
                        />
                        <Button variant="contained" onClick={handleCreateList}>Add List</Button>
                    </Box>

                    {/* Board columns */}
                    <DndContext sensors={sensors} collisionDetection={closestCorners} onDragEnd={handleDragEnd}>
                        <Box display="flex" gap={2} alignItems="flex-start" overflow="auto" pb={2}>
                            {board.lists.map(list => (
                                <ListColumn key={list.id} list={list} onCardAdded={handleCardAdded} />
                            ))}
                        </Box>
                    </DndContext>
                </>
            )}
        </Box>
    )
}