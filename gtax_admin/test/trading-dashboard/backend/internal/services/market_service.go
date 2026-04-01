package services

import (
	"encoding/json"
	"fmt"
	"log"
	"math"
	"math/rand"
	"net/http"
	"os"
	"sort"
	"time"

	"trading-dashboard/internal/models"
	"trading-dashboard/internal/repository"
)

type MarketService struct {
	stockRepo *repository.StockRepository
	priceRepo *repository.PriceRepository
}

func NewMarketService(stockRepo *repository.StockRepository, priceRepo *repository.PriceRepository) *MarketService {
	return &MarketService{
		stockRepo: stockRepo,
		priceRepo: priceRepo,
	}
}

// Alpha Vantage API response structures
type AlphaVantageResponse struct {
	MetaData   map[string]string         `json:"Meta Data"`
	TimeSeries map[string]TimeSeriesData `json:"Time Series (Daily)"`
}

type TimeSeriesData struct {
	Open   string `json:"1. open"`
	High   string `json:"2. high"`
	Low    string `json:"3. low"`
	Close  string `json:"4. close"`
	Volume string `json:"5. volume"`
}

func (s *MarketService) StartDataFetcher() {
	// Initial data fetch
	s.fetchAndStoreMarketData()

	// Set up periodic fetching every 6 hours
	ticker := time.NewTicker(6 * time.Hour)
	for range ticker.C {
		s.fetchAndStoreMarketData()
	}
}

func (s *MarketService) fetchAndStoreMarketData() {
	log.Println("Starting market data fetch...")

	stocks, err := s.stockRepo.GetAll()
	if err != nil {
		log.Printf("Error fetching stocks: %v", err)
		return
	}

	apiKey := os.Getenv("ALPHA_VANTAGE_API_KEY")

	for _, stock := range stocks {
		if apiKey != "" {
			// Try to fetch real data from Alpha Vantage
			if err := s.fetchFromAlphaVantage(stock, apiKey); err != nil {
				log.Printf("Error fetching data for %s from Alpha Vantage: %v, using simulated data", stock.Symbol, err)
				s.generateSimulatedData(stock)
			}
		} else {
			// Use simulated data if no API key
			s.generateSimulatedData(stock)
		}

		// Rate limiting - Alpha Vantage free tier has 5 calls/minute limit
		time.Sleep(15 * time.Second)
	}

	log.Println("Market data fetch completed")
}

func (s *MarketService) fetchFromAlphaVantage(stock models.Stock, apiKey string) error {
	url := fmt.Sprintf("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=%s&apikey=%s&outputsize=compact", stock.Symbol, apiKey)

	resp, err := http.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	var data AlphaVantageResponse
	if err := json.NewDecoder(resp.Body).Decode(&data); err != nil {
		return err
	}

	if data.TimeSeries == nil {
		return fmt.Errorf("no time series data returned")
	}

	for dateStr, prices := range data.TimeSeries {
		date, err := time.Parse("2006-01-02", dateStr)
		if err != nil {
			continue
		}

		price := &models.PriceHistory{
			StockID:    stock.ID,
			Date:       date,
			OpenPrice:  parseFloat(prices.Open),
			HighPrice:  parseFloat(prices.High),
			LowPrice:   parseFloat(prices.Low),
			ClosePrice: parseFloat(prices.Close),
			Volume:     parseInt(prices.Volume),
		}

		if err := s.priceRepo.Create(price); err != nil {
			log.Printf("Error storing price for %s on %s: %v", stock.Symbol, dateStr, err)
		}
	}

	return nil
}

func (s *MarketService) generateSimulatedData(stock models.Stock) {
	// Generate 60 days of simulated historical data
	basePrice := getBasePrice(stock.Symbol)
	volatility := 0.02 // 2% daily volatility

	endDate := time.Now()
	currentPrice := basePrice

	for i := 60; i >= 0; i-- {
		date := endDate.AddDate(0, 0, -i)

		// Skip weekends
		if date.Weekday() == time.Saturday || date.Weekday() == time.Sunday {
			continue
		}

		// Simulate price movement
		change := (rand.Float64()*2 - 1) * volatility * currentPrice
		currentPrice += change

		// Ensure price doesn't go negative
		if currentPrice < 1 {
			currentPrice = basePrice * 0.5
		}

		openPrice := currentPrice * (1 + (rand.Float64()*2-1)*0.01)
		highPrice := math.Max(openPrice, currentPrice) * (1 + rand.Float64()*0.02)
		lowPrice := math.Min(openPrice, currentPrice) * (1 - rand.Float64()*0.02)

		price := &models.PriceHistory{
			StockID:    stock.ID,
			Date:       date,
			OpenPrice:  roundTo2(openPrice),
			HighPrice:  roundTo2(highPrice),
			LowPrice:   roundTo2(lowPrice),
			ClosePrice: roundTo2(currentPrice),
			Volume:     int64(rand.Intn(50000000) + 1000000),
		}

		if err := s.priceRepo.Create(price); err != nil {
			// Ignore duplicate errors
			continue
		}
	}

	log.Printf("Generated simulated data for %s", stock.Symbol)
}

