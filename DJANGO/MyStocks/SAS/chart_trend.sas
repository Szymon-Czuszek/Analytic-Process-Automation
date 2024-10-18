%macro plot_stock_trend(dataset);
	PROC SGPLOT DATA=&dataset;
		TITLE "Stock Price Trend for &dataset";
		SERIES X=Date Y=Open / LINEATTRS=(COLOR=blue) LEGENDLABEL="Open";
		SERIES X=Date Y=High / LINEATTRS=(COLOR=green) LEGENDLABEL="High";
		SERIES X=Date Y=Low / LINEATTRS=(COLOR=red) LEGENDLABEL="Low";
		SERIES X=Date Y=Close / LINEATTRS=(COLOR=black) LEGENDLABEL="Close";
		XAXIS LABEL="Date";
		YAXIS LABEL="Price";
	RUN;

%mend plot_stock_trend;