package repository

import (
	"database/sql"
	"time"
	"trading-dashboard/internal/models"
)

type PriceRepository struct {
	db *sql.DB
}

func NewPriceRepository(db *sql.DB) *PriceRepository {
	return &PriceRepository{db: db}
}

func (r *PriceRepository) Create(price *models.PriceHistory) error {
	query := `INSERT INTO price_history (stock_id, date, open_price, high_price, low_price, close_price, volume) 
		VALUES ($1, $2, $3, $4, $5, $6, $7) 
		ON CONFLICT (stock_id, date) DO UPDATE SET 
			open_price = EXCLUDED.open_price,
			high_price = EXCLUDED.high_price,
			low_price = EXCLUDED.low_price,
			close_price = EXCLUDED.close_price,
			volume = EXCLUDED.volume
		RETURNING id, created_at`
	return r.db.QueryRow(query, price.StockID, price.Date, price.OpenPrice, price.HighPrice, price.LowPrice, price.ClosePrice, price.Volume).
		Scan(&price.ID, &price.CreatedAt)
}

func (r *PriceRepository) GetByStockIDAndDateRange(stockID int, startDate, endDate time.Time) ([]models.PriceHistory, error) {
	query := `SELECT id, stock_id, date, COALESCE(open_price, 0), COALESCE(high_price, 0), COALESCE(low_price, 0), close_price, COALESCE(volume, 0), created_at
		FROM price_history WHERE stock_id = $1 AND date >= $2 AND date <= $3 ORDER BY date ASC`
	rows, err := r.db.Query(query, stockID, startDate, endDate)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var prices []models.PriceHistory
	for rows.Next() {
		var price models.PriceHistory
		if err := rows.Scan(&price.ID, &price.StockID, &price.Date, &price.OpenPrice, &price.HighPrice, &price.LowPrice, &price.ClosePrice, &price.Volume, &price.CreatedAt); err != nil {
			return nil, err
		}
		prices = append(prices, price)
	}
	return prices, nil
}

func (r *PriceRepository) GetLatestPrice(stockID int) (*models.PriceHistory, error) {
	price := &models.PriceHistory{}
	query := `SELECT id, stock_id, date, COALESCE(open_price, 0), COALESCE(high_price, 0), COALESCE(low_price, 0), close_price, COALESCE(volume, 0), created_at
		FROM price_history WHERE stock_id = $1 ORDER BY date DESC LIMIT 1`
	err := r.db.QueryRow(query, stockID).Scan(&price.ID, &price.StockID, &price.Date, &price.OpenPrice, &price.HighPrice, &price.LowPrice, &price.ClosePrice, &price.Volume, &price.CreatedAt)
	if err != nil {
		return nil, err
	}
	return price, nil
}

func (r *PriceRepository) GetPreviousPrice(stockID int, date time.Time) (*models.PriceHistory, error) {
	price := &models.PriceHistory{}
	query := `SELECT id, stock_id, date, COALESCE(open_price, 0), COALESCE(high_price, 0), COALESCE(low_price, 0), close_price, COALESCE(volume, 0), created_at
		FROM price_history WHERE stock_id = $1 AND date < $2 ORDER BY date DESC LIMIT 1`
	err := r.db.QueryRow(query, stockID, date).Scan(&price.ID, &price.StockID, &price.Date, &price.OpenPrice, &price.HighPrice, &price.LowPrice, &price.ClosePrice, &price.Volume, &price.CreatedAt)
	if err != nil {
		return nil, err
	}
	return price, nil
}

func (r *PriceRepository) GetLast30DaysPrices(stockID int) ([]models.PriceHistory, error) {
	endDate := time.Now()
	startDate := endDate.AddDate(0, 0, -30)
	return r.GetByStockIDAndDateRange(stockID, startDate, endDate)
}

func (r *PriceRepository) GetDailyPrices(stockID int, days int) ([]models.PriceHistory, error) {
	query := `SELECT id, stock_id, date, COALESCE(open_price, 0), COALESCE(high_price, 0), COALESCE(low_price, 0), close_price, COALESCE(volume, 0), created_at
		FROM price_history WHERE stock_id = $1 ORDER BY date DESC LIMIT $2`
	rows, err := r.db.Query(query, stockID, days)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var prices []models.PriceHistory
	for rows.Next() {
		var price models.PriceHistory
		if err := rows.Scan(&price.ID, &price.StockID, &price.Date, &price.OpenPrice, &price.HighPrice, &price.LowPrice, &price.ClosePrice, &price.Volume, &price.CreatedAt); err != nil {
			return nil, err
		}
		prices = append(prices, price)
	}

	// Reverse to get chronological order
	for i, j := 0, len(prices)-1; i < j; i, j = i+1, j-1 {
		prices[i], prices[j] = prices[j], prices[i]
	}

	return prices, nil
}
