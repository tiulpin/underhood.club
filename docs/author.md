<!-- markdownlint-disable -->

<a href="../underhood/author.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `author`
Everything related to Twitter API happens right here. 

**Global Variables**
---------------
- **expansions**
- **tweet_fields**
- **media_fields**

---

<a href="../underhood/author.py#L130"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `extract_username`

```python
extract_username(author: Author) → str
```

Get username from description or the first author tweet by searching for @. 



**Args:**
 
 - <b>`author`</b>:  Author class object 



**Returns:**
 username if found else an empty string 


---

<a href="../underhood/author.py#L152"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `extract_name`

```python
extract_name(author: Author) → str
```

Get author name from description or the first author tweet by using Spacy NER. 



**Args:**
 
 - <b>`author`</b>:  Author class object 



**Returns:**
 name if found else an empty string 


---

<a href="../underhood/author.py#L30"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Author`
Class that represents an author inside some underhood account, tweets and has even few API calls when needed. 

<a href="../<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(
    underhood: str,
    twitter_token: InitVar[str],
    name: str = '',
    username: str = '',
    has_twitter: bool = True,
    avatar: str = '',
    first_id: InitVar[int] = 0,
    until_id: InitVar[int] = 0
) → None
```






---

#### <kbd>property</kbd> author_hash

Internal first author tweet hash needed for different purposes. 

---

#### <kbd>property</kbd> description

Profile description property. 



---

<a href="../underhood/author.py#L102"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_tweet`

```python
get_tweet(tweet_id: int) → Tweet
```

Get tweet from Twitter API by id. 


