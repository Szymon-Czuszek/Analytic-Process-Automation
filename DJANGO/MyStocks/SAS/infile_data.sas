%macro import_stock_data(username, filename);
	/* Extract dataset name by removing the last 9 characters */
    %let dataset_name = %substr(&filename, 1, 
		%eval(%length(&filename) - 11));

	DATA &dataset_name;
		INFILE "/home/&username./Stock Data/&filename..csv" DSD MISSOVER FIRSTOBS=2;
		INPUT Date : yymmdd10. Open High Low Close AdjClose Volume;
		FORMAT Date yymmdd10.;

		/* Format the date for display */
	RUN;

%mend import_stock_data;

%import_stock_data(u63805106, CRWD-2024-01-01);