"""
naive_bayes_classifier.py
Naive Bayes intent classifier — trained on labeled example sentences.

Replaces the pure keyword approach in intent_detector.py with a real
probabilistic ML model (pure Python + no external ML libraries needed).

How Naive Bayes works:
  P(intent | words) ∝ P(intent) × ∏ P(word | intent)

We train it on ~60 labeled sentences, then use it to classify new input.
The keyword detector is kept as a fallback when confidence is low.
"""



import re

import math

from collections import defaultdict





                                                                                

                        

                                                              



TRAINING_DATA = [

                                                                                

    ("what is recursion",                           "question"),

    ("explain big o notation",                      "question"),

    ("what are pointers in c",                      "question"),

    ("define normalization in database",            "question"),

    ("how does tcp work",                           "question"),

    ("what is the difference between stack and queue", "question"),

    ("explain deadlock with example",               "question"),

    ("what is machine learning",                    "question"),

    ("describe bubble sort algorithm",              "question"),

    ("how does virtual memory work",                "question"),

    ("what is a primary key",                       "question"),

    ("explain osi model layers",                    "question"),

    ("what is overfitting in ml",                   "question"),

    ("how does binary search work",                 "question"),

    ("what are joins in sql",                       "question"),

    ("tell me about neural networks",               "question"),

    ("what is paging in os",                        "question"),

    ("clarify the concept of inheritance",          "question"),

    ("describe the acid properties",                "question"),

    ("what is time complexity",                     "question"),



                                                                                

    ("study plan for python 5 days 3 hours",        "planning"),

    ("create a study plan for database",            "planning"),

    ("make a schedule for my os exam",              "planning"),

    ("study plan for machine learning 7 days",      "planning"),

    ("help me plan my studies for networks",        "planning"),

    ("i need a revision plan for data structures",  "planning"),

    ("generate a plan for ai 5 days 4 hours",       "planning"),

    ("add plan for python",                         "planning"),

    ("new study plan",                              "planning"),

    ("add task",                                    "planning"),

    ("i want to add a study plan",                  "planning"),

    ("create a timetable for exam preparation",     "planning"),

    ("plan for database 6 days 2 hours per day",    "planning"),

    ("schedule for machine learning course",        "planning"),

    ("exam in 5 days need a plan",                  "planning"),

    ("organize my study sessions for os",           "planning"),

    ("learning path for python beginner",           "planning"),

    ("add a new plan",                              "planning"),

    ("make plan",                                   "planning"),



                                                                                

    ("show my progress",                            "progress"),

    ("how am i doing",                              "progress"),

    ("mark task as done",                           "progress"),

    ("i finished the arrays topic",                 "progress"),

    ("i completed linked lists",                    "progress"),

    ("what tasks are remaining",                    "progress"),

    ("show my tasks",                               "progress"),

    ("update my progress",                          "progress"),

    ("check off recursion",                         "progress"),

    ("i studied sorting today",                     "progress"),

    ("task done",                                   "progress"),

    ("i did the sql chapter",                       "progress"),

    ("how many tasks are left",                     "progress"),

    ("what is my completion status",                "progress"),

    ("my pending tasks",                            "progress"),



                                                                                

    ("what should i study next",                    "suggestion"),

    ("suggest what to do next",                     "suggestion"),

    ("what do i study now",                         "suggestion"),

    ("i am stuck on graphs",                        "suggestion"),

    ("recommend the next topic",                    "suggestion"),

    ("i need advice on what to study",              "suggestion"),

    ("should i take a break",                       "suggestion"),

    ("what is the next topic for me",               "suggestion"),

    ("i am struggling with recursion",              "suggestion"),

    ("what should i focus on",                      "suggestion"),

    ("give me a study tip",                         "suggestion"),

    ("what do i do next",                           "suggestion"),



                                                                                

    ("hello",                                       "general"),

    ("hi there",                                    "general"),

    ("good morning",                                "general"),

    ("thanks a lot",                                "general"),

    ("thank you",                                   "general"),

    ("great job",                                   "general"),

    ("help me",                                     "general"),

    ("what can you do",                             "general"),

    ("who are you",                                 "general"),

    ("good evening",                                "general"),

]





                                                                                



