# TaskFlow — Project Management Tool

A full-stack project management tool (Trello-like) built as a senior-level engineering challenge.

## Tech Stack

**Backend:** Python 3.12, FastAPI, PostgreSQL (Async), SQLAlchemy 2.0, Alembic, Pydantic V2
**Frontend:** React 19, TypeScript, Vite, MUI v6, dnd-kit
**Infrastructure:** Docker, Docker Compose

## Getting Started

### Prerequisites
- Docker Desktop

### Run with one command
```bash
docker compose up --build
```

This spins up:
- PostgreSQL on port 5432
- FastAPI backend on http://localhost:8000
- React frontend on http://localhost:5173

### API Documentation
Visit http://localhost:8000/docs for the full Swagger UI.

---

## Architecture Decisions

### 1. Ordering Algorithm — Floating Point Indexing

Cards need to be reorderable without updating every other card in the list.

**Why not integer ordering?**
Moving a card to position #1 with integer ordering requires updating every card below it — an O(n) write operation that gets expensive fast.

**Our approach — Floating Point Indexing:**
Each card has a `float` order value. When inserting between two cards:
new_order = (card_before.order + card_after.order) / 2
Example:
- Card A: 1000.0
- Card C: 2000.0
- Insert B between them → (1000 + 2000) / 2 = 1500.0
- No other cards need updating — O(1) write

**Rebalancing:**
After many insertions, values can get too close (floating point precision limits).
When the gap between adjacent values falls below a threshold (0.001), we rebalance
all cards in the list by redistributing them evenly with a GAP of 1000.0.

**Why not LexoRank?**
LexoRank (used by Jira) uses string-based ordering with bucket rotation. It's more
robust at massive scale but significantly more complex to implement correctly.
Floating point indexing achieves the same O(1) insert property and is appropriate
for this scale.

---

### 2. Concurrency — Race Condition Handling

**Problem:** Two users drag the same card simultaneously. Without protection,
both reads see the same state, both compute a new order, and one update silently
overwrites the other.

**Our solution — Pessimistic Locking (SELECT FOR UPDATE):**

```python
result = await db.execute(
    select(Card)
    .where(Card.id == card_id)
    .with_for_update()  # locks the row
)
```

When User A starts moving a card, the database locks that row.
User B's request waits until User A's transaction completes before proceeding.
This guarantees sequential processing — no silent overwrites.

**Why pessimistic over optimistic locking?**
Optimistic locking (version numbers) is better for low-contention scenarios.
For card moves — which are frequent, fast, and directly conflict — pessimistic
locking is simpler and more appropriate. The lock is held for milliseconds.

---

### 3. N+1 Query Prevention

`GET /boards/{id}` returns a board with all its lists and all cards in those lists.

**Naive approach (N+1):**
1 query  → fetch board
N queries → fetch each list
N×M queries → fetch cards for each list
For a board with 5 lists and 20 cards each = 106 database queries per request.

**Our approach — selectinload:**
```python
select(Board).options(
    selectinload(Board.lists).selectinload(List.cards)
)
```
SQLAlchemy fires exactly 3 queries total regardless of board size:
1. Fetch the board
2. Fetch all lists for that board
3. Fetch all cards for those lists

---

### 4. Soft Deletes

Entities (Boards, Lists, Cards) are never physically deleted.
Instead, a `deleted_at` timestamp is set. All queries filter `deleted_at == None`.

Deleting a Board logically cascades — its Lists and Cards are unreachable via
the API because queries always join through the parent Board and check its
`deleted_at` status. Data remains in the DB for audit purposes.

---

### 5. Optimistic UI

On card drag and drop:
1. UI updates **immediately** without waiting for the API
2. API call fires in the background
3. If the API **succeeds** → UI state is already correct
4. If the API **fails** → UI reverts to the previous board state (rollback)

This makes the app feel instant while maintaining data consistency.

---

## Project Structure
taskflow/
├── backend/
│   ├── app/
│   │   ├── api/          # route handlers
│   │   ├── core/         # config, security, dependencies
│   │   ├── db/           # database session, engine
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic V2 schemas
│   │   └── services/     # business logic + lexorank
│   └── alembic/          # database migrations
├── frontend/
│   └── src/
│       ├── api/          # axios API client
│       └── components/   # React components
└── docker-compose.yml