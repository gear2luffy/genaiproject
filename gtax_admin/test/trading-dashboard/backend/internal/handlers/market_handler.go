package handlers

import (
	"net/http"
	"strconv"

	"trading-dashboard/internal/services"

	"github.com/gin-gonic/gin"
)

type MarketHandler struct {
	marketService *services.MarketService
}

func NewMarketHandler(marketService *services.MarketService) *MarketHandler {
	return &MarketHandler{marketService: marketService}
}

func (h *MarketHandler) SearchStocks(c *gin.Context) {
	query := c.Query("q")

	stocks, err := h.marketService.SearchStocks(query)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, stocks)
}

func (h *MarketHandler) GetStock(c *gin.Context) {
	symbol := c.Param("symbol")

	stock, err := h.marketService.GetStock(symbol)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Stock not found"})
		return
	}

	c.JSON(http.StatusOK, stock)
}

func (h *MarketHandler) GetPrices(c *gin.Context) {
	symbol := c.Param("symbol")
	daysStr := c.DefaultQuery("days", "30")

	days, err := strconv.Atoi(daysStr)
	if err != nil || days < 1 {
		days = 30
	}

	prices, err := h.marketService.GetPrices(symbol, days)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Stock not found"})
		return
	}

	c.JSON(http.StatusOK, prices)
}

func (h *MarketHandler) GetDailyPrices(c *gin.Context) {
	symbol := c.Param("symbol")

	prices, err := h.marketService.GetPrices(symbol, 1)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Stock not found"})
		return
	}

	c.JSON(http.StatusOK, prices)
}

func (h *MarketHandler) GetDashboardSummary(c *gin.Context) {
	summary, err := h.marketService.GetDashboardSummary()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, summary)
}