class NaiveBayesClassifier:

    """
    Multinomial Naive Bayes with Laplace smoothing.
    Trains on word frequencies per class.
    """



    def __init__(self, alpha: float = 1.0):

        """alpha: Laplace smoothing parameter (1 = add-one smoothing)."""

        self.alpha      = alpha

        self.classes    = []

        self.log_priors = {}                        

        self.log_likelihoods = {}                          

        self.vocab      = set()

        self._trained   = False



    def _tokenize(self, text: str) -> list:

        """Lowercase, remove punctuation, split into words."""

        text = text.lower().strip()

        return re.findall(r'\b[a-z]+\b', text)



    def train(self, data: list):

        """
        Train on list of (text, label) pairs.
        """

                                          

        word_counts  = defaultdict(lambda: defaultdict(int))

        class_totals = defaultdict(int)

        class_counts = defaultdict(int)



        for text, label in data:

            tokens = self._tokenize(text)

            for word in tokens:

                word_counts[label][word] += 1

                class_totals[label]      += 1

                self.vocab.add(word)

            class_counts[label] += 1



        total_docs   = len(data)

        self.classes = list(class_counts.keys())

        vocab_size   = len(self.vocab)



                                         

        for cls in self.classes:

            self.log_priors[cls] = math.log(class_counts[cls] / total_docs)



                                                                            

        self.log_likelihoods = {}

        for cls in self.classes:

            self.log_likelihoods[cls] = {}

            total = class_totals[cls]

            for word in self.vocab:

                count = word_counts[cls].get(word, 0)

                                                                         

                self.log_likelihoods[cls][word] = math.log(

                    (count + self.alpha) / (total + self.alpha * vocab_size)

                )

                                                     

            self.log_likelihoods[cls]["<UNK>"] = math.log(

                self.alpha / (total + self.alpha * vocab_size)

            )



        self._trained = True



    def predict(self, text: str) -> dict:

        """
        Classify text. Returns:
        {
          "intent":     predicted class,
          "confidence": "high" | "medium" | "low",
          "scores":     {class: log_prob, ...},
          "raw":        original text
        }
        """

        if not self._trained:

            raise RuntimeError("Model not trained. Call .train() first.")



        tokens = self._tokenize(text)



                                              

        log_posteriors = {}

        for cls in self.classes:

            score = self.log_priors[cls]

            for word in tokens:

                if word in self.log_likelihoods[cls]:

                    score += self.log_likelihoods[cls][word]

                else:

                    score += self.log_likelihoods[cls]["<UNK>"]

            log_posteriors[cls] = score



                                                       

        best_class = max(log_posteriors, key=log_posteriors.get)



                                                                          

        max_log = max(log_posteriors.values())

        exps    = {c: math.exp(v - max_log) for c, v in log_posteriors.items()}

        total   = sum(exps.values())

        probs   = {c: exps[c] / total for c in exps}



        best_prob = probs[best_class]

        if best_prob >= 0.60:

            confidence = "high"

        elif best_prob >= 0.35:

            confidence = "medium"

        else:

            confidence = "low"



        return {

            "intent":     best_class,

            "confidence": confidence,

            "scores":     probs,

            "raw":        text

        }





                                                                               

_classifier = NaiveBayesClassifier(alpha=1.0)

_classifier.train(TRAINING_DATA)





def classify_intent(text: str) -> dict:

    """
    Public function: classify user intent using Naive Bayes.
    Falls back to keyword detector if confidence is low.
    Returns same schema as detect_intent() for drop-in compatibility.
    """

    nb_result = _classifier.predict(text)



                                           

    if nb_result["confidence"] in ("high", "medium"):

        return {

            "intent":     nb_result["intent"],

            "confidence": nb_result["confidence"],

            "raw":        text,

            "method":     "naive_bayes"

        }



                                                 

    from modules.intent_detector import detect_intent as keyword_detect

    kw_result = keyword_detect(text)

    kw_result["method"] = "keyword_fallback"

    return kw_result





def get_classifier_info() -> dict:

    """Return info about the trained model (useful for viva demos)."""

    return {

        "model":        "Multinomial Naive Bayes",

        "training_samples": len(TRAINING_DATA),

        "vocabulary_size":  len(_classifier.vocab),

        "classes":      _classifier.classes,

        "smoothing":    f"Laplace (alpha={_classifier.alpha})"

    }
