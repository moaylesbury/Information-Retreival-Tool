import sys
import re
from stemming.porter2 import stem
from math import log


def is_odd(number):
    if number % 2 == 0:
        return False
    else:
        return True


def terms_adjacent(aa, bb, proximity):
    # takes input of two lists of form [x,y,z,...]
    # these are non-empty lists of positions the term occurs in document
    # if there are two positions such that pos(b)-pos(a)==1, they are adjacent, and added to matches
    # returns matches, list of positions with adjacent terms
    # print(aa)
    # print(bb)
    matches = []
    for a in aa:
        for b in bb:
            if proximity >= b - a > 0:
                # print("match")
                matches.append([a, b])
    return matches


def recursive_truth_determination(stack):
    # stack will either be at least length 3 if not length 1
    # length 1 means that is the final output
    # length 3n means truth value, logical operator, truth value
    print(stack)
    if len(stack) == 1:
        print("returning: ", stack[0])
        return stack[0]
    else:
        truth_val0 = stack[0]
        logic_op = stack[1]
        truth_val1 = stack[2]
        for index in range(3):
            stack.pop(0)

        if logic_op == "AND":
            print("0")
            if truth_val0 and truth_val1:
                print("1")
                stack.insert(0, True)
            else:
                print("2")
                stack.insert(0, False)


        elif logic_op == "OR":
            if truth_val0 or truth_val1:
                # print("in or")
                stack.insert(0, True)
            else:
                print("2")
                stack.insert(0, False)

        return recursive_truth_determination(stack)


def recursive_split(str, lst):

    split_loc = -1
    for i, ch in enumerate(str):
        if ch == "\"" and i > 0:
            split_loc = i
            break
    if split_loc == -1:
        for _ in str.split(' '):
            lst.append(_)
        return lst
    str1 = str[:split_loc]
    str2 = str[split_loc+1:]

    if str2[0] == " ":
        str2 = str2[1:]



    # preparing to recurse
    lst.append(str1)
    # recurse

    return recursive_split(str2, lst)


def logic_match(operator, term_pair):
    if operator == "AND":
        if term_pair[0] and term_pair[1]:
            return True
    elif operator == "OR":
        if term_pair[0] or term_pair[1]:
            return True
    return False


def logic_matcher(present_terms, logic_operators):
    logic_matcher = {}

    # pairwise matcher
    for counter, _ in enumerate(present_terms):
        if not is_odd(counter):
            logic_matcher[logic_operators[counter]] = [present_terms[counter], present_terms[counter + 1]]

    # now check logic
    for key in logic_matcher.keys():
        if not logic_match(key, logic_matcher[key]):
            return False

    return True


