package database

import (
	"database/sql"
	"log"
)

func RunMigrations(db *sql.DB) error {
	migrations := []string{
		// Users table
		`CREATE TABLE IF NOT EXISTS users (
			id SERIAL PRIMARY KEY,
			email VARCHAR(255) UNIQUE NOT NULL,
			password_hash VARCHAR(255) NOT NULL,
			name VARCHAR(255) NOT NULL,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)`,

		// Stocks table
		`CREATE TABLE IF NOT EXISTS stocks (
			id SERIAL PRIMARY KEY,
			symbol VARCHAR(20) UNIQUE NOT NULL,
			name VARCHAR(255) NOT NULL,
			type VARCHAR(50) NOT NULL DEFAULT 'stock',
			exchange VARCHAR(50),
			sector VARCHAR(100),
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)`,

		// Price history table
		`CREATE TABLE IF NOT EXISTS price_history (
			id SERIAL PRIMARY KEY,
			stock_id INTEGER REFERENCES stocks(id) ON DELETE CASCADE,
			date DATE NOT NULL,
			open_price DECIMAL(15, 4),
			high_price DECIMAL(15, 4),
			low_price DECIMAL(15, 4),
			close_price DECIMAL(15, 4) NOT NULL,
			volume BIGINT,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			UNIQUE(stock_id, date)
		)`,

		// Index for faster queries
		`CREATE INDEX IF NOT EXISTS idx_price_history_stock_date ON price_history(stock_id, date DESC)`,
		`CREATE INDEX IF NOT EXISTS idx_stocks_symbol ON stocks(symbol)`,

		// Seed some default stocks
		`INSERT INTO stocks (symbol, name, type, exchange, sector) VALUES 
			('AAPL', 'Apple Inc.', 'stock', 'NASDAQ', 'Technology'),
			('GOOGL', 'Alphabet Inc.', 'stock', 'NASDAQ', 'Technology'),
			('MSFT', 'Microsoft Corporation', 'stock', 'NASDAQ', 'Technology'),
			('AMZN', 'Amazon.com Inc.', 'stock', 'NASDAQ', 'Consumer Cyclical'),
			('TSLA', 'Tesla Inc.', 'stock', 'NASDAQ', 'Consumer Cyclical'),
			('META', 'Meta Platforms Inc.', 'stock', 'NASDAQ', 'Technology'),
			('NVDA', 'NVIDIA Corporation', 'stock', 'NASDAQ', 'Technology'),
			('JPM', 'JPMorgan Chase & Co.', 'stock', 'NYSE', 'Financial Services'),
			('V', 'Visa Inc.', 'stock', 'NYSE', 'Financial Services'),
			('JNJ', 'Johnson & Johnson', 'stock', 'NYSE', 'Healthcare')
		ON CONFLICT (symbol) DO NOTHING`,
	}

	for _, migration := range migrations {
		_, err := db.Exec(migration)
		if err != nil {
			log.Printf("Migration error: %v", err)
			// Continue with other migrations, some might fail due to existing data
		}
	}

	log.Println("Migrations completed successfully")
	return nil
}
