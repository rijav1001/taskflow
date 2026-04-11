import { Box, Paper, Typography, Button, TextField } from '@mui/material'
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable'
import { useDroppable } from '@dnd-kit/core'
import { useState } from 'react'
import CardItem from './CardItem'
import type { List, Card } from '../api/boards'
import { createCard } from '../api/boards'

interface Props {
    list: List
    onCardAdded: (listId: string, card: Card) => void
}

export default function ListColumn({ list, onCardAdded }: Props) {
    const [adding, setAdding] = useState(false)
    const [title, setTitle] = useState('')

    const { setNodeRef } = useDroppable({ id: list.id, data: { type: 'list', listId: list.id } })

    const sortedCards = [...list.cards].sort((a, b) => a.order - b.order)

    async function handleAddCard() {
        if (!title.trim()) return

        const card = await createCard(title, list.id)
        onCardAdded(list.id, card)
        setTitle('')
        setAdding(false)
    }

    return (
        <Paper sx={{ width: 280, minHeight: 100, p: 1.5, bgcolor: '#ebecf0', flexShrink: 0 }}>
            <Typography fontWeight="bold" mb={1.5} px={0.5}>{list.title}</Typography>

            <SortableContext items={sortedCards.map(c => c.id)} strategy={verticalListSortingStrategy}>
                <Box ref={setNodeRef} minHeight={40}>
                {sortedCards.map(card => (
                    <CardItem key={card.id} card={card} />
                ))}
                </Box>
            </SortableContext>

            {adding ? (
                <Box mt={1}>
                    <TextField
                        fullWidth size="small" placeholder="Card title" value={title}
                        onChange={e => setTitle(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && handleAddCard()}
                        autoFocus sx={{ mb: 1 }}
                    />
                    <Box display="flex" gap={1}>
                        <Button size="small" variant="contained" onClick={handleAddCard}>Add</Button>
                        <Button size="small" onClick={() => setAdding(false)}>Cancel</Button>
                    </Box>
                </Box>
            ) : (
                <Button size="small" fullWidth onClick={() => setAdding(true)} sx={{ mt: 1, justifyContent: 'flex-start' }}>
                + Add a card
                </Button>
            )}
        </Paper>
    )
}