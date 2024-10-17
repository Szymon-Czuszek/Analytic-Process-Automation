%macro import_stock_data(username, filename);
	/* Define the prefix */
    %let prefix = automatedsas-;

	/* Check if the filename starts with the prefix */
    
	%if %index(%upcase(&filename), %upcase(&prefix))=1 %then
		%do;

			/* Remove prefix and the last 11 characters for the dataset name */
        %let dataset_name = %substr(&filename, %length(&prefix) + 1, 
				%eval(%length(&filename) - %length(&prefix) - 11));
		%end;
	%else
		%do;

			/* Remove the last 11 characters for the dataset name */
        %let dataset_name = %substr(&filename, 1, 
				%eval(%length(&filename) - 11));
		%end;

	/* Load the dataset from the appropriate file */
	DATA &dataset_name;
		INFILE "/home/&username./Stock Data/&filename..csv" DSD MISSOVER FIRSTOBS=2;
		INPUT Date : yymmdd10. Open High Low Close AdjClose Volume;
		FORMAT Date yymmdd10.;
	RUN;

%mend import_stock_data;