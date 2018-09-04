
# coding: utf-8

# In[1]:


from nltk.tokenize import sent_tokenize
from nltk.parse.stanford import StanfordDependencyParser
path_to_jar = "stanford-corenlp-full-2018-02-27/stanford-corenlp-3.9.1.jar"
path_to_models_jar = "stanford-corenlp-full-2018-02-27/stanford-corenlp-3.9.1-models.jar"
dependency_parser = StanfordDependencyParser(path_to_jar=path_to_jar, path_to_models_jar=path_to_models_jar)
from copy import deepcopy
import pickle


# # Global Variable

# In[2]:


MR = set() ## MR relation set
MR.add('amod')
MR.add('nmod')
MR.add('pnmod')
MR.add('nsubj')
MR.add('s')
MR.add('dobj')
MR.add('iobj')
MR.add('desc')
MR.add('xcomp') ## test
NN = set() ## NN pos set
NN.add('NN')
NN.add('NNS')
NN.add('NNP')
JJ = set() ## JJ pos set
JJ.add('JJ')
JJ.add('JJS')
JJ.add('JJR')
CONJ = set() ## CONJ relation set
CONJ.add('conj')
modES = set() ## modify relation equality
modES.add('amod')
modES.add('pnmod')
modES.add('nmod')
gjES = set() ## 
gjES.add('dobj')
gjES.add('iobj')
gjES.add('nsubj')


# # Data structure

# In[3]:


class Opinion: ## Opinion word class
    def __init__(self, t, p):
        self.token = t;
        self.polarity = p;
        self.is_seed = False


# In[4]:


class Target: ## target word class
    def __init__(self, t, p):
        self.token = t;
        self.polarity = p;


# In[5]:


class Label:
    def __init__(self, t, p, a):
        self.token = t;
        self.polarity = p;
        self.add_info = a


# In[6]:


class Review_Sent:
    def __init__(self, l, s):
        self.target_list = l
        self.sent = s
        self.pred_target_set = set()


# In[7]:


class Product_Review:
    def __init__(self, t):
        self.title = t
        self.review_sentences_list = []


# # Function

# In[8]:


def dep_rel_equality(a, b):
    if a in modES and b in modES:
        return True
    elif a in gjES and b in gjES:
        return True
    else:
        return False


# In[9]:


def get_opinion_set(Opinion_class_set):
    O_s = set()
    for opinion in Opinion_class_set:
        O_s.add(opinion.token)
    return O_s


# In[10]:


def get_opinion_polarity(opinion_word, Opinion_class_set):
    for opinion in Opinion_class_set:
        if opinion_word == opinion.token:
            return opinion.polarity
    return 0


# In[11]:


def get_target_set(Target_class_set):
    T_s = set()
    for target in Target_class_set:
        T_s.add(target.token)
    return T_s


# In[12]:


def get_target_polarity(target_word, Target_class_set):
    for target in Target_class_set:
        if target_word == target.token:
            return target.polarity
    return 0


# In[13]:


def check_neg_rel(opinion_word, s):
    sent = s.split()
    index = 0
    tok_index = -1
    for token in sent:
        if token == opinion_word:
            tok_index = index
        index += 1
    start_index = 0
    end_index = len(sent) -1 
    if (tok_index - 3) > 0:
        start_index = tok_index - 3
    if (tok_index+3)<(len(sent)-1):
        end_index = tok_index+3
    ##print(tok_index, start_index, end_index)
    for i in range(start_index, end_index, 1):
        if sent[i] == 'not' or sent[i] == 'no' or '''n't''' in sent[i]:
            return -1
    return 1
            


# # Rule

# ## Rule 1 Opinion to Target

# In[14]:


