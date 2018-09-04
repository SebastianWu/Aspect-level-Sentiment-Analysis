# Aspect-level Sentiment Analysis

## Author:  
Yuanxu Wu, Guanquan Dong, Xiaodan Wang

## Prerequisites  
1. python 3.6.3  

## What is inside this folder:  
1. fine_grained_sentiment_analysis.py is the python code to implement this algorithm, which will output a pickled file to store the trained data.  
2. score.py is the python code to generate the score of this algorithm.  
3. Aspect-level_Sentiment_Analysis_NLP_term_project.docx is the report file in word format.  
4. Aspect-level_Sentiment_Analysis_NLP_term_project.pdf is the report file in pdf format.  
5. Canon_G3_part1.txt, Canon_G3_part2.txt, Canon_G3_part3.txt are the input review file.  
6. product_reviews_list_1.data, product_reviews_list_2.data, product_reviews_list_3.data are the pickled data file.  
7. Opinion_Seed.txt is the input opinion seed file.  
8. result.png is the bar chart of our output.  
9. stanford-corenlp-full-2018-02-27 is the stanford dependency parsing package we referenced.  

Because the pickled data already stored in this folder, you can only run the score code to see our output.  

Input review file format is in our report (at IV experiment)  

  
## How to run the algorithm:  
$python3 fine_grained_sentiment_analysis.py <opinion seed file name> <input reviews file name> <output pickle file name>  
for example: $python3 fine_grained_sentiment_analysis.py Opinion_Seed.txt Canon_G3_part1.txt product_reviews_list_1.data  

## How to run the score code:  
1. $python3 score.py <pickled file name>  
for example: $python3 score.py product_reviews_list_1.data  

## Reference:  
stanford dependency parsing package  



