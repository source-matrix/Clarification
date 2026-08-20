package clarification

import "testing"

func TestEnhanceRequiresArguments(t *testing.T) {
	if err := Enhance("", "input.png", "output.png", DefaultOptions()); err == nil {
		t.Fatal("expected missing binary error")
	}
	if err := Enhance("clarification", "", "output.png", DefaultOptions()); err == nil {
		t.Fatal("expected missing input error")
	}
}

func TestDefaultOptions(t *testing.T) {
	options := DefaultOptions()
	if options.Radius != 1.2 || options.Amount != 1.35 || options.Contrast != 8.0 || options.Threshold != 2 {
		t.Fatalf("unexpected defaults: %+v", options)
	}
}