def Rule_1_O_to_T_1(review_sent, opinion_set):
    sent = review_sent.sent ## newly add
    opinion_word_set = get_opinion_set(opinion_set)
    new_T_set = set()
    ##print(sent)
    result = dependency_parser.raw_parse(sent)
    dep = result.__next__()
    for t in dep.triples():
        root_t, dep_rel, leaf_t = t
        ##print(t)
        if leaf_t[0] in opinion_word_set and dep_rel in MR and root_t[1] in NN:
            polarity = get_opinion_polarity(leaf_t[0], opinion_set)
            polarity = polarity * check_neg_rel(leaf_t[0], sent)
            target = Target(root_t[0], polarity)
            new_T_set.add(target)
            is_new_flag = True
            for t in review_sent.pred_target_set:
                if t.token == target.token:
                    t.polarity += target.polarity 
                    is_new_flag = False
                    break
            if is_new_flag:
                review_sent.pred_target_set.add(deepcopy(target))
        elif root_t[0] in opinion_word_set and dep_rel in MR and leaf_t[1] in NN:
            polarity = get_opinion_polarity(root_t[0], opinion_set)
            polarity = polarity * check_neg_rel(leaf_t[0], sent)
            target = Target(leaf_t[0], polarity)
            new_T_set.add(target)
            is_new_flag = True
            for t in review_sent.pred_target_set:
                if t.token == target.token:
                    t.polarity += target.polarity 
                    is_new_flag = False
                    break
            if is_new_flag:
                review_sent.pred_target_set.add(target)
    ## test print
#     for label in review_sent.target_list:
#         print(label.token, label.polarity)
#     print(review_sent.sent)
#     for target in review_sent.pred_target_set:
#         print(target.token, target.polarity)
    return new_T_set


# In[15]:


# l = Label('system', +2, "")
# l_l = []
# l_l.append(l)
# rs = Review_Sent(l_l, "its focusing system is also very flexible")
# o = Opinion("flexible", +2)
# o.is_seed = True
# O_S = set()
# O_S.add(o)
# for t in Rule_1_O_to_T_1(rs, O_S):
#     print(t.token, t.polarity)


# In[16]:


def Rule_1_O_to_T_2(review_sent, opinion_set):
    sent = review_sent.sent ## newly add
    opinion_word_set = get_opinion_set(opinion_set)
    new_T_set = set()
    result = dependency_parser.raw_parse(sent)
    dep = result.__next__()
    H = set() ## head of dependency relation
    for t in dep.triples():
        root_t, dep_rel, leaf_t = t
        if leaf_t[0] in opinion_word_set and dep_rel in MR:
            l = root_t[0]+"#"+leaf_t[0]
            H.add(l)
    for h in H:
        head, leaf = h.split("#")
        for t in dep.triples():
            root_t, dep_rel, leaf_t = t
            if root_t[0] == head and dep_rel in MR and leaf_t[1] in NN:
                polarity = get_opinion_polarity(leaf, opinion_set)
                polarity = polarity * check_neg_rel(leaf_t[0], sent)
                target = Target(leaf_t[0], polarity)
                new_T_set.add(target)
                is_new_flag = True
                for t in review_sent.pred_target_set:
                    if t.token == target.token:
                        t.polarity += target.polarity 
                        is_new_flag = False
                        break
                if is_new_flag:
                    review_sent.pred_target_set.add(deepcopy(target))
    ## test print
#     for label in review_sent.target_list:
#         print(label.token, label.polarity)
#     print(review_sent.sent)
#     for target in review_sent.pred_target_set:
#         print(target.token, target.polarity)
    return new_T_set


# In[17]:


# l = Label('ipod', +2, "")
# l_l = []
# l_l.append(l)
# rs = Review_Sent(l_l, "iPod is not the best mp3 player")
# o = Opinion("best", +2)
# o.is_seed = True
# O_S = set()
# O_S.add(o)
# Rule_1_O_to_T_2(rs, O_S)


# ## Rule 2 Target to Opinion

# In[18]:


