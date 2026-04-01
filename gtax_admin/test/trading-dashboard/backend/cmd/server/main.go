package main

import (
	"log"
	"os"

	"trading-dashboard/internal/database"
	"trading-dashboard/internal/handlers"
	"trading-dashboard/internal/middleware"
	"trading-dashboard/internal/repository"
	"trading-dashboard/internal/services"

	"github.com/gin-gonic/gin"
)

func main() {
	// Initialize database
	db, err := database.Connect()
	if err != nil {
		log.Fatal("Failed to connect to database:", err)
	}
	defer db.Close()

	// Run migrations
	if err := database.RunMigrations(db); err != nil {
		log.Fatal("Failed to run migrations:", err)
	}

	// Initialize repositories
	userRepo := repository.NewUserRepository(db)
	stockRepo := repository.NewStockRepository(db)
	priceRepo := repository.NewPriceRepository(db)

	// Initialize services
	authService := services.NewAuthService(userRepo)
	marketService := services.NewMarketService(stockRepo, priceRepo)

	// Start market data fetcher in background
	go marketService.StartDataFetcher()

	// Initialize handlers
	authHandler := handlers.NewAuthHandler(authService)
	marketHandler := handlers.NewMarketHandler(marketService)

	// Setup router
	router := gin.Default()

	// CORS middleware
	router.Use(middleware.CORSMiddleware())

	// Public routes
	api := router.Group("/api")
	{
		api.POST("/register", authHandler.Register)
		api.POST("/login", authHandler.Login)

		// Protected routes
		protected := api.Group("")
		protected.Use(middleware.AuthMiddleware())
		{
			protected.GET("/user", authHandler.GetCurrentUser)
			protected.GET("/stocks/search", marketHandler.SearchStocks)
			protected.GET("/stocks/:symbol", marketHandler.GetStock)
			protected.GET("/stocks/:symbol/prices", marketHandler.GetPrices)
			protected.GET("/stocks/:symbol/prices/daily", marketHandler.GetDailyPrices)
			protected.GET("/dashboard/summary", marketHandler.GetDashboardSummary)
		}
	}

	// Health check
	router.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "healthy"})
	})

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("Server starting on port %s", port)
	if err := router.Run(":" + port); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}