func getBasePrice(symbol string) float64 {
	prices := map[string]float64{
		"AAPL":  175.0,
		"GOOGL": 140.0,
		"MSFT":  380.0,
		"AMZN":  180.0,
		"TSLA":  245.0,
		"META":  500.0,
		"NVDA":  880.0,
		"JPM":   195.0,
		"V":     280.0,
		"JNJ":   155.0,
	}
	if price, ok := prices[symbol]; ok {
		return price
	}
	return 100.0
}

func (s *MarketService) SearchStocks(query string) ([]models.Stock, error) {
	if query == "" {
		return s.stockRepo.GetAll()
	}
	return s.stockRepo.Search(query)
}

func (s *MarketService) GetStock(symbol string) (*models.Stock, error) {
	return s.stockRepo.GetBySymbol(symbol)
}

func (s *MarketService) GetPrices(symbol string, days int) (*models.PriceResponse, error) {
	stock, err := s.stockRepo.GetBySymbol(symbol)
	if err != nil {
		return nil, err
	}

	prices, err := s.priceRepo.GetDailyPrices(stock.ID, days)
	if err != nil {
		return nil, err
	}

	return &models.PriceResponse{
		Symbol: stock.Symbol,
		Name:   stock.Name,
		Prices: prices,
	}, nil
}

func (s *MarketService) GetDailyPrices(symbol string) (*models.PriceResponse, error) {
	return s.GetPrices(symbol, 1)
}

func (s *MarketService) GetDashboardSummary() (*models.DashboardSummary, error) {
	stocks, err := s.stockRepo.GetAll()
	if err != nil {
		return nil, err
	}

	var stocksWithPrice []models.StockWithPrice

	for _, stock := range stocks {
		latestPrice, err := s.priceRepo.GetLatestPrice(stock.ID)
		if err != nil {
			continue
		}

		prevPrice, err := s.priceRepo.GetPreviousPrice(stock.ID, latestPrice.Date)
		if err != nil {
			// If no previous price, use current price
			prevPrice = latestPrice
		}

		priceChange := latestPrice.ClosePrice - prevPrice.ClosePrice
		changePercent := 0.0
		if prevPrice.ClosePrice > 0 {
			changePercent = (priceChange / prevPrice.ClosePrice) * 100
		}

		stocksWithPrice = append(stocksWithPrice, models.StockWithPrice{
			Stock:         stock,
			CurrentPrice:  roundTo2(latestPrice.ClosePrice),
			PriceChange:   roundTo2(priceChange),
			ChangePercent: roundTo2(changePercent),
		})
	}

	// Sort by change percent for gainers and losers
	gainers := make([]models.StockWithPrice, len(stocksWithPrice))
	copy(gainers, stocksWithPrice)
	sort.Slice(gainers, func(i, j int) bool {
		return gainers[i].ChangePercent > gainers[j].ChangePercent
	})

	losers := make([]models.StockWithPrice, len(stocksWithPrice))
	copy(losers, stocksWithPrice)
	sort.Slice(losers, func(i, j int) bool {
		return losers[i].ChangePercent < losers[j].ChangePercent
	})

	// Get top 5 for each category
	topGainers := gainers
	if len(topGainers) > 5 {
		topGainers = topGainers[:5]
	}

	topLosers := losers
	if len(topLosers) > 5 {
		topLosers = topLosers[:5]
	}

	return &models.DashboardSummary{
		TrendingStocks: stocksWithPrice,
		TopGainers:     topGainers,
		TopLosers:      topLosers,
	}, nil
}

func parseFloat(s string) float64 {
	var f float64
	fmt.Sscanf(s, "%f", &f)
	return f
}

func parseInt(s string) int64 {
	var i int64
	fmt.Sscanf(s, "%d", &i)
	return i
}

func roundTo2(f float64) float64 {
	return math.Round(f*100) / 100
}