def Rule_2_T_to_O_1(review_sent, target_set):
    sent = review_sent.sent ## newly add
    target_word_set = get_opinion_set(target_set)
    new_O_set = set()
    result = dependency_parser.raw_parse(sent)
    dep = result.__next__()
    for t in dep.triples():
        root_t, dep_rel, leaf_t = t
        ##print(t)
        if root_t[0] in target_word_set and dep_rel in MR and leaf_t[1] in JJ:
            polarity = get_target_polarity(root_t[0], target_set)
            opinion = Opinion(leaf_t[0], polarity)
            new_O_set.add(opinion)
            ## update target in review_sent
            is_new_flag = True
            sent_polarity = 0
            for t in review_sent.pred_target_set:
                sent_polarity += t.polarity
                if root_t[0] == t.token:
                    if opinion.polarity!=0:
                        t.polarity = (t.polarity + opinion.polarity)/2
                    is_new_flag = False
            if len(review_sent.pred_target_set)!=0:
                sent_polarity /= len(review_sent.pred_target_set)       
            if is_new_flag:
                if opinion.polarity != 0:
                    target = Target(root_t[0], opinion.polarity)
                    review_sent.pred_target_set.add(target)
                else:
                    target = Target(root_t[0], sent_polarity)
                    review_sent.pred_target_set.add(target)
        elif leaf_t[0] in target_word_set and dep_rel in MR and root_t[1] in JJ:
            polarity = get_target_polarity(leaf_t[0], target_set)
            opinion = Opinion(root_t[0], polarity)
            new_O_set.add(opinion)
            ## update target in review_sent
            is_new_flag = True
            sent_polarity = 0
            for t in review_sent.pred_target_set:
                sent_polarity += t.polarity
                if leaf_t[0] == t.token:
                    if opinion.polarity!=0:
                        t.polarity = (t.polarity + opinion.polarity)/2
                    is_new_flag = False
            if len(review_sent.pred_target_set)!=0:
                sent_polarity /= len(review_sent.pred_target_set)       
            if is_new_flag:
                if opinion.polarity != 0:
                    target = Target(leaf_t[0], opinion.polarity)
                    review_sent.pred_target_set.add(target)
                else:
                    target = Target(leaf_t[0], sent_polarity)
                    review_sent.pred_target_set.add(target)
     ## test print
#     for label in review_sent.target_list:
#         print(label.token, label.polarity)
#     print(review_sent.sent)
#     for target in review_sent.pred_target_set:
#         print(target.token, target.polarity)
    return new_O_set


# In[19]:


# l = Label('screen', +2, "")
# l_l = []
# l_l.append(l)
# rs = Review_Sent(l_l, "The phone has a good screen.")
# t = Target("screen", +2)
# T_S = set()
# T_S.add(t)
# new_O_set = Rule_2_T_to_O_1(rs, T_S)
# print(' new opinion set:')
# for opinion in new_O_set:
#     print(opinion.token, opinion.polarity)


# In[20]:


def Rule_2_T_to_O_2(review_sent, target_set):
    sent = review_sent.sent ## newly add
    target_word_set = get_opinion_set(target_set)
    new_O_set = set()
    result = dependency_parser.raw_parse(sent)
    dep = result.__next__()
    ## result_triples = my_dependency_parser(sent)
    H = set() ## head of dependency relation
    for t in dep.triples():
        root_t, dep_rel, leaf_t = t
        if leaf_t[0] in target_word_set and dep_rel in MR:
            H.add(root_t[0]+"#"+leaf_t[0])
    for h in H:
        head, leaf = h.split("#")
        for t in dep.triples():
            root_t, dep_rel, leaf_t = t
            if root_t[0] == head and dep_rel in MR and leaf_t[1] in JJ:
                polarity = get_target_polarity(leaf, target_set)
                opinion = Opinion(leaf_t[0],polarity)
                new_O_set.add(opinion)
                ## update target in review_sent
                is_new_flag = True
                sent_polarity = 0
                for t in review_sent.pred_target_set:
                    sent_polarity += t.polarity
                    if leaf == t.token:
                        if opinion.polarity!=0:
                            t.polarity = (t.polarity + opinion.polarity)/2
                        is_new_flag = False
                if len(review_sent.pred_target_set)!=0:
                    sent_polarity /= len(review_sent.pred_target_set)       
                if is_new_flag:
                    if opinion.polarity != 0:
                        target = Target(leaf, opinion.polarity)
                        review_sent.pred_target_set.add(target)
                    else:
                        target = Target(leaf, sent_polarity)
                        review_sent.pred_target_set.add(target)
     ## test print
#     for label in review_sent.target_list:
#         print(label.token, label.polarity)
#     print(review_sent.sent)
#     for target in review_sent.pred_target_set:
#         print(target.token, target.polarity)
    return new_O_set


# In[21]:


