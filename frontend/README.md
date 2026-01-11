# Mobile Phone Shopping Assistant - Frontend

React-based chat interface for the AI phone shopping assistant.

## Setup

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## Build

Create production build:
```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── chat/          # Chat interface components
│   │   ├── products/      # Product display components
│   │   ├── ui/            # Reusable UI components
│   │   └── layout/        # Layout components
│   ├── hooks/             # Custom React hooks
│   ├── services/          # API services
│   ├── store/             # Zustand state stores
│   ├── types/             # TypeScript types
│   ├── utils/             # Utility functions
│   └── styles/            # Global styles
├── public/                # Static assets
└── index.html             # Entry point
```

## Features

- Real-time chat interface
- Product cards with expandable details
- Phone comparison
- Dark/Light mode toggle
- Mobile responsive design
- Suggested follow-up questions

## Technologies

- React 18
- TypeScript
- Vite
- Tailwind CSS
- TanStack Query
- Zustand
- Framer Motion
- Lucide Icons
