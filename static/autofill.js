$( function() {
	$("#searchbar").autocomplete({
		delay: 500,
		minLength: 3,
		source: "/getSuggestions"
	});
});