# l = Label('ipod', +2, "")
# l_l = []
# l_l.append(l)
# rs = Review_Sent(l_l, "iPod is the best mp3 player")
# t = Target("iPod", +2)
# T_S = set()
# T_S.add(t)
# new_O_set = Rule_2_T_to_O_2(rs,T_S)
# print(' new opinion set:')
# for opinion in new_O_set:
#     print(opinion.token, opinion.polarity)


# ## Rule 3 Target to Target

# In[22]:


def Rule_3_T_to_T_1(review_sent, target_set):
    sent = review_sent.sent
    target_word_set=get_target_set(target_set)
    ##print(target_word_set)
    new_T_set = set()
    result = dependency_parser.raw_parse(sent)
    dep = result.__next__()
    for t in list(dep.triples()):
        root_t, dep_rel, leaf_t = t
        if leaf_t[0] in target_word_set and root_t[1]in NN and dep_rel in CONJ:
            if root_t[0] not in target_word_set:
                polarity = get_target_polarity(leaf_t[0], target_set)
                target = Target(root_t[0], polarity)
                review_sent.pred_target_set.add(deepcopy(target))
                new_T_set.add(target)
            else:
                polarity = get_target_polarity(leaf_t[0], target_set)
                for target in target_set:
                    if target.token ==root_t[0]:
                        temp = target.polarity
                        target.polarity = (temp+polarity)/2
                        temp=target.polarity 
                for target in target_set:
                    if target.token ==leaf_t[0]:
                        target.polarity = temp
                is_root_new_flag = True
                is_leaf_new_flag = True
                for r_sent in review_sent.pred_target_set:
                    if r_sent.token ==root_t[0]:
                        r_sent.polarity = temp;
                        is_root_new_flag = False
                    if r_sent.token ==leaf_t[0]:
                        r_sent.polarity = temp;
                        is_leaf_new_flag = False
                if is_root_new_flag:        
                    t = Target(root_t[0], temp)
                    review_sent.pred_target_set.add(deepcopy(t))
                if is_leaf_new_flag:
                    t = Target(leaf_t[0], temp)
                    review_sent.pred_target_set.add(deepcopy(t))
                        
        elif root_t[0] in target_word_set and leaf_t[1]in NN and dep_rel in CONJ:
            polarity = get_target_polarity(root_t[0], target_set)
            target = Target(leaf_t[0], polarity)
            review_sent.pred_target_set.add(deepcopy(target))
            new_T_set.add(target)
    ## test print
#     for label in review_sent.target_list:
#         print(label.token, label.polarity)
#     print(review_sent.sent)
#     for target in review_sent.pred_target_set:
#         print(target.token, target.polarity)
    return new_T_set


# In[23]:


# l = Label('', 0, "")
# l_l = []
# l_l.append(l)
# rs = Review_Sent(l_l, "You may have to get more storage to store high quality pictures and recorded movies.")
# t = Target("pictures", +2)
# ##t2 = Target("audio", +1)
# T_S = set()
# T_S.add(t)
# ##T_S.add(t2)
# new_T_set = Rule_3_T_to_T_1(rs, T_S)
# print(' new target set:')
# for target in new_T_set:
#     print(target.token, target.polarity)


# In[24]:


