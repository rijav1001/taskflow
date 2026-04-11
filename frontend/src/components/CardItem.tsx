import { Paper, Typography } from '@mui/material'
import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import type { Card } from '../api/boards'

interface Props {
    card: Card
}

export default function CardItem({ card }: Props) {
    const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
        id: card.id,
        data: { type: 'card', card }
    })

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.4 : 1,
    }

    return (
        <Paper
            ref={setNodeRef}
            style={style}
            {...attributes}
            {...listeners}
            sx={{
                p: 1.5,
                mb: 1,
                cursor: 'grab',
                '&:active': { cursor: 'grabbing' },
                boxShadow: isDragging ? 4 : 1,
            }}
        >
            <Typography variant="body2">{card.title}</Typography>
            {card.description && (
                <Typography variant="caption" color="text.secondary">{card.description}</Typography>
            )}
        </Paper>
    )
}