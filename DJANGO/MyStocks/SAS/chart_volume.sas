%macro generate_volume_chart(dataset);
	/* Check if the dataset parameter is provided */
    %if &dataset=%then
		%do;
			%put ERROR: Dataset parameter is missing.;
			%return;
		%end;

	/* Set a dynamic title for the chart */
	title "Average Volume for Stock: &dataset";

	PROC CHART DATA=&dataset;
		/* Create a horizontal bar chart to show the Average Volume for the stock dataset */
		HBAR DATE / SUMVAR=Volume TYPE=MEAN;
	RUN;

	/* Clear the title after the procedure */
	title;
%mend generate_volume_chart;