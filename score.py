import pickle
import sys

class Opinion: ## Opinion word class
    def __init__(self, t, p):
        self.token = t;
        self.polarity = p;
        self.is_seed = False

class Target: ## target word class
    def __init__(self, t, p):
        self.token = t;
        self.polarity = p;

class Label:
    def __init__(self, t, p, a):
        self.token = t;
        self.polarity = p;
        self.add_info = a

class Review_Sent:
    def __init__(self, l, s):
        self.target_list = l
        self.sent = s
        self.pred_target_set = set()

class Product_Review:
    def __init__(self, t):
        self.title = t
        self.review_sentences_list = []

if len(sys.argv) != 2:
    print("Input format wrong! Please read readme file!")
    sys.exit()

PIK = sys.argv[1]


with open(PIK, "rb") as f:
    pr_list = pickle.load(f)

def compute_f_score(true, positive, true_positive):
    ## return recall, precision, f-score
    return true_positive/true, true_positive/positive, 2*true_positive/(true+positive)

rev_num = 0
labeled_target_num = 0  ## true
pred_correct_target_num = 0 ## true positive
pred_target_num = 0 ## positive
for pr in pr_list:
    print("Review "+str(rev_num)+":\n")
    for review_sent in pr.review_sentences_list:
        if len(review_sent.target_list) != 0:
            print("\tReal Label:")
        for label in review_sent.target_list:
            print(label.token, label.polarity)
        print(review_sent.sent)
        labeled_target_num+=len(review_sent.target_list)
        if len(review_sent.target_list) != 0:
            print("\tPredict Label:")
        for target in review_sent.pred_target_set:
            if target.polarity != 0:
                pred_target_num+=1
                print(target.token, target.polarity)
        if len(review_sent.target_list)>0:
            print("  correct target in this sentence:")
            for target in review_sent.pred_target_set:
                for label in review_sent.target_list:
                    if label.token == target.token and target.polarity!=0:
                        pred_correct_target_num += 1
                        if target.polarity > 0:
                            print(target.token, "+")
                        if target.polarity < 0:
                            print(target.token, "-")
        print("\n")
    rev_num+=1;
print("true: "+str(labeled_target_num)+", positive: "+str(pred_target_num)+", true positive: "+str(pred_correct_target_num))

recall, precision, f_score = compute_f_score(labeled_target_num, pred_target_num, pred_correct_target_num)
print("recall=%.4f, precision=%.4f, f_score=%.4f" % (recall, precision, f_score))