def Rule_3_T_to_T_2(review_sent, target_set):
    sent = review_sent.sent
    target_word_set=get_target_set(target_set)
    new_T_set = set()
    result = dependency_parser.raw_parse(sent)
    dep = result.__next__()
    for i,val in enumerate(list(dep.triples())):
        root_t, dep_rel, leaf_t = val
        ##print(val)
        for j,val2 in enumerate(list(dep.triples()),i):
            root_t2, dep_rel2, leaf_t2 = val2
            ##print(val2)
            if root_t[0] == root_t2[0] and dep_rel_equality(dep_rel, dep_rel2) and leaf_t[1] in NN and leaf_t2[0] in target_word_set and leaf_t[0]!=leaf_t2[0] :
                ##print("here")
                if leaf_t[0] not in target_word_set:
                    polarity = get_target_polarity(leaf_t2[0], target_set)
                    target = Target(leaf_t[0], polarity)
                    review_sent.pred_target_set.add(deepcopy(target))
                    new_T_set.add(target)
                else:
                    polarity = get_target_polarity(leaf_t2[0], target_set)
                    for target in target_set:
                        if target.token ==leaf_t[0]:
                            temp = target.polarity
                            target.polarity = (temp+polarity)/2
                            temp=target.polarity 
                            break
                    for target in target_set:
                        if target.token ==leaf_t2[0]:
                            target.polarity = temp
                            break
                    is_new_flag = True
                    for r_sent in review_sent.pred_target_set:
                        if r_sent.token ==leaf_t[0]:
                            target.polarity = temp
                            temp=target.polarity 
                            is_new_flag = False
                            break
                    if is_new_flag:
                        t = Target(leaf_t[0], temp)
                        review_sent.pred_target_set.add(deepcopy(t))
                    is_new_flag = True
                    for r_sent in review_sent.pred_target_set:
                        if r_sent.token ==leaf_t2[0]:
                            target.polarity = temp
                            is_new_flag = False
                            break
                    if is_new_flag:
                        t = Target(leaf_t2[0], temp)
                        review_sent.pred_target_set.add(deepcopy(t))
    ## test print
#     for label in review_sent.target_list:
#         print(label.token, label.polarity)
#     print(review_sent.sent)
#     for target in review_sent.pred_target_set:
#         print(target.token, target.polarity)
    return new_T_set


# In[25]:


# l = Label('null', +2, "")
# l_l = []
# l_l.append(l)
# rs = Review_Sent(l_l, "You may have to get more storage to store high quality pictures and recorded movies.")
# t = Target("movies", +2)
# ##t2 = Target("G3", +1)
# T_S = set()
# T_S.add(t)
# ##T_S.add(t2)
# new_T_set = Rule_3_T_to_T_2(rs, T_S)
# print(' new target set:')
# for target in new_T_set:
#     print(target.token, target.polarity )


# ## Rule 4 Opinon to Opinion

# In[26]:


#If find new opinion word, then add it to opinion expand set and assign its parent's polarity to it.
#If the finding opinion is not new, and not a opinion seed, then update its polarity with (its polarity + parent polarity)/ 2
#If the finding opinion is not new, and it is a opinion seed, then do nothing
def Rule_4_O_to_O_1(review_sent, opinion_set):
    new_op_set = set()
    sent = review_sent.sent 
    opinion_word_set = get_opinion_set(opinion_set)
    result = dependency_parser.raw_parse(sent)
    dep = result.__next__()
    for t in dep.triples():
        root_t, dep_rel, leaf_t = t
        
        # The moive is A and B, given B(leaf) -> A(root)
        if leaf_t[0] in opinion_word_set and root_t[1] in JJ and dep_rel in CONJ:
            polarity_parent = get_opinion_polarity(leaf_t[0], opinion_set)
            polarity_parent = polarity_parent * check_neg_rel(leaf_t[0], sent) ## not necessary
            
            #child opinion in expand opinion set but not a seed, update child opinion's polarity
            if root_t[0] in opinion_word_set :
                for op in opinion_set:
                    if op.token == root_t[0] and op.is_seed == False:
                        op.polarity = (op.polarity + polarity_parent) / 2.0
            
            #child opinion is new opinion, initialize an new opinion instance and assign parent polarity to it.
            #and add it to opinion expand set
            if root_t[0] not in opinion_word_set:
                opinion = Opinion(root_t[0], polarity_parent)
                opinion_set.add(opinion)
                new_op_set.add(opinion)
                opinion_word_set = get_opinion_set(opinion_set)
        
        ## The moive is A and B, given A(root) -> B(leaf)
        if root_t[0] in opinion_word_set and leaf_t[1] in JJ  and dep_rel in CONJ :
            polarity_parent = get_opinion_polarity(root_t[0], opinion_set)
            polarity_parent = polarity_parent * check_neg_rel(leaf_t[0], sent) ## not necessary
            
            #child opinion in expand opinion set but not a seed, update child opinion's polarity
            if leaf_t[0] in opinion_word_set :
                for op in opinion_set:
                    if op.token == leaf_t[0] and op.is_seed == False:
                        op.polarity = (op.polarity + polarity_parent) / 2.0
            
            #child opinion is new opinion, initialize an new opinion instance and assign parent polarity to it.
            #and add it to opinion expand set
            if leaf_t[0] not in opinion_word_set:
                opinion = Opinion(leaf_t[0], polarity_parent)
                opinion_set.add(opinion)
                new_op_set.add(opinion)
                opinion_word_set = get_opinion_set(opinion_set)
    ## test print
