package scraper

import (
	"github.com/LanNetwork/centrol/internal/article"
)

// Scraper struct
type Scraper struct {
	siteURL string
}

// Scraper constructor. Returns addresss of Scraper with a url.
func NewScraper(siteURL string) *Scraper {
	return &Scraper{siteURL}
}

func (s *Scraper) ScrapeHTMLonly([]article.HTMLonlArticle, error) {

}
