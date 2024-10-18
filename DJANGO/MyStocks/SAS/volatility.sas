%macro calculate_volatility(dataset, window);
	PROC EXPAND DATA=&dataset OUT=&dataset._volatility METHOD=none;
		CONVERT Close=Volatility / TRANSFORMOUT=(MOVSTD &window);
	RUN;

	PROC PRINT DATA=&dataset._volatility;
		TITLE "Volatility of Stock Price for &dataset (Window: &window Days)";
		VAR Date Close Volatility;
	RUN;

%mend calculate_volatility;