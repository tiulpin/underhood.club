<!-- markdownlint-disable -->

<a href="../underhood/utils.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `utils`
It's not AI, it's Machine Learning. 

**Global Variables**
---------------
- **stop_words**

---

<a href="../underhood/utils.py#L23"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `md_link`

```python
md_link(display: str, url: str) → str
```

Make Markdown link from the given URL. 


---

<a href="../underhood/utils.py#L28"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `clean_tweets`

```python
clean_tweets(tweets: list) → uple[Dictionary, list[list[tuple[int, int]]]]
```

Prepare (clean) tweet texts for running topic modeling on it. 



**Args:**
 
 - <b>`tweets`</b>:  list of strings (tweets texts) 



**Returns:**
 cleaned tweets 


---

<a href="../underhood/utils.py#L68"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `print_topics`

```python
print_topics(tweets: list) → None
```

Pretty simple topic-modeling with LDA model on tweets: print the results right into stdout. TODO: make it better 

**Args:**
 
 - <b>`tweets`</b>:  list of tweets 


---

<a href="../underhood/utils.py#L88"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `tweet_id_from_url`

```python
tweet_id_from_url(url: str)
```

Obtain tweet id from environment (from URL). e.g. https://twitter.com/dsunderhood/status/1384130447999787017?s=20 -> 1384130447999787017 


---

<a href="../underhood/utils.py#L17"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `NotionTableOfContents`
Notion table of contents block. 


---

#### <kbd>property</kbd> children





---

#### <kbd>property</kbd> id





---

#### <kbd>property</kbd> is_alias





---

#### <kbd>property</kbd> parent





---

#### <kbd>property</kbd> role





---

#### <kbd>property</kbd> space_info










---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
