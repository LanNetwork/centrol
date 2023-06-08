package main

import (
	"encoding/json"
	"encoding/xml"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"

	"github.com/LanNetwork/centrol/internal/article"
)

var RequestCount int

func main() {
	// Add handler functions
	http.Handle("/api/cnn", &HandlerAccess{url: "http://rss.cnn.com/rss/cnn_topstories.rss"})
	http.Handle("/api/simp", &HandlerAccess{url: "https://feeds.simplecast.com/54nAGcIl"})

	// Make channel for termination signals
	signalChan := make(chan os.Signal, 1)
	signal.Notify(signalChan, syscall.SIGINT, syscall.SIGTERM)

	// goroutines for termination signal & custom commands
	go terminationSignal(signalChan)
	go runtimeCommands(signalChan)
	port := ":8000"
	log.Println("Launched server. Waiting serving and listening on port ", port)
	log.Fatal(http.ListenAndServe(port, nil))
}

// function for custom commands during runtime
func runtimeCommands(signalChan chan os.Signal) {
	fmt.Println("type \"help\" for list of commands")
	for {
		var cmd string
		fmt.Scanln(&cmd)

		// List of the commands and their help entry. Must manually update if you add any.
		commandList := []string{"requests", "help", "exit"}
		commandHelpEntryList := []string{"returns number of GET requests recieved so far", "Displays this list", "Gracefully shuts down the program"}

		// Custom command go here.
		switch cmd {
		case "requests", "r":
			fmt.Println("Requests so far: ", RequestCount)
		case "help":
			for i := range commandList {
				fmt.Println(commandList[i], ": ", commandHelpEntryList[i])
			}
		case "exit":
			signalChan <- syscall.SIGINT // Send termination signal to trigger cleanup and exit in terminationSignal()
		default:
			fmt.Println("Invalid command")
		}
	}
}

// Function for handling termination signal runtime.
func terminationSignal(signalChan chan os.Signal) {
	// Wait for termination signal
	<-signalChan

	// Any cleanup should go here
	log.Println("Program terminated")
	os.Exit(0)
}

// This is an interface to encapsulate data that you want to serve.
type HandlerAccess struct {
	url string
}

// This method implements a specificHandler with some data and serves it to an http.ResponseWriter
func (handlerAccess *HandlerAccess) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	xmlData, err := retrieveRSS(handlerAccess.url)
	if err != nil {
		log.Println(err)
	}

	// We now have the response body in the form of a []byte named xmlData.
	// Use the xml.marshal function to turn it into our custom Go xml object
	var rssFeed article.RSSFeed
	err = xml.Unmarshal([]byte(xmlData), &rssFeed)
	if err != nil {
		log.Println(err)
		return
	}

	// Now we can convert our custom go object (rssFeed) into json using a custom function
	jsonData, err := xmlToJson(rssFeed)
	if err != nil {
		log.Println(err)
		return
	}
	requestingIP := ReadUserIP(r)
	log.Println("Served content to: ", requestingIP)
	w.Header().Set("Content-Type", "application/json")
	w.Write(jsonData)
	RequestCount++
}

// Converts string url, and assigns to byte array of the xml format rss retrieved. Returns byte array and error (nill if successful)
func retrieveRSS(url string) ([]byte, error) {
	// Send HTTP GET request
	resp, err := http.Get(url)

	if err != nil {
		// Handle error fetching data
		log.Println("Failed to fetch XML data: ", err)
		return nil, err
	}
	defer resp.Body.Close() // Close response body when done

	// Read response body
	xmlData, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		// Handle error reading response body
		log.Println("Failed to read response body:", err)
		return nil, err
	}
	return xmlData, nil
}

// Converts byte array of xml format rss into a byte array of json format rss. Returns byte array and error (nill if successful)
func xmlToJson(rssData article.RSSFeed) ([]byte, error) {
	// Marshal rssFeed object into json, for RESTful transmission.
	jsonData, err := json.Marshal(rssData)
	// Go encodes brackets and certain characters as \u codes. There is a way to disable this behavior, but I don't think that's needed.
	// Apparently \u codes are part of the standard JSON library for most things, so unless it's a problem later, don't worry about it.
	if err != nil {
		log.Println("Failed to marshal rssFeed object to JSON:", err)
		return nil, err
	}
	return jsonData, nil
}

func ReadUserIP(r *http.Request) string {
	IPAddress := r.Header.Get("X-Real-Ip")
	if IPAddress == "" {
		IPAddress = r.Header.Get("X-Forwarded-For")
	}
	if IPAddress == "" {
		IPAddress = r.RemoteAddr
	}
	return IPAddress
}