#     for label in review_sent.target_list:
#         print(label.token, label.polarity)
#     print(review_sent.sent)
#     for target in review_sent.pred_target_set:
#         print(target.token, target.polarity)         
    return new_op_set


# In[27]:


# l = Label('camera', +2, "")
# l_l = []
# l_l.append(l)
# rs = Review_Sent(l_l, "The camera is not bad and easy")
# #o = Opinion("easy", +2)
# o2 = Opinion("bad", -1)
# o.is_seed = True
# O_S = set()
# #O_S.add(o)
# O_S.add(o2)
# new_O_set = Rule_4_O_to_O_1(rs, O_S)
# print("all opinion set:")
# for opinion in new_O_set:
#     print(opinion.token, opinion.polarity)


# In[28]:


#"If you want to buy a sexy, cool, accessory-available mp3 player, you can choose iPod."
#((u'player', u'NN'), u'amod', (u'sexy', u'JJ'))
#((u'player', u'NN'), u'amod', (u'cool', u'JJ'))

#no return value
#If find new opinion word, then add it to opinion expand set and assign its parent's polarity to it.
#If the finding opinion is not new, and not a opinion seed, then update its polarity with (its polarity + parent polarity)/ 2
#If the finding opinion is not new, and it is a opinion seed, then do nothing
def Rule_4_O_to_O_2(review_sent, opinion_set):
    new_op_set = set()
    sent = review_sent.sent 
    opinion_word_set = get_opinion_set(opinion_set)
    result = dependency_parser.raw_parse(sent)
    dep = result.__next__()
    for t in dep.triples():
        root_t, dep_rel_t, leaf_t = t
        if leaf_t[0] in opinion_word_set :
            HEAD = root_t[0]
            REL = dep_rel_t
            polarity_parent = get_opinion_polarity(leaf_t[0], opinion_set)
            polarity_parent = polarity_parent * check_neg_rel(leaf_t[0], sent) ## not necessary
            
            for u in dep.triples():
                root_u, dep_rel_u, leaf_u = u
                if leaf_u[0] != leaf_t[0] and dep_rel_equality(dep_rel_u, REL) and root_u[0] == HEAD and leaf_u[1] in JJ:
                    
                    #child opinion in expand opinion set but not a seed, update child opinion's polarity
                    if leaf_u[0] in opinion_word_set :
                        for op in opinion_set:
                            if op.token == leaf_u[0] and op.is_seed == False:
                                op.polarity = (op.polarity + polarity_parent) / 2.0
                        
                    #child opinion is new opinion, initialize an new opinion instance and assign parent polarity to it.
                    #and add it to opinion expand set
                    if leaf_u[0] not in opinion_word_set:
                        opinion = Opinion(leaf_u[0], polarity_parent)
                        opinion_set.add(opinion)
                        new_op_set.add(opinion)
                        opinion_word_set = get_opinion_set(opinion_set)
    ## test print
#     for label in review_sent.target_list:
#         print(label.token, label.polarity)
#     print(review_sent.sent)
#     for target in review_sent.pred_target_set:
#         print(target.token, target.polarity)
    return new_op_set


# In[29]:


# l = Label('player', +2, "")
# l_l = []
# l_l.append(l)
# rs = Review_Sent(l_l, "If you want to buy a sexy, cool, accessory-available mp3 player, you can choose iPod.")
# o = Opinion("sexy", +2)
# o2 = Opinion("cool", +1)
# o.is_seed = True
# O_S = set()
# O_S.add(o)
# O_S.add(o2)
# Rule_4_O_to_O_2(rs, O_S)
# print("all opinion set:")
# for opinion in O_S:
#     print(opinion.token, opinion.polarity)


# # Train Data Retrieve

# In[30]:


import sys
if len(sys.argv) != 4:
    print("Input format wrong! Please read readme file!")
    sys.exit()
