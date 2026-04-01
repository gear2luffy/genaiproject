package repository

import (
	"database/sql"
	"trading-dashboard/internal/models"
)

type StockRepository struct {
	db *sql.DB
}

func NewStockRepository(db *sql.DB) *StockRepository {
	return &StockRepository{db: db}
}

func (r *StockRepository) GetAll() ([]models.Stock, error) {
	query := `SELECT id, symbol, name, type, COALESCE(exchange, ''), COALESCE(sector, ''), created_at, updated_at FROM stocks ORDER BY symbol`
	rows, err := r.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var stocks []models.Stock
	for rows.Next() {
		var stock models.Stock
		if err := rows.Scan(&stock.ID, &stock.Symbol, &stock.Name, &stock.Type, &stock.Exchange, &stock.Sector, &stock.CreatedAt, &stock.UpdatedAt); err != nil {
			return nil, err
		}
		stocks = append(stocks, stock)
	}
	return stocks, nil
}

func (r *StockRepository) GetBySymbol(symbol string) (*models.Stock, error) {
	stock := &models.Stock{}
	query := `SELECT id, symbol, name, type, COALESCE(exchange, ''), COALESCE(sector, ''), created_at, updated_at FROM stocks WHERE symbol = $1`
	err := r.db.QueryRow(query, symbol).Scan(&stock.ID, &stock.Symbol, &stock.Name, &stock.Type, &stock.Exchange, &stock.Sector, &stock.CreatedAt, &stock.UpdatedAt)
	if err != nil {
		return nil, err
	}
	return stock, nil
}

func (r *StockRepository) Search(query string) ([]models.Stock, error) {
	searchQuery := `SELECT id, symbol, name, type, COALESCE(exchange, ''), COALESCE(sector, ''), created_at, updated_at 
		FROM stocks WHERE LOWER(symbol) LIKE LOWER($1) OR LOWER(name) LIKE LOWER($1) ORDER BY symbol LIMIT 20`
	rows, err := r.db.Query(searchQuery, "%"+query+"%")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var stocks []models.Stock
	for rows.Next() {
		var stock models.Stock
		if err := rows.Scan(&stock.ID, &stock.Symbol, &stock.Name, &stock.Type, &stock.Exchange, &stock.Sector, &stock.CreatedAt, &stock.UpdatedAt); err != nil {
			return nil, err
		}
		stocks = append(stocks, stock)
	}
	return stocks, nil
}

func (r *StockRepository) Create(stock *models.Stock) error {
	query := `INSERT INTO stocks (symbol, name, type, exchange, sector) VALUES ($1, $2, $3, $4, $5) 
		ON CONFLICT (symbol) DO UPDATE SET name = EXCLUDED.name, updated_at = CURRENT_TIMESTAMP
		RETURNING id, created_at, updated_at`
	return r.db.QueryRow(query, stock.Symbol, stock.Name, stock.Type, stock.Exchange, stock.Sector).
		Scan(&stock.ID, &stock.CreatedAt, &stock.UpdatedAt)
}

func (r *StockRepository) GetByID(id int) (*models.Stock, error) {
	stock := &models.Stock{}
	query := `SELECT id, symbol, name, type, COALESCE(exchange, ''), COALESCE(sector, ''), created_at, updated_at FROM stocks WHERE id = $1`
	err := r.db.QueryRow(query, id).Scan(&stock.ID, &stock.Symbol, &stock.Name, &stock.Type, &stock.Exchange, &stock.Sector, &stock.CreatedAt, &stock.UpdatedAt)
	if err != nil {
		return nil, err
	}
	return stock, nil
}
