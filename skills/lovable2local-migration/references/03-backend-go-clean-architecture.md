# Guia de Scaffolding do Backend Go com Clean Architecture

Este guia detalha a estrutura de código, dependências e padrões arquiteturais do backend Go, orientados pelas skills `golang-backend-architecture`, `golang-idiomatic-core` e `golang-api-docs`.

---

## 1. Inicialização do Módulo Go

```bash
mkdir -p backend && cd backend
go mod init <repo-name>/backend

# Dependências centrais
go get github.com/gin-gonic/gin
go get github.com/gin-contrib/cors
go get github.com/jackc/pgx/v5/pgxpool
go get github.com/jackc/pgx/v5
go get github.com/golang-jwt/jwt/v5
go get golang.org/x/crypto/bcrypt
go get github.com/google/uuid

# Documentação Swagger
go get github.com/swaggo/swag/cmd/swag
go get github.com/swaggo/gin-swagger
go get github.com/swaggo/files
```

---

## 2. Layout Clean Architecture

```text
backend/
├── cmd/api/main.go               # Ponto de entrada (Gin setup, rotas, graceful shutdown)
├── internal/
│   ├── config/config.go          # Configuração 12-factor via os.Getenv
│   ├── domain/                   # Entidades puras, DTOs e erros sentinela
│   │   ├── user.go
│   │   ├── organization.go
│   │   └── errors.go
│   ├── repository/               # Interfaces de persistência
│   │   ├── user_repository.go
│   │   └── postgres/             # Implementações com pgxpool
│   │       ├── db.go
│   │       └── user_repository.go
│   ├── service/                  # Regras de negócio puras
│   │   ├── auth_service.go
│   │   └── notification_service.go
│   ├── handler/                  # HTTP controllers (JSON bind/render)
│   │   ├── auth_handler.go
│   │   └── health_handler.go
│   ├── middleware/               # Auth JWT, TenantContext, Logger
│   │   ├── auth_middleware.go
│   │   └── tenant_middleware.go
│   └── worker/                   # Concorrência e tarefas assíncronas
│       └── worker_pool.go
└── docs/                         # Especificação OpenAPI gerada pelo swag
```

---

## 3. Conexão Otimizada com `pgxpool` (`internal/repository/postgres/db.go`)

```go
package postgres

import (
    "context"
    "fmt"
    "time"
    "github.com/jackc/pgx/v5/pgxpool"
)

func NewPool(ctx context.Context, databaseURL string) (*pgxpool.Pool, error) {
    config, err := pgxpool.ParseConfig(databaseURL)
    if err != nil {
        return nil, fmt.Errorf("parsing db config: %w", err)
    }

    config.MaxConns = 25
    config.MinConns = 5
    config.MaxConnLifetime = 1 * time.Hour
    config.MaxConnIdleTime = 15 * time.Minute

    pool, err := pgxpool.NewWithConfig(ctx, config)
    if err != nil {
        return nil, fmt.Errorf("creating connection pool: %w", err)
    }

    if err := pool.Ping(ctx); err != nil {
        return nil, fmt.Errorf("pinging database: %w", err)
    }

    return pool, nil
}
```

---

## 4. Middleware de Autenticação JWT (`internal/middleware/auth_middleware.go`)

```go
package middleware

import (
    "context"
    "net/http"
    "strings"
    "github.com/gin-gonic/gin"
    "github.com/golang-jwt/jwt/v5"
    "github.com/google/uuid"
)

type contextKey string
const UserIDKey contextKey = "user_id"

func AuthMiddleware(jwtSecret string) gin.HandlerFunc {
    return func(c *gin.Context) {
        authHeader := c.GetHeader("Authorization")
        if authHeader == "" || !strings.HasPrefix(authHeader, "Bearer ") {
            c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "missing or invalid authorization header"})
            return
        }

        tokenString := strings.TrimPrefix(authHeader, "Bearer ")
        token, err := jwt.Parse(tokenString, func(t *jwt.Token) (interface{}, error) {
            return []byte(jwtSecret), nil
        })

        if err != nil || !token.Valid {
            c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "invalid or expired token"})
            return
        }

        claims, ok := token.Claims.(jwt.MapClaims)
        if !ok {
            c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "invalid token claims"})
            return
        }

        userIDStr, _ := claims["sub"].(string)
        userID, _ := uuid.Parse(userIDStr)

        c.Set(string(UserIDKey), userID)
        c.Request = c.Request.WithContext(context.WithValue(c.Request.Context(), UserIDKey, userID))
        c.Next()
    }
}
```

---

## 5. Swagger e Documentação da API (`golang-api-docs`)

No topo de `cmd/api/main.go`:
```go
// @title           r7-referido REST API
// @version         1.0
// @description     SaaS High-Performance Backend API in Go.
// @host            localhost:8014
// @BasePath        /api/v1
// @schemes         http https
// @securityDefinitions.apikey Bearer
// @in header
// @name Authorization
```

Para gerar os arquivos OpenAPI:
```bash
swag init -g cmd/api/main.go -o ./docs
```

Registro no router Gin:
```go
import (
    _ "r7-referido/backend/docs"
    swaggerFiles "github.com/swaggo/files"
    ginSwagger "github.com/swaggo/gin-swagger"
)

r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))
```