file_name = sys.argv[2] ## review file name
pik_name = sys.argv[3]  ## pickle name it's going to generate
opinion_seed_filename = sys.argv[1] ## opinion seed file name

file = open(file_name)
lines = file.readlines()
Product_Reviews_list = []
print("\tInput review data:\n")
for line in lines:
    if line[0] != '*' and len(line) > 1:
        if line[1] == 't':
            line = line.replace('[t]',"")
            Product_review = Product_Review(line.replace("\n",""))
            Product_Reviews_list.append(Product_review)
        else:
            left, sent = line.split('##')
            temp_lp_list = left.split(',')
            lp_list = []
            for lp in temp_lp_list:
                if '[' in lp:
                    if(len(lp.split('['))>2):
                        l, p, a = lp.split('[')
                        p = int(p.replace(']',""))
                        LP = Label(l, p, a)
                    else:
                        l, p = lp.split('[')
                        p = p.replace(']',"")
                        a = ""
                        LP = Label(l, p, a)
                        lp_list.append(LP)
            Review_sent = Review_Sent(lp_list,sent.replace("\n",""))
            Product_review.review_sentences_list.append(Review_sent)       


# In[31]:


for pr in Product_Reviews_list:
    ##print("new review!")
    print(pr.title)
    for rs in pr.review_sentences_list:
        for lp in rs.target_list:
            print(lp.token, lp.polarity, lp.add_info)
        print( rs.sent+"\n")


# # Double Propagation

# In[32]:


def DoubleProp(opinion_seed, product_review_list):
    #output set initialization
    Opinion_Expand = opinion_seed
    ##print(Opinion_Expand)
    All_Feature = set() 
    itr = 0
    while True:
        print("iteraton "+str(itr)+":")
        ## print(Opinion_Expand) 
        new_feature_i_set = set()
        new_opinion_i_set = set()
        new_feature_j_set = set()
        new_opinion_j_set = set()
        for one_product_review in Product_Reviews_list:
            for st in one_product_review.review_sentences_list:
                #Rule 1
                print("implementing rule1")
                temp_new_feature_R11_set = Rule_1_O_to_T_1(st, Opinion_Expand)
                for new_feature in temp_new_feature_R11_set:
                    is_new_flag = True
                    for feature in All_Feature:
                        if new_feature.token == feature.token:
                            feature.polarity = (feature.polarity + new_feature.polarity)/2.0
                            is_new_flag = False
                            break
                    if is_new_flag:
                        new_feature_i_set.add(new_feature)
                    ##if feature not in All_Feature:#no use "if" since add will handle the repeated feature
                    ##   new_feature_i_set.add(feature)
                temp_new_feature_R12_set = Rule_1_O_to_T_2(st, Opinion_Expand)
                for new_feature in temp_new_feature_R12_set:
                    is_new_flag = True
                    for feature in All_Feature:
                        if new_feature.token == feature.token:
                            feature.polarity = (feature.polarity + new_feature.polarity)/2.0
                            is_new_flag = False
                            break
                    if is_new_flag:
                        new_feature_i_set.add(new_feature)
                    ##if feature not in All_Feature:#no use "if" since add will handle the repeated feature
                    ##   new_feature_i_set.add(feature)

                #Rule 4
                print("implementing rule4")
                temp_new_opinion_R41_set = Rule_4_O_to_O_1(st, Opinion_Expand)
                temp_new_opinion_R42_set = Rule_4_O_to_O_2(st, Opinion_Expand)
                for opinion in temp_new_opinion_R41_set:
                    new_opinion_i_set.add(opinion)
                for opinion in temp_new_opinion_R42_set:
                    new_opinion_i_set.add(opinion)
            

            All_Feature = All_Feature | new_feature_i_set
            Opinion_Expand = Opinion_Expand | new_opinion_i_set

            ##print("2")
           ## print(Opinion_Expand)

            for st in one_product_review.review_sentences_list:
                #Rule 3
                print("implementing rule3")
                temp_new_feature_R31_set = Rule_3_T_to_T_1(st, new_feature_i_set)
                temp_new_feature_R32_set = Rule_3_T_to_T_2(st, new_feature_i_set)
                for feature in temp_new_feature_R31_set:
                    new_feature_j_set.add(feature)
                for feature in temp_new_feature_R32_set:
                    new_feature_j_set.add(feature)
                print("implementing rule2")
                #Rule 2
                temp_new_opinion_R21_set = Rule_2_T_to_O_1(st, new_feature_i_set)
                for new_opinion in temp_new_opinion_R21_set:
                    is_new_flag = True
                    for opinion in Opinion_Expand:
                        if new_opinion.token == opinion.token:
                            opinion.polarity = (opinion.polarity + new_opinion.polarity)/2.0
                            is_new_flag = False
                            break
                    if is_new_flag:
                        new_opinion_j_set.add(new_opinion)
                    ##if opinion not in Opinion_Expand:#no use "if" since add will handle the repeated opinion
                    ##    new_opinion_j_set.add(opinion)
                temp_new_opinion_R22_set = Rule_2_T_to_O_2(st, new_feature_i_set)
                for new_opinion in temp_new_opinion_R22_set:
                    is_new_flag = True
                    for opinion in Opinion_Expand:
                        if new_opinion.token == opinion.token:
                            opinion.polarity = (opinion.polarity + new_opinion.polarity)/2.0
                            is_new_flag = False
                            break
                    if is_new_flag:
                        new_opinion_j_set.add(new_opinion)
                    ##if opinion not in Opinion_Expand:#no use "if" since add will handle the repeated opinion
                    ##    new_opinion_j_set.add(opinion)

            new_feature_i_set = new_feature_i_set | new_feature_j_set
            new_opinion_i_set = new_opinion_i_set | new_opinion_j_set
            ## reset feature polarity to zero for each review
            for feature in new_feature_i_set:
                feature.polarity = 0

        print("new feature i set: \n"+str(len(new_feature_i_set))+" new features")
        for feature in new_feature_i_set:
            print(feature.token, feature.polarity)
        print("new opinion i set: \n"+str(len(new_opinion_i_set))+" new opinions")
        for opinion in new_opinion_i_set:
            print(opinion.token, opinion.polarity)

        All_Feature = All_Feature | new_feature_j_set
        Opinion_Expand = Opinion_Expand | new_opinion_j_set
        
        itr += 1
        
        ##print("3")
        ##print(Opinion_Expand)
        if len(new_feature_i_set) == 0 and len(new_opinion_i_set) == 0:
            break
            
    return All_Feature, Opinion_Expand