class PreProcessor:

    def __init__(self, files):
        # list of tokens for current file
        self.token_stream = []
        # list of token streams for each file for later traversing
        self.all_token_streams = []
        # list of all terms
        self.term_stream = []

        self.files = files
        self.n_files = len(files)
        self.filename = ""
        self.filenames = []

        # stack for logical determination
        self.stack = []

        # for inverted index
        self.term_doc_pos = {}

        # inverted index implemented as a dictionary where keys are terms and values are corresponding column vectors
        # each column vector is self.n_files long, where the ith element represents the occurences of the term in document i
        self.inverted_index_matrix = {}
        # positional inverted index is the same as inverted index with one key difference
        # the ith element is a list of positions the word occurs at in document i
        self.positional_inverted_index = {}

    def read_in(self, filename):
        # reads in .txt or .xml files
        # returns input stream as a string
        input_stream = open(filename, 'r').read()
        return input_stream


    def tokeniser(self, input_stream):
        # reads in data and splits on any non-word to make tokens
        # performs case-folding to ensure all tokens are lowercase
        self.token_stream = re.split(r'[^\w+\']+', input_stream)
        self.token_stream = [t.lower() for t in self.token_stream]

    def stopping_and_stemming(self):
        # performs stopping
        # makes a list of stop words and removes any such words in token stream
        # also makes sure to remove and empty strings
        stop_words = self.read_in("englishST.txt").split()

        # self.token_stream = [stem(t) for t in self.token_stream if t not in stop_words and t != '']
        new_stream = []
        for i in range(len(self.token_stream)):
            if self.token_stream[i] not in stop_words and self.token_stream[i] != '':
                try:
                    new_stream.append(stem(self.token_stream[i]))
                except:
                    new_stream.append(self.token_stream[i])
        self.token_stream = []
        self.token_stream = new_stream

    def inverted_index(self):
        # searches through all token streams for each file for each term looking for positions

        # looping through each term
        print("iteration in inv index")
        for term in self.term_stream:

            # pos list holds all of the doc lists
            doc_pos_list = []
            doc_count_list = []

            # looping through each document
            # print(self.all_token_streams)
            for i, doc in enumerate(self.all_token_streams):

                # list to hold the pos_lists for each doc
                # doc_pos_list = []
                doc_pos = {docnos[i]: []}
                doc_count = {docnos[i]: 0}
                # looping through each token in said document

                for pos, t in enumerate(doc):

                    # check for a match
                    if term == t:

                        # if there is a match, add it to the position list
                        doc_pos[docnos[i]].append(pos)
                        doc_count[docnos[i]] += 1
                if doc_pos[docnos[i]]:
                    doc_pos_list.append(doc_pos)
                    doc_count_list.append(doc_count)
            # print(pos_list)
            self.positional_inverted_index[term] = doc_pos_list
            self.inverted_index_matrix[term] = doc_count_list
        print("inverted index & positional inverted index constructed...")
        # print(self.positional_inverted_index)


    def print_pii(self):
        # print(self.positional_inverted_index.keys())
        f = open("positional_inverted_index.txt", 'w')
        # print(self.positional_inverted_index)
        for term in self.positional_inverted_index.keys():
            # term and df
            f.write(str(term) + ":" + self.df(term) + '\n')

            for doc_pos_list in self.positional_inverted_index[term]:


                for doc in doc_pos_list.keys():
                    pos_list = doc_pos_list[doc]
                    f.write("               " + doc + ": ")
                    for i, pos in enumerate(pos_list):
                        f.write(str(pos))
                        if i < len(pos_list) - 1:
                            f.write(", ")
                        else:
                            f.write('\n')

                            # # document number
                            # f.write("               " + self.filenames[doc] + ": ")
                            # for i, pos in enumerate(doc_pos_list):
                            #     f.write(str(pos))
                            #     if i < len(doc_pos_list) - 1:
                            #         f.write(", ")
                            #     else:
                            #         f.write('\n')




        f.close()

    def df(self, term):
        df = 0
        for doc_pos_list in self.positional_inverted_index[term]:
            if doc_pos_list != []:
                df += 1
        return str(df)

    def pre_processor(self, documents, docnos):


        self.filenames = docnos
        for i, doc in enumerate(documents):

            #
            # testing
            counter = 0
            #

            # set current file as the file name
            self.filename = docnos[i]



            self.tokeniser(doc)

            self.stopping_and_stemming()
            # add token stream to list of all token streams

            # combine all terms into a term stream
            for term in self.token_stream:
                if term not in self.term_stream:
                    self.term_stream.append(term)
            print("Complete")

            self.all_token_streams.append(self.token_stream)




        # perform inverted index and print
        self.inverted_index()
        self.print_pii()


