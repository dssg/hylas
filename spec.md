Getting top features
====================
* HTTP Method: GET
* resource: /top_features
* arguments:
    * n: Number of top features to return (default 10)
* returns: JSON list of strings of top n features
* example:
    
    /top_features?n=3
    
    serves
    
    {"data":["most_important_feature","also_important","less_important"]}
    
Getting data
============
* HTTP method: GET
* resource /top_units
* arguments:
    * n: Number of units (rows) to return (default 10)
    * cols: List of columns to return. 
      (default row_num,pred_proba)
      Should be a list of unquoted column names separated by
      commas.
      In addition to the columns actually appearing in the 
      table, the server should provide two special columns:
        * row_num: The number of the row
        * pred_proba: The probability that a given unit is in
          the requested category.
    * category: Category we are interested in predicting.
      (default 1)
      For example, if we do a binary classification, sklearn
      gives us a certain probability that a unit is in category
      0 and a certain probability that a unit is in category 1.
      The probability of being in the given category is both:
        1. The number returned in the pred_proba column
        2. The way by which we rank our top n rows
      Incidentally, the category corresponds to the column
      in the return value of Python's clf.pred_proba(...)
* returns: JSON dictionary of lists of numbers. Each key in
  the dictionary is a column name. The values are the values
  in the column.
* example:
    
    /top_units?n=2&cols=row_num,most_important_feature,pred_proba&category=1
    
    serves:
    
    {"data":{"row_num":[5,3],"most_important_feature":[1.2,1.5],"pred_proba":[0.97,0.96]}} 