# In[33]:

# # Pos Neg Seed Retrieve
O_S = set() ## opinion seed set
file = open(opinion_seed_filename)
lines = file.readlines()
for line in lines:
    token, polarity = line.split(", ")
    polarity = int(polarity.replace("\n",""))
    o = Opinion(token, polarity)
    o.is_seed = True
    O_S.add(o)
    
# # Double propogation
try:
    print("\tStart double propogation:\n")
    f_s ,o_s = DoubleProp(O_S, Product_Reviews_list)
    print("generate target num:"+str(len(f_s))+"\n")
    print("generate opinon num:"+str(len(o_s))+"\n")
except AssertionError:
    print('invalid input')


# In[34]:


PIK = pik_name
with open(PIK, "wb") as f:
    pickle.dump(Product_Reviews_list, f)


# In[35]:


with open(PIK, "rb") as f:
    pr_list = pickle.load(f)


# In[36]:

print("\tTrained review data:\n")
rev_num = 0
for pr in pr_list:
    print("Review "+str(rev_num)+":\n")
    for review_sent in pr.review_sentences_list:
        if len(review_sent.target_list) != 0:
            print("\tReal Label:")
        for label in review_sent.target_list:
            print(label.token, label.polarity)
        print(review_sent.sent)
        if len(review_sent.target_list) != 0:
            print("\tPredict Label:")
        for target in review_sent.pred_target_set:
            if target.polarity != 0:
                print(target.token, target.polarity)
        if len(review_sent.target_list)>0:
            print("  correct target in this sentence:")
            for target in review_sent.pred_target_set:
                for label in review_sent.target_list:
                    if label.token == target.token:
                        print(target.token, target.polarity)
        print("\n")
    rev_num+=1;