class Search:

    def __init__(self, pos_inv_ind, n, docnos):
        self.positional_inverted_index = pos_inv_ind
        self.n_files = n
        self.stack = []
        self.docnos = docnos
        self.total_terms = 0

    def term_present(self, term):
        if term in self.positional_inverted_index:
            for pos_list in self.positional_inverted_index[term]:
                if pos_list:
                    return True
        return False

    def boolean_search(self, query):
        # list of items in query
        query_list = []
        # hold terms that have a NOT operator before them
        nots = []
        # if there are quotations present then we have a phrase within the query
        if "\"" in query:
            # if both terms are phrases
            if query[0] == '\"' and query[-1] == '\"':
                # split on the logical operator
                if "AND" in query:
                    phrases = [q.strip()[1:-1] for q in query.split("AND")]

                    phrase1 = [stem(x).lower() for x in phrases[0].split(' ')]
                    phrase2 = [stem(x).lower() for x in phrases[1].split(' ')]

                    phrase_docs1 = self.phrase_search(proximity=1, query_list=phrase1)
                    phrase_docs2 = self.phrase_search(proximity=1, query_list=phrase2)
                    print(phrase_docs1)
                    print(phrases[0])
                    print("\n\n\n\n\n\n\n\n")
                    print(phrase_docs2)
                    if phrase_docs1 is not None and phrase_docs2 is not None:
                        return list(set(phrase_docs1).intersection(phrase_docs2))
                    elif phrase_docs1 is not None:
                        return phrase_docs1
                    else:
                        return phrase_docs2
                else:
                    phrases = [q.strip()[1:-1] for q in query.split("OR")]
                    search_terms = phrases[0][0:len(phrases[0])].split(' ')
                    search_terms = [stem(x.lower()) for x in search_terms]
                    print("kjashgashgsahg", search_terms)
                    phrase_docs1 = self.phrase_search(proximity=1, query_list=search_terms)
                    search_terms = phrases[1][0:len(phrases[1])].split(' ')
                    search_terms = [stem(x.lower()) for x in search_terms]
                    print("kjashgashgsahg", search_terms)
                    phrase_docs2 = self.phrase_search(proximity=1, query_list=search_terms)


                    if phrase_docs1 is not None and phrase_docs2 is not None:
                        return list(set(phrase_docs1).union(phrase_docs2))
                    elif phrase_docs1 is not None:
                        return phrase_docs1
                    else:
                        return phrase_docs2


            # otherwise only one phrase is in the query
            else:
                # the first term is a phrase
                if query[0] == '\"':
                    phrase, q = query[1:].split('\"')
                    if len([_ for _ in q.split(' ') if _ != '']) == 2:
                        op, term = [_ for _ in q.split(' ') if _ != '']
                        docs = self.term_present_docs(stem(term.lower()))
                    else:
                        op, _, term = [_ for _ in q.split(' ') if _ != '']
                        docs = self.term_not_present_docs(stem(term.lower()))
                # the second term is a phrase
                elif query[-1] == '\"':
                    q, phrase = query[0:-1].split('\"')
                    if len([_ for _ in q.split(' ') if _ != '']) == 2:
                        term, op = [_ for _ in q.split(' ') if _ != '']
                        docs = self.term_present_docs(stem(term.lower()))
                    else:
                        term, _, op = [_ for _ in q.split(' ') if _ != '']
                        docs = self.term_not_present_docs(stem(term.lower()))
                    print("phrase ", phrase)
                    print("op ", op)
                    print("term ", term)
                search_terms = phrase[0:len(phrase)].split(' ')
                search_terms = [stem(x.lower()) for x in search_terms]

                phrase_docs = self.phrase_search(proximity=1, query_list=search_terms)

                # print(docs)

                if op == "AND":
                    if docs is not None and phrase_docs is not None:
                        return list(set(docs).intersection(phrase_docs))
                    elif docs is not None:
                        return docs
                    else:
                        return phrase_docs
                elif op == "OR":
                    if docs is not None and phrase_docs is not None:
                        return list(set(docs).union(phrase_docs))
                    elif docs is not None:
                        return docs
                    else:
                        return phrase_docs



            # this is the query list. phrases will be of the form term1 term2
            # query_list = recursive_split(query[1:], [])
        elif ' ' in query:
            query_list = query.split()

            # print(split_query)
            # print("======")
            # for i in query_list:
            #     print(i)
            # for i in range(len(query_list)):
                # if ' ' in query_list[i] and not is_odd(i):
                #     # these are the phrases
                #     # split on ' ' for the terms
                #     print(self.phrase_search(proximity=1, query_list=query_list[i].split(' ')))

        if len(query_list) == 2:
            return self.term_not_present_docs(stem(query_list[1].lower()))



        # if the query is a string then it is one term and will be treat as such
        if not query_list:
            # find docs the query is present in
            return self.term_present_docs(stem(query.lower()))
        # otherwise we have multiple terms and logical operators
        else:
            # set to true if a NOT occurs before the term
            NOT_before = False
            docs = {}
            for query in query_list:
                if NOT_before:
                    nots.append(query)
                    NOT_before = False
                if query == "NOT":
                    NOT_before = True
                else:
                    self.stack.append(query)
                if query not in ["AND", "OR", "NOT"]:
                    if query in nots:
                        docs[query] = self.term_not_present_docs(stem(query.lower()))
                    else:
                        docs[query] = self.term_present_docs(stem(query.lower()))
            # print(self.stack)
            # print(docs)

            # if the length of the stack is 3 then we have no NOT operators
            term0 = self.stack[0]
            op = self.stack[1]
            term1 = self.stack[2]
            if op == "AND":
                if docs[term0] is not None and docs[term1] is not None:
                    return list(set(docs[term0]).intersection(docs[term1]))
                elif docs[term0] is not None:
                    return docs[term0]
                else:
                    return docs[term1]
            elif op == "OR":
                if docs[term0] is not None and docs[term1] is not None:
                    return list(set(docs[term0]).union(docs[term1]))
                elif docs[term0] is not None:
                    return docs[term0]
                else:
                    return docs[term1]


    def term_present_docs(self, term):
        docs = []
        # check term is in keys
        if term in self.positional_inverted_index.keys():
            return [int(list(doc_pos.keys())[0]) for doc_pos in self.positional_inverted_index[term]]
        else:
            return None

    def term_not_present_docs(self, term):
        docs = []
        # check term is in keys
        if term in self.positional_inverted_index.keys():
            term_in = [int(list(doc_pos.keys())[0]) for doc_pos in self.positional_inverted_index[term]]
            return [s for s in self.docnos if s not in term_in]
        else:
            return None


    def phrase_search(self, proximity, query_list):

        docs = {}
        matches = []

        # docs contains a lost of documents each term occurs in
        for query in query_list:
            docs[query] = self.term_present_docs(stem(query.lower()))

        # find documents in which both terms appear
        intersection = list(set(docs[query_list[0]]).intersection(docs[query_list[1]]))

        # check if in any of these documents the terms are adjacent
        # find the term positions within these documents
        for doc in intersection:
            term1_pos_list = []
            term2_pos_list = []

            for doc_pos in self.positional_inverted_index[query_list[0]]:
                key = list(doc_pos.keys())[0]
                if int(key) == doc:
                    term1_pos_list = doc_pos[key]

            for doc_pos in self.positional_inverted_index[query_list[1]]:
                key = list(doc_pos.keys())[0]
                if int(key) == doc:
                    term2_pos_list = doc_pos[key]

            if term1_pos_list and term2_pos_list:
                if terms_adjacent(aa=term1_pos_list, bb=term2_pos_list, proximity=proximity):
                    matches.append(doc)
        return [str(m) for m in matches]

        #
        #
        #
        #
        # for document in range(self.n_files):
        #     # check both are present; if either contains [] then the term does not occur
        #     both_present = True
        #     for term in query_list:
        #         if term not in self.positional_inverted_index.keys():
        #             both_present = False
        #             break
        #         if self.positional_inverted_index[term][document] == []:
        #             # print("not both present in doc ", document)
        #             both_present = False
        #             break
        #     if both_present:
        #         # print("terms both present in doc ", document)
        #         matches = terms_adjacent(self.positional_inverted_index[query_list[0]][document],
        #                                  self.positional_inverted_index[query_list[1]][document],
        #                                  proximity)
        #         if matches != []:
        #             # key is converted from integer to corresponding docno
        #             match_list[self.docnos[document]] = matches
        # return match_list
        # # we have our matches, now to inform the user
        # # for doc in match_list.keys():
        # #     occur_indices = [indices[0] for indices in match_list[doc]]
        # #     print("query phrase occurs in document ", doc, " at the following positions\n")
        # #     for index in occur_indices:
        # #         print(index, '\n')

    def proximity_search(self, query_list):
        # takes input of form #15(term1,term2)
        query_list = re.split('[#(,)]', query_list)
        query_list = [i for i in query_list if i != '' and i != ' ']

        proximity = query_list[0]
        term1 = query_list[1]
        term2 = query_list[2]
        if term2[0] == ' ':
            term2 = term2[1:]

        # proximity search is a special version of phrase search
        # the only difference is that the difference in positions is no longer 1, it is specified by the user
        list = [term1,term2]
        list  = [stem(t.lower()) for t in list]
        print(list[0], list[1])
        return self.phrase_search(proximity=int(proximity), query_list=list)









    def tf(self, term, doc):
        # occurences = len(self.positional_inverted_index[term][doc])
        occurences = 0
        for i in self.positional_inverted_index[term]:
            if doc == str(int(list(i.keys())[0])):
                occurences = len(i[doc])
        # print("---in tf---")
        # print(self.positional_inverted_index[term][doc])
        # print("------")
        # total_terms = 0
        # for term in preprocessor.positional_inverted_index.keys():
        #     print(preprocessor.positional_inverted_index[term][doc])
        #     total_terms += sum(preprocessor.positional_inverted_index[term][doc])

        return occurences

    def df(self, term):
        df = 0
        for doc_pos_list in self.positional_inverted_index[term]:
            if doc_pos_list != []:
                df += 1
        return df

    def calc_tt(self, doc):
        total_terms = 0
        for term in self.positional_inverted_index.keys():
            for i in self.positional_inverted_index[term]:
                if doc == str(int(list(i.keys())[0])):
                    total_terms += sum(i[doc])
        self.total_terms = total_terms
        print(total_terms)

    def term_weight(self, term, doc, tf, df):
        # calculates term weight = (1 + log(tf(t,d))) * log(N/df(t)) = lhs*rhs where:     (note both logs have base 10)
        # lhs = 1 + log(tf(t,d))
        # rhs = log(N/df(t))

        # ----------------------------
        # print(tf(term, doc, preprocessor))
        # print(df(term))
        print("1")
        print("term", term)
        print("doc", doc)
        print("log operand: ", self.tf(term, doc))
        lhs = 1 + log(tf)
        rhs = log(self.total_terms / df)
        print("2")
        return lhs * rhs

    def retrieval_score(self, query_list, doc):
        # returns retrieval score for query and document
        score = 0
        for term in query_list:
            print(term)
            # print("inverted index ", self.positional_inverted_index[term][doc])


            print("now calling term weight")
            # print(self.positional_inverted_index[term][doc] != [])
            # checks term exists in the pii
            if term in self.positional_inverted_index.keys():
                if doc in [str(int(list(doc_pos.keys())[0])) for doc_pos in self.positional_inverted_index[term]]:
                    tf = self.tf(term, doc)
                    df = self.df(term)
                    score += self.term_weight(term, doc, tf, df)
                    print("incremented")
        return score

    def ranked_retrieval(self, query_list):

        scores = {}
        for doc in docnos:
            print(doc)
            self.calc_tt(doc)
            if self.total_terms > 0:
                scores[doc] = self.retrieval_score(query_list, doc)
        # scores = sorted(scores)
        return scores
        #
        # print("Retrieval scores for query ranked highest to lowest: \n")
        # for key in scores.keys():
        #     print("document: ", key, " score: ", scores[key], "\n")




