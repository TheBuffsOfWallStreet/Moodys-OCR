Assuming you are in the research cluster with access to the proper Moody's files:

```
python3 extract_text.py "year"
```

This script will do the following:

- Parse directory containing Moody files for year that was given as an argument
- For all 99 iterations of brightness levels, sort and assemble words (sorting could be improved where column defenition is not clear)
- Find optimum iteration by seeing which brightness level had the most frequently occuring words across all 99 iterations
- Grab all ngrams of length greater than two that are all caps in the optimum iteration
- Throw out all ngrams that do not contain a company ending (could change to throw out ngrams that contain stop words)
- Either write to json or write to database (database version commented out)
