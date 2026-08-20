package main

import (
	"fmt"
	clarification "github.com/source-matrix/Clarification/bindings/go/clarification"
)

func main() {
	options := clarification.DefaultOptions()
	if err := clarification.Enhance("clarification", "input.png", "clarified.png", options); err != nil {
		panic(err)
	}
	score, err := clarification.Score("clarification", "clarified.png")
	if err != nil {
		panic(err)
	}
	fmt.Printf("clarified image score: %.4f\n", score)
}
