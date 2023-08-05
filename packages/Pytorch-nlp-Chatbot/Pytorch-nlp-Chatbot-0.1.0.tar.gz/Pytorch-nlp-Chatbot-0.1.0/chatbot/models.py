# Authors: Koro_Is_Coding
# License: Apache v2.0

import requests
from string import Template
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import operator


class SearchException(Exception):
    print("no enough results")


def cal_tfidf(results):
    words = []
    for result in results:
        words.extend(re.sub("[^\w]", " ", result["title"]).split())
        words.extend(re.sub("[^\w]", " ", result["snippet"]).split())

    tv = TfidfVectorizer()
    tv.fit_transform(words)
    return dict(zip(tv.get_feature_names_out(), tv.idf_))


class SearchEngineStruct:
    def __init__(
        self,
        google_api_key="AIzaSyAGHYwrgMmAHlFwM-GmS2anQ7xWu7qcIjA",
        google_engine_key="7a8bd65adc0b760d8",
    ):
        self.google_api_key = google_api_key
        self.google_engine_key = google_engine_key
        self.top_result = list()
        self.relevant = list()
        self.irrelevant = list()
        self.query = ""

    def get_top_result(self):
        return list(self.top_result)

    def set_query(self, seed_query):
        self.query = seed_query

    def get_query(self):
        return self.query

    def call_google_custom_search_api(self):
        URL = Template("https://www.googleapis.com/customsearch/v1?key=$client_key&cx=$engine_key&q=$query")
        url = URL.substitute(
            client_key=self.google_api_key,
            engine_key=self.google_engine_key,
            query=self.query,
        )
        response = requests.get(url)
        if response is None:
            raise SearchException
        else:
            try:
                if len(response.json()["items"]) < 10:
                    raise SearchException
                else:
                    self.top_result = response.json()["items"]
            except KeyError:
                raise SearchException

    def choose_relevant(self):
        """
        This function takes a list of search results and iteratively displays each result to the user
        and asks if it is relevant or not. The user input is used to split the search results into two
        separate lists: relevant and irrelevant.

        Args:
        - results (list of dict): a list of search results returned by the search engine. Each search
          result is a dictionary with the following keys: "link", "title", and "snippet".

        Returns:
        - accuracy (float): the percentage of relevant search results out of the total number of
          search results (i.e., the number of search results in the input list).
        """
        results = self.top_result
        count = 0

        for i in range(len(results)):
            result = results[i]
            print("Result %d" % (i + 1))
            print("[")
            print(" URL: " + result["link"])
            print(" Title: " + result["title"])
            print(" Summary: " + result["snippet"])
            print("]")
            ans = input("Relevant (Y/N)?")

            if ans.upper() == "Y":
                count += 1
                self.relevant.append(result)
                print("RELEVANT")
            else:
                self.irrelevant.append(result)
                print("NOT RELEVANT")
        accuracy = count / float(10)
        return accuracy

    def add_and_reorder_words(self):
        query_old = self.query
        # Calculate TF-IDF scores for words in relevant and irrelevant results
        relevant_tfidf = cal_tfidf(self.relevant)
        irrelevant_tfidf = cal_tfidf(self.irrelevant)
        # Find words that are unique to relevant results
        unique_words = {key: value for key, value in relevant_tfidf.items() if key not in irrelevant_tfidf}
        # Sort unique words by their TF-IDF scores
        unique_words_sorted = sorted(unique_words.items(), key=operator.itemgetter(1))
        # Add the top two new words different from the original query
        count = 0
        modified_query = []
        words_old = query_old.split()
        for key in unique_words_sorted:
            if key[0] in words_old:
                modified_query.append(key[0])
                words_old.remove(key[0])
            elif count < 2 and key[0] not in query_old:
                modified_query.append(key[0])
                count += 1
        # Add the remaining words from the original query
        for word in words_old:
            modified_query.append(word)
            self.query = modified_query