if __name__ == "__main__":

    f = open("./CW1collection/trec.5000.xml")
    input_stream = f.read()

    # parse xml input and get rid of tags
    documents = [x[7:len(x) - 8] for x in re.findall(r"<TEXT>[\s\S]*?</TEXT>", input_stream)]
    docnos = [x[7:len(x) - 8] for x in re.findall(r"<DOCNO>[\s\S]*?</DOCNO>", input_stream)]
    f.close()
    print("Options: ")
    print("\n 1. Preprocess documents \n 2. Import positional index file")
    choice = input("")

    if choice == "1":

        preprocessor = PreProcessor(documents)
        print("Constructing an inverted index...")
        preprocessor.pre_processor(documents, docnos)

    elif choice == "2":

        # reads in positional inverted index to prevent repeat preprocessing =============
        f = open("positional_inverted_index.txt")
        lines = f.readlines()

        p_i_i = {}

        current_term = ""
        for line in lines:
            if line[0] != ' ':

                current_term = line.split(':')[0]
                p_i_i[current_term] = []

            else:
                docno = line.split(":")[0].strip()

                pos = line.split(":")[1].strip().split(',')
                pos = [int(p.strip()) for p in pos]

                doc_pos = {docno: pos}
                p_i_i[current_term].append(doc_pos)

        # print(p_i_i)

        f.close()

        print("positional inverted index successfully read in")
        # read in complete

        # queries
        search = Search(p_i_i, len(documents), docnos)

        f = open("./CW1collection/queries.boolean.txt", 'r')
        query_list = f.read().split('\n')
        query_list = [q[2:] for q in query_list]
        # for i, query in enumerate(query_list[:10]):
        # print(i+1, " ", query)
        #     if i == 0:
        #         print(query)
        #         print(search.boolean_search(query))

        # boolean search
        # q1 = search.boolean_search(query_list[5])
        # print(q1)
        # q2 = search.boolean_search(query_list[1])
        # print(q2)
        #
        # q3 = search.boolean_search(query_list[2])
        # print(q3)
        # search_terms = query_list[3][1:len(query_list[3])-1].split(' ')
        # q4 = search.phrase_search(proximity=1, query_list=search_terms)

        # q5 = search.proximity_search(query_list[4])
        # print(q5)
        # q6 = search.boolean_search(query_list[5])
        #
        # search_terms = query_list[6][1:len(query_list[6])-1].split(' ')
        # q7 = search.phrase_search(proximity=1, query_list=search_terms)
        #
        # print(query_list[3])
        # search_terms = query_list[3][1:len(query_list[3])-1].split(' ')
        # search_terms = [stem(x.lower()) for x in search_terms]
        # q = search.phrase_search(proximity=1, query_list=search_terms)
        q = search.boolean_search(query_list[5])
        print("asdglhadshgsdhghahdgha", q)
        # print(query_list[9])
        # q10 = search.proximity_search(query_list[9])


        # x = "health industry".split(' ')
        # x = [stem(x.lower()) for x in x]
        # q = search.ranked_retrieval(x)
        # print(q)

        results = q
        qno = 6
        f = open("testoutput.txt", 'w')
        for i in sorted(results):
            out = str(qno) + ',' + str(i) + '\n'
            f.write(out)



    else:
        print("Incorrect input. Exiting.")



    #
    # # querying = True
    # # while querying:
    # print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
    # print("~~QUERY MODE~~")
    # print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
    #     # query_type = input("Options:\n 1: Boolean Search\n 2: Phrase Search\n 3: Ranked Retrieval\n 4: Proximity "
    #     #                    "Search\n 5: Exit\n")
    #     # print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
    #     # if query_type == "5":
    #     #     querying = False
    #     # elif query_type == "1":
    #     #     search.boolean_search()
    #     # elif query_type == "2":
    #     #     search.phrase_search(proximity=1)
    #     # elif query_type == "3":
    #     #     search.ranked_retrieval()
    #     # elif query_type == "4":
    #     #     search.proximity_search()
    #     # else:
    #     #     print("incorrect input")
    # f = open("./CW1collection/queries.boolean.txt", 'r')
    # query_list = f.read().split('\n')
    # query_list = [q[2:] for q in query_list]
    # for i, query in enumerate(query_list[:10]):
    #         # print(i+1, " ", query)
    # #     if i == 0:
    # #         print(query)
    # #         print(search.boolean_search(query))

    # boolean search
    # search.boolean_search(query_list[0])
    # search.boolean_search(query_list[1])
    # search.boolean_search(query_list[2])
    #
    # #phrase search
    # search_terms = query_list[3][1:len(query_list[3])-1].split(' ')
    # search.phrase_search(proximity=1, query_list=search_terms)
    #
    # # proximity search
    # search.proximity_search(query_list[4])
    #
    # search_terms = query_list[5][1:12].split(' ')
    # docs = search.phrase_search(proximity=1, query_list=search_terms)
    # # [1:len(query_list[3]) - 1].split(' ')
    # print(query_list[5])
    # print(search_terms)
    # print(query_list[5])
    # search.boolean_search(query_list[5])
    # result = search.boolean_search("\"wall street\" AND \"dow jones\" AND test")
    # result = search.boolean_search("test")
    # print(result)

    #
    #
