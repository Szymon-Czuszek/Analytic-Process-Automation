%macro moving_average(dataset, window);
	DATA &dataset._moving_avg;
		SET &dataset;
		MA_Close=MEAN(LAG1(Close), LAG2(Close), LAG3(Close), LAG4(Close), 
			LAG5(Close));
		FORMAT MA_Close 8.2;
	RUN;

	PROC PRINT DATA=&dataset._moving_avg;
		TITLE "Stock Prices with &window-Day Moving Average for &dataset";
		VAR Date Close MA_Close;
	RUN;

%mend moving_average;