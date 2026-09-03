FROM node:22-alpine AS build

ARG FRONTEND_DIR=DAKER_2026_FINANCE_AI_CHALLENGE_FRONTEND

WORKDIR /app

COPY ${FRONTEND_DIR}/package.json ${FRONTEND_DIR}/package-lock.json ./
RUN npm ci

COPY ${FRONTEND_DIR}/ ./
RUN npm run build

FROM nginx:1.27-alpine AS runtime

ARG DEPLOY_DIR=DAKER_2026_FINANCE_AI_CHALLENGE_BACKEND/deploy

COPY ${DEPLOY_DIR}/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
