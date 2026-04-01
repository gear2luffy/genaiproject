package models

import "time"

type User struct {
	ID           int       `json:"id"`
	Email        string    `json:"email"`
	PasswordHash string    `json:"-"`
	Name         string    `json:"name"`
	CreatedAt    time.Time `json:"created_at"`
	UpdatedAt    time.Time `json:"updated_at"`
}

type Stock struct {
	ID        int       `json:"id"`
	Symbol    string    `json:"symbol"`
	Name      string    `json:"name"`
	Type      string    `json:"type"`
	Exchange  string    `json:"exchange"`
	Sector    string    `json:"sector"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

type PriceHistory struct {
	ID         int       `json:"id"`
	StockID    int       `json:"stock_id"`
	Date       time.Time `json:"date"`
	OpenPrice  float64   `json:"open_price"`
	HighPrice  float64   `json:"high_price"`
	LowPrice   float64   `json:"low_price"`
	ClosePrice float64   `json:"close_price"`
	Volume     int64     `json:"volume"`
	CreatedAt  time.Time `json:"created_at"`
}

type LoginRequest struct {
	Email    string `json:"email" binding:"required,email"`
	Password string `json:"password" binding:"required,min=6"`
}

type RegisterRequest struct {
	Email    string `json:"email" binding:"required,email"`
	Password string `json:"password" binding:"required,min=6"`
	Name     string `json:"name" binding:"required"`
}

type AuthResponse struct {
	Token string `json:"token"`
	User  User   `json:"user"`
}

type StockWithPrice struct {
	Stock
	CurrentPrice   float64 `json:"current_price"`
	PriceChange    float64 `json:"price_change"`
	ChangePercent  float64 `json:"change_percent"`
}

type DashboardSummary struct {
	TrendingStocks []StockWithPrice `json:"trending_stocks"`
	TopGainers     []StockWithPrice `json:"top_gainers"`
	TopLosers      []StockWithPrice `json:"top_losers"`
}

type PriceResponse struct {
	Symbol string         `json:"symbol"`
	Name   string         `json:"name"`
	Prices []PriceHistory `json:"prices"`
}
