import xlrd, json
import unicodedata
import xlsxwriter
import string, re, nltk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
from nltk import word_tokenize, pos_tag
from nltk.stem.porter import PorterStemmer
from collections import defaultdict
words = set(nltk.corpus.words.words())
stop = set(stopwords.words('english'))
exclude = set(string.punctuation)
lemma = WordNetLemmatizer()

token_dict = {}
stemmer = PorterStemmer()

printable = set(string.printable)

def clean(doc):
    stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
    punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
    normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
    normalized = " ".join(stemmer.stem(word) for word in normalized.split())
    return normalized

def strip_non_ascii(s):
    if isinstance(s, unicode):
        nfkd = unicodedata.normalize('NFKD', s)
        return str(nfkd.encode('ASCII', 'ignore').decode('ASCII'))
    else:
        return s

def preprocess_tweet(tweet):
    '''Preprocesses the tweet text and break the hashtags'''

    tweet = strip_non_ascii(tweet)
    
#     print tweet
    tweet = str(tweet.lower())

    if tweet[:1] =="\n":
        tweet=tweet[1:len(tweet)]

    # remove retweet handler
    if tweet[:2] == "rt":
        try:
            colon_idx = tweet.index(": ")
            tweet = tweet[colon_idx + 2:]
        except BaseException:
            pass

    # remove url from tweet
    tweet = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*','URL',tweet)

    # remove non-ascii characters
    tweet = "".join([x for x in tweet if x in printable])

    # additional preprocessing
    tweet = tweet.replace("\n", " ").replace(" https", "").replace("http", "")

    # remove all mentions
    tweet = re.sub(r"@\w+", "@USER", tweet)

    # remove all mentions
    tweet = re.sub(r"#\w+", "#HASH", tweet)

    # padding punctuations
    tweet = re.sub('([,!?():])', r' \1 ', tweet)

    tweet = tweet.replace(". ", " . ").replace("-", " ")

    # shrink blank spaces in preprocessed tweet text to only one space
    tweet = re.sub('\s{2,}', ' ', tweet)

    tweet = " ".join(w for w in nltk.wordpunct_tokenize(tweet) if w.lower() in words or not w.isalpha())

    tweet = re.sub("^\d+\s|\s\d+\s|\s\d+$", " NUM ", tweet)

    # # remove consecutive duplicate tokens which causes an explosion in tree
    # while re.search(r'\b(.+)(\s+\1\b)+', tweet):
    #     tweet = re.sub(r'\b(.+)(\s+\1\b)+', r'\1', tweet)

#     tweet = clean(tweet)

    tweet = tweet.replace('\n','. ').replace('\t',' ').replace(',',' ').replace('"',' ').replace("'"," ").replace(";"," ").replace("\n"," ").replace("\r"," ")

    # remove trailing spaces
    tweet = tweet.strip()



    return tweet

data=[]
with open('Florence.json','r') as sample:
    for i,line in enumerate(sample):
        data.append(json.loads(line))
        #if i==500:
        #    break
print(len(data))
txt=[]
tm=[]
ur=[]
t_id=[]

d=defaultdict(int)
for i,e in enumerate(data):
    text = e['tweet']['text']
    text = strip_non_ascii(text)
    try:
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
    except:
        pass
#     text = preprocess_tweet(text)
#     print (text)
    if text[:2]=='RT':
        continue
    tweet_id = e['tweet']['id']
    time = e['date']
    img = []
    try:
        for item in e['tweet']['urls']:
            img.append(item)
    except:
        continue
    if d[text]==1:
        continue
    d[text]+=1
    t_id.append(tweet_id)
    txt.append(text)
    tm.append(time)
    ur.append(img)

workbook = xlsxwriter.Workbook("florence.xlsx",{'strings_to_numbers': True})
worksheet = workbook.add_worksheet()
i=0
for a,b,c,d in zip(t_id,tm,txt,ur):
    worksheet.write(i,0, a)
    worksheet.write(i,1, b)
    worksheet.write(i,2, c)
    if d:
        worksheet.write(i,3, d[0])
    i+=1
workbook.close()
