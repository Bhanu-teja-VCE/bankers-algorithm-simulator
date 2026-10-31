Complex Engineering Problem - Deadlock Avoidance Using the Banker's Algorithm
A9510 Operating System Laboratory, VCE Hyderabad

Build the report :  pdflatex report.tex   (run twice for the table of contents)
Run the simulator:  cd code && python3 bankers.py ../data/textbook.txt
                    python3 bankers.py ../data/textbook.txt --batch ../data/requests.txt
Run unit tests   :  cd code && python3 test_bankers.py -v
Re-run experiments: cd code && python3 experiments.py ../data && cd .. && python3 code/make_figs.py
