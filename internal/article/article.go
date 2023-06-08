package article

// Article that does not have Atom feed or RSS. Must scrape manually
type HTMLonlArticle struct {
	articleTitle string
	siteURL      string
}

type AtomArticle struct {
	articleTitle string
	siteURL      string
}

// This is a Go object for RSS 2.0. Some RSS feeds may use atom.
// https://feeds.simplecast.com/54nAGcIl for example, is a hybrid document that uses RSS 2.0, and atom.
// Atom elements in the document are labeled with "itunes: whateverfield", because itunes also uses atom 1.0
//
// Also, "media:whateverfield" is a different format. It's a namespace, might be called mrss...

// This Object also has metadata mappings for json, to allow for marshalling into json.
type RSSFeed struct {
	Channel Channel `xml:"channel"`
}

type Channel struct {
	Title string `xml:"title"`
	Link  string `xml:"link"`
	Item  []Item `xml:"item"`
}

type Item struct {
	Title string `xml:"title"`
	// xml Descriptions may be CDATA, which requires parsing out the ctext tag using xml.unmarshal()
	Description string `xml:"description"`
	// content:encoded isn't parsing at all. Why? I think it's just a limitation of Go... Namespaces and such.
	// ContentEncoded CDATA  `xml:"content\\:encoded"`
	PubDate string `xml:"pubDate"`
	Link    string `xml:"link"`
}
