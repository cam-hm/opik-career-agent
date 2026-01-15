# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code
COPY . .

# Build-time env vars (PUBLIC keys only - safe to embed)
ENV NEXT_PUBLIC_API_URL=https://interviewer-backend-766703134732.asia-southeast1.run.app
ENV NEXT_PUBLIC_LIVEKIT_URL=wss://interviewer-wo2fwm01.livekit.cloud
ENV NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_YnJpZ2h0LXVuaWNvcm4tMTIuY2xlcmsuYWNjb3VudHMuZGV2JA
ENV NEXT_PUBLIC_CLERK_SIGN_IN_FORCE_REDIRECT_URL=/dashboard
ENV NEXT_PUBLIC_CLERK_SIGN_UP_FORCE_REDIRECT_URL=/dashboard
ENV NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
ENV NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000

# Copy built assets from builder
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

# Runtime env vars (secrets) are injected by Cloud Run
# CLERK_SECRET_KEY will be set via Cloud Run environment variables

CMD ["node", "server.js"]
